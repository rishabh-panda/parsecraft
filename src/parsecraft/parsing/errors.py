"""Error classes for the parsing stage."""


class ParseError(Exception):
    """Raised when parsing JSON fails.

    This exception is raised when the Parser encounters an issue
    while attempting to parse JSON or validate against a schema.

    Attributes:
        message: Descriptive error message explaining why parsing failed.
        json_str: The JSON string that was attempted to be parsed.
        underlying_error: The original exception that caused the failure.
    """

    def __init__(self, message: str, json_str: str, underlying_error: Exception = None):
        """
        Initialize ParseError.

        Args:
            message: Descriptive error message explaining why parsing failed.
            json_str: The JSON string that was attempted to be parsed.
            underlying_error: The original exception that caused the failure.
        """
        self.message = message
        self.json_str = json_str
        self.underlying_error = underlying_error
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.underlying_error:
            parts.append(f"Underlying error: {self.underlying_error}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"json_str={self.json_str!r}, underlying_error={self.underlying_error!r})"
        )