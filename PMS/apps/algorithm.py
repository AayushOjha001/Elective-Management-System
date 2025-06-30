from random import shuffle

roll_numbers = [i for i in range(501, 549)]
subjects = ['sub1', 'sub2', 'sub3', 'sub4', 'sub5', 'sub6', 'sub7', 'sub8']
subject_votes = {}
data = {}
total = 0

provided_subjects_count = 1

min_student = 7
max_student = 48

min_subjects = len(roll_numbers) / max_student
max_subjects = len(roll_numbers) / min_student

subject_distribution_dict = {}

if max_subjects != int(max_subjects):
    max_subjects = int(max_subjects) + 1
else:
    max_subjects = int(max_subjects)

if min_subjects != int(min_subjects):
    min_subjects = int(min_subjects) + 1
else:
    min_subjects = int(min_subjects)

subject_list_based_on_votes = []
priorities = [i for i in range(0, len(subjects))]
ordered_subjects = {}

for sub in subjects:
    subject_votes[sub] = 0


def generate_data():
    for roll_number in roll_numbers:
        random_data = {}
        shuffle(priorities)
        for i in range(0, len(subjects)):
            random_data[subjects[i]] = priorities[i]
        data[str(roll_number)] = random_data


def get_subject_votes():
    for key in data:
        for sub in subjects:
            subject_votes[sub] = subject_votes[sub] + data[key][sub]


def order_acc_to_votes():
    votes = []
    for key, value in subject_votes.items():
        votes.append(value)
    votes.sort()
    for idx, vote in enumerate(votes):
        for key, value in subject_votes.items():
            if value == vote:
                assigned_key = key
                ordered_subjects[str(idx)] = key
        subject_votes.pop(assigned_key)


def make_an_empty_data_dict():
    for position, subject in ordered_subjects.items():
        subject_distribution_dict[subject] = []


def distribute_subjects():
    make_an_empty_data_dict()
    for allowed_priority in range(0, provided_subjects_count):
        for student in data:
            for subject, priority in data[student].items():
                if priority == allowed_priority:
                    subject_distribution_dict[subject].append(student)


generate_data()
get_subject_votes()

order_acc_to_votes()
print(ordered_subjects)
distribute_subjects()
print(subject_distribution_dict)
sum = 0
for sub, students in subject_distribution_dict.items():
    print(sub, len(students))
    sum += len(students)
print(sum)