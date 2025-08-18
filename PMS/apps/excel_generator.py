"""
Excel file generation utilities for elective subject allocation
Creates separate Excel files for each subject with student lists
"""
import pandas as pd
from io import BytesIO
import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from apps.course.models import ElectiveSubject, ElectiveSession, Batch, Stream
from apps.authuser.models import StudentProxyModel
from apps.algorithm.generic_algorithm import GenericAlgorithm
from apps.utils import get_normalized_result_from_dataframe, filter_result_df_by_desired_subjects


def create_subject_wise_excel_files(batch, semester, stream, result_df):
    """Create separate Excel files for each subject. Returns dict subject->bytes."""
    excel_files = {}
    if result_df is None or result_df.empty:
        return excel_files
    filtered_df = filter_result_df_by_desired_subjects(result_df)
    for subject_name in filtered_df.index:
        assigned_students = [student_col for student_col in filtered_df.columns if filtered_df.at[subject_name, student_col] == 1]
        if not assigned_students:
            continue
        student_details = []
        for index, student_identifier in enumerate(assigned_students, 1):
            try:
                student = StudentProxyModel.objects.get(roll_number=student_identifier, batch=batch, stream=stream)
                student_details.append({
                    'S.N.': index,
                    'Roll Number': student.roll_number,
                    'Student Name': student.name,
                    'Batch': batch.name,
                    'Stream': stream.stream_name,
                    'Subject': subject_name,
                    'Email': getattr(student, 'email', ''),
                    'Phone': getattr(student, 'phone', ''),
                    'Semester': f"{semester.semester}th semester of {semester.level}"
                })
            except StudentProxyModel.DoesNotExist:
                student_details.append({
                    'S.N.': index,
                    'Roll Number': student_identifier,
                    'Student Name': student_identifier,
                    'Batch': batch.name,
                    'Stream': stream.stream_name,
                    'Subject': subject_name,
                    'Email': 'N/A',
                    'Phone': 'N/A',
                    'Semester': f"{semester.semester}th semester of {semester.level}"
                })
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            main_student_df = pd.DataFrame([
                {
                    'S.N.': detail['S.N.'],
                    'Roll Number': detail['Roll Number'],
                    'Student Name': detail['Student Name'],
                    'Email': detail['Email'],
                    'Phone': detail['Phone']
                } for detail in student_details
            ])
            main_student_df.to_excel(writer, sheet_name='Students', index=False)
            summary_df = pd.DataFrame([
                ['Subject Name', subject_name],
                ['Total Students', len(assigned_students)],
                ['Batch', batch.name],
                ['Stream', stream.stream_name],
                ['Semester', f"{semester.semester}th semester of {semester.level}"],
                ['Generated On', pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
            ], columns=['Information', 'Details'])
            summary_df.to_excel(writer, sheet_name='Subject Info', index=False)
            attendance_df = pd.DataFrame({
                'S.N.': [detail['S.N.'] for detail in student_details],
                'Roll Number': [detail['Roll Number'] for detail in student_details],
                'Student Name': [detail['Student Name'] for detail in student_details],
                'Class 1': [''] * len(student_details),
                'Class 2': [''] * len(student_details),
                'Class 3': [''] * len(student_details),
                'Class 4': [''] * len(student_details),
                'Class 5': [''] * len(student_details),
                'Total Present': [''] * len(student_details),
                'Remarks': [''] * len(student_details)
            })
            attendance_df.to_excel(writer, sheet_name='Attendance', index=False)
            detailed_df = pd.DataFrame(student_details)
            detailed_df.to_excel(writer, sheet_name='Detailed Info', index=False)
        output.seek(0)
        excel_files[subject_name] = output.getvalue()
    return excel_files


def generate_all_subject_excel_files(session_id, batch_id, stream_id):
    """Generate Excel files for all subjects (cache disabled)."""
    try:
        session = get_object_or_404(ElectiveSession, pk=session_id)
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        if result_df is None or result_df.empty:
            return None, "No allocation data available"
        excel_files = create_subject_wise_excel_files(batch, session, stream, result_df)
        return excel_files, None
    except Exception as e:
        return None, str(e)


def create_master_excel_with_all_subjects(batch, semester, stream, result_df):
    if result_df is None or result_df.empty:
        return None
    filtered_df = filter_result_df_by_desired_subjects(result_df)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        overview_data = []
        for subject_name in filtered_df.index:
            student_count = sum(filtered_df.loc[subject_name])
            overview_data.append({
                'Subject Name': subject_name,
                'Number of Students': student_count,
                'Batch': batch.name,
                'Stream': stream.stream_name,
                'Semester': f"{semester.semester}th semester of {semester.level}"
            })
        overview_df = pd.DataFrame(overview_data)
        overview_df.to_excel(writer, sheet_name='Overview', index=False)
        for subject_name in filtered_df.index:
            assigned_students = [col for col in filtered_df.columns if filtered_df.at[subject_name, col] == 1]
            if not assigned_students:
                continue
            student_details = []
            for student_identifier in assigned_students:
                try:
                    student = StudentProxyModel.objects.get(roll_number=student_identifier, batch=batch, stream=stream)
                    student_details.append({
                        'Roll Number': student.roll_number,
                        'Student Name': student.name,
                        'Email': getattr(student, 'email', 'N/A'),
                        'Phone': getattr(student, 'phone', 'N/A')
                    })
                except StudentProxyModel.DoesNotExist:
                    student_details.append({
                        'Roll Number': student_identifier,
                        'Student Name': student_identifier,
                        'Email': 'N/A',
                        'Phone': 'N/A'
                    })
            subject_df = pd.DataFrame(student_details)
            safe_sheet_name = subject_name[:30].replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('[', '').replace(']', '')
            subject_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
    output.seek(0)
    return output.getvalue()


def create_zip_of_subject_files(excel_files, batch_name, stream_name, semester_info):
    import zipfile
    from datetime import datetime
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for subject_name, excel_data in excel_files.items():
            safe_filename = f"{subject_name}_{batch_name}_{stream_name}.xlsx".replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('<', '').replace('>', '').replace('|', '')
            zip_file.writestr(safe_filename, excel_data)
        readme_content = f"""
Elective Subject Allocation Results
==================================
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Batch: {batch_name}
Stream: {stream_name}
Semester: {semester_info}
This ZIP file contains separate Excel files for each elective subject.
Each Excel file contains:
- Summary sheet with subject information
- Student List sheet with detailed student information
- Attendance Sheet template
Files included:
{chr(10).join([f"- {subject_name}_{batch_name}_{stream_name}.xlsx" for subject_name in excel_files.keys()])}
        """
        zip_file.writestr("README.txt", readme_content)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()
