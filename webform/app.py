"""
Simple Flask application that collects a user name and email address.
This version skips a database so students can focus on the request flow.

This version includes flash messaging for success alerts.
"""

# 1. Import flash, redirect, and url_for, which are needed for the PRG pattern
from flask import Flask, redirect, render_template, request, url_for, flash

# Create the Flask app object that will handle incoming requests.
app = Flask(__name__)

# 2. A secret key is required to use flash messages (which rely on sessions)
app.secret_key = "a_random_secret_key_change_me"  # IMPORTANT: Change this in production!

# Store submissions in memory so we can show how POST data is handled.
# (In a real app you would save to a database instead.)
SUBMISSIONS = []


@app.route("/", methods=["GET", "POST"])
def index():
    """Display the form and process the submitted data."""
    
    error = None  # Initialize error variable
    
    # When the browser sends data back, the request method switches to POST.
    if request.method == "POST":
        # Pull values out of the submitted form; strip spaces for cleaner input.
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()

        # Only continue when both fields have content.
        if username and email:
            # --- Success Logic ---
            
            # Save the submission so students can see where data would live.
            SUBMISSIONS.append({"username": username, "email": email})
            
            # Store the "Success submit!" message to be shown on the next page load.
            flash("Success submit!") 
            
            # 3. Redirect back to the 'index' view (using the Post-Redirect-Get pattern)
            # This prevents form re-submission on page refresh.
            return redirect(url_for('index'))
        
        else:
            # --- Failure Logic ---
            
            # Set the error message
            error = "Please provide both a user name and an email address."
            
            # Send the user back to the form with the error message and prior values.
            # We re-render here (no redirect) so they can see the error.
            return render_template(
                "index.html",
                error=error,
                username=username,
                email=email,
            )

    # When the page is loaded normally (GET), simply show the form.
    # This will also render any messages queued up by flash().
    return render_template("index.html", error=error)

if __name__ == "__main__":
    # Start the development server so the app can be tested locally.
    app.run(debug=True)