import pandas as pd
from apps.student.models import ElectivePriority
from apps.utils import prepare_pandas_dataframe_from_database


class GenericAlgorithm:
    def __init__(self, batch, semester, stream):
        self.batch = batch
        self.semester = semester
        self.stream = stream
        self.df_of_priorities = prepare_pandas_dataframe_from_database(batch, semester, stream)
        
        # If no priorities exist, initialize empty structures
        if self.df_of_priorities.empty:
            self.result_df = pd.DataFrame()
            self.subjects_list_in_order = []
            return
            
        self.minimum_subject_threshold = semester.min_student
        self.result_df = None
        self.subjects_list_in_order = self.df_of_priorities.index
        # Placeholder dicts retained for potential future per-subject constraints
        self.min_students_per_subject = {}
        self.max_students_per_subject = {}

    def is_masters_student(self, student_name):
        """Return True if the student's academic level name contains 'masters'."""
        from apps.authuser.models import StudentProxyModel
        try:
            student = StudentProxyModel.objects.filter(name=student_name, batch=self.batch, stream=self.stream).first()
            if student:
                return 'masters' in student.level.name.lower()
            return False
        except Exception:
            return False

    def get_desired_number_of_subjects_for_student(self, student):
        """
        For Masters students: dynamically allow the number of subjects they actually selected ( >=1 )
        For others: use desired_number_of_subjects if set, else fallback to 2.
        """
        if self.is_masters_student(student):
            actual_selections = ElectivePriority.objects.filter(
                student__name=student,
                session=self.semester
            ).count()
            return actual_selections if actual_selections > 0 else 1

        priority_entry = ElectivePriority.objects.filter(
            student__name=student,
            session=self.semester
        ).first()
        if priority_entry and priority_entry.desired_number_of_subjects:
            return priority_entry.desired_number_of_subjects
        return 2

    def arrange_df_according_to_priority_sum(self):
        priority_sum = []
        for i in range(0, len(self.subjects_list_in_order)):
            row_sum = self.df_of_priorities.iloc[i].sum(skipna=True)
            priority_sum.append(row_sum)
        self.df_of_priorities['priority_sum'] = priority_sum
        self.df_of_priorities = self.df_of_priorities.sort_values('priority_sum')
        self.df_of_priorities.pop('priority_sum')
        return self.df_of_priorities

    def is_subject_at_capacity(self, subject_index):
        """Capacity enforcement currently disabled (always returns False)."""
        return False

    def insert_from_priority_to_result(self):
        self.df_of_priorities = self.arrange_df_according_to_priority_sum()
        student_columns = [col for col in self.df_of_priorities.columns
                           if col not in ['number_of_students', 'priority_sum'] and not col.startswith('Unnamed')]

        self.result_df = pd.DataFrame({}, index=self.df_of_priorities.index.to_list(),
                                      columns=student_columns)
        # Initialize every cell to 0
        for index in self.result_df.index:
            for column in self.result_df.columns:
                self.result_df.at[index, column] = 0

        total_assignments = 0  # retained for potential future use

        for column in student_columns:
            student_priorities = self.df_of_priorities[column].dropna()
            if student_priorities.empty:
                continue
            student_priorities = student_priorities.sort_values()
            indices = student_priorities.index.to_list()
            desired_subject_count = self.get_desired_number_of_subjects_for_student(column)
            assigned_count = 0
            for subject_index in indices:
                if assigned_count >= desired_subject_count:
                    break
                if not pd.isna(self.df_of_priorities.at[subject_index, column]):
                    if not self.is_subject_at_capacity(subject_index):
                        self.result_df.at[subject_index, column] = 1
                        self.df_of_priorities.at[subject_index, column] = 999
                        assigned_count += 1
                        total_assignments += 1

    def arrange_priority_for_a_particular_student(self, student):
        student_priorities = self.df_of_priorities[student].dropna()
        if student_priorities.empty:
            return
        student_priorities = student_priorities.sort_values()
        indices = student_priorities.index.to_list()
        for subject_index in indices:
            if not pd.isna(self.df_of_priorities.at[subject_index, student]) and not self.is_subject_at_capacity(subject_index):
                self.result_df.at[subject_index, student] = 1
                self.df_of_priorities.at[subject_index, student] = 999
                break

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
        from apps.course.views import get_cached_allocation
        cached_result = get_cached_allocation(self.batch.pk, self.semester.pk, self.stream.pk)
        if cached_result is not None:
            self.result_df = cached_result
            return self.result_df
        self.insert_from_priority_to_result()
        # After initial allocation, allow masters students flexible allocation
        self.allocate_masters_students_flexibly()
        for _ in range(0, len(self.subjects_list_in_order)):
            self.start_eliminating_from_bottom()
        self.display_result()
        return self.result_df

    def display_result(self):
        # Silenced debug output (placeholder for future logging)
        pass

    def allocate_masters_students_flexibly(self):
        """Assign all selected subjects to masters students (capacity disabled)."""
        masters_students = [col for col in self.result_df.columns if self.is_masters_student(col)]
        for student in masters_students:
            student_priorities = self.df_of_priorities[student].dropna()
            if student_priorities.empty:
                continue
            student_priorities = student_priorities.sort_values()
            for subject_index in student_priorities.index:
                if not pd.isna(self.df_of_priorities.at[subject_index, student]):
                    if self.result_df.at[subject_index, student] == 0:
                        self.result_df.at[subject_index, student] = 1
                        self.df_of_priorities.at[subject_index, student] = 999
        return True

# algorithm = GenericAlgorithm()
# algorithm.run()