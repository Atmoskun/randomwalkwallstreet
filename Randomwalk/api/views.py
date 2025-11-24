import time
from django.shortcuts import render
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt 

# --- Constants for Simulation ---
# NOTE: API key handling is managed by the canvas environment.
MAX_RETRIES = 5

# --- Helper Function: Quarter Comparison ---
def compare_quarters(q1: str, q2: str) -> int:
    """
    Compares two quarter strings (e.g., '2023Q1').
    
    Returns:
    -1 if q1 < q2 (q1 is earlier)
     0 if q1 == q2 (q1 is the same)
     1 if q1 > q2 (q1 is later)
    """
    # Convert 'YYYYQZ' format to a comparable integer (YYYY * 10 + Z)
    def quarter_to_int(q: str) -> int:
        year = int(q[:4])
        quarter_num = int(q[5:])
        return year * 10 + quarter_num

    val1 = quarter_to_int(q1)
    val2 = quarter_to_int(q2)

    if val1 < val2:
        return -1
    elif val1 == val2:
        return 0
    else:
        return 1

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
    This function returns a mock result in English, which varies based on the selected quarters.
    """
    # Simulate network latency
    time.sleep(1)
    
    # Simple logic to vary the analysis based on the time period included in the raw data
    is_early_period = '2020Q1' in data_prompt or '2020Q2' in data_prompt
    is_recent_period = '2025Q3' in data_prompt or '2025Q4' in data_prompt

    analysis = ""
    
    # --- MOCK API CALL RESULT (English) ---
    if 'Amazon' in data_prompt:
        base_analysis = "Amazon demonstrated exceptional performance across the period, primarily driven by a robust 63.9% increase in Total Revenue and a massive 202.1% surge in Net Income. Strong operational execution translated revenue gains directly into high-level profitability, indicating strong overall financial health and market dominance."
        
        if is_early_period:
            analysis = f"Historical Context: The analysis covering the early 2020 quarters shows {base_analysis} The stability of AWS was critical in mitigating early market volatility during the beginning of the period."
        elif is_recent_period:
            analysis = f"Future Outlook: {base_analysis} The recent trend (2025Q3/Q4) suggests a shift towards maximizing high-margin services (AWS), positioning the company well for sustained, though slower, growth."
        else:
            analysis = base_analysis # Default analysis
            
    elif 'Microsoft' in data_prompt:
        base_analysis = "Microsoft delivered solid financial results, marked by a 60.4% rise in Total Revenue and a comparable 63.2% growth in Net Income. The company's Intelligent Cloud (Azure) remained the core growth driver."
        
        if is_early_period:
            analysis = f"Historical Context: The period including early 2020 quarters highlights the resilience of Microsoft's cloud strategy. {base_analysis} The rapid shift to remote work substantially boosted the usage of Azure and Office 365."
        elif is_recent_period:
            analysis = f"Future Outlook: {base_analysis} The strong recent performance in the Productivity segment indicates continued enterprise commitment to the Office ecosystem, promising reliable future revenue streams."
        else:
            analysis = base_analysis # Default analysis
            
    else:
        analysis = "Analysis could not be generated due to missing or unrecognized data. Please select valid company and quarter ranges."
        
    return analysis

# --- Main View Function ---
@csrf_exempt 
async def quarterly_selection_view(request: HttpRequest):
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
            
            # --- VALIDATION CHECK: Start Quarter vs. End Quarter ---
            # If start_q is later than end_q (result is 1)
            if compare_quarters(start_q, end_q) == 1:
                context['analysis_result'] = "Error: The Starting Quarter cannot be later than the Ending Quarter. Please select a valid range."
                # We render the template immediately with the error message
                return render(request, 'api/index.html', context)
            # --- END VALIDATION CHECK ---

            try:
                # Get simulated raw data
                raw_data = get_stock_data(company, start_q, end_q)
                
                # Call the analysis function (simulated)
                analysis_text = await call_gemini_api(raw_data)
                
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
