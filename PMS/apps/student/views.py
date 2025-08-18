from django.template.response import TemplateResponse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import pandas as pd
from apps.authuser.models import StudentProxyModel
from apps.course.forms import PriorityEntryDetailFormset
from apps.course.models import ElectiveSubject
from apps.student.formsets import PriorityFormset
from apps.system.views import get_admin_context
import openpyxl


def clean_whitespace(text):
    """
    Normalize whitespace in text:
    - Strip leading/trailing whitespace
    - Collapse internal whitespace runs to a single space
    - Return empty string for None / NaN-like values
    """
    if not text or str(text).lower() == 'nan':
        return ''
    cleaned = str(text).strip()
    cleaned = ' '.join(cleaned.split())
    return cleaned


def enter_priority_in_bulk(request, *args, **kwargs):
    context = get_admin_context()
    context['has_data'] = False
    
    if request.method == 'GET':
        form = PriorityEntryDetailFormset()
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
                # Invalidate cache after manual priority entry
                batch = form.cleaned_data.get('batch', None)
                if batch and semester and stream:
                    pass  # removed cache invalidation
                context['message'] = 'Data inserted successfully'
                context['is_success'] = True
    context['form'] = form
    return TemplateResponse(
        request,
        'admin/priority/enter_priority_in_bulk.html',
        context
    )


def download_priority_template(request, academic_level):
    """
    Generates and serves a downloadable Excel template for students to enter their elective priorities.
    The template structure is dynamic based on the academic level:
    - For 'Bachelors', the template includes standard priority columns.
    - For 'Masters', an additional 'no_of_electives' column is added.
    """
    wb = openpyxl.Workbook()

    # Main sheet with sample data
    ws = wb.active
    ws.title = 'PriorityData'
    headers = [
        'Name', 'Roll Number', 'Email', 'Priority 1', 'Priority 2', 'Priority 3', 'Priority 4', 'Priority 5'
    ]
    
    sample_rows = [
        ['John Doe', '079bct001', 'john.doe@example.com', 'Subject A', 'Subject B', 'Subject C', 'Subject D', 'Subject E'],
        ['Jane Smith', '079bct002', 'jane.smith@example.com', 'Subject B', 'Subject A', 'Subject D', 'Subject C', 'Subject E'],
        ['Bob Johnson', '079bct003', 'bob.johnson@example.com', 'Subject C', 'Subject D', 'Subject A', 'Subject B', 'Subject E'],
    ]

    if academic_level.lower() == 'masters':
        headers.insert(3, 'no_of_electives')
        # Add sample data for the new column
        for i in range(len(sample_rows)):
            sample_rows[i].insert(3, 2) # Default value for no_of_electives

    ws.append(headers)

    for row in sample_rows:
        ws.append(row)

    # Instruction sheet
    notes = wb.create_sheet(title='INSTRUCTIONS')
    notes.append(['Bulk Priority Upload Template Usage'])
    notes.append(['1. Do not change header names.'])
    notes.append(['2. Name, Roll Number, Email are required for identification.'])
    notes.append(['3. At least Priority 1 and Priority 2 are required.'])
    notes.append(['4. Remove example rows before uploading your real data.'])
    notes.append(['5. Subject names must exactly match those configured for the selected semester & stream.'])
    if academic_level.lower() == 'masters':
        notes.append(['6. `no_of_electives` column is for Masters students to specify their desired number of electives.'])
        notes.append(['7. Students will be assigned electives based on their priority and the number they specified.'])
    else:
        notes.append(['6. Students will be assigned 2 electives by default (can be changed in admin interface).'])


    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=priority_template.xlsx'
    wb.save(response)
    return response


def extract_student_pref(file, semester, stream, batch):
    """
    Extract student elective priority preferences from an uploaded Excel file.

    Supported formats:
      NEW (recommended template):
        Name | Roll Number | Email | Priority 1 | Priority 2 | Priority 3 | Priority 4 | Priority 5 | [optional no_of_electives]
      LEGACY:
        Roll Number | Priority 1 | Priority 2 | Priority 3 | Priority 4 | Priority 5 | [optional no_of_electives]

    Rules:
      - Minimum required priorities: Priority 1 & Priority 2 (must be non-empty for a row to be valid)
      - Masters level: column no_of_electives REQUIRED (enforced if semester.level.name contains 'masters')
      - no_of_electives bounds: 1..5 (defaults to 2 if absent / invalid; required for masters)
      - Only the first `no_of_electives` non-empty priorities are recorded
      - Subject names matched case-insensitively; partial match fallback (contains) is attempted
      - Duplicate subjects within a row are rejected
      - Rolls validated with a minimal length check (>5 chars)
      - If NEW format used, provided Name & Email must match DB (case-insensitive) when present
    Returns dict { success: bool, count: int?, error: str? }
    """
    try:
        df = pd.read_excel(file)

        # Detect new vs legacy format
        has_new_format = 'Name' in df.columns and 'Email' in df.columns

        if has_new_format:
            required_columns = ['Name', 'Roll Number', 'Email', 'Priority 1', 'Priority 2']
        else:
            required_columns = ['Roll Number', 'Priority 1', 'Priority 2']

        has_no_of_electives = 'no_of_electives' in df.columns

        # Masters-specific enforcement
        try:
            level_name = semester.level.name if semester and hasattr(semester, 'level') else ''
        except Exception:
            level_name = ''
        if level_name and 'masters' in level_name.lower() and not has_no_of_electives:
            return {
                'success': False,
                'error': "Missing required column: no_of_electives. Masters uploads must include this column (see Masters template)."
            }

        # Validate required columns
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return {
                'success': False,
                'error': f"Missing required columns: {', '.join(missing)}. Required columns are: {', '.join(required_columns)}"
            }

        if df.empty:
            return {
                'success': False,
                'error': 'Excel file is empty. Please add student data.'
            }

        # Subjects available for the context (semester + stream)
        available_subjects = list(
            ElectiveSubject.objects.filter(elective_for=semester, stream=stream)
            .values_list('subject_name', flat=True)
        )

        processed_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                roll_number = clean_whitespace(row.get('Roll Number', ''))
                name = clean_whitespace(row.get('Name', '')) if has_new_format else None
                email = clean_whitespace(row.get('Email', '')) if has_new_format else None

                priorities_raw = [
                    clean_whitespace(row.get('Priority 1', '')),
                    clean_whitespace(row.get('Priority 2', '')),
                    clean_whitespace(row.get('Priority 3', '')),
                    clean_whitespace(row.get('Priority 4', '')),
                    clean_whitespace(row.get('Priority 5', '')),
                ]

                # Desired number of electives
                if has_no_of_electives:
                    desired = row.get('no_of_electives', 2)
                    try:
                        desired = int(desired) if pd.notna(desired) else 2
                    except (ValueError, TypeError):
                        desired = 2
                else:
                    desired = 2
                desired = max(1, min(5, desired))

                # Basic validations
                if not roll_number:
                    errors.append(f'Row {index + 2}: Roll Number is empty')
                    continue
                if len(roll_number) < 6:
                    errors.append(f'Row {index + 2}: Invalid roll number format. Expected format similar to 079bct007')
                    continue
                if has_new_format:
                    if not name:
                        errors.append(f'Row {index + 2}: Name is empty')
                        continue
                    if not email:
                        errors.append(f'Row {index + 2}: Email is empty')
                        continue

                # Collect priorities up to desired count
                priorities = [p for p in priorities_raw if p][:desired]
                if len(priorities) < desired:
                    errors.append(
                        f'Row {index + 2}: Student wants {desired} electives but only provided {len(priorities)} valid priorities'
                    )
                    continue

                # Validate subjects (case-insensitive, allow partial fallback)
                invalid_subjects = []
                matched_subjects = {}
                for p in priorities:
                    normalized_p = ' '.join(p.split()).strip()
                    exact = None
                    for db_subj in available_subjects:
                        normalized_db = ' '.join(db_subj.split()).strip()
                        if normalized_p.lower() == normalized_db.lower():
                            exact = db_subj
                            break
                    if exact:
                        matched_subjects[p] = exact
                        continue
                    # partial fallback
                    partial = None
                    for db_subj in available_subjects:
                        normalized_db = ' '.join(db_subj.split()).strip()
                        if normalized_p.lower() in normalized_db.lower():
                            partial = db_subj
                            break
                    if partial:
                        matched_subjects[p] = partial
                    else:
                        invalid_subjects.append(p)

                if invalid_subjects:
                    errors.append(
                        f"Row {index + 2}: Invalid subject names: {', '.join(invalid_subjects)}"
                    )
                    continue

                if len(set(priorities)) != len(priorities):
                    errors.append(
                        f'Row {index + 2}: Duplicate subjects found. Each subject should appear only once.'
                    )
                    continue

                # Persist priorities
                from apps.student.models import ElectivePriority
                try:
                    student = StudentProxyModel.objects.get(roll_number=roll_number)
                except StudentProxyModel.DoesNotExist:
                    errors.append(
                        f'Row {index + 2}: Student with roll number "{roll_number}" not found in database'
                    )
                    continue

                # Validate name/email if present
                if has_new_format:
                    if name and student.name and student.name.strip().lower() != name.strip().lower():
                        errors.append(
                            f'Row {index + 2}: Name mismatch for roll number {roll_number}. Expected: "{student.name}", Got: "{name}"'
                        )
                        continue
                    if email and getattr(student, 'email', None) and student.email.strip().lower() != email.strip().lower():
                        errors.append(
                            f'Row {index + 2}: Email mismatch for roll number {roll_number}. Expected: "{student.email}", Got: "{email}"'
                        )
                        continue

                # Clear existing priorities for this semester/session
                ElectivePriority.objects.filter(student=student, session=semester).delete()

                for idx_p, subj_display in enumerate(priorities, start=1):
                    actual_name = matched_subjects.get(subj_display, subj_display)
                    subject_obj = ElectiveSubject.objects.get(
                        subject_name=actual_name, elective_for=semester, stream=stream
                    )
                    ElectivePriority.objects.create(
                        student=student,
                        subject=subject_obj,
                        priority=idx_p,
                        session=semester,
                        desired_number_of_subjects=desired,
                    )

                processed_count += 1

            except ElectiveSubject.DoesNotExist as e:
                errors.append(
                    f'Row {index + 2}: Subject not found in database - {str(e)}'
                )
            except Exception as e:
                errors.append(f'Row {index + 2}: Error processing row - {str(e)}')

        if errors:
            # Summarize first few errors to keep message concise
            summary = f'Processed {processed_count} students successfully. Errors: {"; ".join(errors[:3])}'
            if len(errors) > 3:
                summary += f' and {len(errors) - 3} more errors.'
            return {
                'success': True,
                'count': processed_count,
                'error': summary,
            }
        return {
            'success': True,
            'count': processed_count,
            'error': None,
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to read Excel file: {str(e)}'
        }
