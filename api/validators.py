"""Provide validation helpers for incoming API requests.

This module validates JSON request bodies, checks for required fields,
and verifies string values before they are processed by the API layer.

Validation failures raise ValidationError with a descriptive message.
"""
import json

from .exceptions import ValidationError


def parse_json(request):
    """Parse a JSON string and ensure the result is an object.

    Args:
        request: JSON-formatted string received by the API.

    Returns:
        The parsed JSON object as a dictionary.

    Raises:
        ValidationError: If the request is not a string, contains
            invalid JSON, or does not represent a JSON object.
    """
    if not isinstance(request, str):
        raise ValidationError("Request must be a JSON string.")

    try:
        data = json.loads(request)
    except json.JSONDecodeError:
        raise ValidationError("Invalid JSON request.")

    if not isinstance(data, dict):
        raise ValidationError("JSON request must be an object.")

    return data


def require_fields(data, fields):
    """Ensure that all required fields exist in a dictionary.

    Args:
        data: Dictionary containing the parsed request data.
        fields: Names of the fields required for the operation.

    Raises:
        ValidationError: If one or more required fields are missing.
            The error message lists all missing field names.
    """
    missing = [
        field for field in fields
        if field not in data
    ]

    if missing:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing)}"
        )


def validate_string(value, field, max_length):
    """Validate a non-empty string against a maximum length.

    The function rejects values that are not strings, strings
    containing only whitespace, and strings longer than max_length.
    The original string is returned without trimming whitespace.

    Args:
        value: Value to validate.
        field: Field name used in validation error messages.
        max_length: Maximum permitted number of characters.

    Returns:
        The original string if it passes validation.

    Raises:
        ValidationError: If the value is not a string, is empty after
            whitespace checking, or exceeds the maximum length.
    """
    if not isinstance(value, str):
        raise ValidationError(
            f"{field} must be a string."
        )

    if not value.strip():
        raise ValidationError(
            f"{field} cannot be empty."
        )

    if len(value) > max_length:
        raise ValidationError(
            f"{field} cannot exceed {max_length} characters."
        )
    return value