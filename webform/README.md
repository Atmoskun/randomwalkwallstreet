# Simple Signup Form

This example pairs a minimal HTML form with a Flask backend that stores user names and email addresses in a SQLite database.

## Prerequisites

- Python 3.9+ recommended
- `pip` to install dependencies

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell
pip install -r requirements.txt
```

## Run the App

```bash
python app.py
```

Open your browser to http://127.0.0.1:5000/ to submit entries. Submissions are stored in `submissions.db` alongside `app.py`.
