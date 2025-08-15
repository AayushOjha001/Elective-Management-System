from django.template.response import TemplateResponse
import pandas as pd
from apps.authuser.models import StudentProxyModel
from apps.course.forms import PriorityEntryDetailFormset
from apps.course.models import ElectiveSubject
from apps.student.formsets import PriorityFormset
from apps.system.views import get_admin_context


def clean_whitespace(text):
    """
    Clean all types of whitespace from text:
    - Strip leading/trailing whitespace
    - Replace multiple internal spaces with single space
    - Handle various whitespace characters
    """
    if not text or str(text).lower() == 'nan':
        return ''
    
    # Convert to string and normalize whitespace
    cleaned = str(text).strip()
    # Replace multiple whitespace characters with single space
    cleaned = ' '.join(cleaned.split())
    return cleaned


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
    Expected format: Roll Number | Priority 1 | Priority 2 | Priority 3 | Priority 4 | Priority 5 | [Optional: no_of_electives]
    Where priorities contain subject names, not numbers
    
    The no_of_electives column is optional:
    - If present, uses the specified number for each student (bounded between 1-5)
    - If not present, defaults to 2 electives for all students
    """
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Define required columns (minimum needed)
        required_columns = ['Roll Number', 'Priority 1', 'Priority 2']
        
        # Check if optional no_of_electives column exists
        has_no_of_electives = 'no_of_electives' in df.columns
        
        # Check if all required columns exist
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                'success': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}. Required columns are: {", ".join(required_columns)}'
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
          # Process each row
        processed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:                # Extract data and apply comprehensive whitespace cleaning using helper function
                roll_number = clean_whitespace(row['Roll Number'])
                priority_1 = clean_whitespace(row['Priority 1'])
                priority_2 = clean_whitespace(row['Priority 2'])
                priority_3 = clean_whitespace(row['Priority 3'])
                priority_4 = clean_whitespace(row['Priority 4'])
                priority_5 = clean_whitespace(row['Priority 5'])
                
                # Extract desired number of electives if column exists, otherwise default to 2
                if has_no_of_electives:
                    no_of_electives = row.get('no_of_electives', 2)
                    # Handle potential NaN or non-numeric values
                    try:
                        no_of_electives = int(no_of_electives) if pd.notna(no_of_electives) else 2
                        # Ensure reasonable bounds (between 1 and 5)
                        no_of_electives = max(1, min(5, no_of_electives))
                    except (ValueError, TypeError):
                        no_of_electives = 2
                else:
                    no_of_electives = 2
                
                # Validate roll number
                if not roll_number:
                    errors.append(f'Row {index + 2}: Roll Number is empty')
                    continue
                if len(roll_number) < 6:  # Minimum length check
                    errors.append(f'Row {index + 2}: Invalid roll number format. Expected format: 079bct007')
                    continue
                      # Collect priorities based on desired number of electives
                all_priorities = [priority_1, priority_2, priority_3, priority_4, priority_5]
                priorities = []
                
                # Only collect the number of priorities the student wants
                for i in range(min(no_of_electives, len(all_priorities))):
                    if all_priorities[i]:  # clean_whitespace already handles nan and empty cases
                        priorities.append(all_priorities[i])
                
                # Ensure we have at least the desired number of non-empty priorities
                if len(priorities) < no_of_electives:
                    errors.append(f'Row {index + 2}: Student wants {no_of_electives} electives but only provided {len(priorities)} valid priorities')
                    continue# Validate that subjects exist in database (flexible matching)
                invalid_subjects = []
                matched_subjects = {}  # Store mapping of input to actual database subject
                
                for priority in priorities:
                    # Normalize priority for matching (remove extra spaces, consistent casing)
                    normalized_priority = ' '.join(priority.split()).strip()
                    
                    # Try exact match first (case-insensitive)
                    exact_match = None
                    for db_subject in available_subjects:
                        normalized_db_subject = ' '.join(db_subject.split()).strip()
                        if normalized_priority.lower() == normalized_db_subject.lower():
                            exact_match = db_subject
                            break
                    
                    if exact_match:
                        matched_subjects[priority] = exact_match
                    else:
                        # Try partial match (input subject is contained in database subject)
                        partial_match = None
                        for db_subject in available_subjects:
                            normalized_db_subject = ' '.join(db_subject.split()).strip()
                            if normalized_priority.lower() in normalized_db_subject.lower():
                                partial_match = db_subject
                                break
                        
                        if partial_match:
                            matched_subjects[priority] = partial_match
                        else:
                            invalid_subjects.append(priority)
                
                if invalid_subjects:
                    errors.append(f'Row {index + 2}: Invalid subject names: {", ".join(invalid_subjects)}')
                    continue
                  # Check for duplicate subjects
                if len(set(priorities)) != len(priorities):
                    errors.append(f'Row {index + 2}: Duplicate subjects found. Each subject should appear only once.')
                    continue
                
                # Find student by roll number and save priorities
                try:
                    student = StudentProxyModel.objects.get(roll_number=roll_number)
                    print(f"Processing: {roll_number} (Student: {student.name})")
                    print(f"Priorities: {priorities}")
                    print(f"Desired number of electives: {no_of_electives}")
                    
                    # Save priorities to database
                    from apps.student.models import ElectivePriority
                    
                    # Clear existing priorities for this student for this session
                    ElectivePriority.objects.filter(student=student, session=semester).delete()
                    
                    # Save new priorities
                    for priority_index, subject_name in enumerate(priorities, 1):
                        # Use matched subject name from database
                        actual_subject_name = matched_subjects.get(subject_name, subject_name)
                        subject = ElectiveSubject.objects.get(subject_name=actual_subject_name)
                        ElectivePriority.objects.create(
                            student=student,
                            subject=subject,
                            priority=priority_index,
                            session=semester,  # Set the session/semester
                            desired_number_of_subjects=no_of_electives  # Use the extracted value
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
