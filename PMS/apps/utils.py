import pandas as pd
from django.shortcuts import get_object_or_404

from apps.authuser.models import StudentProxyModel
from apps.course.models import ElectiveSubject
from apps.student.models import ElectivePriority


# Legacy function - commented out since OneSubjectAlgorithm and TwoSubjectAlgorithm are deprecated
# def get_suitable_algorithm_class(subject_count=1):
#     print(subject_count)  
#     if subject_count == 1:
#         return OneSubjectAlgorithm
#     elif subject_count == 2:
#         return TwoSubjectAlgorithm
#     else:
#         raise NotImplementedError


def normalize_result(result):
    normalized_data_list = []
    for subject_id in result:
        normalized_data = {}
        normalized_data['subject_name'] = get_object_or_404(ElectiveSubject, pk=subject_id).subject_name
        normalized_data['students'] = [{'student_name': student.name, 'roll_number': student.roll_number} for student in
                                       StudentProxyModel.objects.filter(roll_number__in=result[subject_id])]
        student_count = StudentProxyModel.objects.filter(roll_number__in=result[subject_id]).count()
        normalized_data['student_count'] = student_count
        normalized_data['student_count_1'] = student_count + 1
        normalized_data['row_count'] = 1 if student_count == 0 else student_count
        normalized_data_list.append(normalized_data)
    return normalized_data_list


def check_if_the_data_entry_is_complete(batch, stream, semester):
    available_subjects_count = ElectiveSubject.objects.filter(elective_for=semester, stream=stream).count()
    student_queryset = StudentProxyModel.objects.filter(batch=batch, stream=stream)
    if available_subjects_count == 0:
        return False
    # for student in student_queryset:
    #     priority_selection_count = ElectivePriority.objects.filter(student=student, session=semester).count()
    #     if priority_selection_count != available_subjects_count:
    #         return False
    return True


def get_outliers_message(batch, stream, semester):
    outliers = dict()
    incomplete_data_entry = list()
    available_subjects_count = ElectiveSubject.objects.filter(elective_for=semester, stream=stream).count()
    student_queryset = StudentProxyModel.objects.filter(batch=batch, stream=stream)
    # for student in student_queryset:
    #     priority_selection_count = ElectivePriority.objects.filter(student=student, session=semester).count()
    #     if priority_selection_count != available_subjects_count:
    #         message = '%s (%s) has only %d elective selections' % (
    #             student.name, student.roll_number, priority_selection_count)
    #         incomplete_data_entry.append(message)
    outliers['Incomplete data entry'] = incomplete_data_entry
    return incomplete_data_entry


def prepare_pandas_dataframe_from_database(batch, semester, stream):
    priorities_qs = ElectivePriority.objects.filter(
        student__batch=batch,
        student__stream=stream,
        session=semester
    ).select_related('student', 'subject')
    subjects = list(ElectiveSubject.objects.filter(elective_for=semester, stream=stream).values_list('subject_name', flat=True))
    if not subjects:
        return pd.DataFrame()
    roll_numbers = list(priorities_qs.values_list('student__roll_number', flat=True).distinct())
    if not roll_numbers:
        return pd.DataFrame(index=subjects)
    df = pd.DataFrame(index=subjects, columns=roll_numbers, dtype='float')
    for subj in subjects:
        for rn in roll_numbers:
            df.at[subj, rn] = float('nan')
    for pr in priorities_qs:
        subj_name = pr.subject.subject_name
        rn = pr.student.roll_number
        if subj_name in df.index and rn in df.columns:
            df.at[subj_name, rn] = pr.priority
    return df


def filter_result_df_by_desired_subjects(result_df):
    if result_df is None or result_df.empty:
        return result_df
    from apps.student.models import ElectivePriority
    filtered_df = result_df.copy()
    for roll in filtered_df.columns:
        if str(roll).startswith('Unnamed') or roll == 'number_of_students':
            continue
        student_assignments = []
        for subject in filtered_df.index:
            if filtered_df.at[subject, roll] == 1:
                ep = ElectivePriority.objects.filter(student__roll_number=roll, subject__subject_name=subject).first()
                priority = ep.priority if ep else 999
                desired = ep.desired_number_of_subjects if ep and ep.desired_number_of_subjects else 2
                student_assignments.append({'subject': subject, 'priority': priority, 'desired': desired})
        if not student_assignments:
            continue
        student_assignments.sort(key=lambda x: x['priority'])
        desired = student_assignments[0]['desired'] if student_assignments else 2
        for subject in filtered_df.index:
            filtered_df.at[subject, roll] = 0
        for i, item in enumerate(student_assignments):
            if i < desired:
                filtered_df.at[item['subject'], roll] = 1
            else:
                break
    return filtered_df


def get_student_queryset(batch, stream):
    return StudentProxyModel.objects.filter(batch=batch, stream=stream)


def get_subjects(stream, semester):
    return ElectiveSubject.objects.filter(elective_for=semester, stream=stream)


def get_nth_object(queryset, n):
    i = 0
    for object in queryset:
        if i == n:
            return object
        i += 1
    return None


def get_object_index(queryset, object):
    i = 0
    for obj in queryset:
        if obj == object:
            return i
        i += 1
    return None


def get_normalized_result_from_dataframe(result_df):
    """Normalize allocation DataFrame (index=subjects, columns=roll numbers) for template rendering."""
    if result_df is None or result_df.empty:
        return []
    from apps.authuser.models import StudentProxyModel
    roll_numbers = [c for c in result_df.columns if not str(c).startswith('Unnamed') and c != 'number_of_students']
    students_map = {s.roll_number: s for s in StudentProxyModel.objects.filter(roll_number__in=roll_numbers)}
    normalized = []
    for subject in result_df.index:
        assigned_rolls = [rn for rn in roll_numbers if result_df.at[subject, rn] == 1]
        students = [students_map[rn] for rn in assigned_rolls if rn in students_map]
        count = len(students)
        normalized.append({
            'subject_name': subject,
            'students': students,
            'student_count': count,
            'student_count_1': count + 1,
            'row_count': 1 if count == 0 else count
        })
    return normalized
