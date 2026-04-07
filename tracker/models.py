from django.db import models
from django.contrib.auth.models import User


class Mark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()
    total = models.IntegerField()
    date = models.DateField()

    def percentage(self):
        return round((self.marks / self.total) * 100, 2)

    def __str__(self):
        return self.exam


from django.utils import timezone

class Assignment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    due_date = models.DateField()
    status = models.CharField(max_length=20, default="Pending")

    def get_deadline_status(self):

        today = timezone.now().date()

        if self.status == "Completed":
            return "completed"

        if self.due_date < today:
            return "overdue"

        elif self.due_date == today:
            return "today"

        elif (self.due_date - today).days == 1:
            return "tomorrow"

        return "upcoming"


class Task(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True , null=True)

    due_date = models.DateField()

    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title