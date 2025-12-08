import time
import os
import json
import httpx 
import random 
from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse 
from django.views.decorators.csrf import csrf_exempt 
from .prompts import TREND_PROMPT 

# --- Constants for Simulation and API ---
MAX_RETRIES = 5
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025" 
API_URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# --- Helper Function: Quarter Comparison ---
def compare_quarters(q1: str, q2: str) -> int:
    """
    Compares two quarter strings (e.g., '2023Q1').
    """
    def quarter_to_int(q: str) -> int:
        year = int(q[:4])
        quarter_num = int(q[5:])
        return year * 10 + quarter_num

    val1 = quarter_to_int(q1)
    val2 = quarter_to_int(q2)

    if val1 < val2: return -1
    elif val1 == val2: return 0
    else: return 1

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
    Simulates fetching complex financial data.
    """
    start_y, start_q_num = start_q[:4], start_q[5:]
    end_y, end_q_num = end_q[:4], end_q[5:]
    
    if company == 'Amazon':
        ticker = "AMZN"
        data = f"""
--- Earnings Call Excerpt: Amazon_{start_y}Q{start_q_num}.txt ---
Management Introduction: "Our primary focus remains the aggressive expansion of the global AWS cloud infrastructure."
Analyst Question: "Given the capital expenditure, can you provide guidance on when the retail segment might see substantial leverage?"

--- Earnings Call Excerpt: Amazon_{end_y}Q{end_q_num}.txt ---
Management Introduction: "We have initiated a significant cost-cutting program across all non-core business segments."
Analyst Question: "Market consensus is shifting from volume growth to free cash flow generation."
"""
    elif company == 'Microsoft':
        ticker = "MSFT"
        data = f"""
--- Earnings Call Excerpt: Microsoft_{start_y}Q{start_q_num}.txt ---
Management Introduction: "Azure growth is accelerating, and we are heavily investing in generative AI capabilities."
Analyst Question: "The LinkedIn business unit has shown slower growth. Is this a structural issue?"

--- Earnings Call Excerpt: Microsoft_{end_y}Q{end_q_num}.txt ---
Management Introduction: "Our strategic focus is the commercialization of Co-pilot across the entire M365 suite."
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
        'full_text': data
    }

# --- Core Function: Call the Real Gemini API ---
async def call_gemini_api(api_data: dict) -> str:
    """
    Calls the Gemini API to fetch a plain text analytical paragraph.
    """
    system_instruction = TREND_PROMPT.format(
        ticker=api_data.get('ticker', 'UNKNOWN'),
        start_q=api_data.get('start_q', 'Q1'),
        start_y=api_data.get('start_y', '2023'),
        end_q=api_data.get('end_q', 'Q4'),
        end_y=api_data.get('end_y', '2023'),
    )
    
    user_query = f"Analyze the following file excerpts and output the result according to the provided instructions:\n\n---\n{api_data.get('full_text', 'No content provided.')}\n---\n"
    
    api_key = os.environ.get('GOOGLE_API_KEY', os.environ.get('GEMINI_API_KEY', ""))
    api_url = f"{API_URL_BASE}/{GEMINI_MODEL}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"role": "user", "parts": [{"text": user_query}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client: 
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    api_url, 
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(payload)
                )
                response.raise_for_status()
                result = response.json()
                
                try:
                    final_text = result['candidates'][0]['content']['parts'][0]['text']
                    return final_text.strip() 
                except (KeyError, IndexError) as e:
                    return f"API Structure Error: The model returned an unexpected format. Details: {e}"

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt) 
                else:
                    return f"API Error (HTTP {e.response.status_code}): {e.response.text}"
            except Exception as e:
                return f"An unexpected error occurred during API call: {type(e).__name__} - {e}"

    return "Error: API call failed after multiple retries."

# --- Main View Function ---
@csrf_exempt 
async def quarterly_selection_view(request: HttpRequest):
    """
    Renders the main page and handles the form submission for financial analysis.
    """
    context = {
        'quarters': get_quarter_options(),
        'companies': ['Amazon', 'Microsoft'],
        'analysis_result': None,
        'selected_company': None,
        'selected_start': None,
        'selected_end': None,
    }

    if request.method == 'POST':
        company = request.POST.get('company')
        start_q = request.POST.get('start_quarter')
        end_q = request.POST.get('end_quarter')
        
        context['selected_company'] = company
        context['selected_start'] = start_q
        context['selected_end'] = end_q

        if company and start_q and end_q:
            if compare_quarters(start_q, end_q) == 1:
                context['analysis_result'] = "Error: Starting quarter cannot be later than the ending quarter."
                return render(request, 'api/index.html', context)

            try:
                api_data = get_stock_data(company, start_q, end_q)
                analysis_text = await call_gemini_api(api_data)
                context['analysis_result'] = analysis_text
            except Exception as e:
                context['analysis_result'] = f"An error occurred during analysis: {e}"
        else:
            context['analysis_result'] = "Please select all fields (Company, Starting Quarter, and Ending Quarter)."

    return render(request, 'api/index.html', context)

# --- Analytics / Tracking View ---
@csrf_exempt
def update_visit_time(request: HttpRequest):
    """
    Simple API endpoint to update/log visit time.
    """
    return JsonResponse({'status': 'success', 'message': 'Visit time updated'})

# --- CRITICAL: A/B Testing Endpoint with Google Analytics ---
@csrf_exempt
def ab_test_view(request: HttpRequest):
    """
    Standardized Analytics Endpoint for A/B Testing.
    Endpoint: /9ad7709
    """
    # 1. Variants
    variants = ["kudos", "thanks"]
    selected_variant = random.choice(variants)
    
    # 2. YOUR GOOGLE ANALYTICS ID
    GA_MEASUREMENT_ID = "G-TK15963VF3"
    
    # 3. Render HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>A/B Test - patient-sky</title>
        
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());

          gtag('config', '{GA_MEASUREMENT_ID}');

          // CUSTOM EVENT: TRACK VARIANT SHOWN
          gtag('event', 'ab_variant_shown', {{
            'event_category': 'AB Testing',
            'event_label': '{selected_variant}',
            'team_name': 'patient-sky'
          }});
        </script>

        <style>
            body {{ font-family: sans-serif; text-align: center; padding-top: 50px; }}
            button {{ padding: 15px 30px; font-size: 20px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 5px; }}
            button:hover {{ background: #0056b3; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ font-size: 18px; margin: 10px 0; }}
        </style>
        
        <script>
            function trackClick() {{
                console.log("Button clicked: {selected_variant}");
                
                // CUSTOM EVENT: TRACK BUTTON CLICK
                gtag('event', 'ab_button_click', {{
                    'event_category': 'AB Testing',
                    'event_label': '{selected_variant}'
                }});
                
                alert("You clicked {selected_variant}! (Tracked in Google Analytics)");
            }}
        </script>
    </head>
    <body>
        <h1>Team: patient-sky</h1>
        <h3>Team Members:</h3>
        <ul>
            <li>keyboard-munger</li>
            <li>cooperative-dinosaur</li>
            <li>enthusiastic-sheep</li>
        </ul>
        <br><br>
        
        <!-- The button -->
        <button id="abtest" onclick="trackClick()">{selected_variant}</button>
        
    </body>
    </html>
    """
    return HttpResponse(html_content)
