#!/usr/bin/env python
"""
Simple test for Excel generation functionality
"""
import os
import sys
import django

# Add the project directory to sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

# Now import our modules
from apps.excel_generator import create_subject_wise_excel_files
import pandas as pd

def test_basic_functionality():
    """Basic test to verify the function works"""
    print("🧪 Testing basic Excel generation...")
    
    # Create a simple test DataFrame
    result_df = pd.DataFrame({
        'Student1': [1, 0, 1],  # Gets Subject1 and Subject3
        'Student2': [0, 1, 0],  # Gets Subject2
        'Student3': [1, 1, 0],  # Gets Subject1 and Subject2
    }, index=['Subject1', 'Subject2', 'Subject3'])
    
    print("Test data:")
    print(result_df)
    print()
    
    # Mock objects
    class MockBatch:
        name = "Test Batch 2021"
        pk = 1
    
    class MockSemester:
        semester = 7
        level = "Bachelor"
        pk = 1
    
    class MockStream:
        stream_name = "Computer Engineering"
        pk = 1
    
    batch = MockBatch()
    semester = MockSemester()
    stream = MockStream()
    
    try:
        excel_files = create_subject_wise_excel_files(batch, semester, stream, result_df)
        
        if excel_files:
            print(f"✅ Success! Generated {len(excel_files)} Excel files:")
            for subject_name, data in excel_files.items():
                print(f"  - {subject_name}: {len(data)} bytes")
                
                # Save to /tmp for inspection
                filename = f"/tmp/{subject_name.replace(' ', '_')}_test.xlsx"
                with open(filename, 'wb') as f:
                    f.write(data)
                print(f"    Saved to: {filename}")
        else:
            print("❌ No files generated")
        
        return len(excel_files) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
