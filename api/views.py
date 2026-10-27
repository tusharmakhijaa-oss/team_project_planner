"""Handle HTTP requests for the project planner API.

This module connects Django views to user, team, project board, and
task API classes. It provides shared JSON request processing,
response formatting, HTTP method validation, and error handling.
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .user_api import UserAPI
from .team_api import TeamAPI
from .board_api import ProjectBoardAPI
from .exceptions import (
    PlannerError,
    ValidationError,
    NotFoundError,
    DuplicateError,
    ConflictError,
)

user_api = UserAPI()
team_api = TeamAPI()
board_api = ProjectBoardAPI()


def api_endpoint(methods, callback):
    """Create a view with common JSON request and response handling.

    Validate the HTTP method, decode the request body, invoke the
    supplied callback, and convert the result into a JSON response.
    Known application exceptions are translated into HTTP error
    responses.

    Args:
        methods: List of HTTP methods allowed for the endpoint.
        callback: Function that processes the request and its body.

    Returns:
        A CSRF-exempt Django view that returns a JsonResponse.

    HTTP status codes:
        200: Successful GET or non-POST request.
        201: Successful POST request.
        400: Invalid JSON or request data.
        404: Requested resource not found.
        405: HTTP method not allowed.
        409: Duplicate resource or operation conflict.
        500: Other known application-level errors.
    """

    
    def view(request):
        """Process an incoming HTTP request.

        Args:
            request: The incoming Django HTTP request.

        Returns:
            A JSON response containing the operation result or an
            error message.
        """
        if request.method not in methods:
            response = JsonResponse(
                {"error": "Method not allowed"},
                status=405,
            )
            response["Allow"] = ", ".join(methods)
            return response

        try:
            body = request.body.decode("utf-8")
            result = callback(request, body)
            payload = json.loads(result) if isinstance(result, str) else result
            return JsonResponse(
                payload,
                safe=not isinstance(payload, list),
                status=201 if request.method == "POST" else 200,
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid JSON request."}, status=400)
        except ValidationError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except DuplicateError as exc:
            return JsonResponse({"error": str(exc)}, status=409)
        except ConflictError as exc:
            return JsonResponse({"error": str(exc)}, status=409)
        except NotFoundError as exc:
            return JsonResponse({"error": str(exc)}, status=404)
        except PlannerError as exc:
            return JsonResponse({"error": str(exc)}, status=500)

    view.__name__ = callback.__name__
    return csrf_exempt(view)


# User endpoints

def _create_user(request, body):
    """Create a user using the supplied JSON request body."""
    return user_api.create_user(body)


def _list_users(request, body):
    """Retrieve the list of registered users."""
    return user_api.list_users()


def _describe_user(request, body):
    """Retrieve details of the user specified in the request body."""
    return user_api.describe_user(body)


def _update_user(request, body):
    """Update the user specified in the request body."""
    return user_api.update_user(body)


def _get_user_teams(request, body):
    """Retrieve the teams associated with a specified user."""
    return user_api.get_user_teams(body)

# Register user endpoints and their permitted HTTP methods.
create_user = api_endpoint(["POST"], _create_user)
list_users = api_endpoint(["GET"], _list_users)
describe_user = api_endpoint(["POST"], _describe_user)
update_user = api_endpoint(["PUT", "PATCH"], _update_user)
get_user_teams = api_endpoint(["POST"], _get_user_teams)


# Team endpoints

def _create_team(request, body):
    """Create a team using the supplied JSON request body."""
    return team_api.create_team(body)


def _list_teams(request, body):
    """Retrieve the list of teams."""
    return team_api.list_teams()


def _describe_team(request, body):
    """Retrieve details of the team specified in the request body."""
    return team_api.describe_team(body)


def _update_team(request, body):
    """Update the team specified in the request body."""
    return team_api.update_team(body)


def _add_users_to_team(request, body):
    """Add users to the team specified in the request body."""
    return team_api.add_users_to_team(body)


def _remove_users_from_team(request, body):
    """Remove users from the team specified in the request body."""
    return team_api.remove_users_from_team(body)


def _list_team_users(request, body):
    """Retrieve the members of the team specified in the request body."""
    return team_api.list_team_users(body)


create_team = api_endpoint(["POST"], _create_team)
list_teams = api_endpoint(["GET"], _list_teams)
describe_team = api_endpoint(["POST"], _describe_team)
update_team = api_endpoint(["PUT", "PATCH"], _update_team)
add_users_to_team = api_endpoint(["POST"], _add_users_to_team)
remove_users_from_team = api_endpoint(["POST"], _remove_users_from_team)
list_team_users = api_endpoint(["POST"], _list_team_users)


# Project board and task endpoints

def _create_board(request, body):
    """Create a project board using the supplied JSON request body."""
    return board_api.create_board(body)


def _close_board(request, body):
    """Close the project board specified in the request body."""
    return board_api.close_board(body)


def _add_task(request, body):
    """Add a task to a project board."""
    return board_api.add_task(body)


def _update_task_status(request, body):
    """Update the status of a task."""
    return board_api.update_task_status(body)


def _list_boards(request, body):
    """Retrieve project boards matching the supplied criteria."""
    return board_api.list_boards(body)


def _export_board(request, body):
    """Export the specified project board to a text file."""
    return board_api.export_board(body)

# Register project board and task endpoints with their HTTP methods.

create_board = api_endpoint(["POST"], _create_board)
close_board = api_endpoint(["POST"], _close_board)
add_task = api_endpoint(["POST"], _add_task)
update_task_status = api_endpoint(["PATCH", "PUT"], _update_task_status)
list_boards = api_endpoint(["POST"], _list_boards)
export_board = api_endpoint(["POST"], _export_board)
