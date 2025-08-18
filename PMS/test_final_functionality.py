#!/usr/bin/env python
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append('/home/aayush/Desktop/Elective-Management-System/PMS')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PMS.settings')
django.setup()

import requests

print("=== Testing Dynamic Template URLs ===")

# Test both academic levels
base_url = "http://127.0.0.1:8001"
academic_levels = ['bachelors', 'masters']

for level in academic_levels:
    url = f"{base_url}/download-priority-template/{level}/"
    print(f"\nTesting {level.upper()} template:")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            if 'excel' in content_type or 'spreadsheet' in content_type:
                print("✅ Excel file downloaded successfully!")
                print(f"File size: {len(response.content)} bytes")
            else:
                print("⚠️  Response received but might not be Excel format")
                print(f"Response content (first 100 chars): {response.text[:100]}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server might not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n=== Testing Complete ===")
print("If both templates download successfully, the dynamic Excel template feature is working!")
print("You can now:")
print("1. Visit the admin panel and navigate to the priority entry form")
print("2. Select 'Bachelor' or 'Masters' from the Level dropdown")
print("3. Click 'Download Sample Template' to get the appropriate template")
print("   - Bachelor: 8 columns (standard format)")
print("   - Masters: 9 columns (with no_of_electives after Email)")
