import pandas as pd
from django.shortcuts import get_object_or_404

from apps.authuser.models import StudentProxyModel
from apps.course.models import ElectiveSubject
from apps.one_subject_algorithm import OneSubjectAlgorithm
from apps.student.models import ElectivePriority
from apps.two_subject_algorithm import TwoSubjectAlgorithm


def get_suitable_algorithm_class(subject_count=1):
    print(subject_count)
    if subject_count == 1:
        return OneSubjectAlgorithm
    elif subject_count == 2:
        return TwoSubjectAlgorithm
    else:
        raise NotImplementedError


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
    for student in student_queryset:
        priority_selection_count = ElectivePriority.objects.filter(student=student, session=semester).count()
        if priority_selection_count != available_subjects_count:
            return False
    return True


def get_outliers_message(batch, stream, semester):
    outliers = dict()
    incomplete_data_entry = list()
    available_subjects_count = ElectiveSubject.objects.filter(elective_for=semester, stream=stream).count()
    student_queryset = StudentProxyModel.objects.filter(batch=batch, stream=stream)
    for student in student_queryset:
        priority_selection_count = ElectivePriority.objects.filter(student=student, session=semester).count()
        if priority_selection_count != available_subjects_count:
            message = '%s (%s) has only %d elective selections' % (
                student.name, student.roll_number, priority_selection_count)
            incomplete_data_entry.append(message)
    outliers['Incomplete data entry'] = incomplete_data_entry
    return incomplete_data_entry


def prepare_pandas_dataframe_from_database(batch, semester, stream):
    students_names = list(StudentProxyModel.objects.filter(batch=batch, stream=stream).values_list('name', flat=True))
    subjects = list(
        ElectiveSubject.objects.filter(elective_for=semester, stream=stream).values_list('subject_name', flat=True))

    df = pd.DataFrame(data={}, index=subjects, columns=students_names)
    for index in df.index:
        for column in df.columns:
            if ElectivePriority.objects.filter(student__name=column, subject__subject_name=index,
                                               session=semester).exists():
                df.at[index, column] = ElectivePriority.objects.get(student__name=column, subject__subject_name=index,
                                                                    session=semester).priority
            else:
                raise ValueError("All data are not available in the database.")

    return df


def get_normalized_result_from_dataframe(result_df):
    priority_sum = []
    for i in range(0, len(result_df.index)):
        priority_sum.append(sum(result_df.iloc[i]))
    result_df['number_of_students'] = priority_sum
    normalized_data_list = []
    for subject in result_df.index:
        normalized_data = dict()
        normalized_data['subject_name'] = subject
        students = []
        for student in result_df.columns:
            if result_df.at[subject, student]:
                students.append(student)
        print(students)
        normalized_data['students'] = StudentProxyModel.objects.filter(name__in=students)
        student_count = result_df.at[subject, 'number_of_students']
        normalized_data['student_count'] = student_count
        normalized_data['student_count_1'] = student_count + 1
        normalized_data['row_count'] = 1 if student_count == 0 else student_count
        normalized_data_list.append(normalized_data)
    print(normalized_data_list)
    return normalized_data_list


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
