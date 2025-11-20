from django.db import models

class PageView(models.Model):
    path = models.CharField(max_length=255, unique=True)
    visits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.path} - {self.visits} visits"

class SiteVisit(models.Model):
    path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=40, db_index=True)
    time_spent_seconds = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Visit to {self.path} at {self.timestamp}"
