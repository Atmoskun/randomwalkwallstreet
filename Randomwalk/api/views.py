from django.shortcuts import render
# 1. Import BOTH functions from your analysis file
from .analysis import get_file_paths_for_range, run_teammate_analysis 

# This helper function generates your quarter list
def get_quarter_options():
    quarters = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            quarters.append(f"{year}Q{quarter}")
    quarters.append("2025Q1")
    quarters.append("2025Q2")
    return quarters

def quarterly_selection_view(request):
    company_options = ["Amazon", "Microsoft"]
    quarter_options = get_quarter_options()
    
    analysis_result = None
    selected_company = request.POST.get('company')
    selected_start = request.POST.get('start_quarter')
    selected_end = request.POST.get('end_quarter')

    if request.method == 'POST':
        try:
            # 2. Call your function to get the list of file paths.
            file_list_to_process = get_file_paths_for_range(
                selected_company, 
                selected_start, 
                selected_end
            )
            
            # 3. (TEAMMATE'S JOB) Pass the file list to your teammate's function.
            analysis_result = run_teammate_analysis(file_list_to_process)
            
        except ValueError as e:
            # 4. Catch any errors from your file-list function (e.g., bad date range)
            analysis_result = f"Error: {str(e)}\n\nPlease select a valid range."
        except FileNotFoundError as e:
            analysis_result = f"Error: Missing data file.\n\n{str(e)}"
        except Exception as e:
            analysis_result = f"An unexpected error occurred: {str(e)}"

    context = {
        'company_options': company_options,
        'quarter_options': quarter_options,
        'analysis_result': analysis_result,
        'selected_company': selected_company,
        'selected_start': selected_start,
        'selected_end': selected_end,
    }
    
    return render(request, 'api/index.html', context)
