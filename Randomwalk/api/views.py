import time
from django.shortcuts import render
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt # <-- New required import

# --- Constants for Simulation ---
# NOTE: API key handling is managed by the canvas environment.
MAX_RETRIES = 5

# --- Helper Function: Generate Quarter Options ---
def get_quarter_options() -> list:
    """Generates a list of quarter strings from 2020Q1 to 2025Q4."""
    # Note: range(2020, 2026) correctly includes years up to 2025 (i.e., 2020, 2021, 2022, 2023, 2024, 2025).
    quarters = []
    for year in range(2020, 2026):
        for q in range(1, 5):
            quarters.append(f"{year}Q{q}")
    return quarters

# --- Helper Function: Simulate Stock Data Fetching ---
def get_stock_data(company: str, start_q: str, end_q: str) -> str:
    """
    Simulates fetching complex financial data for the given period.
    All displayed text is in English.
    """
    if company == 'Amazon':
        data = f"""
Company: Amazon (AMZN)
Period: {start_q} to {end_q}

Key Metrics (Millions USD):
| Metric | {start_q} | {end_q} | Change (%) |
|---|---|---|---|
| Total Revenue | 87,430 | 143,300 | +63.9% |
| Net Income | 4,200 | 12,690 | +202.1% |
| AWS Growth Rate | 30% | 20% | -10.0 ppt |
| Operating Cash Flow | 49,000 | 84,500 | +72.4% |

Narrative:
Amazon showed strong revenue growth driven by its e-commerce segment and continued expansion of AWS, although the growth rate of AWS has moderated slightly. Operational efficiency improved significantly, leading to a substantial increase in net income.
"""
    elif company == 'Microsoft':
        data = f"""
Company: Microsoft (MSFT)
Period: {start_q} to {end_q}

Key Metrics (Millions USD):
| Metric | {start_q} | {end_q} | Change (%) |
|---|---|---|---|
| Total Revenue | 35,020 | 56,190 | +60.4% |
| Net Income | 10,750 | 17,550 | +63.2% |
| Azure Growth Rate | 45% | 35% | -10.0 ppt |
| Productivity/Business | 11,830 | 18,340 | +55.0% |

Narrative:
Microsoft's performance was bolstered by the growth of its Intelligent Cloud segment (Azure), though at a decelerated pace. The Productivity and Business Processes segment (Office 365) also saw robust growth. The company maintained high-profit margins.
"""
    else:
        data = "No specific data found for this company in the simulated dataset."
        
    return data

# --- Core Function: Simulate Gemini API Call ---
async def call_gemini_api(data_prompt: str) -> str:
    """
    Simulates calling the Gemini API to fetch a financial analysis.
    This function returns a mock result in English.
    """
    # Simulate network latency
    time.sleep(1)
            
    # --- MOCK API CALL RESULT (English) ---
    if 'Amazon' in data_prompt:
        return "Amazon demonstrated exceptional performance across the period, primarily driven by a robust 63.9% increase in Total Revenue and a massive 202.1% surge in Net Income. While AWS cloud service growth moderated slightly, strong operational execution translated revenue gains directly into high-level profitability, indicating strong overall financial health and market dominance during the selected quarters."
    elif 'Microsoft' in data_prompt:
        return "Microsoft delivered solid financial results, marked by a 60.4% rise in Total Revenue and a comparable 63.2% growth in Net Income. The company's Intelligent Cloud (Azure) remained the core growth driver, despite a 10-point deceleration in its growth rate. The consistent performance of the Productivity segment highlights the stability and high-margin nature of Microsoft's diversified business model over the selected period."
    else:
        return "Analysis could not be generated due to missing or unrecognized data. Please select valid company and quarter ranges."
    # --- END MOCK API CALL RESULT ---

# --- Main View Function ---
@csrf_exempt # <--- This decorator bypasses the 403 CSRF error for POST requests
def quarterly_selection_view(request: HttpRequest):
    """
    Renders the main page and handles form submission for financial analysis.
    This function handles both GET (initial load) and POST (form submission) requests.
    """
    
    # 1. Initialize Context Variables
    context = {
        'quarters': get_quarter_options(),
        'companies': ['Amazon', 'Microsoft'], # Hardcoded for now
        'analysis_result': None, # No result on initial load
        'selected_company': None,
        'selected_start': None,
        'selected_end': None,
    }

    # 2. Handle POST Request (User clicks Submit button)
    if request.method == 'POST':
        # Retrieve user selections from POST data
        company = request.POST.get('company')
        start_q = request.POST.get('start_quarter')
        end_q = request.POST.get('end_quarter')
        
        # Store selections back into context to maintain selected state on re-render
        context['selected_company'] = company
        context['selected_start'] = start_q
        context['selected_end'] = end_q

        # Validate that all fields have been selected
        if company and start_q and end_q:
            try:
                # Get simulated raw data
                raw_data = get_stock_data(company, start_q, end_q)
                
                # Call the analysis function (simulated)
                analysis_text = call_gemini_api(raw_data) 
                
                # Add the final analysis text to the context
                context['analysis_result'] = analysis_text

            except Exception as e:
                # Catch any errors during data fetching or analysis
                context['analysis_result'] = f"An error occurred during analysis: {e}"
        else:
            # Error message is in English
            context['analysis_result'] = "Please select all fields (Company, Starting Quarter, and Ending Quarter)."

    # 3. Render Template
    # Renders the same template for both GET and POST, passing the updated context
    return render(request, 'api/index.html', context)


