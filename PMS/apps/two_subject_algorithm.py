from apps.student.models import ElectivePriority


class TwoSubjectAlgorithm():
    def __init__(self, students_queryset, semester, subjects=[]):
        self.ok_students = list()
        self.student_queryset = students_queryset
        self.notok_students = list(student.roll_number for student in students_queryset) + list(
            student.roll_number for student in students_queryset)
        self.ok_subjects = list()
        self.notok_subjects = subjects

        self.threshold = semester.subjects_provided
        self.semester = semester
        self.priority_of = {}
        self.solution = {i: set() for i in self.notok_subjects}

    def intersection(self, l1, l2):
        '''analogous to set intersection between two lists'''
        return set(l1).intersection(set(l2))

    def populate_data(self):
        # randomly giving priorities to students as for now
        for student in self.student_queryset:
            self.priority_of[student.roll_number] = list(
                ElectivePriority.objects.filter(student__roll_number=student.roll_number,
                                                session=self.semester).order_by(
                    'priority').values_list('subject_id', flat=True))

    def display_question(self):
        '''displays students with their priorities'''
        for i in self.priority_of:
            print(i, end='---')
            print(*self.priority_of[i], sep=' ', end='\t \t')
            # if i % 3 == 0:
            #     print('')
        print('')

    def display_answer(self):
        '''displays a dictionary in formatted way'''
        for i in self.solution:
            print(i, *self.solution[i], sep='\t')
        print('ok subjects are  ', self.ok_subjects)
        print('ok students are', self.ok_students)
        print('notok subjects are  ', self.notok_subjects)
        print('notok students are', self.notok_students)
        print('\n\n\n')

    def assign(self, j, z):
        for x in self.notok_students[:]:
            temp = self.priority_of[x][j - 1]
            if z == 0:
                if temp in self.notok_subjects:
                    self.solution[temp].add(x)
            if z == 1:
                if temp in self.ok_subjects:
                    self.solution[temp].add(x)
                    self.ok_students.append(x)
                    self.notok_students.remove(x)

    def check(self, temp_list):
        for x in temp_list[:]:
            self.solution[x] = self.intersection(self.solution[x], self.notok_students)
            l = len(self.solution[x])
            if l >= self.threshold:
                self.ok_subjects.append(x)
                self.notok_subjects.remove(x)
                for y in self.solution[x]:
                    self.ok_students.append(y)
                    self.notok_students.remove(y)

    def calculate(self):
        self.assign(1, 0)
        self.assign(2, 0)
        self.notok_subjects.sort(key=lambda x: len(self.solution[x]), reverse=True)
        self.check(self.notok_subjects)
        for i in range(3, 8):
            self.assign(i, 0)
            self.notok_subjects.sort(key=lambda x: len(self.solution[x]), reverse=True)
            self.check(self.notok_subjects)
            self.assign(i, 1)
            self.check(self.notok_subjects)

    def run(self):
        self.populate_data()
        # self.display_question()
        self.calculate()
        # self.display_answer()

    def get_result(self):
        return self.solution
