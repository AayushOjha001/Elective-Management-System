#!/usr/bin/env python3
"""
Test script to verify whitespace handling fixes in CSV and Excel imports
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/abhiyan/Elective-Management-System-2/PMS')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

# Now import the functions we want to test
from apps.student.views import clean_whitespace

def test_clean_whitespace():
    """Test the clean_whitespace helper function"""
    print("Testing clean_whitespace function...")
    
    test_cases = [
        # Test case format: (input, expected_output, description)
        ("  Abhiyan Khanal  ", "Abhiyan Khanal", "Leading and trailing spaces"),
        ("Abhiyan  Khanal", "Abhiyan Khanal", "Multiple internal spaces"),
        ("  Machine   Learning  ", "Machine Learning", "Mixed whitespace issues"),
        ("", "", "Empty string"),
        ("   ", "", "Only whitespace"),
        ("NaN", "", "NaN value"),
        ("nan", "", "lowercase nan"),
        ("Data\t\tMining", "Data Mining", "Tab characters"),
        ("  \n  Web   Development  \n  ", "Web Development", "Newlines and mixed whitespace"),
        ("079bct007", "079bct007", "Normal roll number"),
        ("  079bct007  ", "079bct007", "Roll number with spaces"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = clean_whitespace(input_text)
        if result == expected:
            print(f"✅ PASS: {description}")
            print(f"   Input: '{input_text}' -> Output: '{result}'")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Input: '{input_text}'")
            print(f"   Expected: '{expected}'")
            print(f"   Got: '{result}'")
            failed += 1
        print()
    
    print(f"Test Results: {passed} passed, {failed} failed")
    return failed == 0

def test_import_functions():
    """Test that the import functions can be loaded without errors"""
    print("Testing import function availability...")
    
    try:
        from apps.student.views import extract_student_pref
        print("✅ extract_student_pref function imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import extract_student_pref: {e}")
        return False
    
    try:
        from apps.authuser.admin import StudentAdmin
        print("✅ StudentAdmin class imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import StudentAdmin: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Whitespace Handling Fixes")
    print("=" * 50)
    
    # Test the clean_whitespace function
    whitespace_test_passed = test_clean_whitespace()
    
    print("\n" + "=" * 50)
    
    # Test that import functions are available
    import_test_passed = test_import_functions()
    
    print("\n" + "=" * 50)
    print("Overall Test Results:")
    
    if whitespace_test_passed and import_test_passed:
        print("🎉 All tests PASSED! Whitespace handling fixes are working correctly.")
        return 0
    else:
        print("💥 Some tests FAILED. Please review the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
