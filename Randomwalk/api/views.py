import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from pathlib import Path

# Import our custom modules
# We comment out the model import since we decided not to use a DB for now.
# from .models import EarningsCallSummary 
from .analysis import (
    generate_trend_analysis, 
    get_file_paths_for_range, 
    get_quarter_options
)


# --- 1. Web Interface View ---

def quarterly_selection_view(request):
    """
    Renders the main page with quarter selection options.
    """
    context = {
        'quarters': get_quarter_options(),
        'companies': ['Amazon', 'Microsoft'] # Hardcoding for now
    }
    # NOTE: You need to have 'api/quarterly_selection.html' in your templates folder
    return render(request, 'api/quarterly_selection.html', context)


# --- 2. API Endpoint: Health Check ---

def health(request):
    """
    Returns a simple JSON response to indicate the API is running.
    """
    return JsonResponse({'status': 'ok', 'message': 'API is running'})


# --- 3. API Endpoint: Analysis ---

@require_http_methods(["POST"])
def analyze(request):
    """
    Handles the POST request for trend analysis.
    Reads form data, runs the LLM analysis, and returns the result.
    """
    try:
        # 1. Parse JSON Request Body
        # The frontend will send a POST request with JSON data
        data = json.loads(request.body)
        
        company = data.get('company')
        start_q = data.get('start_quarter')
        end_q = data.get('end_quarter')
        # Ticker is used inside the prompt
        ticker = company[0:4].upper() 
        
        if not all([company, start_q, end_q]):
            return JsonResponse({'error': 'Missing required parameters (company, start_quarter, end_quarter).'}, status=400)

        # 2. Get File Paths
        try:
            file_path_list = get_file_paths_for_range(company, start_q, end_q)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except FileNotFoundError as e:
            # Note: This is crucial for debugging missing data files
            return JsonResponse({'error': f'Data file error: {str(e)}'}, status=500)
        
        # 3. Generate Analysis
        # The analysis function handles LLM calling and JSON parsing internally
        analysis_result = generate_trend_analysis(
            file_path_list,
            company,
            start_q,
            end_q,
            ticker
        )
        
        # 4. Return Result
        # The result is already a human-readable string from analysis.py
        return JsonResponse({'status': 'success', 'result': analysis_result})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        
    except Exception as e:
        # Catch-all for unexpected server errors (e.g., API key issue, networking)
        print(f"Server Error during analysis: {e}")
        return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)
# --- End of File ---