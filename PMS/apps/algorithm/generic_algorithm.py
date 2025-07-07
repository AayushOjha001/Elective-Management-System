import pandas as pd

from apps.student.models import ElectivePriority
from apps.utils import prepare_pandas_dataframe_from_database
from apps.authuser.models import StudentProxyModel
from apps.course.models import ElectiveSession, ElectiveSubject


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


class FlexibleElectiveAlgorithm(GenericAlgorithm):
    """
    Algorithm for master's students with flexible elective selection
    Allows students to choose subjects across different semesters and years
    """
    
    def __init__(self, batch, semester, stream):
        super().__init__(batch, semester, stream)
        self.masters_students = self.get_masters_students()
        self.flexible_priorities_df = self.prepare_flexible_priorities_dataframe()
    
    def get_masters_students(self):
        """Get students who are in master's level and using flexible elective mode"""
        return StudentProxyModel.objects.filter(
            batch=self.batch,
            stream=self.stream,
            level__name__icontains='master',  # Adjust based on your level naming
            is_flexible_elective_mode=True
        )
    
    def prepare_flexible_priorities_dataframe(self):
        """Prepare priority dataframe for flexible elective selection"""
        # Get all available subjects across all semesters for this stream
        all_subjects = ElectiveSubject.objects.filter(stream=self.stream)
        
        # Get master's students
        masters_students = list(self.masters_students.values_list('name', flat=True))
        
        # Create dataframe with all subjects and master's students
        df = pd.DataFrame(data={}, index=[subject.subject_name for subject in all_subjects], 
                         columns=masters_students)
        
        # Fill priorities based on student selections
        for student_name in masters_students:
            student = StudentProxyModel.objects.get(name=student_name)
            for subject in all_subjects:
                # Check if student has selected this subject for any semester
                priority_obj = ElectivePriority.objects.filter(
                    student=student,
                    subject=subject,
                    is_flexible_selection=True
                ).first()
                
                if priority_obj:
                    df.at[subject.subject_name, student_name] = priority_obj.priority
                else:
                    df.at[subject.subject_name, student_name] = 999  # Not selected
        
        return df
    
    def get_flexible_desired_subjects_for_student(self, student_name):
        """Get desired number of subjects for master's student in flexible mode"""
        student = StudentProxyModel.objects.get(name=student_name)
        
        # Get student's elective requirements (you can customize this)
        # For master's students, typically they need 6-8 electives total
        total_required = 6  # Can be made configurable
        
        # Get completed subjects count
        completed_count = student.completed_electives if hasattr(student, 'completed_electives') else 0
        
        # Calculate remaining required
        remaining_required = total_required - completed_count
        
        # For current semester, allow 1-3 subjects
        return min(remaining_required, 3)
    
    def run_flexible_assignment(self):
        """Run flexible elective assignment for master's students"""
        if self.flexible_priorities_df.empty:
            return pd.DataFrame()
        
        # Create result dataframe
        self.result_df = pd.DataFrame({}, 
                                     index=self.flexible_priorities_df.index.to_list(),
                                     columns=self.flexible_priorities_df.columns)
        
        # Initialize with zeros
        for index in self.result_df.index:
            for column in self.result_df.columns:
                self.result_df.at[index, column] = 0
        
        # Assign subjects based on priorities
        for student_name in self.flexible_priorities_df.columns:
            # Sort subjects by priority for this student
            student_priorities = self.flexible_priorities_df[student_name].sort_values()
            
            # Get desired number of subjects for this student
            desired_count = self.get_flexible_desired_subjects_for_student(student_name)
            
            # Assign top priority subjects
            assigned_count = 0
            for subject_name, priority in student_priorities.items():
                if assigned_count >= desired_count:
                    break
                if priority < 999:  # Subject is selected by student
                    self.result_df.at[subject_name, student_name] = 1
                    assigned_count += 1
        
        # Apply minimum threshold constraints
        self.apply_flexible_minimum_threshold()
        
        return self.result_df
    
    def apply_flexible_minimum_threshold(self):
        """Apply minimum threshold constraints for flexible mode"""
        # Remove subjects with too few students
        subjects_to_remove = []
        for subject_name in self.result_df.index:
            student_count = self.result_df.loc[subject_name].sum()
            if student_count > 0 and student_count < self.minimum_subject_threshold:
                subjects_to_remove.append(subject_name)
        
        # Remove subjects that don't meet minimum threshold
        for subject_name in subjects_to_remove:
            # Reassign students to their next priority subjects
            for student_name in self.result_df.columns:
                if self.result_df.at[subject_name, student_name] == 1:
                    self.result_df.at[subject_name, student_name] = 0
                    self.reassign_student_to_next_priority(student_name, subject_name)
        
        # Remove empty subjects from result
        for subject_name in subjects_to_remove:
            if subject_name in self.result_df.index:
                self.result_df = self.result_df.drop(subject_name)
    
    def reassign_student_to_next_priority(self, student_name, excluded_subject):
        """Reassign student to their next priority subject"""
        student_priorities = self.flexible_priorities_df[student_name].sort_values()
        
        for subject_name, priority in student_priorities.items():
            if subject_name != excluded_subject and priority < 999:
                # Check if this subject is available and not at capacity
                if subject_name in self.result_df.index:
                    current_students = self.result_df.loc[subject_name].sum()
                    if current_students < 50:  # Maximum capacity per subject
                        self.result_df.at[subject_name, student_name] = 1
                        break
    
    def run(self):
        """Override run method to handle both regular and flexible modes"""
        # Check if there are master's students in flexible mode
        if self.masters_students.exists():
            # Run flexible assignment for master's students
            flexible_result = self.run_flexible_assignment()
            
            # Run regular assignment for other students
            regular_result = super().run()
            
            # Combine results (you can customize this logic)
            return self.combine_results(flexible_result, regular_result)
        else:
            # Run regular algorithm for all students
            return super().run()
    
    def combine_results(self, flexible_result, regular_result):
        """Combine flexible and regular results"""
        # This is a simple combination - you can customize based on your needs
        if flexible_result.empty:
            return regular_result
        elif regular_result.empty:
            return flexible_result
        else:
            # Combine both dataframes
            combined_result = pd.concat([flexible_result, regular_result])
            return combined_result


# algorithm = GenericAlgorithm()
# algorithm.run()
