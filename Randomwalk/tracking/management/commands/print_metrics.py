from django.core.management.base import BaseCommand
from tracking.models import PageView, SiteVisit
from django.db.models import Sum, Avg

class Command(BaseCommand):
    help = 'Prints page view and site visit metrics'

    def handle(self, *args, **kwargs):
        self.stdout.write("Page Views:")
        for page_view in PageView.objects.all():
            self.stdout.write(f"- {page_view.path}: {page_view.visits} visits")

        self.stdout.write("\nSite Visits:")
        for visit in SiteVisit.objects.all():
            self.stdout.write(f"- {visit.path} at {visit.timestamp} (Session: {visit.session_key}, Time Spent: {visit.time_spent_seconds}s)")

        self.stdout.write("\nAggregated Metrics:")
        total_visits = PageView.objects.aggregate(total_visits=Sum('visits'))['total_visits']
        self.stdout.write(f"Total Page Visits: {total_visits}")

        avg_time = SiteVisit.objects.aggregate(avg_time=Avg('time_spent_seconds'))['avg_time']
        self.stdout.write(f"Average Time Spent per Visit: {avg_time:.2f} seconds")
