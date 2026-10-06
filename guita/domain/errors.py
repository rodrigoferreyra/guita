"""Domain and application errors with user-facing messages."""


class GuitaError(Exception):
    """Base error for Guita. Message is suitable for CLI stderr."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationError(GuitaError):
    """Invalid user input."""


class NotFoundError(GuitaError):
    """Requested entity does not exist."""


class InsufficientBalanceError(GuitaError):
    """Operation would produce an invalid (negative) account balance."""


class ConflictError(GuitaError):
    """Operation conflicts with existing state."""