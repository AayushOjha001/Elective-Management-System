from random import shuffle


def intersection(l1, l2):
    '''analogous to set intersection between two lists'''
    return set(l1).intersection(set(l2))


def display_question():
    '''displays students with their priorities'''
    for i in priority_of:
        print(i, end='---')
        print(* priority_of[i], sep=' ', end='\t \t')
        if i % 3 == 0:
            print('')
    print('')


def display_answer():
    '''displays a dictionary in formatted way'''
    for i in solution:
        print(i, *solution[i], sep='\t')
    print('ok subjects are  ', ok_subjects)
    print('ok students are', ok_students)
    print('notok subjects are  ', notok_subjects)
    print('notok students are', notok_students)
    print('\n\n\n')


def assign(j, z):
    for x in notok_students[:]:
        temp = priority_of[x][j - 1]
        if z == 0:
            if temp in notok_subjects:
                solution[temp].add(x)
        if z == 1:
            if temp in ok_subjects:
                solution[temp].add(x)
                ok_students.append(x)
                notok_students.remove(x)


def check(temp_list):
    for x in temp_list[:]:
        solution[x] = intersection(solution[x], notok_students)
        l = len(solution[x])
        if l >= threshold:
            ok_subjects.append(x)
            notok_subjects.remove(x)
            for y in solution[x]:
                ok_students.append(y)
                notok_students.remove(y)


def calculate():
    assign(1, 0)
    assign(2, 0)
    notok_subjects.sort(key=lambda x: len(solution[x]), reverse=True)
    check(notok_subjects)
    for i in range(3, 8):
        assign(i, 0)
        notok_subjects.sort(key=lambda x: len(solution[x]), reverse=True)
        check(notok_subjects)
        assign(i, 1)
        check(notok_subjects)


ok_students = list()
notok_students = list(i for i in range(501, 549)) + list(i for i in range(501, 549))
ok_subjects = list()
notok_subjects = ['nep', 'eng', 'math', 'soc', 'phy', 'bio', 'his', 'chem', 'geo', 'coa']

threshold = 14

priority_of = {}
solution = {i: set() for i in notok_subjects}

# randomly giving priorities to students as for now
for i in range(501, 549):
    temp = notok_subjects[:]
    shuffle(temp)
    priority_of[i] = temp[:]  # consider a student can pick 4 subjects

display_question()
calculate()
display_answer()