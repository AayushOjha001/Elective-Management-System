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
    # Get only students who have at least one elective priority selection for this semester
    students_with_priorities = ElectivePriority.objects.filter(
        student__batch=batch, 
        student__stream=stream, 
        session=semester
    ).values_list('student__name', flat=True).distinct()
    
    students_names = list(students_with_priorities)
    subjects = list(
        ElectiveSubject.objects.filter(elective_for=semester, stream=stream).values_list('subject_name', flat=True))
    
    # If no students have selected any electives, return empty DataFrame
    if not students_names:
        return pd.DataFrame()
    
    # Initialize DataFrame with NaN values
    df = pd.DataFrame(data={}, index=subjects, columns=students_names)
    
    # Only populate cells where students have actually made priority selections
    for index in df.index:
        for column in df.columns:
            try:
                # Try to get the priority for this student-subject combination
                # Use filter().first() to handle potential duplicate records
                priority_obj = ElectivePriority.objects.filter(student__name=column, subject__subject_name=index,
                                                              session=semester).first()
                if priority_obj:
                    df.at[index, column] = priority_obj.priority
                else:
                    # If student hasn't selected this subject, leave it as NaN
                    df.at[index, column] = float('nan')
            except ElectivePriority.DoesNotExist:
                # If student hasn't selected this subject, leave it as NaN
                df.at[index, column] = float('nan')

    return df


def get_normalized_result_from_dataframe(result_df):
    normalized_data_list = []
    for subject in result_df.index:
        normalized_data = dict()
        normalized_data['subject_name'] = subject
        students = []
        
        for student in result_df.columns:
            # Skip non-student columns like 'number_of_students'
            if student in ['number_of_students'] or student.startswith('Unnamed'):
                continue
            
            if result_df.at[subject, student] == 1:  # Only students assigned (value = 1)
                students.append(student)
        
        normalized_data['students'] = StudentProxyModel.objects.filter(name__in=students)
        
        # Calculate student count from actual assignments, not from a separate column
        student_count = len(students)
        normalized_data['student_count'] = student_count
        normalized_data['student_count_1'] = student_count + 1
        normalized_data['row_count'] = 1 if student_count == 0 else student_count
        normalized_data_list.append(normalized_data)
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
