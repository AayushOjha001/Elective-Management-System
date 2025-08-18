from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
import pandas as pd
from io import BytesIO
from .models import ElectiveSession, Batch, Stream
from apps.algorithm.generic_algorithm import GenericAlgorithm
from apps.utils import prepare_pandas_dataframe_from_database, filter_result_df_by_desired_subjects
from apps.excel_generator import (
    create_subject_wise_excel_files, 
    generate_all_subject_excel_files,
    create_master_excel_with_all_subjects,
    create_zip_of_subject_files
)
import zipfile
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import os
import pickle

def download_allocation_result(request, session_id):
    session = get_object_or_404(ElectiveSession, pk=session_id)
    
    try:
        # Get batch and stream from URL parameters
        batch_id = request.GET.get('batch')
        stream_id = request.GET.get('stream')
        
        if not batch_id or not stream_id:
            return HttpResponse("Missing batch or stream parameter", status=400)
        
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # CRITICAL: Prepare the dataframe first (this was missing!)
        prepare_pandas_dataframe_from_database(batch, session, stream)
        
        # Run the algorithm with the correct parameters
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
          # Check if result_df has data
        if result_df is None or result_df.empty:
            return HttpResponse("No allocation data available for the selected parameters", status=400)
        
        # Filter the results based on each student's desired number of subjects
        filtered_df = filter_result_df_by_desired_subjects(result_df)
        
        # Create Excel file with the filtered results
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write the main allocation results (filtered to show only desired number of subjects)
            filtered_df.to_excel(writer, sheet_name='Student Allocations', index=True)
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="allocation_results_{batch.name}_{stream.stream_name}_sem{session.semester}.xlsx"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating Excel file: {str(e)}", status=500)

def download_subject_wise_excel_files(request, session_id):
    """Download all subject allocation results as individual Excel files in a ZIP"""
    session = get_object_or_404(ElectiveSession, pk=session_id)
    
    try:
        # Get batch and stream from URL parameters
        batch_id = request.GET.get('batch')
        stream_id = request.GET.get('stream')
        
        if not batch_id or not stream_id:
            return HttpResponse("Missing batch or stream parameter", status=400)
        
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # Run the algorithm
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            return HttpResponse("No allocation data available", status=400)
        
        # Generate Excel files for each subject
        excel_files = create_subject_wise_excel_files(batch, session, stream, result_df)
        
        if not excel_files:
            return HttpResponse("No subjects with allocated students found", status=400)
        
        # Create ZIP file with all subject Excel files
        zip_data = create_zip_of_subject_files(
            excel_files, 
            batch.name, 
            stream.stream_name,
            f"{session.semester}th semester of {session.level}"
        )
        
        response = HttpResponse(
            zip_data,
            content_type='application/zip'
        )
        response['Content-Disposition'] = f'attachment; filename="subject_wise_allocations_{batch.name}_{stream.stream_name}_sem{session.semester}.zip"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating subject-wise Excel files: {str(e)}", status=500)


def download_master_excel_with_subjects(request, session_id):
    """Download a single Excel file with separate sheets for each subject"""
    session = get_object_or_404(ElectiveSession, pk=session_id)
    
    try:
        # Get batch and stream from URL parameters
        batch_id = request.GET.get('batch')
        stream_id = request.GET.get('stream')
        
        if not batch_id or not stream_id:
            return HttpResponse("Missing batch or stream parameter", status=400)
        
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # Run the algorithm
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            return HttpResponse("No allocation data available", status=400)
        
        # Generate master Excel file with all subjects
        excel_data = create_master_excel_with_all_subjects(batch, session, stream, result_df)
        
        if excel_data is None:
            return HttpResponse("No subjects with allocated students found", status=400)
        
        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="master_allocation_{batch.name}_{stream.stream_name}_sem{session.semester}.xlsx"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating master Excel file: {str(e)}", status=500)


def download_individual_subject_excel(request, session_id, subject_name):
    """Download Excel file for a single subject"""
    session = get_object_or_404(ElectiveSession, pk=session_id)
    
    try:
        # Get batch and stream from URL parameters
        batch_id = request.GET.get('batch')
        stream_id = request.GET.get('stream')
        
        if not batch_id or not stream_id:
            return HttpResponse("Missing batch or stream parameter", status=400)
        
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # Run the algorithm
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            return HttpResponse("No allocation data available", status=400)
        
        # Check if subject exists in results
        if subject_name not in result_df.index:
            return HttpResponse(f"Subject '{subject_name}' not found in allocation results", status=404)
        
        # Generate Excel files for all subjects and get the specific one
        excel_files = create_subject_wise_excel_files(batch, session, stream, result_df)
        
        if subject_name not in excel_files:
            return HttpResponse(f"No students allocated to subject '{subject_name}'", status=404)
        
        excel_data = excel_files[subject_name]
        
        # Create safe filename
        safe_filename = f"{subject_name}_{batch.name}_{stream.stream_name}_sem{session.semester}.xlsx"
        safe_filename = safe_filename.replace('/', '-').replace('\\', '-').replace('?', '').replace('*', '').replace('<', '').replace('>', '').replace('|', '')
        
        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating Excel file for subject '{subject_name}': {str(e)}", status=500)

@require_http_methods(["POST"])
def move_student(request):
    """
    Move a student from one subject to another
    """
    try:
        data = json.loads(request.body)
        student_name = data.get('student_name')
        from_subject = data.get('from_subject')
        to_subject = data.get('to_subject')
        session_id = data.get('session_id')
        batch_id = data.get('batch_id')
        stream_id = data.get('stream_id')
        
        if not all([student_name, from_subject, to_subject, session_id, batch_id, stream_id]):
            return JsonResponse({'success': False, 'error': 'Missing required parameters'})
        
        # Get the objects
        session = get_object_or_404(ElectiveSession, pk=session_id)
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # Load the current allocation data
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            return JsonResponse({'success': False, 'error': 'No allocation data found'})
        
        # Check if the student exists and is currently assigned to from_subject
        if student_name not in result_df.columns:
            return JsonResponse({'success': False, 'error': f'Student {student_name} not found in allocation data'})
        
        if from_subject not in result_df.index:
            return JsonResponse({'success': False, 'error': f'Subject {from_subject} not found'})
            
        if to_subject not in result_df.index:
            return JsonResponse({'success': False, 'error': f'Subject {to_subject} not found'})
        
        # Check if student is actually assigned to from_subject
        if result_df.at[from_subject, student_name] != 1:
            return JsonResponse({'success': False, 'error': f'Student {student_name} is not currently assigned to {from_subject}'})
        
        # Perform the move
        result_df.at[from_subject, student_name] = 0  # Remove from old subject
        result_df.at[to_subject, student_name] = 1    # Add to new subject
        
        # Save the updated allocation (we'll create a simple cache mechanism)
        cache_key = f"allocation_{batch_id}_{session_id}_{stream_id}"
        cache_data = {
            'result_df': result_df,
            'timestamp': pd.Timestamp.now()
        }
        
        # Store in a simple file-based cache (you might want to use Redis or database in production)
        cache_dir = "/tmp/elective_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(f"{cache_dir}/{cache_key}.pkl", 'wb') as f:
            pickle.dump(cache_data, f)
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully moved {student_name} from {from_subject} to {to_subject}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def delete_student(request):
    """
    Remove a student from their assigned subject
    """
    try:
        data = json.loads(request.body)
        student_name = data.get('student_name')
        from_subject = data.get('from_subject')
        session_id = data.get('session_id')
        batch_id = data.get('batch_id')
        stream_id = data.get('stream_id')
        
        if not all([student_name, from_subject, session_id, batch_id, stream_id]):
            return JsonResponse({'success': False, 'error': 'Missing required parameters'})
        
        # Get the objects
        session = get_object_or_404(ElectiveSession, pk=session_id)
        batch = get_object_or_404(Batch, pk=batch_id)
        stream = get_object_or_404(Stream, pk=stream_id)
        
        # Load the current allocation data
        algorithm = GenericAlgorithm(batch, session, stream)
        result_df = algorithm.run()
        
        if result_df is None or result_df.empty:
            return JsonResponse({'success': False, 'error': 'No allocation data found'})
        
        # Check if the student exists and is currently assigned to from_subject
        if student_name not in result_df.columns:
            return JsonResponse({'success': False, 'error': f'Student {student_name} not found in allocation data'})
        
        if from_subject not in result_df.index:
            return JsonResponse({'success': False, 'error': f'Subject {from_subject} not found'})
        
        # Check if student is actually assigned to from_subject
        if result_df.at[from_subject, student_name] != 1:
            return JsonResponse({'success': False, 'error': f'Student {student_name} is not currently assigned to {from_subject}'})
        
        # Remove the student
        result_df.at[from_subject, student_name] = 0
        
        # Save the updated allocation
        cache_key = f"allocation_{batch_id}_{session_id}_{stream_id}"
        cache_data = {
            'result_df': result_df,
            'timestamp': pd.Timestamp.now()
        }
        
        # Store in cache
        cache_dir = "/tmp/elective_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(f"{cache_dir}/{cache_key}.pkl", 'wb') as f:
            pickle.dump(cache_data, f)
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully removed {student_name} from {from_subject}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_cached_allocation(batch_id, session_id, stream_id):
    """Get cached allocation data if it exists and is less than 1 hour old."""
    cache_key = f"allocation_{batch_id}_{session_id}_{stream_id}"
    cache_file = f"/tmp/elective_cache/{cache_key}.pkl"
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            if (pd.Timestamp.now() - cache_data['timestamp']).total_seconds() < 3600:
                return cache_data['result_df']
        except Exception:
            return None
    return None