#!/usr/bin/env python3
"""
Test script to verify that students only get the number of priorities they want
"""

import pandas as pd
import sys

# Add the project root to Python path
sys.path.append('/home/abhiyan/Elective-Management-System-2/PMS')

def test_priority_limitation():
    """Test that students only get their desired number of priorities"""
    
    print("Testing priority limitation based on no_of_electives...\n")
    
    # Test data with different desired elective counts
    test_data = {
        'Roll Number': ['080msdsa001', '080msdsa002', '080msdsa003', '080msdsa004'],
        'Priority 1': ['Quantum Computing', 'Applied IoT', 'Scalable Architecture', 'Business Intelligence'],
        'Priority 2': ['Applied IoT', 'Quantum Computing', 'Applied IoT', 'Quantum Computing'],
        'Priority 3': ['Business Intelligence', 'Business Intelligence', 'Quantum Computing', 'Applied IoT'],
        'Priority 4': ['Social Computing', 'Social Computing', 'Social Computing', 'Social Computing'],
        'Priority 5': ['Scalable Architecture', 'Scalable Architecture', 'Business Intelligence', 'Scalable Architecture'],
        'no_of_electives': [2, 2, 3, 1]  # Different desired numbers
    }
    
    df = pd.DataFrame(test_data)
    
    # Check if column exists
    has_no_of_electives = 'no_of_electives' in df.columns
    print(f"Has no_of_electives column: {has_no_of_electives}")
    print()
    
    # Process each row
    for index, row in df.iterrows():
        roll_number = str(row['Roll Number']).strip()
        
        # Extract desired number of electives
        if has_no_of_electives:
            no_of_electives = row.get('no_of_electives', 2)
            try:
                no_of_electives = int(no_of_electives) if pd.notna(no_of_electives) else 2
                no_of_electives = max(1, min(5, no_of_electives))
            except (ValueError, TypeError):
                no_of_electives = 2
        else:
            no_of_electives = 2
        
        # Collect priorities based on desired number
        priority_1 = str(row['Priority 1']).strip() if pd.notna(row['Priority 1']) else ''
        priority_2 = str(row['Priority 2']).strip() if pd.notna(row['Priority 2']) else ''
        priority_3 = str(row['Priority 3']).strip() if pd.notna(row['Priority 3']) else ''
        priority_4 = str(row['Priority 4']).strip() if pd.notna(row['Priority 4']) else ''
        priority_5 = str(row['Priority 5']).strip() if pd.notna(row['Priority 5']) else ''
        
        all_priorities = [priority_1, priority_2, priority_3, priority_4, priority_5]
        priorities = []
        
        # Only collect the number of priorities the student wants
        for i in range(min(no_of_electives, len(all_priorities))):
            if all_priorities[i]:
                priorities.append(all_priorities[i])
        
        print(f"Student {roll_number}:")
        print(f"  Wants: {no_of_electives} electives")
        print(f"  Will get priorities: {priorities}")
        print(f"  Number of priorities collected: {len(priorities)}")
        print()

if __name__ == "__main__":
    test_priority_limitation()
