#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

from apps.student.models import ElectivePriority
from apps.authuser.models import StudentProxyModel
from apps.algorithm.generic_algorithm import GenericAlgorithm
from apps.course.models import ElectiveSession

# Find Nikesh
print("=== Debugging Nikesh's Issue ===")
nikesh = StudentProxyModel.objects.filter(name__icontains='nikesh').first()
if nikesh:
    print(f"Found student: {nikesh.name} - {nikesh.roll_number}")
    
    # Get his priorities
    priorities = ElectivePriority.objects.filter(student=nikesh).order_by('priority')
    print(f"Nikesh has {priorities.count()} priorities:")
    for p in priorities:
        print(f"  Priority {p.priority}: {p.subject.subject_name} (desired: {p.desired_number_of_subjects})")
    
    if priorities.exists():
        session = priorities.first().session
        print(f"Session: {session}")
        print(f"Batch: {nikesh.batch}")
        print(f"Stream: {nikesh.stream}")
        print(f"Level: {nikesh.level}")
        
        # Test the algorithm
        print("\n=== Testing Algorithm ===")
        algo = GenericAlgorithm(nikesh.batch, session, nikesh.stream)
        
        # Check desired count calculation
        desired = algo.get_desired_number_of_subjects_for_student(nikesh.roll_number)
        print(f"Algorithm thinks Nikesh should get {desired} subjects")
        
        # Check if he's detected as masters
        is_masters = algo.is_masters_student(nikesh.roll_number)
        print(f"Is masters student: {is_masters}")
        
        # Run algorithm and check result
        result_df = algo.run()
        if result_df is not None and not result_df.empty and nikesh.roll_number in result_df.columns:
            assigned_subjects = []
            for subj in result_df.index:
                if result_df.at[subj, nikesh.roll_number] == 1:
                    assigned_subjects.append(subj)
            print(f"Nikesh is assigned to {len(assigned_subjects)} subjects: {assigned_subjects}")
        else:
            print("Nikesh not found in result DataFrame")
            
        # Check original priorities DataFrame
        if algo.original_priorities is not None and nikesh.roll_number in algo.original_priorities.columns:
            original_series = algo.original_priorities[nikesh.roll_number].dropna()
            print(f"Original priorities in DataFrame: {len(original_series)} subjects")
            for subj, priority in original_series.items():
                print(f"  {subj}: priority {priority}")
else:
    print("Nikesh not found")
