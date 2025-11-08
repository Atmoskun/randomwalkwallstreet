import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .file_reader import build_doc_path, read_text_from_path
from .llm_router import call_llm
from .prompts import TREND_PROMPT


@csrf_exempt
def health(request):
    return JsonResponse({"status": "ok"})


@csrf_exempt
def analyze(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON body")

    ticker = data.get("ticker")
    start = data.get("start")  # {"year": 2020, "quarter": 1}
    end_ = data.get("end")     # {"year": 2021, "quarter": 4}
    doc_files = data.get("doc_files", [])  # ["Amazon_2020_Q1.txt", ...]
    model = data.get("model", "gpt-4o")    # default model

    # Basic validation
    if not ticker or not start or not end_ or not doc_files:
        return HttpResponseBadRequest(
            "Required fields: ticker, start, end, doc_files"
        )

    # Load context from the selected files
    context_parts = []
    used_files = []

    for filename in doc_files:
        try:
            path = build_doc_path(filename)
            text = read_text_from_path(path)
            # For MVP, truncate long files to control token usage
            snippet = text[:8000]
            context_parts.append(f"[FILE: {filename}]\n{snippet}")
            used_files.append(filename)
        except Exception as e:
            # For now, just skip unreadable files and include error info
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
        "Only use the provided context. "
        "Always return valid JSON as specified."
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

    # Try to parse output as JSON; if it fails, return raw text as fallback
    try:
        analysis = json.loads(analysis_json_str)
    except Exception:
        analysis = {"raw_output": analysis_json_str}

    return JsonResponse(
        {
            "ticker": ticker,
            "period": f"{start['year']}Q{start['quarter']} - {end_['year']}Q{end_['quarter']}",
            "model_used": model,
            "docs_used": used_files,
            "summary": analysis,
        },
        json_dumps_params={"ensure_ascii": False},
    )

