import time
import os
import json
import httpx # Import asynchronous HTTP client
from django.shortcuts import render
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt 
from .prompts import TREND_PROMPT, ANALYSIS_SCHEMA # Import prompt and JSON Schema

# --- Constants for Simulation and API ---
# NOTE: API key handling is managed by the canvas environment.
MAX_RETRIES = 5
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# --- Helper Function: Quarter Comparison ---
def compare_quarters(q1: str, q2: str) -> int:
    """
    Compares two quarter strings (e.g., '2023Q1').
    
    Returns:
    -1 if q1 < q2 (q1 is earlier)
     0 if q1 == q2 (q1 is same)
     1 if q1 > q2 (q1 is later)
    """
    # Converts 'YYYYQZ' format to a comparable integer
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
    quarters = []
    for year in range(2020, 2026):
        for q in range(1, 5):
            quarters.append(f"{year}Q{q}")
    return quarters

# --- Helper Function: Simulate Stock Data Fetching ---
def get_stock_data(company: str, start_q: str, end_q: str) -> dict:
    """
    Simulates fetching complex financial data and earnings transcripts, 
    which will serve as the "context" for the LLM analysis.
    """
    # Extract year and quarter numbers for prompt formatting
    start_y, start_q_num = start_q[:4], start_q[5:]
    end_y, end_q_num = end_q[:4], end_q[5:]
    
    # Simulate actual transcript/report content for LLM analysis
    if company == 'Amazon':
        ticker = "AMZN"
        # Simulate Amazon transcript excerpts
        data = f"""
--- Earnings Call Excerpt: Amazon_{start_y}Q{start_q_num}.txt ---
Management Introduction: "Our primary focus remains the aggressive expansion of the global AWS cloud infrastructure, even if this puts pressure on near-term margins. We believe the long-term opportunity from Cloud CapEx is critical."
Analyst Question: "Given the capital expenditure, can you provide guidance on when the retail segment might see substantial leverage and operating margin expansion?"

--- Earnings Call Excerpt: Amazon_{end_y}Q{end_q_num}.txt ---
Management Introduction: "We have initiated a significant cost-cutting program across all non-core business segments. Profitability, especially in our mature business areas, is now a key performance indicator. AI integration in fulfillment centers is driving efficiencies."
Analyst Question: "Market consensus is shifting from volume growth to free cash flow generation. How does the current supply chain risk profile influence your capital expenditure strategy for the next 12 months?"
"""
    elif company == 'Microsoft':
        ticker = "MSFT"
        # Simulate Microsoft transcript excerpts
        data = f"""
--- Earnings Call Excerpt: Microsoft_{start_y}Q{start_q_num}.txt ---
Management Introduction: "Azure growth is accelerating, and we are heavily investing in generative AI capabilities. We believe this represents a critical inflection point for enterprise computing."
Analyst Question: "The LinkedIn business unit has shown slower growth. Is this a structural issue, or are you confident you can improve its monetization in the coming quarters?"

--- Earnings Call Excerpt: Microsoft_{end_y}Q{end_q_num}.txt ---
Management Introduction: "Our strategic focus is the commercialization of Co-pilot across the entire M365 suite. We are maintaining strict control over headcount to ensure margin expansion while funding AI R&D."
Analyst Question: "Given Azure's increasing market dominance, particularly in the European Union, what are the regulatory risks involved?"
"""
    else:
        return { 'full_text': "No simulated data found for this company." }
        
    return {
        'ticker': ticker,
        'start_y': start_y,
        'start_q': start_q_num,
        'end_y': end_y,
        'end_q': end_q_num,
        'full_text': data # This is the "transcript" content
    }


# --- Core Function: Call the Real Gemini API ---
async def call_gemini_api(api_data: dict) -> str:
    """
    Calls the Gemini API to fetch structured JSON analysis based on the simulated transcript data.
    """
    
    # 1. Prepare the Prompt
    # Fill the TREND_PROMPT template with user selections and simulation data
    system_instruction = TREND_PROMPT.format(
        ticker=api_data.get('ticker', 'UNKNOWN'),
        start_q=api_data.get('start_q', 'Q1'),
        start_y=api_data.get('start_y', '2023'),
        end_q=api_data.get('end_q', 'Q4'),
        end_y=api_data.get('end_y', '2023'),
    )
    
    # The actual query sent to the model, containing the prompt instructions and content to analyze
    user_query = f"Analyze the following file excerpts and output the JSON result according to the provided instructions:\n\n---\n{api_data.get('full_text', 'No content provided.')}\n---\n"
    
    # 2. Prepare API Request Parameters
    api_key = os.environ.get('GEMINI_API_KEY', "") # In a production environment, set GEMINI_API_KEY env var
    api_url = f"{API_URL_BASE}/{GEMINI_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_query}]
            }
        ],
        "config": {
            # Ensure model returns JSON matching the schema
            "responseMimeType": "application/json",
            "responseSchema": ANALYSIS_SCHEMA
        },
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        }
    }
    
    # 3. Execute API Call (using httpx for asynchronous operation)
    async with httpx.AsyncClient(timeout=30.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                # Perform the POST request
                response = await client.post(
                    api_url, 
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload)
                )
                response.raise_for_status() # Check for 4xx/5xx errors
                
                # Check response structure
                result = response.json()
                
                # Extract the JSON string from the response
                json_string = result['candidates'][0]['content']['parts'][0]['text']
                
                # Format the JSON string for pretty display on the page
                parsed_json = json.loads(json_string)
                # Use indent=2 for human-readable output
                return json.dumps(parsed_json, indent=2, ensure_ascii=False)

            except httpx.HTTPStatusError as e:
                # Handle rate limiting (429)
                if e.response.status_code == 429 and attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limited (429). Retrying in {wait_time} seconds...")
                    await time.sleep(wait_time)
                else:
                    return f"API Error (HTTP {e.response.status_code}): {e.response.text}"
            except Exception as e:
                return f"An unexpected error occurred during API call: {e}"

    return "Error: API call failed after multiple retries."


# --- Main View Function ---
@csrf_exempt 
async def quarterly_selection_view(request: HttpRequest):
    """
    Renders the main page and handles the form submission for financial analysis.
    """
    
    # 1. Initialize context variables
    context = {
        'quarters': get_quarter_options(),
        'companies': ['Amazon', 'Microsoft'], # Hardcoded for now
        'analysis_result': None, # No result on initial load
        'selected_company': None,
        'selected_start': None,
        'selected_end': None,
    }

    # 2. Handle POST Request (User clicks submit button)
    if request.method == 'POST':
        # Retrieve user selections from POST data
        company = request.POST.get('company')
        start_q = request.POST.get('start_quarter')
        end_q = request.POST.get('end_quarter')
        
        # Store selections back to context to preserve state on re-render
        context['selected_company'] = company
        context['selected_start'] = start_q
        context['selected_end'] = end_q

        # Validate that all fields are selected
        if company and start_q and end_q:
            
            # --- Validation Check: Start Quarter vs End Quarter ---
            if compare_quarters(start_q, end_q) == 1:
                context['analysis_result'] = "Error: Starting quarter cannot be later than the ending quarter. Please select a valid range."
                return render(request, 'api/index.html', context)
            # --- End Validation Check ---

            try:
                # Get simulated raw data (now returns a dict with all data)
                api_data = get_stock_data(company, start_q, end_q)
                
                # Call the real API function
                analysis_text = await call_gemini_api(api_data)
                
                # Add the final analysis text to the context
                context['analysis_result'] = analysis_text

            except Exception as e:
                # Catch any errors that occur during data fetching or analysis
                context['analysis_result'] = f"An error occurred during analysis: {e}"
        else:
            context['analysis_result'] = "Please select all fields (Company, Starting Quarter, and Ending Quarter)."

    # 3. Render the template
    return render(request, 'api/index.html', context)
