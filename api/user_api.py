
import json

from .base.user_base import UserBase
from .exceptions import NotFoundError, DuplicateError, ValidationError
from .storage import JSONStorage
from .utils import generate_id, utc_now
from .validators import parse_json, require_fields, validate_string


class UserAPI(UserBase):
    """Provide concrete user-management operations using JSON storage.

    This class implements the :class:`UserBase` interface and handles
    user creation, retrieval, updating, and team lookup. Application
    data is persisted through ``JSONStorage`` rather than exposing the
    underlying files to API consumers.
    """

    def __init__(self):
        """Initialize storage handlers used by the user API.

        Three storage collections are initialized:

        * ``users.json`` stores user records.
        * ``teams.json`` stores team records.
        * ``team_members.json`` stores team membership relationships.
        """

        self.users = JSONStorage("users.json")
        self.teams = JSONStorage("teams.json")
        self.memberships = JSONStorage("team_members.json")

    def create_user(self, request: str) -> str:
        """Create a new user.

        The username must be unique, and both the username and display
        name are subject to the length constraints defined by
        :class:`UserBase`.

        Args:
            request: JSON string containing ``name`` and
                ``display_name``.

        Returns:
            JSON string containing the generated user ID.

        Raises:
            ValidationError: If the request is invalid or a field
                violates its validation constraints.
            DuplicateError: If a user with the same name already exists.
        """

        data = parse_json(request)
        require_fields(data, ["name", "display_name"])

        name = validate_string(data["name"], "name", 64)
        display_name = validate_string(
            data["display_name"], "display_name", 64
        )

        users = self.users.all()

        if any(user["name"].casefold() == name.casefold() for user in users):
            raise DuplicateError("A user with this name already exists.")

        user_id = generate_id("usr")
        users.append({
            "id": user_id,
            "name": name,
            "display_name": display_name,
            "creation_time": utc_now(),
        })
        self.users.save_all(users)

        return json.dumps({"id": user_id})

    def list_users(self) -> str:
        """Return all users.

        Returns:
            JSON list containing each user's name, display name, and
            creation time.
        """
        users = self.users.all()

        result = [
            {
                "name": user["name"],
                "display_name": user["display_name"],
                "creation_time": user["creation_time"],
            }
            for user in users
        ]

        return json.dumps(result)

    def describe_user(self, request: str) -> str:
        """Return details for a specific user.

        Args:
            request: JSON string containing the user ID.

        Returns:
            JSON string containing the user's name, description, and
            creation time. The ``description`` field represents the
            user's display name to match the supplied base interface.

        Raises:
            ValidationError: If the request is missing the required ID
                or contains an invalid ID.
            NotFoundError: If the requested user does not exist.
        """

        data = parse_json(request)
        require_fields(data, ["id"])
        user_id = validate_string(data["id"], "id", 128)

        user = self._find_user(user_id)

        # The supplied contract uses "description" in this response.
        return json.dumps({
            "name": user["name"],
            "description": user["display_name"],
            "creation_time": user["creation_time"],
        })

    def update_user(self, request: str) -> str:
        """Update a user's display name.

        A user's name is immutable after creation. If ``name`` is
        included in the request, it must match the existing username.
        The display name follows the update-specific length constraint
        defined by :class:`UserBase`.

        Args:
            request: JSON string containing the user ID and updated
                user information.

        Returns:
            JSON string confirming that the user was updated.

        Raises:
            ValidationError: If the request is invalid, the display name
                exceeds its maximum length, or an attempt is made to
                change the username.
            NotFoundError: If the requested user does not exist.
        """

        data = parse_json(request)
        require_fields(data, ["id", "user"])

        user_id = validate_string(data["id"], "id", 128)
        user_data = data["user"]

        if not isinstance(user_data, dict):
            raise ValidationError("'user' must be a JSON object.")

        require_fields(user_data, ["display_name"])

        user = self._find_user(user_id)

        # The username is immutable. Allow it in the request only if unchanged.
        if "name" in user_data:
            requested_name = validate_string(
                user_data["name"], "name", 64
            )
            if requested_name != user["name"]:
                raise ValidationError("A user's name cannot be changed.")

        display_name = validate_string(
            user_data["display_name"], "display_name", 128
        )

        users = self.users.all()
        for existing_user in users:
            if existing_user["id"] == user_id:
                existing_user["display_name"] = display_name
                break

        self.users.save_all(users)
        return json.dumps({"message": "User updated successfully."})

    def get_user_teams(self, request: str) -> str:
        """Return all teams to which a user belongs.

        The method first verifies that the requested user exists and
        then resolves team memberships using the membership storage.

        Args:
            request: JSON string containing the user ID.

        Returns:
            JSON list containing the name, description, and creation
            time of each team associated with the user.

        Raises:
            ValidationError: If the request is missing the required ID
                or contains an invalid ID.
            NotFoundError: If the requested user does not exist.

        
        """

        data = parse_json(request)
        require_fields(data, ["id"])
        user_id = validate_string(data["id"], "id", 128)

        # Also validate that this user exists.
        self._find_user(user_id)

        teams = self.teams.all()
        memberships = self.memberships.all()

        team_ids = set()
        for membership in memberships:
            if user_id in membership.get("user_ids", []):
                team_ids.add(membership["team_id"])

        result = [
            {
                "name": team["name"],
                "description": team["description"],
                "creation_time": team["creation_time"],
            }
            for team in teams
            if team["id"] in team_ids
        ]

        return json.dumps(result)

    def _find_user(self, user_id):
        """Find a user by ID.

        This is an internal helper used by the public user operations.

        Args:
            user_id: Unique identifier of the user to find.

        Returns:
            Dictionary containing the matching user record.

        Raises:
            NotFoundError: If no user exists with the supplied ID.
        """
        
        for user in self.users.all():
            if user["id"] == user_id:
                return user

        raise NotFoundError(f"User '{user_id}' was not found.")
