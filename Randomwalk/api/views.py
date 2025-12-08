import time
import os
import json
import httpx # Import asynchronous HTTP client
import random # <--- ADDED for A/B testing
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse # <--- ADDED HttpResponse
from django.views.decorators.csrf import csrf_exempt 
# Updated import: Only TREND_PROMPT is needed now
from .prompts import TREND_PROMPT 

# --- Constants for Simulation and API ---
MAX_RETRIES = 5
# Using the fastest model available in the preview environment
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
        # q format is 'YYYYQZ', e.g., '2023Q1'
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
        # FIX: Changed {end_y_num} to {end_q_num} below to prevent crash
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


# --- Core Function: Call the Real Gemini API (Updated for Plain Text) ---
async def call_gemini_api(api_data: dict) -> str:
    """
    Calls the Gemini API to fetch a plain text analytical paragraph based on the simulated transcript data.
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
    user_query = f"Analyze the following file excerpts and output the result according to the provided instructions:\n\n---\n{api_data.get('full_text', 'No content provided.')}\n---\n"
    
    # 2. Prepare API Request Parameters
    api_key = os.environ.get('GOOGLE_API_KEY', os.environ.get('GEMINI_API_KEY', ""))
    
    print(f"DEBUG: API Key Loaded (first 4 chars): {api_key[:4]}...")

    api_url = f"{API_URL_BASE}/{GEMINI_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_query}]
            }
        ],
        # REMOVED: generationConfig for JSON schema
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        }
    }
    
    # 3. Execute API Call (using httpx for asynchronous operation)
    async with httpx.AsyncClient(timeout=60.0) as client: 
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
                
                # --- Simplified Text Extraction ---
                try:
                    # Extract the raw text string from the response
                    final_text = result['candidates'][0]['content']['parts'][0]['text']
                    # Strip any surrounding whitespace or markdown fences, if any
                    return final_text.strip() 
                except (KeyError, IndexError) as e:
                    # If the expected path is missing, print the raw response for debugging
                    print(f"API Response Structure Error: Missing expected key in response. Raw Response: {json.dumps(result, indent=2)}")
                    return f"API Structure Error: The model returned an unexpected format. Details: {e}"
                # --- End Simplified Text Extraction ---

            except httpx.HTTPStatusError as e:
                # Handle rate limiting (429)
                if e.response.status_code == 429 and attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    print(f"Rate limited (429). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time) 
                elif e.response.status_code == 400:
                    error_message = f"API Error (HTTP 400): {e.response.text}"
                    print(error_message)
                    return error_message
                else:
                    return f"API Error (HTTP {e.response.status_code}): {e.response.text}"
            except Exception as e:
                print(f"Generic Unexpected Error: {type(e).__name__} - {e}")
                return f"An unexpected error occurred during API call: {type(e).__name__} - {e}"

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

# --- Analytics / Tracking View ---
# This is the function that was MISSING in your uploaded file!
@csrf_exempt
def update_visit_time(request: HttpRequest):
    """
    Simple API endpoint to update/log visit time.
    """
    return JsonResponse({'status': 'success', 'message': 'Visit time updated'})

# --- CRITICAL: A/B Testing Endpoint ---
# Hash: 9ad7709
@csrf_exempt
def ab_test_view(request: HttpRequest):
    """
    Standardized Analytics Endpoint for A/B Testing.
    Endpoint: /9ad7709
    """
    # 1. Variants
    variants = ["kudos", "thanks"]
    
    # 2. Random selection
    # We use simple random choice here as requested.
    selected_variant = random.choice(variants)
    
    # 3. Analytics Tracking (Simple Server-Side Logging)
    # This prints to your Render logs so you can count them later.
    print(f"A/B TEST TRACKING: Visitor at /9ad7709 saw variant: {selected_variant}")
    
    # 4. Render HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>A/B Test - patient-sky</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; padding-top: 50px; }}
            button {{ padding: 15px 30px; font-size: 20px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; }}
            button:hover {{ background: #0056b3; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ font-size: 18px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>Team: patient-sky</h1>
        <h3>Team Members:</h3>
        <ul>
            <li>bald-chicken</li>
            <li>keyboard-munger</li>
            <li>enthusiastic-sheep</li>
        </ul>
        <br><br>
        <button id="abtest">{selected_variant}</button>
    </body>
    </html>
    """
    return HttpResponse(html_content)
