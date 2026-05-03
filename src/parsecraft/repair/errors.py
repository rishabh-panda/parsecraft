"""Error classes for the repair stage."""


class RepairError(Exception):
    """Raised when all repair strategies fail.

    This exception is raised when the Repairer is unable to fix
    the invalid JSON using any of the available repair strategies.

    Attributes:
        message: Descriptive error message explaining why repair failed.
        original_error: The original exception that caused the failure.
        attempted_strategies: List of repair strategies that were tried.
    """

    def __init__(self, message: str, original_error: Exception, attempted_strategies: list = None):
        """
        Initialize RepairError.

        Args:
            message: Descriptive error message explaining why repair failed.
            original_error: The original exception that caused the failure.
            attempted_strategies: List of repair strategies that were tried.
        """
        self.message = message
        self.original_error = original_error
        self.attempted_strategies = attempted_strategies or []
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        parts.append(f"Original error: {self.original_error}")
        if self.attempted_strategies:
            parts.append(f"Attempted strategies: {', '.join(self.attempted_strategies)}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"original_error={self.original_error!r}, "
            f"attempted_strategies={self.attempted_strategies!r})"
        )