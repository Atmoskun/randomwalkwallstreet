Sprint 2 Plan

Date and duration: Nov 5 to Nov 12, one week

Sprint goal: Get a working web app that can take a ticker and quarter range, run analysis, and return basic insights.

Selected user stories:
1. As a user, I can select ticker + quarter range so that results focus on the exact period.	valid ticker; invalid quarter rejected; range inclusive; persisted in URL. (3 points)
2. As a router service, I can pass doc_paths[] to the analysis API so the backend reads only those files.	rejects paths outside allowed folder; returns 400 on missing file; logs used paths. (5 points)
3. As a user, I see Top 5 themes with quarter-by-quarter heat and one or more citations per theme.	JSON schema validated; ≥1 quote/file path per theme; handles no-evidence gracefully. (8 points)
4. As a PM/analyst, I see turning points detected with linked quotes. (5 points)
5. As a developer, I can switch LLM models per request. (5 points)

Total story points: 26 points

Team member assignment:
Alex Xu → front-end
Peter Yang → backend
Sarah Zhang → integration and testing

Identified risks:
Deploying a Django app to Render for the first time will have unforeseen configuration challenges.
Merging two separate apps built by different developers will be complex.
LLM API limits access.
Long files may cause slow responses.
