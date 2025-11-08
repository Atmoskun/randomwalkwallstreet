TREND_PROMPT = """You are a professional equity analyst.
Company: {ticker}
Period: Q{start_q} {start_y} to Q{end_q} {end_y}

Use ONLY the provided context (excerpts from earnings calls/annual reports).
Tasks:
1) Summarize the top 3-5 management focus themes and how they evolved by quarter.
2) Identify any turning points (e.g., shift from growth to margin/FCF focus), citing evidence.
3) List key risks or uncertainties, citing evidence.

Return JSON with:
- themes: [{label, definition, quarters:[{y,q,notes}], evidence:[{path, snippet}]}]
- turning_points: [{y,q, description, evidence:[{path, snippet}]}]
- risks: [{label, description, evidence:[{path, snippet}]}]
If insufficient evidence, leave arrays empty.
"""

