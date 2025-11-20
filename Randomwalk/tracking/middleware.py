from .models import PageView, SiteVisit
from django.utils import timezone

class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude admin paths to avoid tracking admin activity
        if request.path.startswith('/admin'):
            return self.get_response(request)

        # Update visit count
        path = request.path
        page_view, _ = PageView.objects.get_or_create(path=path)
        page_view.visits += 1
        page_view.save()

        # Record the start time of the visit
        request.session['start_time'] = timezone.now().isoformat()

        response = self.get_response(request)

        # Record the visit details after the response is generated
        if not request.user.is_authenticated:
            return response

        if not request.session.session_key:
            request.session.create()

        start_time_str = request.session.get('start_time')
        if start_time_str:
            start_time = timezone.datetime.fromisoformat(start_time_str)
            end_time = timezone.now()
            time_spent = (end_time - start_time).seconds

            SiteVisit.objects.create(
                path=path,
                session_key=request.session.session_key,
                time_spent_seconds=time_spent
            )

        return response
