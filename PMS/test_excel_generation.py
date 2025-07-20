#!/usr/bin/env python
"""
Test script for Excel generation functionality
"""
import os
import sys
import django

# Setup Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

# Now we can import Django models and functions
from apps.excel_generator import create_subject_wise_excel_files, create_zip_of_subject_files
from apps.algorithm.algorithm_data import get_data_frame, subjects_list_in_order, students_list
import pandas as pd


def test_excel_generation_with_mock_data():
    """Test the Excel generation with mock data"""
    print("🧪 Testing Excel file generation with mock data...")
    
    # Create sample result data (binary allocation matrix)
    # This simulates the output from the algorithm
    result_df = pd.DataFrame({
        'Abhinav': [1, 0, 0, 1, 0, 0],    # Abhinav gets sub1 and sub4
        'Aakalpa': [0, 1, 1, 0, 0, 0],   # Aakalpa gets sub2 and sub3
        'Abishek': [1, 0, 0, 0, 1, 0],   # Abishek gets sub1 and sub5
        'Anushandhan': [0, 1, 0, 0, 0, 0], # Anushandhan gets sub2
        'Ashim': [0, 0, 1, 1, 0, 0],     # Ashim gets sub3 and sub4
        'Aashish': [0, 0, 0, 0, 1, 1]    # Aashish gets sub5 and sub6
    }, index=subjects_list_in_order)
    
    print("📊 Sample allocation matrix:")
    print(result_df)
    print()
    
    # Show which students are assigned to each subject
    print("📋 Subject assignments:")
    for subject in result_df.index:
        assigned_students = [student for student in result_df.columns if result_df.at[subject, student] == 1]
        print(f"   - {subject}: {assigned_students}")
    print()
    
    # Mock batch, semester, stream objects for testing
    class MockBatch:
        def __init__(self):
            self.name = "2021 Batch"
            self.pk = 1
    
    class MockSemester:
        def __init__(self):
            self.semester = 7
            self.level = "Bachelor"
            self.pk = 1
    
    class MockStream:
        def __init__(self):
            self.stream_name = "Computer Engineering"
            self.pk = 1
    
    # Create mock objects
    batch = MockBatch()
    semester = MockSemester()
    stream = MockStream()
    
    try:
        print("📝 Generating Excel files...")
        excel_files = create_subject_wise_excel_files(batch, semester, stream, result_df)
        
        if not excel_files:
            print("❌ No Excel files generated.")
            return False
        
        print(f"✅ Generated {len(excel_files)} Excel files:")
        for subject_name, excel_data in excel_files.items():
            file_size = len(excel_data)
            print(f"   - {subject_name}: {file_size} bytes")
        
        # Save files to /tmp for inspection
        print("\n💾 Saving files to /tmp/ for inspection:")
        for subject_name, excel_data in excel_files.items():
            safe_filename = subject_name.replace(' ', '_').replace('/', '-')
            filepath = f"/tmp/{safe_filename}_students.xlsx"
            
            with open(filepath, 'wb') as f:
                f.write(excel_data)
            
            print(f"   - Saved: {filepath}")
        
        # Test ZIP creation
        print("\n📦 Creating ZIP file...")
        zip_data = create_zip_of_subject_files(
            excel_files,
            batch.name,
            stream.stream_name,
            f"{semester.semester}th semester of {semester.level}"
        )
        
        zip_filepath = "/tmp/all_subjects_test.zip"
        with open(zip_filepath, 'wb') as f:
            f.write(zip_data)
        
        print(f"✅ Created ZIP file: {zip_filepath}")
        print(f"   ZIP size: {len(zip_data)} bytes")
        
        print("\n🎉 Test completed successfully!")
        print("\nℹ️  Files created in /tmp/:")
        print("   - Individual Excel files for each subject with student lists")
        print("   - ZIP file containing all subject files")
        print("   - Each Excel file contains multiple sheets:")
        print("     * 'Students' - Main list with roll numbers and names")
        print("     * 'Subject Info' - Summary information")
        print("     * 'Attendance' - Attendance tracking template")
        print("     * 'Detailed Info' - Complete details")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_excel_generation_with_mock_data()
    exit(0 if success else 1)
        def __init__(self):
            self.name = "Test Batch 2025"
    
    class MockStream:
        def __init__(self):
            self.stream_name = "Computer Science"
    
    class MockSemester:
        def __init__(self):
            self.semester = 7
            self.level = "Bachelor"
    
    batch = MockBatch()
    stream = MockStream()
    semester = MockSemester()
    
    try:
        # Test Excel file creation
        from apps.excel_generator import create_zip_of_subject_files
        
        # For testing, let's create a simple result matrix
        test_result = pd.DataFrame({
            'Abhinav': [1, 1, 0, 0, 0, 0],
            'Aakalpa': [1, 0, 1, 1, 0, 0],
            'Aashish': [0, 1, 0, 1, 1, 0]
        }, index=['sub1', 'sub2', 'sub3', 'sub4', 'sub5', 'sub6'])
        
        print("\nTest result matrix:")
        print(test_result)
        
        # Test subject-wise breakdown
        for subject in test_result.index:
            assigned_students = []
            for student in test_result.columns:
                if test_result.at[subject, student] == 1:
                    assigned_students.append(student)
            
            if assigned_students:
                print(f"\n{subject}: {assigned_students}")
        
        print("\n✅ Excel generation logic test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in Excel generation: {str(e)}")


if __name__ == "__main__":
    test_excel_generation()
