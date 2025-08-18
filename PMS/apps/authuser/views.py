from django.shortcuts import render
from django.http import HttpResponse
import csv

# Create your views here.

def download_student_sample_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=student_sample_upload.csv'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Roll number', 'Email'])
    writer.writerow(['John Doe', '078BCT001', '078bct001.johndoe@pcampus.edu.np'])
    writer.writerow(['Jane Smith', '078BCT002', '078bct002.janesmith@pcampus.edu.np'])
    writer.writerow(['Ram Bahadur', '078BCT003', '078bct003.rambahadur@pcampus.edu.np'])
    return response
