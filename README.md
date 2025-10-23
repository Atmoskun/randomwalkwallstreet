# Project Title
How Wall Street Analysts Shift Their Focus Across Multiple Earnings Seasons

# Overview
By leveraging large language models (LLMs) to process earnings call transcripts, the project aims to analyze how Wall Street analysts shift their focus of questions across multiple earnings seasons.

# User Journey 
0 Registration & Authentication
Users must first register and log in to access the platform’s analytical tools.
(Core feature: secure user database and session management.)

1 ompany & Period Selection
After authentication, users can select specific companies (e.g., Microsoft, Amazon) and desired time ranges (e.g., Q1 2020 – Q2 2025) for analysis.
(Core feature: interactive selection interface and query handling.)

2 Automated Transcript Analysis
On the backend, the system retrieves the relevant earnings call transcripts and uses a large language model to process them.
(Core feature: LLM pipeline integrated with pre-stored financial transcripts.)

3 Analyst Attention Mapping
Using customized prompt engineering, the LLM identifies shifts in analyst attention by analyzing the analysts' questions asked during each earnings call. The model then summarizes changes in analysts' focus.
(Core feature: LLM prompt engineering.)

# Core Databases
1 User Database
Stores user registration credentials.

2 Earnings Transcript Database
Contains historical earnings call transcripts for Microsoft and Amazon from Q1 2020 through Q2 2025, referred by company and reporting period.

3 Prompt Engineering Repository
Stores and version-controls optimized prompts used for transcript interpretation. A sample prompt would be: You are the best investor in the market. Based on the following earnings call transcripts from [21Q4] to [23Q3] of [Microsoft], how has the focus of analysts shifted during that period? 

# Usage Sample
A user wants to know how analysts' focus has changed from 21Q4 to 23Q3 for Microsoft. He logs into the system and specifies the company and earnings call period. The system outputs...

###
Here is a breakdown of the shifting analyst focus on Microsoft earnings calls from late 2021 (FY21 Q4) to mid-2023 (FY23 Q3):

1. Late 2021 - Early 2022 (FY21 Q4 - FY22 Q2): Focus on Growth Durability
Primary Concern: Could the accelerated digital transformation and cloud growth driven by the pandemic be sustained?
Key Topics: Azure growth trajectory, M365/Teams seat expansion (SMB/Frontline), E5 upsell, PC market strength, margin expansion potential.
Macro: Acknowledged but secondary; viewed digital tech as potentially deflationary.

2. Mid 2022 - Early 2023 (FY22 Q3 - FY23 Q2): Navigating Macro Headwinds & Optimization
Primary Concern: Impact of worsening global macro conditions (inflation, FX, war, potential recession) on Microsoft's business.
Key Topics: Emergence of "customer optimization" impacting Azure growth, Azure deceleration slope, impact of PC market decline, advertising slowdown, SMB weakness, cost control measures, FX headwinds, OpEx management, the value proposition of suites (E5).
AI: Growing interest in specific products like GitHub Copilot and Azure OpenAI.

3. Mid 2023 (FY23 Q3): The AI Revolution Amid Optimization
Primary Concern: Understanding the massive opportunity, investment, and implications of Generative AI, while still tracking optimization trends.
Key Topics: OpenAI partnership details, AI integration strategy (Azure, M365, Copilots), AI monetization, AI CapEx and impact on Azure margins, duration of the customer optimization cycle, resilience of Office 365.
Macro: Optimization cycle remains a key focus within the broader macro discussion.

Overall Shift:
Analysts' attention moved from sustaining hyper-growth post-pandemic, to scrutinizing resilience against macro headwinds (leading to the "optimization" narrative), and then pivoted sharply to the transformative potential and costs of Generative AI, while still monitoring the optimization cycle.
###