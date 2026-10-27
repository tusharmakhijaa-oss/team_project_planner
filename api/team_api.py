
import json

from .base.team_base import TeamBase
from .exceptions import (
    ConflictError,
    DuplicateError,
    NotFoundError,
    ValidationError,
)
from .storage import JSONStorage
from .utils import generate_id, utc_now
from .validators import parse_json, require_fields, validate_string


class TeamAPI(TeamBase):
    """Implement team and membership operations using JSON storage.

    The class extends TeamBase and stores team records and membership
    records in separate JSON files.

    Attributes:
        MAX_TEAM_MEMBERS: Maximum number of users allowed in a team.
        teams: Storage for team records.
        users: Storage for user records.
        memberships: Storage for team membership records.
    """

    MAX_TEAM_MEMBERS = 50

    def __init__(self):
        """Initialize JSON storage for teams, users, and memberships."""
        self.teams = JSONStorage("teams.json")
        self.users = JSONStorage("users.json")
        self.memberships = JSONStorage("team_members.json")

    def create_team(self, request: str) -> str:
        """Create a team and add its administrator as the first member.

        Args:
            request: JSON string containing ``name``, ``description``,
                and ``admin`` (the ID of an existing user).

        Returns:
            A JSON string containing the newly created team's ID.

        Raises:
            ValidationError: If required fields or values are invalid.
            NotFoundError: If the specified administrator does not exist.
            DuplicateError: If a team with the same name already exists.
        """
        data = parse_json(request)
        require_fields(data, ["name", "description", "admin"])

        name = validate_string(data["name"], "name", 64)
        description = validate_string(
            data["description"], "description", 128
        )
        admin_id = validate_string(data["admin"], "admin", 128)

        self._find_user(admin_id)
        teams = self.teams.all()

        if any(team["name"].casefold() == name.casefold()
               for team in teams):
            raise DuplicateError("A team with this name already exists.")

        # The team administrator is also its initial member.
        team_id = generate_id("team")
        teams.append({
            "id": team_id,
            "name": name,
            "description": description,
            "admin": admin_id,
            "creation_time": utc_now(),
        })

        memberships = self.memberships.all()
        memberships.append({
            "team_id": team_id,
            "user_ids": [admin_id],
        })

        self.teams.save_all(teams)
        self.memberships.save_all(memberships)

        return json.dumps({"id": team_id})

    def list_teams(self) -> str:
        """Return a JSON list of all teams.

        Returns:
            A JSON string containing each team's name, description,
            creation time, and administrator ID.
        """
        result = [
            {
                "name": team["name"],
                "description": team["description"],
                "creation_time": team["creation_time"],
                "admin": team["admin"],
            }
            for team in self.teams.all()
        ]
        return json.dumps(result)

    def describe_team(self, request: str) -> str:
        """Return the details of a specific team.

        Args:
            request: JSON string containing the team's ``id``.

        Returns:
            A JSON string containing the team's details.

        Raises:
            ValidationError: If the request or team ID is invalid.
            NotFoundError: If the team does not exist.
        """
        data = parse_json(request)
        require_fields(data, ["id"])
        team_id = validate_string(data["id"], "id", 128)

        team = self._find_team(team_id)

        return json.dumps({
            "name": team["name"],
            "description": team["description"],
            "creation_time": team["creation_time"],
            "admin": team["admin"],
        })

    def update_team(self, request: str) -> str:
        """Update a team's name, description, and administrator.

        The new administrator is added to the team's membership if
        they are not already a member. Existing memberships are retained.

        Args:
            request: JSON string containing ``id`` and a ``team`` object.
                The team object must contain ``name``, ``description``,
                and ``admin``.

        Returns:
            A JSON string containing a success message.

        Raises:
            ValidationError: If input data is invalid or adding the
                administrator would exceed the membership limit.
            NotFoundError: If the team or administrator does not exist.
            DuplicateError: If another team already uses the new name.
        """
        data = parse_json(request)
        require_fields(data, ["id", "team"])

        team_id = validate_string(data["id"], "id", 128)
        team_data = data["team"]

        if not isinstance(team_data, dict):
            raise ValidationError("'team' must be a JSON object.")

        require_fields(team_data, ["name", "description", "admin"])

        name = validate_string(team_data["name"], "name", 64)
        description = validate_string(
            team_data["description"], "description", 128
        )
        admin_id = validate_string(team_data["admin"], "admin", 128)

        team = self._find_team(team_id)
        self._find_user(admin_id)

        teams = self.teams.all()

        for existing in teams:
            if (
                existing["id"] != team_id
                and existing["name"].casefold() == name.casefold()
            ):
                raise DuplicateError(
                    "Another team already uses this name."
                )

        for existing in teams:
            if existing["id"] == team_id:
                existing["name"] = name
                existing["description"] = description
                existing["admin"] = admin_id
                break

        # Keep the new administrator as a member as well.
        memberships = self.memberships.all()
        membership = self._find_membership(team_id, memberships)
        if admin_id not in membership["user_ids"]:
            if len(membership["user_ids"]) >= self.MAX_TEAM_MEMBERS:
                raise ValidationError(
                    "The team cannot exceed 50 members."
                )
            membership["user_ids"].append(admin_id)

        self.teams.save_all(teams)
        self.memberships.save_all(memberships)

        return json.dumps({"message": "Team updated successfully."})

    def add_users_to_team(self, request: str) -> str:
        """Add existing users to a team's membership.

        User IDs already present in the team are ignored. All supplied
        users are validated before the membership list is modified.

        Args:
            request: JSON string containing ``id`` and ``users``.
                ``id`` identifies the team, and ``users`` is a list
                of user IDs.

        Returns:
            A JSON string containing the team ID and number of users
            actually added.

        Raises:
            ValidationError: If the request is invalid or the membership
                limit would be exceeded.
            NotFoundError: If the team, membership record, or a user
                does not exist.
        """
        data = parse_json(request)
        require_fields(data, ["id", "users"])

        team_id = validate_string(data["id"], "id", 128)
        team = self._find_team(team_id)
        user_ids = self._validate_user_ids(data["users"])

        memberships = self.memberships.all()
        membership = self._find_membership(team_id, memberships)

        # Validate every user before changing membership data.
        for user_id in user_ids:
            self._find_user(user_id)

        new_user_ids = [
            user_id for user_id in user_ids
            if user_id not in membership["user_ids"]
        ]

        if len(membership["user_ids"]) + len(new_user_ids) > (
            self.MAX_TEAM_MEMBERS
        ):
            raise ValidationError("A team cannot have more than 50 members.")

        membership["user_ids"].extend(new_user_ids)
        self.memberships.save_all(memberships)

        return json.dumps({
            "message": "Users added to team successfully.",
            "team_id": team["id"],
            "added_count": len(new_user_ids),
        })

    def remove_users_from_team(self, request: str) -> str:
        """Remove users from a team's membership.

        The current team administrator cannot be removed until the
        administrator role has been transferred to another user.

        Args:
            request: JSON string containing ``id`` and ``users``.
                ``id`` identifies the team, and ``users`` is a list
                of user IDs to remove.

        Returns:
            A JSON string containing the team ID and number of users
            removed.

        Raises:
            ValidationError: If the request or user ID list is invalid.
            NotFoundError: If the team, membership record, or any
                requested membership is missing.
            ConflictError: If the request attempts to remove the
                current administrator.
        """
        data = parse_json(request)
        require_fields(data, ["id", "users"])

        team_id = validate_string(data["id"], "id", 128)
        team = self._find_team(team_id)
        user_ids = self._validate_user_ids(data["users"])

        memberships = self.memberships.all()
        membership = self._find_membership(team_id, memberships)

        # Do not allow removing the current administrator from membership.
        if team["admin"] in user_ids:
            raise ConflictError(
                "Change the team administrator before removing them."
            )

        missing = [
            user_id for user_id in user_ids
            if user_id not in membership["user_ids"]
        ]
        if missing:
            raise NotFoundError(
                f"These users are not members of the team: {', '.join(missing)}"
            )

        membership["user_ids"] = [
            user_id for user_id in membership["user_ids"]
            if user_id not in user_ids
        ]
        self.memberships.save_all(memberships)

        return json.dumps({
            "message": "Users removed from team successfully.",
            "team_id": team["id"],
            "removed_count": len(user_ids),
        })

    def list_team_users(self, request: str) -> str:
        """Return the users who belong to a specific team.

        Args:
            request: JSON string containing the team's ``id``.

        Returns:
            A JSON string containing a list of member objects. Each
            object includes the user's ID, name, and display name.

        Raises:
            ValidationError: If the request or team ID is invalid.
            NotFoundError: If the team or its membership record is
                not found.
        """
        data = parse_json(request)
        require_fields(data, ["id"])

        team_id = validate_string(data["id"], "id", 128)
        self._find_team(team_id)

        memberships = self.memberships.all()
        membership = self._find_membership(team_id, memberships)
        users = self.users.all()
        users_by_id = {user["id"]: user for user in users}

        result = []
        for user_id in membership["user_ids"]:
            user = users_by_id.get(user_id)
            if user is not None:
                result.append({
                    "id": user["id"],
                    "name": user["name"],
                    "display_name": user["display_name"],
                })

        return json.dumps(result)

    def _find_user(self, user_id):
        """Find and return a user by ID.

        Args:
            user_id: Unique identifier of the user.

        Returns:
            The matching user record.

        Raises:
            NotFoundError: If no user has the supplied ID.
        """
        for user in self.users.all():
            if user["id"] == user_id:
                return user
        raise NotFoundError(f"User '{user_id}' was not found.")

    def _find_team(self, team_id):
        """Find and return a team by ID.

        Args:
            team_id: Unique identifier of the team.

        Returns:
            The matching team record.

        Raises:
            NotFoundError: If no team has the supplied ID.
        """
        for team in self.teams.all():
            if team["id"] == team_id:
                return team
        raise NotFoundError(f"Team '{team_id}' was not found.")

    def _find_membership(self, team_id, memberships):
        """Find a team's membership record.

        Args:
            team_id: Unique identifier of the team.
            memberships: Collection of membership records to search.

        Returns:
            The matching membership record.

        Raises:
            NotFoundError: If the team has no membership record.
        """
        for membership in memberships:
            if membership["team_id"] == team_id:
                return membership

        raise NotFoundError(
            f"Membership record for team '{team_id}' was not found."
        )

    def _validate_user_ids(self, value):
        """Validate a list of user IDs.

        The list must contain between one and MAX_TEAM_MEMBERS unique,
        non-empty string IDs.

        Args:
            value: Value supplied as the ``users`` request field.

        Returns:
            The validated list of user IDs.

        Raises:
            ValidationError: If the value is not a valid list of IDs.
        """
        if not isinstance(value, list):
            raise ValidationError("'users' must be a list of user IDs.")

        if not value:
            raise ValidationError("'users' cannot be an empty list.")

        if len(value) > self.MAX_TEAM_MEMBERS:
            raise ValidationError("You can submit at most 50 user IDs.")

        user_ids = []
        for user_id in value:
            user_ids.append(validate_string(user_id, "user ID", 128))

        if len(set(user_ids)) != len(user_ids):
            raise ValidationError("'users' cannot contain duplicate IDs.")

        return user_ids
