"""Provide utility functions for IDs and UTC timestamps.

This module contains reusable helper functions used by the project
planner API to generate unique resource identifiers and timestamps.
"""
import uuid
from datetime import datetime, timezone


def generate_id(prefix):
    """Generate a unique identifier with the specified prefix.

    A UUID4 hexadecimal string is appended to the prefix, separated
    by an underscore. This format can be used for users, teams,
    project boards, and other resources.

    Args:
        prefix: Prefix identifying the resource type, such as ``"user"``
            or ``"team"``.

    Returns:
        A string containing the prefix and a unique UUID4 value.
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def utc_now():
    """Return the current UTC timestamp in ISO 8601 format.

    The timestamp includes timezone information so that it can be
    stored consistently and interpreted independently of the server's
    local timezone.

    Returns:
        The current UTC timestamp as an ISO 8601 formatted string.
    """
    return datetime.now(timezone.utc).isoformat()