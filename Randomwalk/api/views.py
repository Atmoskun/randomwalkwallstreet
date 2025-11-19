import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

# --- Imports for the new Architecture ---
from .llm_router import call_llm
# We need to import the database model we created
# from .models import EarningsCallSummary 

# ---------- Helper Functions ----------

def get_quarter_options():
    """
    Build the list of available quarter options for the dropdown.
    """
    quarters = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            quarters.append(f"{year}Q{quarter}")
    return quarters

def get_trend_analysis(summaries_text, ticker, start_q, end_q):
    """
    Helper function to call the LLM for trend analysis.
    It uses the 'summaries' from the database as context.
    """
    system_prompt = (
        "You are an expert financial analyst. "
        "Your task is to analyze the evolution of management focus and investor concerns "
        "over a period of time, based strictly on the provided quarterly summaries."
    )

    user_prompt = (
        f"Here are the quarterly summaries for {ticker} from {start_q} to {end_q}.\n"
        f"Please identify the key qualitative changes and trends.\n"
        f"What topics became more important? What topics faded away?\n\n"
        f"--- SUMMARIES START ---\n{summaries_text}\n--- SUMMARIES END ---"
    )

    # *** KEY CHANGE: We force the use of Gemini Flash here for speed and free cost ***
    # Make sure your .env has GEMINI_API_KEY (or GOOGLE_API_KEY)
    return call_llm("gemini/gemini-1.5-flash", system_prompt, user_prompt)


# ---------- HTML view (The one your website uses) ----------

def quarterly_selection_view(request):
    """
    This is the view for your Web Interface (Figure 2).
    Now it queries the DATABASE instead of reading files.
    """
    # Options for the dropdowns
    company_options = ["Amazon", "Microsoft"]
    quarter_options = get_quarter_options()

    analysis_result = None
    selected_company = request.POST.get("company")
    selected_start = request.POST.get("start_quarter")
    selected_end = request.POST.get("end_quarter")

    if request.method == "POST":
        try:
            # 1. Validation
            if not selected_company or not selected_start or not selected_end:
                raise ValueError("Please select Company, Start Quarter, and End Quarter.")

            if selected_start > selected_end:
                raise ValueError("Start quarter cannot be after End quarter.")

            # 2. Query the Database (Phase B Logic)
            # We look for summaries that match the company and fall within the time range.
            summaries_qs = EarningsCallSummary.objects.filter(
                company_name__iexact=selected_company, # iexact ignores case (Amazon vs amazon)
                quarter__gte=selected_start,
                quarter__lte=selected_end
            ).order_by('quarter')

            if not summaries_qs.exists():
                analysis_result = (
                    f"No data found in database for {selected_company} ({selected_start}-{selected_end}).\n"
                    "Have you run the preprocessing script yet?\n"
                    "Run: python manage.py process_earnings_calls"
                )
            else:
                # 3. Combine the short summaries into one text
                combined_text = ""
                for item in summaries_qs:
                    combined_text += f"\n=== Quarter: {item.quarter} ===\n"
                    combined_text += item.summary
                    combined_text += "\n"

                # 4. Call LLM (Gemini) to analyze the trend
                # This is fast because we are only sending summaries, not whole PDFs
                analysis_result = get_trend_analysis(
                    combined_text, selected_company, selected_start, selected_end
                )

        except Exception as e:
            analysis_result = f"Error: {str(e)}"

    context = {
        "company_options": company_options,
        "quarter_options": quarter_options,
        "analysis_result": analysis_result,
        "selected_company": selected_company,
        "selected_start": selected_start,
        "selected_end": selected_end,
    }

    return render(request, "api/index.html", context)


# ---------- JSON API Endpoint (Optional, for external access) ----------

@csrf_exempt
def analyze(request):
    """
    API version of the above logic.
    POST /api/analyze
    Body: { "ticker": "Amazon", "start": "2020Q1", "end": "2020Q4" }
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        ticker = data.get("ticker")
        start = data.get("start") # Expecting string e.g. "2020Q1"
        end_ = data.get("end")    # Expecting string e.g. "2020Q4"
        
        # Database Query
        summaries_qs = EarningsCallSummary.objects.filter(
            company_name__iexact=ticker,
            quarter__gte=start,
            quarter__lte=end_
        ).order_by('quarter')

        if not summaries_qs.exists():
            return JsonResponse({"error": "No summaries found. Please run ingestion script."}, status=404)

        combined_text = "\n".join([s.summary for s in summaries_qs])
        
        # Call LLM
        result = get_trend_analysis(combined_text, ticker, start, end_)
        
        return JsonResponse({"result": result})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    