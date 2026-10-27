class PlannerError(Exception):
    """Base exception for the planner application."""


class ValidationError(PlannerError):
    """Raised when request validation fails."""


class NotFoundError(PlannerError):
    """Raised when a requested resource does not exist."""


class DuplicateError(PlannerError):
    """Raised when a unique constraint is violated."""


class ConflictError(PlannerError):
    """Raised when an operation conflicts with the current state."""