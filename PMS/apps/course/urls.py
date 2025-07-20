from django.urls import path
from . import views

urlpatterns = [
    # ... your existing urls ...
    
    # Download all results (existing)
    path('session/<int:session_id>/download/', views.download_allocation_result, name='download_allocation_result'),
    
    # Download subject-wise Excel files as ZIP
    path('session/<int:session_id>/download-subjects-zip/', views.download_subject_wise_excel_files, name='download_subject_wise_excel_files'),
    
    # Download master Excel with all subjects as sheets
    path('session/<int:session_id>/download-master/', views.download_master_excel_with_subjects, name='download_master_excel_with_subjects'),
    
    # Download individual subject Excel file
    path('session/<int:session_id>/download-subject/<str:subject_name>/', views.download_individual_subject_excel, name='download_individual_subject_excel'),

    # Student editing functionality
    path('move-student/', views.move_student, name='move_student'),
    path('delete-student/', views.delete_student, name='delete_student'),
]