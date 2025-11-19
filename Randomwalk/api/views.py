import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from pathlib import Path

# Import our custom modules
# We comment out the model import since we are not using a DB model for this API logic
# from .models import EarningsCallSummary 
from .analysis import (
    generate_trend_analysis, 
    get_file_paths_for_range, 
    get_quarter_options
)


# --- 1. Web Interface View (Mapped to '/') ---

def quarterly_selection_view(request):
    """
    Renders the main page with quarter selection options.
    
    The critical fix: The template name is 'index.html' because 
    settings.py already points DIRS to the 'api/templates' folder.
    """
    context = {
        'quarters': get_quarter_options(),
        'companies': ['Amazon', 'Microsoft'] # Hardcoding for now
    }
    # We confirmed this simple template name works with the DIRS configuration
    # Assuming the file is located at Randomwalk/api/templates/index.html
    return render(request, 'index.html', context)


# --- 2. API Endpoint: Health Check (Mapped to 'api/health') ---

def health(request):
    """
    Returns a simple JSON response to indicate the API is running.
    """
    return JsonResponse({'status': 'ok', 'message': 'API is running'})


# --- 3. API Endpoint: Analysis (Mapped to 'api/analyze') ---

@require_http_methods(["POST"])
def analyze(request):
    """
    Handles the POST request for trend analysis.
    Reads form data, runs the LLM analysis, and returns the result.
    """
    try:
        # 1. Parse JSON Request Body
        data = json.loads(request.body)
        
        company = data.get('company')
        start_q = data.get('start_quarter')
        end_q = data.get('end_quarter')
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
        analysis_result = generate_trend_analysis(
            file_path_list,
            company,
            start_q,
            end_q,
            ticker
        )
        
        # 4. Return Result
        return JsonResponse({'status': 'success', 'result': analysis_result})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        
    except Exception as e:
        print(f"Server Error during analysis: {e}")
        return JsonResponse({'error': f'Internal Server Error: {str(e)}'}, status=500)
    
    