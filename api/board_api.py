
import json
from pathlib import Path

from .base.project_board_base import ProjectBoardBase
from .exceptions import (
    ConflictError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from .storage import JSONStorage
from .utils import generate_id, utc_now
from .validators import parse_json, require_fields, validate_string


BASE_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = BASE_DIR / "out"


class ProjectBoardAPI(ProjectBoardBase):
    """Provide project board and task management operations.

    This class implements :class:`ProjectBoardBase` and manages project
    boards, tasks, task assignments, task statuses, and board exports.

    Data is persisted using JSON files through :class:`JSONStorage`.
    The storage implementation is kept separate from the API business
    logic so that callers do not interact directly with the filesystem.
    """

    VALID_STATUSES = {"OPEN", "IN_PROGRESS", "COMPLETE"}

    def __init__(self):
        """Initialize storage handlers and the board export directory.

        The API maintains separate JSON storage collections for boards,
        tasks, teams, users, and team memberships. The output directory
        used by board exports is also created if it does not already
        exist.
        """
        self.boards = JSONStorage("project_boards.json")
        self.tasks = JSONStorage("tasks.json")
        self.teams = JSONStorage("teams.json")
        self.users = JSONStorage("users.json")
        self.memberships = JSONStorage("team_members.json")
        OUT_DIR.mkdir(parents=True, exist_ok=True)

    def create_board(self, request: str) -> str:
        """Create a new project board for a team.

        Board names must be unique within their associated team.
        Newly created boards start with an ``OPEN`` status.

        Args:
            request: JSON string containing the board name,
                description, team ID, and optional creation time.

        Returns:
            JSON string containing the generated board ID.

        Raises:
            ValidationError: If required fields are missing or contain
                invalid values.
            DuplicateError: If a board with the same name already
                exists for the specified team.
            NotFoundError: If the specified team does not exist.
        """
        data = parse_json(request)
        require_fields(data, ["name", "description", "team_id"])

        name = validate_string(data["name"], "name", 64)
        description = validate_string(
            data["description"], "description", 128
        )
        team_id = validate_string(data["team_id"], "team_id", 128)

        self._find_team(team_id)

        # A board name must be unique within its team.
        boards = self.boards.all()
        for board in boards:
            if (
                board["team_id"] == team_id
                and board["name"].casefold() == name.casefold()
            ):
                raise DuplicateError(
                    "This team already has a board with that name."
                )

        creation_time = data.get("creation_time", utc_now())
        creation_time = validate_string(
            creation_time, "creation_time", 64
        )

        board_id = generate_id("board")
        boards.append({
            "id": board_id,
            "name": name,
            "description": description,
            "team_id": team_id,
            "creation_time": creation_time,
            "status": "OPEN",
            "end_time": None,
        })
        self.boards.save_all(boards)

        return json.dumps({"id": board_id})

    def close_board(self, request: str) -> str:
        """Close a project board when all its tasks are complete.

        A board can only be closed when every task associated with it
        has a ``COMPLETE`` status. Once closed, the board's status is
        changed to ``CLOSED`` and an end timestamp is recorded.

        Args:
            request: JSON string containing the board ID.

        Returns:
            JSON string containing a success message and board ID.

        Raises:
            ValidationError: If the request is missing the board ID or
                contains an invalid ID.
            NotFoundError: If the specified board does not exist.
            ConflictError: If the board is already closed or contains
                incomplete tasks.
        """

        data = parse_json(request)
        require_fields(data, ["id"])

        board_id = validate_string(data["id"], "id", 128)
        board = self._find_board(board_id)

        if board["status"] == "CLOSED":
            raise ConflictError("This board is already closed.")

        tasks = [
            task for task in self.tasks.all()
            if task["board_id"] == board_id
        ]

        incomplete_tasks = [
            task for task in tasks
            if task["status"] != "COMPLETE"
        ]

        if incomplete_tasks:
            raise ConflictError(
                "Cannot close the board until all tasks are complete."
            )

        boards = self.boards.all()
        for item in boards:
            if item["id"] == board_id:
                item["status"] = "CLOSED"
                item["end_time"] = utc_now()
                break

        self.boards.save_all(boards)

        return json.dumps({
            "message": "Board closed successfully.",
            "id": board_id,
        })

    def add_task(self, request: str) -> str:
        """Add a task to an open project board.

        The assigned user must exist and must belong to the team that
        owns the board. Task titles must be unique within a board.

        Args:
            request: JSON string containing the board ID, task title,
                description, assigned user ID, and optional creation
                time.

        Returns:
            JSON string containing the generated task ID.

        Raises:
            ValidationError: If the request is invalid or the assigned
                user does not belong to the board's team.
            DuplicateError: If another task with the same title exists
                on the board.
            NotFoundError: If the board, user, or team membership does
                not exist.
            ConflictError: If the board is closed.
        """
        data = parse_json(request)
        require_fields(
            data,
            ["board_id", "title", "description", "user_id"],
        )

        board_id = validate_string(data["board_id"], "board_id", 128)
        title = validate_string(data["title"], "title", 64)
        description = validate_string(
            data["description"], "description", 128
        )
        user_id = validate_string(data["user_id"], "user_id", 128)

        board = self._find_board(board_id)

        if board["status"] != "OPEN":
            raise ConflictError("Tasks can only be added to open boards.")

        user = self._find_user(user_id)

        # A task must be assigned to a member of the board's team.
        membership = self._find_membership(board["team_id"])
        if user_id not in membership["user_ids"]:
            raise ValidationError(
                "The assigned user must belong to the board's team."
            )

        tasks = self.tasks.all()

        for task in tasks:
            if (
                task["board_id"] == board_id
                and task["title"].casefold() == title.casefold()
            ):
                raise DuplicateError(
                    "A task with this title already exists on this board."
                )

        creation_time = data.get("creation_time", utc_now())
        creation_time = validate_string(
            creation_time, "creation_time", 64
        )

        task_id = generate_id("task")
        tasks.append({
            "id": task_id,
            "board_id": board_id,
            "title": title,
            "description": description,
            "user_id": user["id"],
            "creation_time": creation_time,
            "status": "OPEN",
        })
        self.tasks.save_all(tasks)

        return json.dumps({"id": task_id})

    def update_task_status(self, request: str) -> str:
        """Update the status of an existing task.

        Tasks belonging to closed boards cannot be updated.

        Args:
            request: JSON string containing the task ID and requested
                status.

        Returns:
            JSON string containing the task ID, updated status, and a
            success message.

        Raises:
            ValidationError: If the request is invalid or the requested
                status is not one of the supported statuses.
            NotFoundError: If the specified task or its board does not
                exist.
            ConflictError: If the task belongs to a closed board.
        """

        data = parse_json(request)
        require_fields(data, ["id", "status"])

        task_id = validate_string(data["id"], "id", 128)
        status = validate_string(data["status"], "status", 32).upper()

        if status not in self.VALID_STATUSES:
            raise ValidationError(
                "Status must be OPEN, IN_PROGRESS, or COMPLETE."
            )

        tasks = self.tasks.all()
        task = next(
            (item for item in tasks if item["id"] == task_id),
            None,
        )

        if task is None:
            raise NotFoundError(f"Task '{task_id}' was not found.")

        board = self._find_board(task["board_id"])
        if board["status"] != "OPEN":
            raise ConflictError(
                "Tasks on a closed board cannot be updated."
            )

        task["status"] = status
        self.tasks.save_all(tasks)

        return json.dumps({
            "message": "Task status updated successfully.",
            "id": task_id,
            "status": status,
        })

    def list_boards(self, request: str) -> str:
        """Return all open boards belonging to a team.

        Args:
            request: JSON string containing the team ID.

        Returns:
            JSON list containing the ID and name of each open board
            belonging to the specified team.

        Raises:
            ValidationError: If the request is invalid.
            NotFoundError: If the specified team does not exist.
        """
        data = parse_json(request)
        require_fields(data, ["team_id"])

        team_id = validate_string(data["team_id"], "team_id", 128)
        self._find_team(team_id)

        result = [
            {"id": board["id"], "name": board["name"]}
            for board in self.boards.all()
            if (
                board["team_id"] == team_id
                and board["status"] == "OPEN"
            )
        ]

        return json.dumps(result)

    def export_board(self, request: str) -> str:
        """Export a project board and its tasks to a text file.

        The generated file contains board metadata and a readable list
        of tasks, including task descriptions, assigned users, status,
        and creation times.

        Args:
            request: JSON string containing the board ID.

        Returns:
            JSON string containing the generated output filename.

        Raises:
            ValidationError: If the request is invalid.
            NotFoundError: If the specified board does not exist.
            StorageError: If the output file cannot be written.
        """
        data = parse_json(request)
        require_fields(data, ["id"])

        board_id = validate_string(data["id"], "id", 128)
        board = self._find_board(board_id)
        tasks = [
            task for task in self.tasks.all()
            if task["board_id"] == board_id
        ]

        users_by_id = {
            user["id"]: user for user in self.users.all()
        }

        lines = [
            f"PROJECT BOARD: {board['name']}",
            "=" * 60,
            f"Board ID: {board['id']}",
            f"Description: {board['description']}",
            f"Team ID: {board['team_id']}",
            f"Status: {board['status']}",
            f"Created: {board['creation_time']}",
            f"Ended: {board['end_time'] or 'Not closed'}",
            "",
            "TASKS",
            "-" * 60,
        ]

        if not tasks:
            lines.append("No tasks on this board.")
        else:
            for index, task in enumerate(tasks, start=1):
                assigned_user = users_by_id.get(task["user_id"], {})
                display_name = assigned_user.get(
                    "display_name", task["user_id"]
                )

                lines.extend([
                    f"{index}. {task['title']}",
                    f"   Task ID: {task['id']}",
                    f"   Description: {task['description']}",
                    f"   Assigned to: {display_name}",
                    f"   Status: {task['status']}",
                    f"   Created: {task['creation_time']}",
                    "",
                ])

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"{board_id}.txt"
        file_path = OUT_DIR / filename

        try:
            file_path.write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            from .exceptions import StorageError
            raise StorageError("Unable to export the project board.") from exc

        return json.dumps({"out_file": filename})

    def _find_board(self, board_id):
        """Find a project board by its ID.

        Args:
            board_id: Unique identifier of the board.

        Returns:
            Dictionary containing the matching board record.

        Raises:
            NotFoundError: If the board does not exist.
        """
        for board in self.boards.all():
            if board["id"] == board_id:
                return board
        raise NotFoundError(f"Board '{board_id}' was not found.")

    def _find_team(self, team_id):
        """Find a team by its ID.

        Args:
            team_id: Unique identifier of the team.

        Returns:
            Dictionary containing the matching team record.

        Raises:
            NotFoundError: If the team does not exist.
        """
        for team in self.teams.all():
            if team["id"] == team_id:
                return team
        raise NotFoundError(f"Team '{team_id}' was not found.")

    def _find_user(self, user_id):
        """Find a user by their ID.

        Args:
            user_id: Unique identifier of the user.

        Returns:
            Dictionary containing the matching user record.

        Raises:
            NotFoundError: If the user does not exist.
        """
        for user in self.users.all():
            if user["id"] == user_id:
                return user
        raise NotFoundError(f"User '{user_id}' was not found.")

    def _find_membership(self, team_id):
        """Find the membership record for a team.

        Args:
            team_id: Unique identifier of the team.

        Returns:
            Dictionary containing the team's membership record.

        Raises:
            NotFoundError: If no membership record exists for the team.
        """
        for membership in self.memberships.all():
            if membership["team_id"] == team_id:
                return membership
        raise NotFoundError(
            f"Membership record for team '{team_id}' was not found."
        )
