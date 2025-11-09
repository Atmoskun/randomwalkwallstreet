import time
import os
from django.conf import settings # Allows access to BASE_DIR

# =====================================================================
#   - Determine the list of files to be used.
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

def get_file_paths_for_range(company, start_q, end_q):
    """
    (YOUR FUNCTION)
    Takes the user's selections and returns a list of
    full file paths for the teammate to analyze.
    """
    print(f"[Your Job] Finding files for {company} from {start_q} to {end_q}")

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
        # ASSUMPTION: Files are named 'Amazon_2020Q1.txt' or 'Microsoft_2020Q1.txt'
        # Adjust this line if your file naming is different.
        file_name = f"{company}_{quarter}.txt"
        # ---
        
        # This builds the full path, e.g., /path/to/your/project/data/Amazon_2020Q1.txt
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)
        
        # (Optional but recommended) Check if the file actually exists
        # if not os.path.exists(file_path):
        #     raise FileNotFoundError(f"File not found: {file_name}")
            
        files_to_analyze.append(file_path)

    print(f"[Your Job] Found {len(files_to_analyze)} files. Passing to teammate.")
    return files_to_analyze


# =====================================================================
# YOUR TEAMMATE'S RESPONSIBILITY: 
#   - Read files from the list and generate analysis.
# =====================================================================

def run_teammate_analysis(file_path_list):
    """
    (TEAMMATE'S FUNCTION)
    This is a placeholder for your teammate's analysis code.
    It receives the list of file paths you generated.
    It should return a single string with the analysis results.
    """
    print(f"[Teammate] Received {len(file_path_list)} files to analyze.")
    
    # --- START OF TEAMMATE'S PLACEHOLDER ---
    # Your teammate will replace all this logic.
    
    time.sleep(0.5) # Simulate analysis time
    
    if not file_path_list:
        return "No files were selected for analysis."

    # Your teammate would loop through the files and read them:
    # analysis_summary = ""
    # for path in file_path_list:
    #     with open(path, 'r') as f:
    #         content = f.read()
    #         # ... (do complex analysis on content) ...
    #         analysis_summary += ...
    
    # This demo just lists the files it was given
    file_names_for_display = [os.path.basename(f) for f in file_path_list]
    
    result_string = (
        f"✅ Analysis Complete.\n"
        f"Processed {len(file_names_for_display)} files:\n\n"
        f" - " + "\n - ".join(file_names_for_display)
        + "\n\n(This is the dummy analysis result. Your teammate's real summary will go here.)"
    )
    # --- END OF TEAMMATE'S PLACEHOLDER ---

    print("[Teammate] Analysis complete. Returning results string.")
    return result_string
