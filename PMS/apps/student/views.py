from django.template.response import TemplateResponse
import pandas as pd
import re
from apps.authuser.models import StudentProxyModel
from apps.course.forms import PriorityEntryDetailFormset
from apps.course.models import ElectiveSubject
from apps.student.formsets import PriorityFormset
from apps.system.views import get_admin_context


def enter_priority_in_bulk(request, *args, **kwargs):
    context = get_admin_context()
    context['has_data'] = False
    
    if request.method == 'GET':
        form = PriorityEntryDetailFormset    
    elif '_upload_excel' in request.POST:
        form = PriorityEntryDetailFormset(request.POST)
        excel_file = request.FILES.get('excel_file')
        
        if excel_file:
            # Check if form data has semester/session info
            if form.is_valid():
                semester = form.cleaned_data.get('semester', None)
                stream = form.cleaned_data.get('stream', None)
                batch = form.cleaned_data.get('batch', None)
                
                try:
                    result = extract_student_pref(excel_file, semester, stream, batch)
                    if result['success']:
                        if result['error']:
                            context['message'] = f'Excel file processed with warnings: {result["error"]}'
                        else:
                            context['message'] = f'Excel file "{excel_file.name}" uploaded successfully! {result["count"]} students processed.'
                    else:
                        context['message'] = f'Error: {result["error"]}'
                except Exception as e:
                    context['message'] = f'Error processing Excel file: {str(e)}'
            else:
                context['message'] = 'Please select Batch, Level, Stream, and Semester before uploading Excel file.'
        else:
            context['message'] = 'Please select an Excel file to upload.'
    elif '_get_formset' in request.POST:
        form = PriorityEntryDetailFormset(request.POST)
        if form.is_valid():
            stream = form.cleaned_data.get('stream', None)
            semester = form.cleaned_data.get('semester', None)
            batch = form.cleaned_data.get('batch', None)
            subjects = ElectiveSubject.objects.filter(elective_for=semester, stream=stream)
            student_queryset = StudentProxyModel.objects.filter(batch=batch, stream=stream)
            initial_data = [{'student': student, 'priority': ''} for student in student_queryset]
            context['has_data'] = True
            context['formset'] = PriorityFormset(priority_detail_form_data=form.cleaned_data, initial=initial_data)
            context['elective_subjects'] = subjects
            context['form_data'] = form.cleaned_data
    elif '_post_priorities' in request.POST:
        form = PriorityEntryDetailFormset(request.POST)
        if form.is_valid():
            stream = form.cleaned_data.get('stream', None)
            semester = form.cleaned_data.get('semester', None)
            subjects = ElectiveSubject.objects.filter(elective_for=semester, stream=stream)
            context['has_data'] = True
            formset = PriorityFormset(priority_detail_form_data=form.cleaned_data, data=request.POST)
            context['formset'] = formset
            context['elective_subjects'] = subjects
            context['form_data'] = form.cleaned_data
            if formset.is_valid():
                formset.save()
                context['message'] = 'Data inserted successfully'
                context['is_success'] = True
    context['form'] = form
    return TemplateResponse(
        request,
        'admin/priority/enter_priority_in_bulk.html',
        context
    )
def extract_student_pref(file, semester, stream, batch):
    """
    Extract student preferences from Excel file
    Supports flexible headers and priority columns (Priority 1..N).
    For masters students, if desired electives column is missing/empty, defaults to 3.
    For non-masters students, default remains 2.
    """
    try:
        def _normalize_text(value):
            text = '' if value is None else str(value)
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        def _normalize_key(value):
            return _normalize_text(value).lower()

        def _normalize_subject(value):
            # Handles entries like: "Quantum Computing (Dr. ... )"
            text = _normalize_text(value)
            text = re.sub(r'\([^)]*\)', '', text)
            text = re.sub(r'\s+', ' ', text).strip().lower()
            return text

        def _find_column(df_columns, aliases):
            normalized = {_normalize_key(col): col for col in df_columns}
            for alias in aliases:
                alias_key = _normalize_key(alias)
                if alias_key in normalized:
                    return normalized[alias_key]
            return None

        # Read Excel file
        df = pd.read_excel(file)

        # Detect columns in a flexible way
        roll_number_column = _find_column(df.columns, [
            'Roll Number', 'Roll No', 'Roll No.', 'Roll', 'Symbol Number', 'Student ID'
        ])
        if not roll_number_column:
            return {
                'success': False,
                'error': 'Could not find a roll number column. Supported headers: Roll Number / Roll No / Roll.'
            }

        desired_elective_column = _find_column(df.columns, [
            'How many electives do you want to register?',
            'How many electives do you want to take?',
            'No of electives',
            'Number of electives',
            'Desired Number of Subjects',
            'Desired number of subjects'
        ])

        priority_columns = []
        for col in df.columns:
            key = _normalize_key(col)
            match = re.match(r'^priority\s*(\d+)$', key)
            if match:
                priority_columns.append((int(match.group(1)), col))

        priority_columns = [col for _, col in sorted(priority_columns, key=lambda x: x[0])]
        if not priority_columns:
            return {
                'success': False,
                'error': 'No priority columns found. Expected columns like Priority 1, Priority 2, ...'
            }
        
        # Validate that DataFrame is not empty
        if df.empty:
            return {
                'success': False,
                'error': 'Excel file is empty. Please add student data.'
            }
        
        # Get available subjects from database for the specified semester and stream
        available_subjects = list(ElectiveSubject.objects.filter(
            elective_for=semester, 
            stream=stream
        ).values_list('subject_name', flat=True))

        # Build normalized lookup for robust matching
        normalized_subject_lookup = {}
        for subject_name in available_subjects:
            normalized_subject_lookup[_normalize_key(subject_name)] = subject_name
            normalized_subject_lookup[_normalize_subject(subject_name)] = subject_name
        
        # Process each row
        processed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extract data
                roll_number = _normalize_text(row.get(roll_number_column))
                
                # Validate roll number
                if not roll_number or roll_number.lower() == 'nan':
                    errors.append(f'Row {index + 2}: Roll Number is empty')
                    continue
                if len(roll_number) < 6:  # Minimum length check
                    errors.append(f'Row {index + 2}: Invalid roll number format. Expected format: 079bct007')
                    continue
                # Collect all priorities from Priority 1..N
                priorities = [_normalize_text(row.get(col)) for col in priority_columns]
                
                # Remove empty/nan values
                priorities = [p for p in priorities if p and p.lower() != 'nan']

                if not priorities:
                    errors.append(f'Row {index + 2}: No priorities provided')
                    continue

                  # Validate that subjects exist in database (flexible matching)
                invalid_subjects = []
                matched_subjects = {}  # Store mapping of input to actual database subject
                
                for priority in priorities:
                    priority_key = _normalize_key(priority)
                    priority_subject_key = _normalize_subject(priority)

                    exact_match = normalized_subject_lookup.get(priority_key) or normalized_subject_lookup.get(priority_subject_key)

                    if exact_match is not None:
                        matched_subjects[priority] = exact_match
                    else:
                        # Try partial match in both directions
                        partial_match = None
                        for db_subject in available_subjects:
                            db_key = _normalize_key(db_subject)
                            db_subject_key = _normalize_subject(db_subject)
                            if (
                                priority_key in db_key or db_key in priority_key or
                                priority_subject_key in db_subject_key or db_subject_key in priority_subject_key
                            ):
                                partial_match = db_subject
                                break
                        
                        if partial_match:
                            matched_subjects[priority] = partial_match
                        else:
                            invalid_subjects.append(priority)
                
                if invalid_subjects:
                    errors.append(f'Row {index + 2}: Invalid subject names: {", ".join(invalid_subjects)}')
                    continue
                
                # Check for duplicate subjects (after matching with DB names)
                resolved_priorities = [matched_subjects[p] for p in priorities]
                if len(set(resolved_priorities)) != len(resolved_priorities):
                    errors.append(f'Row {index + 2}: Duplicate subjects found. Each subject should appear only once.')
                    continue
                  # TODO: Save to database
                # Find student by roll number and save priorities
                try:
                    student = StudentProxyModel.objects.get(roll_number=roll_number)

                    # Determine desired number of subjects
                    is_masters_student = bool(student.level and 'masters' in student.level.name.lower())
                    default_desired_count = 3 if is_masters_student else 2
                    desired_number_of_subjects = default_desired_count

                    if desired_elective_column:
                        desired_raw = row.get(desired_elective_column)
                        if pd.notna(desired_raw):
                            desired_text = _normalize_text(desired_raw)
                            try:
                                parsed_value = int(float(desired_text))
                                if parsed_value > 0:
                                    desired_number_of_subjects = parsed_value
                            except (TypeError, ValueError):
                                pass

                    # Cannot request more subjects than priorities provided
                    desired_number_of_subjects = min(desired_number_of_subjects, len(resolved_priorities))
                    
                    # Save priorities to database
                    from apps.student.models import ElectivePriority
                      # Clear existing priorities for this student for this session
                    ElectivePriority.objects.filter(student=student, session=semester).delete()
                      # Save new priorities
                    for priority_index, actual_subject_name in enumerate(resolved_priorities, 1):
                        subject = ElectiveSubject.objects.get(
                            subject_name=actual_subject_name,
                            elective_for=semester,
                            stream=stream,
                        )
                        ElectivePriority.objects.create(
                            student=student,
                            subject=subject,
                            priority=priority_index,
                            session=semester,  # Set the session/semester
                            desired_number_of_subjects=desired_number_of_subjects
                        )
                    
                except StudentProxyModel.DoesNotExist:
                    errors.append(f'Row {index + 2}: Student with roll number "{roll_number}" not found in database')
                    continue
                except ElectiveSubject.DoesNotExist as e:
                    errors.append(f'Row {index + 2}: Subject not found in database - {str(e)}')
                    continue
                
                processed_count += 1
                
            except Exception as e:
                errors.append(f'Row {index + 2}: Error processing row - {str(e)}')
        
        # Return results
        if errors:
            error_msg = f'Processed {processed_count} students successfully. Errors: {"; ".join(errors[:3])}'  # Show first 3 errors
            if len(errors) > 3:
                error_msg += f' and {len(errors) - 3} more errors.'
            return {
                'success': True,
                'count': processed_count,
                'error': error_msg
            }
        else:
            return {
                'success': True,
                'count': processed_count,
                'error': None
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to read Excel file: {str(e)}'
        }
