from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import pandas as pd
from io import BytesIO
from .models import ElectiveSession, Batch, Stream
from apps.algorithm.generic_algorithm import GenericAlgorithm
from apps.utils import prepare_pandas_dataframe_from_database

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
        
        # Create Excel file with the actual results
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Write the main allocation results
            result_df.to_excel(writer, sheet_name='Student Allocations', index=True)
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="allocation_results_{batch.name}_{stream.stream_name}_sem{session.semester}.xlsx"'
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error generating Excel file: {str(e)}", status=500)