import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# Frontend selection helpers
# ---
# FIX 1: Import get_quarter_options from analysis, don't define it here
from .analysis import (
    get_file_paths_for_range,
    generate_trend_analysis,
    get_quarter_options
)
# ---

# Backend API helpers
from .file_reader import build_doc_path, read_text_from_path
from .llm_router import call_llm
from .prompts import TREND_PROMPT


# ---------- HTML view for quarter / company selection (coworker-facing) ----------

# The get_quarter_options() function is now imported from api/analysis.py (see above)

def quarterly_selection_view(request):
    """
    Renders an HTML page where the user can:
      - select a company
      - select start and end quarter
    On POST:
      - uses get_file_paths_for_range(...) to build the file list
      - calls generate_trend_analysis(file_list) to get analysis
      - shows the analysis result on the page

    This view is for the interactive web UI (server-rendered).
    """
    company_options = ["Amazon", "Microsoft"]
    quarter_options = get_quarter_options() # This now calls the imported function

    analysis_result = None
    selected_company = request.POST.get("company")
    selected_start = request.POST.get("start_quarter")
    selected_end = request.POST.get("end_quarter")

    if request.method == "POST":
        try:
            # ---
            # This is the correct, two-step logic
            # ---
            
            # 1. Call the file selection function
            file_list_to_process = get_file_paths_for_range(
                selected_company,
                selected_start,
                selected_end,
            )

            # ---
            # Determine the ticker here
            ticker = "AMZN" if selected_company == "Amazon" else "MSFT"
            # ---

            # 2. Call the analysis function with the list of files AND the ticker
            analysis_result = generate_trend_analysis(
                file_list_to_process,
                selected_company,
                selected_start,
                selected_end,
                ticker # Pass the ticker as an argument
            )

        except ValueError as e:
            analysis_result = f"Error: {str(e)}\n\nPlease select a valid range."
        except FileNotFoundError as e:
            analysis_result = f"Error: Missing data file.\n\n{str(e)}"
        except Exception as e:
            analysis_result = f"An unexpected error occurred: {str(e)}"

    context = {
        "company_options": company_options,
        "quarter_options": quarter_options,
        "analysis_result": analysis_result,
        "selected_company": selected_company,
        "selected_start": selected_start,
        "selected_end": selected_end,
    }

    # Template path: templates/api/index.html
    return render(request, "api/index.html", context)


# ---------- JSON API endpoints for programmatic access (your backend contract) ----------

@csrf_exempt
def health(request):
    """
    Simple health check endpoint: GET /api/health
    """
    return JsonResponse({"status": "ok"})


@csrf_exempt
def analyze(request):
    """
    POST /api/analyze
    
    (FIXED: Corrected example format in docstring)

    Expected JSON body:
    {
      "ticker": "AMZN",
      "start": { "year": 2020, "quarter": 1 },
      "end":   { "year": 2020, "quarter": 4 },
      "model": "gpt-4o",
      "doc_files": [
        "Amazon_2020Q1.txt",
        "Amazon_2020Q2.txt",
        "Amazon_2020Q3.txt",
        "Amazon_2020Q4.txt"
      ]
    }

    This is a pure API endpoint for your frontend / other services:
      - It reads the requested files from the /data directory.
      - It builds a contextual prompt.
      - It calls the selected LLM via llm_router.call_llm.
      - It returns a structured JSON summary.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    # Parse JSON payload
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON body")

    ticker = data.get("ticker")
    start = data.get("start")      # dict: {"year": int, "quarter": int}
    end_ = data.get("end")         # dict: {"year": int, "quarter": int}
    doc_files = data.get("doc_files", [])
    model = data.get("model", "gpt-4o")

    # Basic validation
    if not ticker or not start or not end_ or not doc_files:
        return HttpResponseBadRequest(
            "Required fields: ticker, start, end, doc_files"
        )

    # Build context from files
    context_parts = []
    used_files = []

    for filename in doc_files:
        try:
            path = build_doc_path(filename)
            text = read_text_from_path(path)

            # For MVP: truncate to reduce token usage
            snippet = text[:8000]

            context_parts.append(f"[FILE: {filename}]\n{snippet}")
            used_files.append(filename)
        except Exception as e:
            # Keep error info for debugging; you may remove this in production
            context_parts.append(f"[FILE: {filename}] ERROR: {e}")

    if not used_files:
        return JsonResponse(
            {"error": "No readable documents in doc_files."},
            status=400,
        )

    context = "\n\n---\n\n".join(context_parts)

    # Build prompts
    system_prompt = (
        "You are an equity analyst. "
        "Use ONLY the provided context. "
        "Always return strictly valid JSON following the given schema."
    )

    user_prompt = TREND_PROMPT.format(
        ticker=ticker,
        start_q=start["quarter"],
        start_y=start["year"],
        end_q=end_["quarter"],
        end_y=end_["year"],
    ) + "\n\nContext starts below:\n\n" + context

    # Call LLM
    try:
        analysis_json_str = call_llm(model, system_prompt, user_prompt)
    except Exception as e:
        return JsonResponse({"error": f"LLM call failed: {e}"}, status=500)

    # Parse JSON; if LLM output is not valid JSON, wrap raw content
    try:
        analysis = json.loads(analysis_json_str)
    except Exception:
        analysis = {"raw_output": analysis_json_str}

    return JsonResponse(
        {
            "ticker": ticker,
            "period": f"{start['year']}Q{start['quarter']} - "
                      f"{end_['year']}Q{end_['quarter']}",
            "model_used": model,
            "docs_used": used_files,
            "summary": analysis,
        },
        json_dumps_params={"ensure_ascii": False},
    )
