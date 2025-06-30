import pandas as pd

from apps.student.models import ElectivePriority
from apps.utils import prepare_pandas_dataframe_from_database


class GenericAlgorithm:

    def __init__(self, batch, semester, stream):
        self.batch = batch
        self.semester = semester
        self.stream = stream
        self.df_of_priorities = prepare_pandas_dataframe_from_database(batch, semester, stream)
        self.minimum_subject_threshold = semester.min_student
        self.result_df = None
        self.subjects_list_in_order = self.df_of_priorities.index

    def get_desired_number_of_subjects_for_student(self, student):
        # print('desired_number_of_subject('+student+')='+str(desired_number_of_subjects_dict.get(student, 2)))
        # print(student)
        return ElectivePriority.objects.filter(student__name=student,
                                               session=self.semester).first().desired_number_of_subjects

    def arrange_df_according_to_priority_sum(self):
        priority_sum = []
        for i in range(0, len(self.subjects_list_in_order)):
            priority_sum.append(sum(self.df_of_priorities.iloc[i]))
        self.df_of_priorities['priority_sum'] = priority_sum
        self.df_of_priorities = self.df_of_priorities.sort_values('priority_sum')
        self.df_of_priorities.pop('priority_sum')
        return self.df_of_priorities

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
            for i in range(0, desired_subject_count):
                self.result_df.at[indices[i], column] = 1
                self.df_of_priorities.at[indices[i], column] = 999

    def arrange_priority_for_a_particular_student(self, student):
        self.df_of_priorities = self.df_of_priorities.sort_values(student)
        indices = self.df_of_priorities.index.to_list()
        self.result_df.at[indices[0], student] = 1
        self.df_of_priorities.at[indices[0], student] = 999

    def start_eliminating_from_bottom(self):
        for index in reversed(self.result_df.index):
            if sum(self.result_df.loc[index]) == 0:
                self.result_df = self.result_df.drop(index)
            elif sum(self.result_df.loc[index]) < self.minimum_subject_threshold:
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

# algorithm = GenericAlgorithm()
# algorithm.run()
