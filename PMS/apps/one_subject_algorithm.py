from apps.student.models import ElectivePriority


class OneSubjectAlgorithm():

    def __init__(self, students_queryset, semester, subjects=[]):
        # list of students and subjects. initially they are all notok.
        # student is ok_student if it gets any subject
        # subject is ok_subject if it contains no of students >= self.threshold
        self.ok_students = list()
        self.notok_students = list(student.roll_number for student in students_queryset)
        self.ok_subjects = list()
        self.notok_subjects = subjects
        self.subject_count = len(subjects)
        self.threshold = semester.subjects_provided
        self.semester = semester
        # self.priority_of is a dictionary of students with their priorities
        # self.solution is the main ans
        self.priority_of = {}
        self.solution = {i: set() for i in self.notok_subjects}

        print( self.notok_students, subjects, self.threshold, self.notok_students, semester)

    def populate_data(self):
        # randomly giving priorities to students as for now
        for i in self.notok_students:
            # consider a student can pick self.subject_count subjects
            self.priority_of[i] = list(ElectivePriority.objects.filter(student__roll_number=i,
                                                                       session=self.semester).order_by(
                'priority').values_list('subject_id', flat=True))

    def display_question(self):
        '''displays students with their priorities'''
        for i in self.priority_of:
            print(i, end='---')
            print(*self.priority_of[i], sep=' ', end='\t \t')
            # if i % 5 == 0:
            #     print('')
        print('')

    def display_answer(self):
        '''displays a dictionary in formatted way'''
        for i in self.solution:
            print(i, *self.solution[i], sep='\t')
        # print('ok subjects are  ', self.ok_subjects)
        # print('ok students are', self.ok_students)
        # print('notok subjects are  ', self.notok_subjects)
        # print('notok students are', self.notok_students)
        # print('\n\n\n')

    def difference(self, l1, l2):
        '''analogous to set different for any two lists'''
        return set(l1).difference(set(l2))

    def assign(self, j, z):
        ''' self.assigns every subject remaining students according to students' jth priority'''
        for x in self.notok_students[:]:
            temp = self.priority_of[x][j - 1]
            if z == 0:
                if temp in self.notok_subjects:
                    self.solution[temp].add(x)
            else:
                if temp in self.ok_subjects:
                    self.solution[temp].add(x)
                    self.ok_students.append(x)
                    self.notok_students.remove(x)

    def check(self, temp_list):
        ''' its function is to convert self.notok_subjects to self.ok_subjects if it has required number of students'''
        for x in temp_list[:]:
            self.solution[x] = self.difference(self.solution[x], self.ok_students)
            l = len(self.solution[x])
            if l >= self.threshold:
                self.ok_subjects.append(x)
                self.notok_subjects.remove(x)
                for y in self.solution[x]:
                    self.ok_students.append(y)
                    self.notok_students.remove(y)

    def calculate(self):
        ''' it performs main calculation stuff'''

        for i in range(1,
                       self.subject_count + 1):  # loops self.subject_count times. (earlier we considered every student picks self.subject_count subjects so)
            self.assign(i, 0)
            self.notok_subjects.sort(key=lambda x: len(self.solution[x]), reverse=True)
            self.check(self.notok_subjects)
            # display_answer()
            self.assign(i, 1)
            self.check(self.notok_subjects)
            # display_answer()

        # usually every student gets subject acc to above algorithm. however in some case all self.subject_count
        # priority subjects of some student
        # may still be self.notok_subjects. in that case he is self.assigned ok_subject having minimum no of student
        if len(self.notok_students) == 0:
            pass
        self.ok_subjects.sort(key=lambda x: len(self.solution[x]))
        for x in self.notok_students[:]:
            self.solution[self.ok_subjects[0]].add(x)
            self.ok_students.append(x)
            self.notok_students.remove(x)
        self.check(self.notok_subjects)

    def run(self):
        self.populate_data()
        # self.display_question()
        self.calculate()
        # self.display_answer()

    def get_result(self):
        return self.solution
