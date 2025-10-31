# mailinglist/views.py

from django.shortcuts import render
from .models import Submission  # Import your Submission model

def index(request):
    
    # 1. Prepare an empty message variable
    message_to_show = ""
    
    # 2. Check if the user pressed the "Submit" button (POST)
    if request.method == "POST":
        
        # 3. Get the data from the form
        #    (Corresponds to name="username" in index.html)
        name_from_form = request.POST.get("username")
        #    (Corresponds to name="email" in index.html)
        email_from_form = request.POST.get("email")
        
        # 4. Validate (Even though HTML has 'required', checking again is safer)
        if name_from_form and email_from_form:
        
            # 5. Save the data to the database
            Submission.objects.create(
                username=name_from_form, 
                email=email_from_form
            )
            
            # 6. Prepare a "Submission successful" message
            message_to_show = "Submission successful! Thank you, " + name_from_form
        
        else:
            # 7. If someone bypassed the HTML 'required' attribute
            message_to_show = "Please fill out all fields!"

    # 8. 
    # Render the index.html webpage
    # And pass the 'success_message' variable to the HTML
    #
    # (Note: The path must match yours, e.g., 'mailinglist/index.html')
    return render(request, 'mailinglist/index.html', {
        'success_message': message_to_show
    })