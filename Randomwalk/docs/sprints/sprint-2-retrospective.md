Sprint 2 Retrospective

Date: Nov 12, 2025
Attendees: Alex Xu, Peter Yang, Sarah Zhang

What went well?

Successful App Merge: The integration of the mailinglist and api apps was successful, with shared settings and correct URL routing (/ and /analysis/).
Database Connection: We successfully configured a production PostgreSQL database and proved it works.
Critical Team Debugging: The team worked together to debug several "show-stopper" bugs that are common in production.
Identified and added the missing psycopg2-binary database driver.

What didn't go well?

Incomplete Error Handling: The initial try/except blocks were not good enough. The api/analysis.py block was too narrow.
Initial Config Gaps: We initially failed to set the SECRET_KEY and DATABASE_URL in the Render environment, which caused confusion and deploy failures.

What to improve? (Action Items)
Improve Error Reporting: The fix in api/views.py to import traceback and print the full error was a lifesaver. So we need to make this a standard pattern for all top-level view functions in Sprint 3. (Assignee: Peter, Due: end of sprint 3)
Test Requirements Locally: We hit errors in requirements.txt that could have been caught locally. So all developers must run pip install -r requirements.txt in a clean local virtual environment to validate it before merging a PR. (Assignee: all, Due: ongoing)
