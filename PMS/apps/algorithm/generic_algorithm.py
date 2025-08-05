import pandas as pd
from apps.student.models import ElectivePriority
from apps.utils import prepare_pandas_dataframe_from_database
from apps.course.models import ElectiveSubject


class GenericAlgorithm:
    def __init__(self, batch, semester, stream):
        self.batch = batch
        self.semester = semester
        self.stream = stream
        self.df_of_priorities = prepare_pandas_dataframe_from_database(batch, semester, stream)
        
        # Check if we have any students with elective selections
        if self.df_of_priorities.empty:
            self.result_df = pd.DataFrame()
            self.subjects_list_in_order = []
            self.min_students_per_subject = {}
            self.max_students_per_subject = {}
            return
            
        self.minimum_subject_threshold = semester.min_student
        # self.maximum_subject_limit = 24  # Maximum students per subject
        self.result_df = None
        self.subjects_list_in_order = self.df_of_priorities.index
          # Fetch subject-specific min/max student counts from the database
        self.min_students_per_subject = {}
        self.max_students_per_subject = {}
        for subject_name in self.subjects_list_in_order:
            subject = ElectiveSubject.objects.get(subject_name=subject_name, elective_for=self.semester, stream=self.stream)
            self.min_students_per_subject[subject_name] = subject.min_students
            self.max_students_per_subject[subject_name] = subject.max_students

    def is_masters_student(self, student_name):
        """Check if a student is a Masters student based on their academic level"""
        from apps.authuser.models import StudentProxyModel
        try:
            # Get the first student with this name, batch, and stream
            # If there are multiple students with the same name, we take the first one
            student = StudentProxyModel.objects.filter(name=student_name, batch=self.batch, stream=self.stream).first()
            if student:
                return 'masters' in student.level.name.lower()
            return False
        except Exception:
            return False

    def get_desired_number_of_subjects_for_student(self, student):
        """
        Get the desired number of subjects for a student.
        For Masters students: return the actual number of subjects they selected (flexible)
        For Bachelor students: return the configured desired_number_of_subjects or default to 2
        """
        # Check if this is a Masters student
        if self.is_masters_student(student):
            # For Masters students, return the actual number of subjects they selected
            actual_selections = ElectivePriority.objects.filter(
                student__name=student, 
                session=self.semester
            ).count()
            return actual_selections if actual_selections > 0 else 1
        
        # For non-Masters students, use the original logic
        priority_entry = ElectivePriority.objects.filter(student__name=student,
                                               session=self.semester).first()
        if priority_entry and priority_entry.desired_number_of_subjects:
            return priority_entry.desired_number_of_subjects
        
        return 2

    def arrange_df_according_to_priority_sum(self):
        priority_sum = []
        for i in range(0, len(self.subjects_list_in_order)):            # Calculate sum excluding NaN values (students who didn't select this subject)
            row_sum = self.df_of_priorities.iloc[i].sum(skipna=True)
            priority_sum.append(row_sum)
        self.df_of_priorities['priority_sum'] = priority_sum
        self.df_of_priorities = self.df_of_priorities.sort_values('priority_sum')
        self.df_of_priorities.pop('priority_sum')
        return self.df_of_priorities

    def is_subject_at_capacity(self, subject_index):
        """Check if a subject has reached the maximum capacity"""
        if self.result_df is None:
            return False
        
        current_count = sum(self.result_df.loc[subject_index])
        max_capacity = self.max_students_per_subject.get(subject_index, 24)  # Default to 24 if not set
        return current_count >= max_capacity

    def insert_from_priority_to_result(self):
        self.df_of_priorities = self.arrange_df_according_to_priority_sum()
        
        # Filter out non-student columns before processing
        student_columns = [col for col in self.df_of_priorities.columns 
                          if col not in ['number_of_students', 'priority_sum'] and not col.startswith('Unnamed')]
          # Filter out non-student columns before processing
        student_columns = [col for col in self.df_of_priorities.columns 
                          if col not in ['number_of_students', 'priority_sum'] and not col.startswith('Unnamed')]
        
        self.result_df = pd.DataFrame({}, index=self.df_of_priorities.index.to_list(),
                                      columns=student_columns)
        # initializing every cell 0
        for index in self.result_df.index:
            for column in self.result_df.columns:
                self.result_df.at[index, column] = 0
        
        total_assignments = 0
        
        for column in student_columns:  # Only iterate through actual student columns
            # Create a series for this student with only non-NaN values (subjects they selected)
            student_priorities = self.df_of_priorities[column].dropna()
            
            if student_priorities.empty:
                continue
                  # Sort by priority (lower numbers = higher priority)
            student_priorities = student_priorities.sort_values()
            indices = student_priorities.index.to_list()
            
            desired_subject_count = self.get_desired_number_of_subjects_for_student(column)
            
            assigned_count = 0
            for subject_index in indices:
                if assigned_count >= desired_subject_count:
                    break
                
                # Only assign if student actually selected this subject (not NaN)
                if not pd.isna(self.df_of_priorities.at[subject_index, column]):
                    # Check if subject hasn't reached maximum capacity
                    if not self.is_subject_at_capacity(subject_index):
                        self.result_df.at[subject_index, column] = 1
                        self.df_of_priorities.at[subject_index, column] = 999
                        assigned_count += 1
                        total_assignments += 1

    def arrange_priority_for_a_particular_student(self, student):
        # Get only the subjects this student has selected (non-NaN values)
        student_priorities = self.df_of_priorities[student].dropna()
        if student_priorities.empty:
            return
            
        student_priorities = student_priorities.sort_values()
        indices = student_priorities.index.to_list()
          # Find the first subject that hasn't reached capacity and student has selected
        for subject_index in indices:
            if not pd.isna(self.df_of_priorities.at[subject_index, student]) and not self.is_subject_at_capacity(subject_index):
                self.result_df.at[subject_index, student] = 1
                self.df_of_priorities.at[subject_index, student] = 999
                break
    
    def start_eliminating_from_bottom(self):
        for index in reversed(self.result_df.index):
            if sum(self.result_df.loc[index]) == 0:
                self.result_df = self.result_df.drop(index)
            elif sum(self.result_df.loc[index]) < self.min_students_per_subject.get(index, 0):
                for column in self.result_df.columns:
                    if self.result_df.at[index, column]:
                        self.result_df.at[index, column] = 0
                        self.arrange_priority_for_a_particular_student(column)

    def run(self):
        # Check if we have cached data first
        from apps.course.views import get_cached_allocation
        cached_result = get_cached_allocation(self.batch.pk, self.semester.pk, self.stream.pk)
        
        if cached_result is not None:
            self.result_df = cached_result
            return self.result_df
          # If no cached data, run the normal algorithm
        self.insert_from_priority_to_result()
        
        # After initial allocation, apply specialized Masters student allocation
        self.allocate_masters_students_flexibly()
        
        for i in range(0, len(self.subjects_list_in_order)):
            self.start_eliminating_from_bottom()
        self.display_result()
        return self.result_df

    def display_result(self):
        # Method kept for compatibility, no debug output
        pass

    def allocate_masters_students_flexibly(self):
        """
        Special allocation method for Masters students that tries to give them 
        all subjects they selected in their priority list, respecting subject capacity limits.
        """
        from apps.authuser.models import StudentProxyModel
        
        # Get all Masters students in this batch/stream
        masters_students = []
        for column in self.result_df.columns:
            if self.is_masters_student(column):
                masters_students.append(column)
        
        # For each Masters student, try to allocate all their selected subjects
        for student in masters_students:
            student_priorities = self.df_of_priorities[student].dropna()
            if student_priorities.empty:
                continue
                
            # Sort by priority (lower numbers = higher priority)
            student_priorities = student_priorities.sort_values()
            
            # Try to assign all subjects the student selected
            for subject_index in student_priorities.index:
                # Only assign if student actually selected this subject (not NaN)
                if not pd.isna(self.df_of_priorities.at[subject_index, student]):
                    # Check if subject hasn't reached maximum capacity
                    if not self.is_subject_at_capacity(subject_index):
                        # Check if student is not already assigned to this subject
                        if self.result_df.at[subject_index, student] == 0:
                            self.result_df.at[subject_index, student] = 1
                            # Mark as assigned in priority DataFrame
                            self.df_of_priorities.at[subject_index, student] = 999
        
        return True

# algorithm = GenericAlgorithm()
# algorithm.run()