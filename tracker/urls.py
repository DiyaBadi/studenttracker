from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # LOGIN
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # MARKS
    path('marks/', views.marks, name='marks'),
    path('delete-mark/<int:id>/', views.delete_mark, name='delete_mark'),

    # ASSIGNMENTS
    path("assignments/", views.assignments, name="assignments"),
    path("complete-assignment/<int:id>/", views.complete_assignment, name="complete_assignment"),
    path("delete-assignment/<int:id>/", views.delete_assignment, name="delete_assignment"),


    # TASKS
    path("tasks/", views.tasks, name="tasks"),
    path("complete-task/<int:id>/", views.complete_task, name="complete_task"),
    path("delete-task/<int:id>/", views.delete_task, name="delete_task"),
    

    # PROFILE
    path('profile/', views.profile, name='profile'),

    # LOGOUT
    path('', views.hero, name='hero'), 
    path('logout/', views.user_logout ,name='logout'),
     
    path('change-password/', views.change_password, name='change_password'),
     
     
     
     path("edit/<int:id>/", views.edit_mark, name="edit_mark"),
     path("update_mark/<int:id>/", views.update_mark, name="update_mark"),
]