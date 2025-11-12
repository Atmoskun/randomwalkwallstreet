import json
from pathlib import Path
from django.conf import settings

# Our helper modules
from .llm_router import call_llm
from .file_reader import build_doc_path, read_text_from_path
from .prompts import TREND_PROMPT

# --- Function 1: Quarter Options (Helper) ---

def get_quarter_options():
    """
    Build the list of available quarter options for the dropdown.
    Adjust the range as needed when new data is added.
    """
    quarters = []
    for year in range(2020, 2025):
        for quarter in range(1, 5):
            quarters.append(f"{year}Q{quarter}")
    # Explicit extra entries
    quarters.append("2025Q1")
    quarters.append("2025Q2")
    return quarters

# --- Function 2: File Path Logic (Your Responsibility) ---

def get_file_paths_for_range(company, start_q, end_q):
    """
    Given a company, start quarter, and end quarter, build the list
    of all fully-qualified file paths to be analyzed.
    """
    all_quarters = get_quarter_options()
    
    try:
        start_index = all_quarters.index(start_q)
        end_index = all_quarters.index(end_q)
    except ValueError:
        raise ValueError("Invalid quarter selection.")

    if start_index > end_index:
        raise ValueError("Start quarter must be before or the same as end quarter.")
        
    # Slice the list to get all quarters in the range (inclusive)
    selected_quarters = all_quarters[start_index : end_index + 1]
    
    files_to_process = []
    for quarter in selected_quarters:
        # Use the format: Amazon_2020Q1.txt
        filename = f"{company}_{quarter}.txt"
        
        # Use our centralized path builder from file_reader.py
        full_path = build_doc_path(filename)
        
        # Check if the file actually exists before adding it
        if not full_path.exists():
            raise FileNotFoundError(f"Missing data file: {filename}")
            
        files_to_process.append(full_path)
        
    return files_to_process

# --- Function 3: Analysis Logic (Your Responsibility) ---

def generate_trend_analysis(file_path_list, company, start_q, end_q, ticker):
    """
    Reads text from files, builds a prompt, calls the LLM,
    and formats the JSON response into a human-readable string.
    
    This is the "main" analysis function.
    """
    
    # 1. Read context from all files
    context_parts = []
    for path in file_path_list:
        try:
            text = read_text_from_path(path)
            # Truncate to save tokens (adjust as needed)
            snippet = text[:8000]
            context_parts.append(f"[FILE: {path.name}]\n{snippet}\n")
        except Exception as e:
            context_parts.append(f"[FILE: {path.name}] ERROR: Could not read file. {e}\n")
    
    context = "\n---\n".join(context_parts)
    
    # 2. Build Prompts
    system_prompt = (
        "You are an expert equity research analyst. "
        "Use ONLY the provided context. "
        "Return a valid JSON object matching the requested schema."
    )
    
    # Get the correct year/quarter for the prompt
    start_y, start_q_num = start_q.split('Q')
    end_y, end_q_num = end_q.split('Q')
    
    user_prompt = TREND_PROMPT.format(
        ticker=ticker,
        start_q=start_q_num,
        start_y=start_y,
        end_q=end_q_num,
        end_y=end_y,
    ) + "\n\n--- CONTEXT BEGINS ---\n" + context + "\n--- CONTEXT ENDS ---"

    
    # 3. Call LLM and Format Response
    #
    # *** THIS IS THE CORRECTED PART ***
    # The entire block is now inside the try...except
    #
    try:
        # Step 3a: Call the LLM
        # This is where API Key errors, rate limits, etc. will happen
        result = call_llm(
            model_name="gpt-4o",  # Using a powerful model by default
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # Step 3b: Parse the JSON response
        # This will fail if the LLM returns non-JSON text
        json_result = json.loads(result)
        
        # Step 3c: Format the JSON into a human-readable string
        # This is the part that was failing before. Now it is protected.
        output_lines = ["Analysis successful:\n"]
        
        output_lines.append("== Major Themes ==")
        for theme in json_result.get("themes", []):
            output_lines.append(f"\n- Theme: {theme.get('name', 'N/A')}")
            output_lines.append(f"  Summary: {theme.get('summary', 'N/A')}")
            for ev in theme.get("evidence", []):
                output_lines.append(f"    - Evidence: \"{ev.get('quote', '...')}\" (Source: {ev.get('file', 'N/A')})")

        output_lines.append("\n\n== Turning Points ==")
        for point in json_result.get("turning_points", []):
            output_lines.append(f"\n- Point ({point.get('year', 'Y')} Q{point.get('quarter', 'Q')}): {point.get('description', 'N/A')}")
            for ev in point.get("evidence", []):
                output_lines.append(f"    - Evidence: \"{ev.get('quote', '...')}\" (Source: {ev.get('file', 'N/A')})")
        
        output_lines.append("\n\n== Key Risks ==")
        for risk in json_result.get("risks", []):
             output_lines.append(f"\n- Risk: {risk.get('name', 'N/A')}")
             output_lines.append(f"  Description: {risk.get('description', 'N/A')}")
             for ev in risk.get("evidence", []):
                output_lines.append(f"    - Evidence: \"{ev.get('quote', '...')}\" (Source: {ev.get('file', 'N/A')})")

        return "\n".join(output_lines)

    # Specific error for bad JSON
    except json.JSONDecodeError:
        return (f"Error: LLM returned invalid JSON. Could not parse response.\n\n"
                f"Raw LLM Output:\n{result}")
    
    # Specific error for bad JSON structure (like missing "themes")
    except KeyError as e:
        return f"Error during analysis: LLM returned an invalid JSON structure. Missing key: {str(e)}"
    
    # General catch-all for any other errors (e.g., API keys, rate limits)
    except Exception as e:
        return f"Error during LLM call: {str(e)}"
