#!/usr/bin/env python3
"""
Test script to verify the no_of_electives column logic implementation
This simulates how the Excel import function would handle the optional column.
"""

import pandas as pd
import os
import sys

# Add the project root to Python path
sys.path.append('/home/abhiyan/Elective-Management-System-2/PMS')

def test_no_of_electives_logic():
    """Test the logic for handling the optional no_of_electives column"""
    
    print("Testing no_of_electives column logic...\n")
    
    # Test Case 1: Excel file WITH no_of_electives column
    print("=== Test Case 1: With no_of_electives column ===")
    data_with_col = {
        'Roll Number': ['079bct001', '079bct002', '079bct003', '079bct004'],
        'Priority 1': ['Machine Learning', 'Data Mining', 'AI', 'Blockchain'],
        'Priority 2': ['Data Mining', 'AI', 'Machine Learning', 'IoT'],
        'Priority 3': ['AI', 'Machine Learning', 'Data Mining', 'Machine Learning'],
        'Priority 4': ['Blockchain', 'IoT', 'Blockchain', 'AI'],
        'Priority 5': ['IoT', 'Blockchain', 'IoT', 'Data Mining'],
        'no_of_electives': [3, 2, 4, 1]  # Different values for each student
    }
    
    df_with_col = pd.DataFrame(data_with_col)
    
    # Check if column exists
    has_no_of_electives = 'no_of_electives' in df_with_col.columns
    print(f"Has no_of_electives column: {has_no_of_electives}")
    
    # Process each row
    for index, row in df_with_col.iterrows():
        roll_number = str(row['Roll Number']).strip()
        
        # Extract desired number of electives
        if has_no_of_electives:
            no_of_electives = row.get('no_of_electives', 2)
            try:
                no_of_electives = int(no_of_electives) if pd.notna(no_of_electives) else 2
                # Ensure reasonable bounds (between 1 and 5)
                no_of_electives = max(1, min(5, no_of_electives))
            except (ValueError, TypeError):
                no_of_electives = 2
        else:
            no_of_electives = 2
            
        print(f"Student {roll_number}: wants {no_of_electives} electives")
    
    print()
    
    # Test Case 2: Excel file WITHOUT no_of_electives column
    print("=== Test Case 2: Without no_of_electives column ===")
    data_without_col = {
        'Roll Number': ['079bct005', '079bct006', '079bct007'],
        'Priority 1': ['Machine Learning', 'Data Mining', 'AI'],
        'Priority 2': ['Data Mining', 'AI', 'Machine Learning'],
        'Priority 3': ['AI', 'Machine Learning', 'Data Mining'],
        'Priority 4': ['Blockchain', 'IoT', 'Blockchain'],
        'Priority 5': ['IoT', 'Blockchain', 'IoT']
    }
    
    df_without_col = pd.DataFrame(data_without_col)
    
    # Check if column exists
    has_no_of_electives = 'no_of_electives' in df_without_col.columns
    print(f"Has no_of_electives column: {has_no_of_electives}")
    
    # Process each row
    for index, row in df_without_col.iterrows():
        roll_number = str(row['Roll Number']).strip()
        
        # Extract desired number of electives
        if has_no_of_electives:
            no_of_electives = row.get('no_of_electives', 2)
            try:
                no_of_electives = int(no_of_electives) if pd.notna(no_of_electives) else 2
                # Ensure reasonable bounds (between 1 and 5)
                no_of_electives = max(1, min(5, no_of_electives))
            except (ValueError, TypeError):
                no_of_electives = 2
        else:
            no_of_electives = 2
            
        print(f"Student {roll_number}: wants {no_of_electives} electives (default)")
    
    print()
    
    # Test Case 3: Edge cases with invalid values
    print("=== Test Case 3: Edge cases with invalid values ===")
    data_edge_cases = {
        'Roll Number': ['079bct008', '079bct009', '079bct010', '079bct011', '079bct012'],
        'Priority 1': ['ML', 'DM', 'AI', 'BC', 'IoT'],
        'Priority 2': ['DM', 'AI', 'ML', 'IoT', 'BC'],
        'Priority 3': ['AI', 'ML', 'DM', 'ML', 'AI'],
        'Priority 4': ['BC', 'IoT', 'BC', 'AI', 'DM'],
        'Priority 5': ['IoT', 'BC', 'IoT', 'DM', 'ML'],
        'no_of_electives': [6, 0, None, 'invalid', 3.5]  # Out of bounds and invalid values
    }
    
    df_edge_cases = pd.DataFrame(data_edge_cases)
    
    # Check if column exists
    has_no_of_electives = 'no_of_electives' in df_edge_cases.columns
    print(f"Has no_of_electives column: {has_no_of_electives}")
    
    # Process each row
    for index, row in df_edge_cases.iterrows():
        roll_number = str(row['Roll Number']).strip()
        original_value = row.get('no_of_electives', 2)
        
        # Extract desired number of electives
        if has_no_of_electives:
            no_of_electives = row.get('no_of_electives', 2)
            try:
                no_of_electives = int(no_of_electives) if pd.notna(no_of_electives) else 2
                # Ensure reasonable bounds (between 1 and 5)
                no_of_electives = max(1, min(5, no_of_electives))
            except (ValueError, TypeError):
                no_of_electives = 2
        else:
            no_of_electives = 2
            
        print(f"Student {roll_number}: original='{original_value}' -> final={no_of_electives} electives")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    test_no_of_electives_logic()
