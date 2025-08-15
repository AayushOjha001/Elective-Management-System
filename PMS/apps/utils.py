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


def filter_result_df_by_desired_subjects(result_df):
    """
    Filter the result dataframe to only show assignments up to each student's desired number of subjects.
    This preserves all algorithmic assignments but limits the output based on student preferences.
    
    Returns a filtered copy of the result_df where each student only has assignments 
    equal to their desired_number_of_subjects.
    """
    if result_df is None or result_df.empty:
        return result_df
    
    # Create a copy of the result dataframe
    filtered_df = result_df.copy()
    
    # Process each student column
    for student in filtered_df.columns:
        if student in ['number_of_students'] or student.startswith('Unnamed'):
            continue
            
        # Get all subjects this student is assigned to
        student_assignments = []
        for subject in filtered_df.index:
            if filtered_df.at[subject, student] == 1:
                # Get this student's priority for this subject
                try:
                    priority_entry = ElectivePriority.objects.filter(
                        student__name=student,
                        subject__subject_name=subject
                    ).first()
                    priority = priority_entry.priority if priority_entry else 999
                    desired_count = priority_entry.desired_number_of_subjects if priority_entry and priority_entry.desired_number_of_subjects else 2
                except:
                    priority = 999
                    desired_count = 2
                    
                student_assignments.append({
                    'subject': subject,
                    'priority': priority,
                    'desired_count': desired_count
                })
        
        if not student_assignments:
            continue
            
        # Sort by priority (lower number = higher priority)
        student_assignments.sort(key=lambda x: x['priority'])
        
        # Get the desired count
        desired_count = student_assignments[0]['desired_count'] if student_assignments else 2
        
        # Clear all assignments for this student first
        for subject in filtered_df.index:
            filtered_df.at[subject, student] = 0
            
        # Reassign only the top N assignments based on desired count
        for i, assignment in enumerate(student_assignments):
            if i < desired_count:
                filtered_df.at[assignment['subject'], student] = 1
            else:
                break
    
    return filtered_df


def get_normalized_result_from_dataframe(result_df):
    """
    Normalize the algorithm result dataframe into a format suitable for templates and Excel generation.
    This function now respects each student's desired number of subjects by only showing their top N assignments.
    """
    # First, create a mapping of student assignments with their priorities
    student_assignments = {}
    
    # Collect all assignments for each student
    for student in result_df.columns:
        if student in ['number_of_students'] or student.startswith('Unnamed'):
            continue
            
        student_assignments[student] = []
        for subject in result_df.index:
            if result_df.at[subject, student] == 1:
                # Get this student's priority for this subject to determine ranking
                try:
                    priority_entry = ElectivePriority.objects.filter(
                        student__name=student,
                        subject__subject_name=subject
                    ).first()
                    priority = priority_entry.priority if priority_entry else 999
                    desired_count = priority_entry.desired_number_of_subjects if priority_entry and priority_entry.desired_number_of_subjects else 2
                except:
                    priority = 999
                    desired_count = 2
                    
                student_assignments[student].append({
                    'subject': subject,
                    'priority': priority,
                    'desired_count': desired_count
                })
    
    # Limit each student's assignments to their desired number of subjects
    filtered_assignments = {}
    for student, assignments in student_assignments.items():
        if not assignments:
            continue
            
        # Sort by priority (lower number = higher priority)
        assignments.sort(key=lambda x: x['priority'])
        
        # Get the desired count (should be the same for all assignments of this student)
        desired_count = assignments[0]['desired_count'] if assignments else 2
        
        # Keep only the top N assignments based on desired count
        filtered_assignments[student] = assignments[:desired_count]
    
    # Now build the normalized data structure
    normalized_data_list = []
    for subject in result_df.index:
        normalized_data = dict()
        normalized_data['subject_name'] = subject
        students = []
        
        # Only include students who should be assigned to this subject based on their desired count
        for student, assignments in filtered_assignments.items():
            for assignment in assignments:
                if assignment['subject'] == subject:
                    students.append(student)
                    break
        
        normalized_data['students'] = StudentProxyModel.objects.filter(name__in=students)
        
        # Calculate student count from filtered assignments
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
