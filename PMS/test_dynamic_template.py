#!/usr/bin/env python
"""
Test script to verify that the dynamic Excel template generation works correctly
for both Bachelors and Masters academic levels.
"""

import os
import sys
import django
from django.test import RequestFactory
from django.http import HttpRequest

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

from apps.student.views import download_priority_template
import openpyxl
from io import BytesIO

def test_template_generation():
    """Test that the template generation works for both academic levels."""
    factory = RequestFactory()
    request = factory.get('/download-priority-template/bachelors/')
    
    print("Testing Bachelors template...")
    
    # Test Bachelors template
    response_bachelors = download_priority_template(request, 'bachelors')
    
    # Load the Excel content
    excel_content_bachelors = BytesIO(response_bachelors.content)
    wb_bachelors = openpyxl.load_workbook(excel_content_bachelors)
    ws_bachelors = wb_bachelors.active
    
    # Get headers for Bachelors
    headers_bachelors = [cell.value for cell in ws_bachelors[1]]
    print(f"Bachelors headers: {headers_bachelors}")
    
    print("\nTesting Masters template...")
    
    # Test Masters template
    response_masters = download_priority_template(request, 'masters')
    
    # Load the Excel content
    excel_content_masters = BytesIO(response_masters.content)
    wb_masters = openpyxl.load_workbook(excel_content_masters)
    ws_masters = wb_masters.active
    
    # Get headers for Masters
    headers_masters = [cell.value for cell in ws_masters[1]]
    print(f"Masters headers: {headers_masters}")
    
    # Verify the differences
    print("\nVerification:")
    print(f"Bachelors has {len(headers_bachelors)} columns")
    print(f"Masters has {len(headers_masters)} columns")
    
    # Check that Masters has one more column than Bachelors
    if len(headers_masters) == len(headers_bachelors) + 1:
        print("✅ Masters template has one additional column as expected")
    else:
        print("❌ Masters template does not have the expected number of columns")
    
    # Check that the additional column is 'no_of_electives'
    if 'no_of_electives' in headers_masters and 'no_of_electives' not in headers_bachelors:
        print("✅ Masters template includes 'no_of_electives' column")
    else:
        print("❌ Masters template does not include 'no_of_electives' column")
    
    # Check position of no_of_electives (should be after Email)
    try:
        email_index = headers_masters.index('Email')
        no_of_electives_index = headers_masters.index('no_of_electives')
        if no_of_electives_index == email_index + 1:
            print("✅ 'no_of_electives' column is positioned correctly after 'Email'")
        else:
            print(f"❌ 'no_of_electives' column is at position {no_of_electives_index}, expected {email_index + 1}")
    except ValueError as e:
        print(f"❌ Error finding column positions: {e}")
    
    # Check sample data
    print("\nSample data verification:")
    
    # Get second row (first data row)
    sample_row_bachelors = [cell.value for cell in ws_bachelors[2]]
    sample_row_masters = [cell.value for cell in ws_masters[2]]
    
    print(f"Bachelors sample row: {sample_row_bachelors}")
    print(f"Masters sample row: {sample_row_masters}")
    
    if len(sample_row_masters) == len(sample_row_bachelors) + 1:
        print("✅ Masters sample data has correct number of columns")
    else:
        print("❌ Masters sample data has incorrect number of columns")

if __name__ == "__main__":
    test_template_generation()
