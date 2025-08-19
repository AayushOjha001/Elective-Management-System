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

    def is_masters_student(self, student_identifier):
        """Columns store roll numbers; detect masters by roll_number."""
        from apps.authuser.models import StudentProxyModel
        try:
            student = StudentProxyModel.objects.filter(roll_number=student_identifier, batch=self.batch, stream=self.stream).first()
            if student and student.level and student.level.name:
                return 'masters' in student.level.name.lower()
            return False
        except Exception:
            return False

    def get_desired_number_of_subjects_for_student(self, student_identifier):
        """Use roll_number; masters get count of their priority selections; others use desired_number_of_subjects or default 2."""
        if self.is_masters_student(student_identifier):
            actual_selections = ElectivePriority.objects.filter(
                student__roll_number=student_identifier,
                session=self.semester
            ).count()
            return actual_selections if actual_selections > 0 else 1
        priority_entry = ElectivePriority.objects.filter(
            student__roll_number=student_identifier,
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
        """Capacity enforcement disabled (always False)."""
        return False

    def insert_from_priority_to_result(self):
        self.df_of_priorities = self.arrange_df_according_to_priority_sum()
        student_columns = [col for col in self.df_of_priorities.columns
                           if col not in ['number_of_students', 'priority_sum'] and not str(col).startswith('Unnamed')]
        self.result_df = pd.DataFrame({}, index=self.df_of_priorities.index.to_list(), columns=student_columns)
        for index in self.result_df.index:
            for column in self.result_df.columns:
                self.result_df.at[index, column] = 0
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
                        assigned_count += 1

    def arrange_priority_for_a_particular_student(self, student):
        student_priorities = self.df_of_priorities[student].dropna()
        if student_priorities.empty:
            return
        student_priorities = student_priorities.sort_values()
        indices = student_priorities.index.to_list()
        for subject_index in indices:
            if not pd.isna(self.df_of_priorities.at[subject_index, student]) and not self.is_subject_at_capacity(subject_index):
                if self.result_df.at[subject_index, student] == 0:
                    self.result_df.at[subject_index, student] = 1
                break

    def start_eliminating_from_bottom(self):
        """Eliminate underfilled subjects and reassign affected students to next priorities."""
        subjects_to_drop = []
        for index in list(self.result_df.index):
            current_assigned = sum(self.result_df.loc[index])
            if current_assigned == 0:
                subjects_to_drop.append(index)
            elif current_assigned < self.minimum_subject_threshold:
                # collect students to reassign
                students_to_reassign = [col for col in self.result_df.columns if self.result_df.at[index, col] == 1]
                # clear assignments for this subject
                for col in students_to_reassign:
                    self.result_df.at[index, col] = 0
                subjects_to_drop.append(index)
                # reassign each student
                for student in students_to_reassign:
                    self.reassign_student(student, excluded_subjects=subjects_to_drop)
        # actually drop after processing to keep indexes available during reassignment
        for subj in subjects_to_drop:
            if subj in self.result_df.index:
                self.result_df = self.result_df.drop(subj)

    def reassign_student(self, student, excluded_subjects=None):
        # student is roll number
        if excluded_subjects is None:
            excluded_subjects = []
        desired = self.get_desired_number_of_subjects_for_student(student)
        currently_assigned = [s for s in self.result_df.index if self.result_df.at[s, student] == 1]
        if len(currently_assigned) >= desired:
            return
        if student not in self.df_of_priorities.columns:
            return
        # Use a separate copy of priorities (original order) without altering df values to determine preference order
        student_priorities = self.df_of_priorities[student].dropna().sort_values()
        for subject_index in student_priorities.index:
            if subject_index in excluded_subjects:
                continue
            if subject_index not in self.result_df.index:
                continue
            if self.result_df.at[subject_index, student] == 1:
                continue
            self.result_df.at[subject_index, student] = 1
            currently_assigned.append(subject_index)
            if len(currently_assigned) >= desired:
                break

    def fill_remaining_assignments(self):
        """After eliminations, attempt to satisfy desired counts for each student where possible.
        Falls back to assigning non-priority subjects (least loaded) if priorities exhausted."""
        def assign_any_available(student, needed):
            if needed <= 0:
                return
            # subjects still present
            available_subjects = [s for s in self.result_df.index if self.result_df.at[s, student] == 0]
            # sort by current load ascending
            available_subjects.sort(key=lambda s: sum(self.result_df.loc[s]))
            for subj in available_subjects:
                if needed <= 0:
                    break
                self.result_df.at[subj, student] = 1
                needed -= 1
        changed = True
        max_passes = 5
        passes = 0
        while changed and passes < max_passes:
            changed = False
            passes += 1
            for student in self.result_df.columns:
                desired = self.get_desired_number_of_subjects_for_student(student)
                current = sum(self.result_df.at[subj, student] == 1 for subj in self.result_df.index)
                if current < desired:
                    before = current
                    self.reassign_student(student)
                    after = sum(self.result_df.at[subj, student] == 1 for subj in self.result_df.index)
                    current = after
                    if current < desired:
                        assign_any_available(student, desired - current)
                        after2 = sum(self.result_df.at[subj, student] == 1 for subj in self.result_df.index)
                        if after2 > before:
                            changed = True
                    elif after > before:
                        changed = True

    def run(self):
        from apps.course.views import get_cached_allocation
        cached_result = get_cached_allocation(self.batch.pk, self.semester.pk, self.stream.pk)
        if cached_result is not None:
            self.result_df = cached_result
            return self.result_df
        self.insert_from_priority_to_result()
        # Masters flexible assignment now that detection works with roll numbers
        self.allocate_masters_students_flexibly()
        for _ in range(0, len(self.subjects_list_in_order)):
            self.start_eliminating_from_bottom()
        # Final pass to fill remaining desired slots
        self.fill_remaining_assignments()
        self.display_result()
        return self.result_df

    def display_result(self):
        # Silent placeholder
        pass

    def allocate_masters_students_flexibly(self):
        """Assign all selected subjects to masters students (capacity disabled) using roll numbers without mutating priority values."""
        masters_students = [col for col in self.result_df.columns if self.is_masters_student(col)]
        for student in masters_students:
            if student not in self.df_of_priorities.columns:
                continue
            student_priorities = self.df_of_priorities[student].dropna().sort_values()
            for subject_index in student_priorities.index:
                if subject_index not in self.result_df.index:
                    continue
                if self.result_df.at[subject_index, student] == 0:
                    self.result_df.at[subject_index, student] = 1
        return True