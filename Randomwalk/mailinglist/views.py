# mailinglist/views.py

from django.shortcuts import render, redirect  # <--- CHANGED: Added redirect
from .models import Submission  # Import your Submission model

def index(request):
    
    # 1. Prepare an empty message variable
    message_to_show = ""
    
    # 2. Check if the user pressed the "Submit" button (POST)
    if request.method == "POST":
        name_from_form = request.POST.get("username")
        email_from_form = request.POST.get("email")
        
        # 4. Validate (Even though HTML has 'required', checking again is safer)
        if name_from_form and email_from_form:
        
            # 5. Save the data to the database
            Submission.objects.create(
                username=name_from_form, 
                email=email_from_form
            )
            
            # 6. Submission is successful! Redirect to the analysis page.
            #    This is the line you wanted to change.
            return redirect('/analysis/') # <--- CHANGED: This is the new line
        
        else:
            # 7. If someone bypassed the HTML 'required' attribute
            message_to_show = "Please fill out all fields!"

    # 8. 
    # Render the index.html webpage
    # This part now only runs for the *first* page load (GET request)
    # or if the form submission was invalid.
    return render(request, 'mailinglist/index.html', {
        'success_message': message_to_show
    })

def earnings(request):
    return render(request, 'mailinglist/earnings.html')
