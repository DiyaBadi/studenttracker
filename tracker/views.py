from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import date
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta


# Import models
from .models import Mark, Assignment, Task

# Import aggregation functions
from django.db.models import Max, Avg

# --------------------------
# Home Page
# --------------------------
def home(request):
    return render(request, "index.html")

# --------------------------
# Register User
# --------------------------
def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "register.html")

# --------------------------
# Login User
# --------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "login.html")

# --------------------------
# Logout
# --------------------------
@login_required


def user_logout(request):
    logout(request)  # ends the user session
    return redirect('hero')  # redirect to your hero page
# --------------------------
# Dashboard
# --------------------------
@login_required
def dashboard(request):
    #send_deadline_notifications()

    marks = Mark.objects.filter(user=request.user).order_by("date")

    labels = []
    data = []

    for m in marks:
        percentage = (m.marks / m.total) * 100
        labels.append(m.exam)
        data.append(round(percentage, 2))

    # Pending assignments
    pending_assignments = Assignment.objects.filter(
        user=request.user, status="Pending"
    ).count()

    # Pending tasks
    pending_tasks = Task.objects.filter(user=request.user, completed=False).count()

    # Average marks
    average_marks = round(sum(data) / len(data), 2) if data else 0

    # Upcoming deadlines
    upcoming_assignments = Assignment.objects.filter(
        user=request.user, status="Pending"
    ).order_by("due_date")[:5]

    context = {
        "pending_assignments": pending_assignments,
        "pending_tasks": pending_tasks,
        "average_marks": average_marks,
        "upcoming_assignments": upcoming_assignments,
        "labels": labels,
        "data": data,
    }

    return render(request, "dashboard.html", context)
# --------------------------
# Change Username
# --------------------------
@login_required
def change_username(request):
    if request.method == "POST":
        new_username = request.POST.get("username")
        user = request.user
        user.username = new_username
        user.save()
        messages.success(request, "Username updated successfully")
        return redirect("profile")

    return render(request, "change_username.html")

# --------------------------
# Marks Tracker
# --------------------------

@login_required
def marks(request):

    marks = Mark.objects.filter(user=request.user)

    edit_mark = None

    if 'edit' in request.GET:
        edit_mark = Mark.objects.get(id=request.GET['edit'])

    if request.method == "POST":

        exam = request.POST['exam']
        subject = request.POST['subject']
        date = request.POST['date']
        marks_scored = request.POST['marks']
        total = request.POST['total']

        if request.POST.get("mark_id"):

            mark = Mark.objects.get(id=request.POST['mark_id'])
            mark.exam = exam
            mark.subject = subject
            mark.date = date
            mark.marks = marks_scored
            mark.total = total
            mark.save()

        else:

            Mark.objects.create(
                user=request.user,
                exam=exam,
                subject=subject,
                date=date,
                marks=marks_scored,
                total=total
            )

        return redirect('marks')

    total_exams = marks.count()

    total_percentage = 0
    highest_marks = 0
    subject_scores = {}

    for m in marks:

        if m.total > 0:
            percentage = (m.marks / m.total) * 100
        else:
            percentage = 0

        m.percentage = round(percentage,2)

        total_percentage += percentage

        if percentage > highest_marks:
            highest_marks = percentage

        subject_scores.setdefault(m.subject, []).append(percentage)

    average_marks = round(total_percentage / total_exams,2) if total_exams else 0

    best_subject = "-"
    weak_subject = "-"

    if subject_scores:

        subject_avg = {s: sum(v)/len(v) for s,v in subject_scores.items()}

        best_subject = max(subject_avg,key=subject_avg.get)
        weak_subject = min(subject_avg,key=subject_avg.get)

    context = {
        "marks": marks,
        "total_exams": total_exams,
        "average_marks": average_marks,
        "highest_marks": round(highest_marks,2),
        "best_subject": best_subject,
        "weak_subject": weak_subject,
        "edit_mark": edit_mark
    }

    return render(request,"marks.html",context)
    
@login_required
def edit_mark(request, id):
    mark = get_object_or_404(Mark, id=id, user=request.user)

    if request.method == "POST":
        mark.exam = request.POST.get("exam")
        mark.subject = request.POST.get("subject")
        mark.marks = int(request.POST.get("marks"))
        mark.total = int(request.POST.get("total"))
        mark.date = request.POST.get("date")
        mark.save()
        messages.success(request, "Mark updated successfully")
        return redirect("marks")

    return render(request, "edit_mark.html", {"mark": mark})

@login_required
def delete_mark(request, id):
    mark = get_object_or_404(Mark, id=id, user=request.user)
    mark.delete()
    messages.success(request, "Mark deleted successfully")
    return redirect("marks")

# --------------------------
# Assignments
# --------------------------

@login_required
def assignments(request):

    if request.method == "POST":

        title = request.POST.get("title")
        subject = request.POST.get("subject")
        due_date = request.POST.get("due_date")

        Assignment.objects.create(
            user=request.user,
            title=title,
            subject=subject,
            due_date=due_date,
            status="Pending"
        )

        return redirect("assignments")

    assignments = Assignment.objects.filter(user=request.user).order_by("due_date")

    total = assignments.count()
    pending = assignments.filter(status="Pending").count()
    completed = assignments.filter(status="Completed").count()

    context = {
        "assignments": assignments,
        "total": total,
        "pending": pending,
        "completed": completed
    }

    return render(request, "assignments.html", context)


@login_required
def complete_assignment(request,id):

    assignment = Assignment.objects.get(id=id)

    assignment.status = "Completed"

    assignment.save()

    return redirect("assignments")
@login_required
def delete_assignment(request, id):

    assignment = Assignment.objects.get(id=id)

    assignment.delete()

    return redirect("assignments")
# --------------------------
# Tasks
# --------------------------



@login_required
def tasks(request):

    if request.method == "POST":
        title = request.POST.get("title")
        due_date = request.POST.get("due_date")

        Task.objects.create(
            user=request.user,
            title=title,
            due_date=due_date
        )

        return redirect("tasks")
    tasks=Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(completed=False).count()
    completed_tasks = tasks.filter(completed=True).count()
    
    context = {
        "tasks": tasks,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks
    }

    return render(request, "tasks.html", context)

@login_required
def complete_task(request,id):
    task = Task.objects.get(id=id , user=request.user)
    task.completed = True
    task.save()
    return redirect("tasks")


@login_required
def delete_task(request,id):
    task = Task.objects.get(id=id , user=request.user)
    task.delete()
    return redirect("tasks")

# --------------------------
# Profile Page
# --------------------------
@login_required
def profile(request):
    return render(request, "profile.html")

from django.http import JsonResponse
import json

def update_mark(request,id):

    if request.method == "POST":

        data = json.loads(request.body)

        mark = Mark.objects.get(id=id, user=request.user)

        mark.exam = data["exam"]
        mark.subject = data["subject"]
        mark.date = data["date"]
        mark.marks = data["marks"]
        mark.total = data["total"]

        mark.save()

        return JsonResponse({"status":"success"})


#def send_deadline_notifications():

    tomorrow = timezone.now().date() + timedelta(days=1)

    assignments = Assignment.objects.filter(
        due_date=tomorrow,
        status="Pending"
    )

    for a in assignments:

        send_mail(
            "Assignment Reminder",
            f"Reminder: Your assignment '{a.title}' for {a.subject} is due tomorrow.",
            "your_email@gmail.com",
            [a.user.email],
            fail_silently=True,
        )

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keeps user logged in
            return redirect('profile')  # redirect after success

    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})

def hero(request):
    return render(request, "index.html")
    