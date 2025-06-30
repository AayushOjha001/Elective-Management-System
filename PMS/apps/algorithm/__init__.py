"""
The Algorithm goes like this:

STEP 1: First, arrange the priority listing of the students in a TABULAR FORMAT with rows the column header containing the
        list of students and rows index containing the list of the subjects and each cell containing the priority for
        the students (Column) priority for the subject (Row).
        example:

                      Abhinav  Aakalpa  Abishek  Anushandhan  Ashim  Aashish
            sub1        2        3        3            2      3        3
            sub2        1        1        2            1      4        4
            sub3        3        4        1            3      1        5
            sub4        4        2        4            4      2        1
            sub5        5        5        5            5      5        2
            sub6        6        6        6            6      6        6


STEP 2: Now, calculate the sum of priorities for every ROW (Subject).

                  Abhinav  Aakalpa  Abishek  Anushandhan  Ashim  Aashish  priority_sum
        sub1        2        3        3            2      3        3            16
        sub2        1        1        2            1      4        4            13
        sub3        3        4        1            3      1        5            17
        sub4        4        2        4            4      2        1            17
        sub5        5        5        5            5      5        2            27
        sub6        6        6        6            6      6        6            36

        Arrange the subjects (Rows) based on the priority_sum

                  Abhinav  Aakalpa  Abishek  Anushandhan  Ashim  Aashish
        sub2        1        1        2            1      4        4
        sub1        2        3        3            2      3        3
        sub3        3        4        1            3      1        5
        sub4        4        2        4            4      2        1
        sub5        5        5        5            5      5        2
        sub6        6        6        6            6      6        6


STEP 3: Make a similar table for storing the result and assign all values to zero.
        Let us call this table result_df

                 Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       0       0       0           0     0       0
        sub1       0       0       0           0     0       0
        sub3       0       0       0           0     0       0
        sub4       0       0       0           0     0       0
        sub5       0       0       0           0     0       0
        sub6       0       0       0           0     0       0

STEP 4: Let desired_number_of_subject(student) be the number a subjects an student desires to
        study.
        Here Let,
        desired_number_of_subject(Abhinav)=2
        desired_number_of_subject(Aakalpa)=3
        desired_number_of_subject(Abishek)=2
        desired_number_of_subject(Anushandhan)=1
        desired_number_of_subject(Ashim)=3
        desired_number_of_subject(Aashish)=2

        Now insert the subjects to the result_df based on the students priority selection.
        We indicate a student getting a subject by 1 for corresponding student in column and
        subject in row.

                 Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     0       0
        sub1       1       1       0           0     1       0
        sub3       0       0       1           0     1       0
        sub4       0       1       0           0     1       1
        sub5       0       0       0           0     0       1
        sub6       0       0       0           0     0       0

        When a subject is provided to a student, we put the priority for that student to that subject to
        some very high value say 999. So its neglected every time we arrange the priority in ascending order

              Abhinav  Aakalpa  Abishek  Anushandhan  Ashim  Aashish
        sub4        4      999        4            4    999      999
        sub5        5        5        5            5      5      999
        sub1      999      999        3            2    999        3
        sub2      999      999      999          999      4        4
        sub3        3        4      999            3    999        5
        sub6        6        6        6            6      6        6


STEP 5: We start eliminating the result_df table from bottom row as it has the lowest possibility of being selected
        If there are less than the threshold number of students in any subject(which is 3 in this example) the the subject is eliminated and
        the students selecting that subject in earlier priority has to be shifted to some later priority subject.

        Step 5 is repeated until all the subjects has minimum threshold student

        1th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub3       0       0       0           0     0       0
        sub4       0       1       0           0     1       1
        sub5       0       0       0           0     0       0



        2th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub4       0       1       0           0     1       1



        3th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub4       0       1       0           0     1       1



        4th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub4       0       1       0           0     1       1



        5th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub4       0       1       0           0     1       1



        6th iteration

              Abhinav Aakalpa Abishek Anushandhan Ashim Aashish
        sub2       1       1       1           1     1       0
        sub1       1       1       1           0     1       1
        sub4       0       1       0           0     1       1


        Here we obtain the result only in second iteration, but to make sure
        we iterate for number_of_subjects times





"""
