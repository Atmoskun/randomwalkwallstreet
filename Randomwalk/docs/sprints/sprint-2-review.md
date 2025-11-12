Sprint 2 Review

Sprint Goal

Deploy a working "v0.1" web application to the Render staging environment. The app must successfully connect a database, serve a frontend, and demonstrate the core end-to-end analysis loop.

Goal Status: ACHIEVED

Completed Work

All 26 planned story points were completed. The team successfully integrated the mailinglist and api apps and deployed a working application to Render that achieves the full end-to-end logic.

Staging URL: https://randomwalkwallstreet.onrender.com/

Demo & Screenshots

"Signup" Page (/): The mailinglist app serves as the entry point, capturing user info and saving it to the production PostgreSQL database.

Analysis Page (/analysis/): After signup, the user is correctly redirected to the api app.

End-to-End Test:

User selects "Amazon", "2020Q1" to "2020Q2".

User clicks "Submit".

The backend api/views.py correctly calls api/analysis.py.

The app correctly reads Amazon_2020Q1.txt and Amazon_2020Q2.txt.

The app builds the prompt and successfully calls the OpenAI API.

The AI's JSON response is caught, parsed, and formatted.

The final analysis is displayed in the "Output Data" box.

Completed User Stories

Issue

User Story

Story Points

Notes

#1

"As a user, I can select ticker + quarter range..."

3

Done. (Frontend: Alex) Implemented in api/templates/api/index.html.

#2

"As a router service, I can pass doc_paths[]..."

5

Done. (Backend: Peter) Implemented in api/analysis.py (get_file_paths_for_range).

#3

"As a user, I see Top 5 themes..."

8

Done. (Backend: Peter) Implemented in api/analysis.py (generate_trend_analysis) and api/prompts.py.

#4

"As a PM/analyst, I see turning points..."

5

Done. (Backend: Peter) Bundled with Story #3 in the same LLM prompt.

#5

"As a developer, I can switch LLM models..."

5

Done. (Backend: Peter) litellm and llm_router.py are implemented.

Unplanned Work (Technical Overhead & Debugging)

A significant amount of work was dedicated by the whole team (especially Integration) to production-izing and debugging the merged application:

Configured a new production PostgreSQL database on Render.

Merged and refactored the two separate Django apps (mailinglist and api).

Created build.sh for Render deployment.

Wrote production settings.py (Whitenoise, dj_database_url, environment variables).

Resolved multiple critical deployment-blocking bugs (see Retrospective).

Sprint Metrics

Planned Story Points: 26

Completed Story Points: 26

Velocity: 26

Completion Rate: 100%

Lessons Learned

Deployment is a "Real" Feature: The effort to configure production (build.sh, settings.py, database, environment variables) is significant and must be treated as a high-priority, team-wide task.

Error Messages are Critical: The initial, generic error messages (like An unexpected error occurred...) were useless. Improving the try/except blocks to show the full traceback was the key to solving the bugs.

Local vs. Production: The app worked locally but failed on Render due to requirements.txt issues and database drivers (psycopg2). The production environment is the only "real" test.

Product Backlog Updates

A new "Technical Debt" issue was identified to refactor the massive requirements.txt file, as it slows down deployments (see Retrospective).

A new bug was created and resolved: "Login page does not redirect to analysis page." (Fixed in mailinglist/views.py).
