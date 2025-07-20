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
        print("\n📦 Testing ZIP creation...")
        zip_data = create_zip_of_subject_files(excel_files)
        
        if zip_data:
            zip_filepath = "/tmp/all_subject_excel_files.zip"
            with open(zip_filepath, 'wb') as f:
                f.write(zip_data)
            print(f"✅ ZIP file created: {zip_filepath} ({len(zip_data)} bytes)")
        else:
            print("❌ Failed to create ZIP file")
            return False
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during Excel generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_with_real_data():
    """Test with actual data from the algorithm"""
    print("\n🧪 Testing with real algorithm data...")
    
    try:
        # Get actual data from algorithm
        result_df = get_data_frame()
        print(f"📊 Real data matrix shape: {result_df.shape}")
        print(f"   - Subjects: {list(result_df.index)}")
        print(f"   - Students: {list(result_df.columns)}")
        
        # Mock objects (you'll need to replace with actual objects from your models)
        class MockBatch:
            def __init__(self):
                self.name = "Real Batch 2021"
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
        
        batch = MockBatch()
        semester = MockSemester()
        stream = MockStream()
        
        excel_files = create_subject_wise_excel_files(batch, semester, stream, result_df)
        
        if excel_files:
            print(f"✅ Generated {len(excel_files)} Excel files with real data")
            for subject_name in excel_files.keys():
                print(f"   - {subject_name}")
        else:
            print("❌ No Excel files generated with real data")
        
        return bool(excel_files)
        
    except Exception as e:
        print(f"❌ Error with real data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("TESTING EXCEL GENERATION SYSTEM")
    print("=" * 50)
    
    # Test with mock data first
    success1 = test_excel_generation_with_mock_data()
    
    print("\n" + "=" * 50)
    
    # Test with real data
    success2 = test_with_real_data()
    
    print("\n" + "=" * 50)
    
    if success1 and success2:
        print("🎉 ALL TESTS PASSED!")
        exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        exit(1)
