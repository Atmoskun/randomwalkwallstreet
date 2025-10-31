"""
Simple Flask application that collects a user name and email address.
This version skips a database so students can focus on the request flow.
"""

from flask import Flask, redirect, render_template, request, url_for

# Create the Flask app object that will handle incoming requests.
app = Flask(__name__)

# Store submissions in memory so we can show how POST data is handled.
# (In a real app you would save to a database instead.)
SUBMISSIONS = []


@app.route("/", methods=["GET", "POST"])
def index():
    """Display the form and process the submitted data."""
    # When the browser sends data back, the request method switches to POST.
    if request.method == "POST":
        # Pull values out of the submitted form; strip spaces for cleaner input.
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        # Only continue when both fields have content.
        if username and email:
            # Save the submission so students can see where data would live.
            SUBMISSIONS.append({"username": username, "email": email})
            # Redirect to a new page so the browser does not resubmit the form.
            return redirect(url_for("success"))

        # Send the user back to the form with an error message and prior values.
        return render_template(
            "index.html",
            error="Please provide both a user name and an email address.",
            username=username,
            email=email,
        )

    # When the page is loaded normally (GET), simply show the empty form.
    return render_template("index.html")


@app.route("/success")
def success():
    """Show a confirmation page after a successful submission."""
    return render_template("success.html")


if __name__ == "__main__":
    # Start the development server so the app can be tested locally.
    app.run(debug=True)
