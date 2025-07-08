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
    
    def get_desired_number_of_subjects_for_student(self, student):
        # print('desired_number_of_subject('+student+')='+str(desired_number_of_subjects_dict.get(student, 2)))
        # print(student)
        priority_entry =  ElectivePriority.objects.filter(student__name=student,
                                               session=self.semester).first()
        
        if priority_entry and priority_entry.desired_number_of_subjects:
            return priority_entry.desired_number_of_subjects
        
        return 2
    
    def arrange_df_according_to_priority_sum(self):
        priority_sum = []
        for i in range(0, len(self.subjects_list_in_order)):
            priority_sum.append(sum(self.df_of_priorities.iloc[i]))
        self.df_of_priorities['priority_sum'] = priority_sum
        self.df_of_priorities = self.df_of_priorities.sort_values('priority_sum')
        self.df_of_priorities.pop('priority_sum')
        return self.df_of_priorities
    
    def is_subject_at_capacity(self, subject_index):
        """Check if a subject has reached the maximum capacity of 24 students"""
        return False
    
    def insert_from_priority_to_result(self):
        self.df_of_priorities = self.arrange_df_according_to_priority_sum()
        self.result_df = pd.DataFrame({}, index=self.df_of_priorities.index.to_list(),
                                      columns=self.df_of_priorities.columns)
        # initializing every cell 0
        for index in self.result_df.index:
            for column in self.result_df.columns:
                self.result_df.at[index, column] = 0
        
        for column in self.df_of_priorities.columns:
            self.df_of_priorities = self.df_of_priorities.sort_values(column)
            indices = self.df_of_priorities.index.to_list()
            print(column)
            desired_subject_count = self.get_desired_number_of_subjects_for_student(column)
            
            assigned_count = 0
            for i in range(0, len(indices)):
                if assigned_count >= desired_subject_count:
                    break
                
                subject_index = indices[i]
                # Check if subject hasn't reached maximum capacity
                if not self.is_subject_at_capacity(subject_index):
                    self.result_df.at[subject_index, column] = 1
                    self.df_of_priorities.at[subject_index, column] = 999
                    assigned_count += 1
    
    def arrange_priority_for_a_particular_student(self, student):
        self.df_of_priorities = self.df_of_priorities.sort_values(student)
        indices = self.df_of_priorities.index.to_list()
        
        # Find the first subject that hasn't reached capacity
        for subject_index in indices:
            if not self.is_subject_at_capacity(subject_index):
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
        self.insert_from_priority_to_result()
        for i in range(0, len(self.subjects_list_in_order)):
            self.start_eliminating_from_bottom()
        self.display_result()
        return self.result_df
    
    def display_result(self):
        print(self.result_df)
        # Display subject capacity information
        print("\nSubject Capacity Summary:")
        for subject in self.result_df.index:
            student_count = sum(self.result_df.loc[subject])
            print(f"{subject}: {student_count} students")

# algorithm = GenericAlgorithm()
# algorithm.run()