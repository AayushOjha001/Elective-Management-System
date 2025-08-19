#!/usr/bin/env python
import os
import sys
import django

# Add the parent directory to Python path
sys.path.append('/home/aayush/Desktop/Elective-Management-System/PMS')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

from apps.algorithm.generic_algorithm import GenericAlgorithm
from apps.course.models import Batch, ElectiveSession, Stream
from apps.student.models import ElectivePriority
from apps.authuser.models import StudentProxyModel

def test_nikesh_allocation():
    print("Testing Nikesh DC allocation...")
    
    try:
        # Get the test data
        batch = Batch.objects.first()
        semester = ElectiveSession.objects.first()
        stream = Stream.objects.first()
        
        if not all([batch, semester, stream]):
            print("Missing test data (batch/semester/stream)")
            return
        
        print(f"Using: Batch={batch}, Semester={semester}, Stream={stream}")
        
        # Find Nikesh DC
        nikesh_priorities = ElectivePriority.objects.filter(
            student__name__icontains="nikesh",
            session=semester
        )
        
        if not nikesh_priorities.exists():
            print("Nikesh DC not found in priorities")
            return
        
        nikesh_student = nikesh_priorities.first().student
        print(f"Found student: {nikesh_student.name}")
        
        # Check how many subjects Nikesh chose
        chosen_count = nikesh_priorities.count()
        print(f"Nikesh chose {chosen_count} subjects:")
        for priority in nikesh_priorities.order_by('priority'):
            print(f"  Priority {priority.priority}: {priority.subject.subject_name}")
        
        # Run the algorithm
        print("\nRunning allocation algorithm...")
        algorithm = GenericAlgorithm(batch, semester, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            print("Algorithm returned empty result")
            return
        
        print(f"Result DataFrame shape: {result_df.shape}")
        
        # Check Nikesh's allocation
        nikesh_column = None
        for col in result_df.columns:
            if "nikesh" in str(col).lower():
                nikesh_column = col
                break
        
        if nikesh_column is None:
            print("Nikesh not found in result columns")
            print("Available columns:", list(result_df.columns))
            return
        
        nikesh_allocation = result_df[nikesh_column]
        assigned_subjects = nikesh_allocation[nikesh_allocation == 1].index.tolist()
        
        print(f"\nNikesh's final allocation ({len(assigned_subjects)} subjects):")
        for subject in assigned_subjects:
            print(f"  - {subject}")
        
        # Check if he got the right number
        if len(assigned_subjects) == chosen_count:
            print(f"\n✅ SUCCESS: Nikesh got {len(assigned_subjects)} subjects as expected!")
        else:
            print(f"\n❌ PROBLEM: Nikesh got {len(assigned_subjects)} subjects but chose {chosen_count}")
        
        # Show subject enrollments
        print(f"\nSubject enrollments (min threshold: {semester.min_student}):")
        for subject in result_df.index:
            enrollment = sum(result_df.loc[subject])
            status = "✅" if enrollment >= semester.min_student else "❌"
            print(f"  {subject}: {enrollment} students {status}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nikesh_allocation()
