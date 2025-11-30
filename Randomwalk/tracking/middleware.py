from .models import PageView, SiteVisit

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Get the response first
        # We process after the view to ensure we only track valid pages (e.g., status 200)
        response = self.get_response(request)

        # 2. Filtering logic
        # Exclude admin pages, static files, favicons, and error pages (non-200)
        if (request.path.startswith(('/admin', '/static', '/favicon.ico')) or 
            response.status_code != 200):
            return response

        # 3. Ensure Session exists
        # This generates a session_key for anonymous users, allowing us to track unique visitors
        if not request.session.session_key:
            request.session.save()

        # 4. Update aggregate PageView count
        # This tracks the total number of times a specific URL has been hit
        path = request.path
        page_view, _ = PageView.objects.get_or_create(path=path)
        page_view.visits += 1
        page_view.save()

        # 5. Log the individual visit (SiteVisit)
        # We set time_spent_seconds to 0 because the backend cannot accurately measure client-side duration
        SiteVisit.objects.create(
            path=path,
            session_key=request.session.session_key,
            time_spent_seconds=0 
        )

        return response