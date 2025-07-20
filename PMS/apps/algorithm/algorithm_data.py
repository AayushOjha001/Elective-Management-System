import pandas as pd

subjects_list_in_order = ['sub1', 'sub2', 'sub3', 'sub4', 'sub5', 'sub6']

# subjects_list_in_order = ["Bioinformatics - Prof. Dr. Shashidhar Ram Joshi",
#                           "Software Defined Networks - Dr. Nanda Bikram Adhikari",
#                           "Advanced Switching and Routing for Enterprise Networks - Kumar Pudasaini",
#                           "Natural Language Processing - Dr. Aman Shakya",
#                           "Advanced Data Mining - Dr. Arun Kumar Timalsina",
#                           "Digital Color and Imaging Technology - Dr. Dibakar Raj Pant",
#                           "Advanced Database Systems - Om Prakash Mahato"]

students_list = ['Abhinav', 'Aakalpa', 'Abishek', 'Anushandhan', 'Ashim', 'Aashish']
desired_number_of_subjects_dict = {
    'Abhinav': 2,
    'Aakalpa': 3,
    'Abishek': 2,
    'Anushandhan': 1,
    'Ashim': 3,
    'Aashish': 2
}
# desired_number_of_subjects_dict = {
# "Avash Mulmi"	:2,
# "Bansaj Pradhan":1,
# "Deepak Paudel":2,
# "Nabin Khadka":2,
# "Nimesh Pudasaini":2,
# "Nishant Mahat":2,
# "Pankaj Dhakal":2,
# "Promisha Mishra":1,
# "Rachana Kunwar":1,
# "Rojin Shrestha":1,
# "Sijan Shrestha":1,
# "Sujan Shrestha":1,
# "Sujil Devkota"	:2,
# "Suresh Mainali":1,
# "Suresh Pokharel":1,
# "Susmita Sharma":1,
# "Suwan Babu Bastola":1,
# "Suyash Bhakta Mathema":2,
# "Uttam Parajuli":2,
# "Sujit Kumar Sharma":1,
# }
priority_selection_dict = {
    # the order of list is ['number of desired subjects', ...priority for subjects in order of the subject list]
    'Abhinav': [2, 1, 3, 4, 5, 6],
    'Aakalpa': [3, 1, 4, 2, 5, 6],
    'Abishek': [3, 2, 1, 4, 5, 6],
    'Anushandhan': [2, 1, 3, 4, 5, 6],
    'Ashim': [3, 4, 1, 2, 5, 6],
    'Aashish': [3, 4, 5, 1, 2, 6]
}

priority_selection_data = {
    'students': ['Abhinav', 'Aakalpa', 'Aashish', 'Abhishek', 'Anusandhan', 'Ashim', ],
    'desired_subject_count': [2, 2, 2, 2, 2, 2],
    'sub1': [1, 4, 2, 2, 4, 1],
    'sub2': [2, 3, 1, 4, 5, 4],
    'sub3': [4, 1, 4, 3, 1, 2],
    'sub4': [5, 2, 3, 1, 6, 6],
    'sub5': [6, 5, 5, 5, 2, 3],
    'sub6': [3, 6, 6, 6, 3, 5],
}


def get_valid_data(data=priority_selection_data):
    copied_data = {**data}
    students = data.pop('students')
    desired_subject_counts = data.pop('desired_subject_count')
    for key, value in data.items():
        if not (len(value) == len(students) == len(desired_subject_counts)):
            raise ValueError
    return copied_data


def get_data_frame():
    # sheets = pd.read_excel('priority.xlsx', sheet_name=['Sheet1', ])
    # df = sheets.get('Sheet1')
    # df.index = subjects_list_in_order
    # df.pop("Subjects")
    # print(df)
    # return df
    df = pd.DataFrame(priority_selection_dict, index=subjects_list_in_order)
    return df


get_data_frame()

