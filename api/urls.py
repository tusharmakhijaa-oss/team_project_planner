"""Define URL routes for the project planner API.

This module maps HTTP paths to view functions for user management,
team management, project boards, and task operations.

Include this URL configuration in the main Django URL configuration
to expose the API endpoints.
"""

from django.urls import path

from . import views

urlpatterns = [
    # User management endpoints.
    path("users/create/", views.create_user, name="create_user"),
    path("users/", views.list_users, name="list_users"),
    path("users/describe/", views.describe_user, name="describe_user"),
    path("users/update/", views.update_user, name="update_user"),
    path("users/teams/", views.get_user_teams, name="get_user_teams"),

    # Team management endpoints.
    path("teams/create/", views.create_team, name="create_team"),
    path("teams/", views.list_teams, name="list_teams"),
    path("teams/describe/", views.describe_team, name="describe_team"),
    path("teams/update/", views.update_team, name="update_team"),
    path("teams/users/add/", views.add_users_to_team, name="add_users_to_team"),
    path("teams/users/remove/", views.remove_users_from_team, name="remove_users_from_team"),
    path("teams/users/", views.list_team_users, name="list_team_users"),

    # Project board and task endpoints.
    path("boards/create/", views.create_board, name="create_board"),
    path("boards/close/", views.close_board, name="close_board"),
    path("boards/", views.list_boards, name="list_boards"),
    path("boards/export/", views.export_board, name="export_board"),
    path("tasks/add/", views.add_task, name="add_task"),
    path("tasks/status/", views.update_task_status, name="update_task_status"),
]
