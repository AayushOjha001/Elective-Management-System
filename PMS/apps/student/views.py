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
    """Normalize whitespace in text."""
    if not text or str(text).lower() == 'nan':
        return ''
    cleaned = str(text).strip()
    return ' '.join(cleaned.split())

def enter_priority_in_bulk(request, *args, **kwargs):
    context = get_admin_context()
    context['has_data'] = False
    if request.method == 'GET':
        form = PriorityEntryDetailFormset()
    elif '_upload_excel' in request.POST:
        form = PriorityEntryDetailFormset(request.POST)
        excel_file = request.FILES.get('excel_file')
        if excel_file:
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
                batch = form.cleaned_data.get('batch', None)
                if batch and semester and stream:
                    pass  # potential cache invalidation placeholder
                context['message'] = 'Data inserted successfully'
                context['is_success'] = True
    context['form'] = form
    return TemplateResponse(request, 'admin/priority/enter_priority_in_bulk.html', context)

def download_priority_template(request, academic_level):
    """Generate dynamic Excel priority template (bachelors vs masters)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'PriorityData'
    headers = ['Name', 'Roll Number', 'Email', 'Priority 1', 'Priority 2', 'Priority 3', 'Priority 4', 'Priority 5']
    is_masters = academic_level.lower() == 'masters'
    if is_masters:
        headers.insert(3, 'no_of_electives')
    ws.append(headers)
    if is_masters:
        sample_rows = [
            ['Ram Sharma', '079msc001', 'ram.sharma@pcampus.edu.np', 3, 'Advanced Database Systems', 'Machine Learning', 'Cloud Computing', 'Data Mining', 'Distributed Systems'],
            ['Sita Karki', '079msc002', 'sita.karki@pcampus.edu.np', 2, 'Natural Language Processing', 'Computer Vision', 'Deep Learning', 'Big Data Analytics', 'Network Security'],
            ['Hari Thapa', '079msc003', 'hari.thapa@pcampus.edu.np', 4, 'Software Architecture', 'Blockchain Technology', 'IoT Systems', 'AI Ethics', 'High Performance Computing']
        ]
    else:
        sample_rows = [
            ['Arun Poudel', '079bct001', 'arun.poudel@pcampus.edu.np', 'Web Technologies', 'Database Management', 'AI Fundamentals', 'Computer Graphics', 'Network Programming'],
            ['Priya Singh', '079bct002', 'priya.singh@pcampus.edu.np', 'Software Engineering', 'Mobile Computing', 'Data Science', 'Cybersecurity', 'Digital Design'],
            ['Kumar Shrestha', '079bct003', 'kumar.shrestha@pcampus.edu.np', 'Operating Systems', 'Computer Networks', 'Machine Learning Basics', 'Web Development', 'System Programming']
        ]
    for r in sample_rows:
        ws.append(r)
    notes = wb.create_sheet(title='INSTRUCTIONS')
    notes.append(['Priority Upload Template Instructions'])
    notes.append(['1. Do not modify header names.'])
    notes.append(['2. Name, Roll Number, Email required.'])
    notes.append(['3. At least Priority 1 & 2 required.'])
    notes.append(['4. Remove example rows before real data.'])
    notes.append(['5. Subject names must match configured subjects.'])
    if is_masters:
        notes.append(['6. no_of_electives mandatory; value 1-5; provide >= that many priorities.'])
    else:
        notes.append(['6. Default assignment is 2 electives unless overridden in admin.'])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=priority_template_{academic_level.lower()}.xlsx'
    wb.save(response)
    return response

def extract_student_pref(file, semester, stream, batch):
    """Parse uploaded Excel and persist student priorities with validation."""
    try:
        df = pd.read_excel(file)
        has_new_format = 'Name' in df.columns and 'Email' in df.columns
        if has_new_format:
            required_columns = ['Name', 'Roll Number', 'Email', 'Priority 1', 'Priority 2']
        else:
            required_columns = ['Roll Number', 'Priority 1', 'Priority 2']
        has_no_of_electives = 'no_of_electives' in df.columns
        try:
            level_name = semester.level.name if semester and hasattr(semester, 'level') else ''
        except Exception:
            level_name = ''
        if level_name and 'masters' in level_name.lower() and not has_no_of_electives:
            return {'success': False, 'error': 'Missing required column: no_of_electives (Masters).'}
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            return {'success': False, 'error': f'Missing required columns: {", ".join(missing)}'}
        if df.empty:
            return {'success': False, 'error': 'Excel file is empty.'}
        available_subjects = list(ElectiveSubject.objects.filter(elective_for=semester, stream=stream).values_list('subject_name', flat=True))
        processed = 0
        errors = []
        for idx, row in df.iterrows():
            try:
                roll = clean_whitespace(row['Roll Number'])
                if has_new_format:
                    name = clean_whitespace(row['Name'])
                    email = clean_whitespace(row['Email'])
                else:
                    name = email = None
                p1 = clean_whitespace(row['Priority 1'])
                p2 = clean_whitespace(row['Priority 2'])
                p3 = clean_whitespace(row.get('Priority 3', ''))
                p4 = clean_whitespace(row.get('Priority 4', ''))
                p5 = clean_whitespace(row.get('Priority 5', ''))
                if has_no_of_electives:
                    noe = row.get('no_of_electives', 2)
                    try:
                        noe = int(noe) if pd.notna(noe) else 2
                        noe = max(1, min(5, noe))
                    except (ValueError, TypeError):
                        noe = 2
                else:
                    noe = 2
                if not roll:
                    errors.append(f'Row {idx+2}: Roll Number empty'); continue
                if has_new_format:
                    if not name:
                        errors.append(f'Row {idx+2}: Name empty'); continue
                    if not email:
                        errors.append(f'Row {idx+2}: Email empty'); continue
                if len(roll) < 6:
                    errors.append(f'Row {idx+2}: Invalid roll number format'); continue
                all_p = [p1, p2, p3, p4, p5]
                priorities = []
                for i in range(min(noe, len(all_p))):
                    if all_p[i]:
                        priorities.append(all_p[i])
                if len(priorities) < noe:
                    errors.append(f'Row {idx+2}: Wants {noe} electives but only {len(priorities)} priorities given'); continue
                invalid = []
                matched = {}
                for pr in priorities:
                    norm = ' '.join(pr.split()).strip()
                    exact = None
                    for dbs in available_subjects:
                        nd = ' '.join(dbs.split()).strip()
                        if norm.lower() == nd.lower():
                            exact = dbs; break
                    if exact:
                        matched[pr] = exact
                    else:
                        part = None
                        for dbs in available_subjects:
                            nd = ' '.join(dbs.split()).strip()
                            if norm.lower() in nd.lower():
                                part = dbs; break
                        if part:
                            matched[pr] = part
                        else:
                            invalid.append(pr)
                if invalid:
                    errors.append(f'Row {idx+2}: Invalid subjects: {", ".join(invalid)}'); continue
                if len(set(priorities)) != len(priorities):
                    errors.append(f'Row {idx+2}: Duplicate subjects'); continue
                try:
                    student = StudentProxyModel.objects.get(roll_number=roll)
                    if has_new_format:
                        if name and student.name.strip().lower() != name.strip().lower():
                            errors.append(f'Row {idx+2}: Name mismatch for {roll}'); continue
                        if email and getattr(student, 'email', None) and student.email and student.email.strip().lower() != email.strip().lower():
                            errors.append(f'Row {idx+2}: Email mismatch for {roll}'); continue
                    from apps.student.models import ElectivePriority
                    ElectivePriority.objects.filter(student=student, session=semester).delete()
                    for pr_idx, subj_name in enumerate(priorities, 1):
                        actual = matched.get(subj_name, subj_name)
                        subject = ElectiveSubject.objects.get(subject_name=actual, elective_for=semester, stream=stream)
                        ElectivePriority.objects.create(student=student, subject=subject, priority=pr_idx, session=semester, desired_number_of_subjects=noe)
                except StudentProxyModel.DoesNotExist:
                    errors.append(f'Row {idx+2}: Student {roll} not found'); continue
                except ElectiveSubject.DoesNotExist as e:
                    errors.append(f'Row {idx+2}: Subject not found - {str(e)}'); continue
                processed += 1
            except Exception as e:
                errors.append(f'Row {idx+2}: Error - {str(e)}')
        if errors:
            msg = f'Processed {processed} students. Errors: {"; ".join(errors[:3])}'
            if len(errors) > 3:
                msg += f' and {len(errors)-3} more errors.'
            return {'success': True, 'count': processed, 'error': msg}
        return {'success': True, 'count': processed, 'error': None}
    except Exception as e:
        return {'success': False, 'error': f'Failed to read Excel file: {str(e)}'}
