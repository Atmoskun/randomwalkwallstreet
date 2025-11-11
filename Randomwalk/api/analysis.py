import time
import os
import json
from pathlib import Path
from django.conf import settings

# 1. IMPORT YOUR TEAMMATE'S NEW HELPER FILES
from .file_reader import read_text_from_path
from .llm_router import call_llm
from .prompts import TREND_PROMPT


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def get_quarter_options():
    """Helper function to get a master list of all quarters."""
    quarters = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            quarters.append(f"{year}Q{quarter}")
    quarters.append("2025Q1")
    quarters.append("2025Q2")
    return quarters

# =====================================================================
# FUNCTION 1: FILE SELECTION
# =====================================================================

def get_file_paths_for_range(company, start_q, end_q):
    """
    (This is the file-path logic, moved into the correct function)
    Takes the user's selections and returns a list of
    full file paths for the teammate to analyze.
    """
    print(f"[File Job] Finding files for {company} from {start_q} to {end_q}")
    all_quarters = get_quarter_options()
    
    try:
        start_index = all_quarters.index(start_q)
        end_index = all_quarters.index(end_q)
    except ValueError:
        raise ValueError(f"Invalid quarter selection ({start_q} or {end_q}).")

    if start_index > end_index:
        raise ValueError(f"Start quarter '{start_q}' is after end quarter '{end_q}'.")

    selected_quarters = all_quarters[start_index : end_index + 1]
    
    files_to_analyze = []
    for quarter in selected_quarters:
        
        # ---
        # The correct filename format
        # f"{company}_{quarter}.txt"
        file_name = f"{company}_{quarter}.txt"
        # ---
        
        # Use Path objects like in file_reader.py
        file_path = Path(settings.BASE_DIR) / 'data' / file_name
        files_to_analyze.append(file_path)

    print(f"[File Job] Found {len(files_to_analyze)} files. Passing to analysis.")
    return files_to_analyze


# =====================================================================
# FUNCTION 2: ANALYSIS LOGIC
# =====================================================================

def generate_trend_analysis(file_path_list, company, start_q, end_q):
    """
    (This is the analysis logic, moved into the correct function)
    This function takes the file list and other selections,
    reads the files, calls the LLM, and returns a
    formatted string for the webpage.
    """
    print(f"[Analysis Job] Received {len(file_path_list)} files. Starting analysis.")
    
    try:
        # 1. Build context from files
        context_parts = []
        used_files = []
        
        for path in file_path_list:
            filename = path.name # Get filename from Path object
            try:
                # read_text_from_path takes a Path object, which we have
                text = read_text_from_path(path)
                snippet = text[:8000] # Use 8000 char limit
                
                context_parts.append(f"[FILE: {filename}]\n{snippet}")
                used_files.append(filename)
            except FileNotFoundError:
                context_parts.append(f"[FILE: {filename}] ERROR: File not found.")
            except Exception as e:
                context_parts.append(f"[FILE: {filename}] ERROR: {e}")

        if not used_files:
            return "Error: No readable documents found for the selected range."

        context = "\n\n---\n\n".join(context_parts)

        # 2. Build prompts
        system_prompt = (
            "You are an equity analyst. "
            "Use ONLY the provided context. "
            "Always return strictly valid JSON following the given schema."
        )

        # Parse quarters to get year/quarter numbers for the prompt
        start_y, start_q_num = start_q.split('Q')
        end_y, end_q_num = end_q.split('Q')
        
        # Guess the ticker
        ticker = "AMZN" if company == "Amazon" else "MSFT"

        user_prompt = TREND_PROMPT.format(
            ticker=ticker,
            start_q=start_q_num,
            start_y=start_y,
            end_q=end_q_num,
            end_y=end_y,
        ) + "\n\nContext starts below:\n\n" + context

        # 3. Call LLM
        # Using "gpt-4o" as the default
        print("[Analysis Job] Calling LLM... This may take a moment.")
        analysis_json_str = call_llm("gpt-4o", system_prompt, user_prompt)
        print("[Analysis Job] LLM call complete.")
        
        # 4. Format the JSON result for the webpage
        try:
            analysis_data = json.loads(analysis_json_str)
            # Convert the Python dictionary back into a nicely formatted JSON string
            formatted_json_output = json.dumps(analysis_data, indent=2)
        except Exception:
            # If the LLM didn't return valid JSON, just show the raw text
            formatted_json_output = analysis_json_str

        # Build the final string for the <pre> tag in the HTML
        result_string = (
            f"✅ Analysis Complete for {company} ({start_q} to {end_q})\n"
            f"Model Used: gpt-4o\n"
            f"Documents Used: {', '.join(used_files)}\n\n"
            f"--- ANALYSIS SUMMARY (JSON) ---\n"
            f"{formatted_json_output}"
        )
        
        return result_string

    except Exception as e:
        # Catch any errors during the analysis
        print(f"[Analysis Job] Analysis failed: {e}")
        return f"An unexpected error occurred during analysis: {str(e)}"
