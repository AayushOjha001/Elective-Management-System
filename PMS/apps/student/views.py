from django.template.response import TemplateResponse
import pandas as pd
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
    Expected format: Roll Number | Priority 1 | Priority 2 | Priority 3 | Priority 4 | Priority 5
    Where priorities contain subject names, not numbers
    """
    try:
        # Read Excel file
        df = pd.read_excel(file)
        
        # Define required columns
        required_columns = ['Roll Number', 'Priority 1', 'Priority 2', 'Priority 3', 'Priority 4', 'Priority 5']
        
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
            try:
                # Extract data
                roll_number = str(row['Roll Number']).strip()
                priority_1 = str(row['Priority 1']).strip()
                priority_2 = str(row['Priority 2']).strip()
                priority_3 = str(row['Priority 3']).strip()
                priority_4 = str(row['Priority 4']).strip()
                priority_5 = str(row['Priority 5']).strip()
                
                # Validate roll number
                if not roll_number or roll_number.lower() == 'nan':
                    errors.append(f'Row {index + 2}: Roll Number is empty')
                    continue
                if len(roll_number) < 6:  # Minimum length check
                    errors.append(f'Row {index + 2}: Invalid roll number format. Expected format: 079bct007')
                    continue
                # Collect all priorities
                priorities = [priority_1, priority_2, priority_3, priority_4, priority_5]
                
                # Remove empty/nan values
                priorities = [p for p in priorities if p and p.lower() != 'nan']
                  # Validate that subjects exist in database (flexible matching)
                invalid_subjects = []
                matched_subjects = {}  # Store mapping of input to actual database subject
                
                for priority in priorities:
                    # Try exact match first
                    exact_match = None
                    for db_subject in available_subjects:
                        if priority.lower() == db_subject.lower():
                            exact_match = db_subject
                            break
                    
                    if exact_match:
                        matched_subjects[priority] = exact_match
                    else:
                        # Try partial match (input subject is contained in database subject)
                        partial_match = None
                        for db_subject in available_subjects:
                            if priority.lower() in db_subject.lower():
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
                  # TODO: Save to database
                # Find student by roll number and save priorities
                try:
                    student = StudentProxyModel.objects.get(roll_number=roll_number)
                    print(f"Processing: {roll_number} (Student: {student.name})")
                    print(f"Priorities: {priorities}")
                    
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
                            desired_number_of_subjects=2  # Default value
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
