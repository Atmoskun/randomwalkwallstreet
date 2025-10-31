from pathlib import Path
import sqlite3

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE_PATH = Path(__file__).resolve().parent / "submissions.db"


def init_db() -> None:
    """Create the submissions table if it does not exist."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            )
            """
        )


@app.before_first_request
def setup() -> None:
    init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        if username and email:
            with sqlite3.connect(DATABASE_PATH) as connection:
                connection.execute(
                    "INSERT INTO submissions (username, email) VALUES (?, ?)",
                    (username, email),
                )
            return redirect(url_for("success"))

        return render_template(
            "index.html",
            error="Please provide both a user name and an email address.",
            username=username,
            email=email,
        )

    return render_template("index.html")


@app.route("/success")
def success():
    return render_template("success.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
