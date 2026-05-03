"""Error classes for the validation stage."""


class ValidationError(Exception):
    """Raised when data validation fails.

    This exception is raised when the Validator finds one or more
    validation errors in the data.

    Attributes:
        message: Descriptive error message explaining why validation failed.
        errors: List of individual validation errors.
    """

    def __init__(self, message: str, errors: list = None):
        """
        Initialize ValidationError.

        Args:
            message: Descriptive error message explaining why validation failed.
            errors: List of individual validation errors.
        """
        self.message = message
        self.errors = errors or []
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        if self.errors:
            parts.append("Validation errors:")
            for i, error in enumerate(self.errors, 1):
                parts.append(f"  {i}. {error}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"errors={self.errors!r})"
        )


class FieldValidationError:
    """Represents a single field validation error.

    Attributes:
        field: The field path that failed validation.
        message: Descriptive error message.
        expected_type: Expected type for the field (optional).
        actual_value: The actual value that caused the error (optional).
    """

    def __init__(
        self,
        field: str,
        message: str,
        expected_type: str = None,
        actual_value: object = None
    ):
        self.field = field
        self.message = message
        self.expected_type = expected_type
        self.actual_value = actual_value

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"Field '{self.field}': {self.message}"]
        if self.expected_type:
            parts.append(f"  Expected type: {self.expected_type}")
        if self.actual_value is not None:
            parts.append(f"  Actual value: {repr(self.actual_value)[:50]}")
        return " | ".join(parts)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'field': self.field,
            'message': self.message,
            'expected_type': self.expected_type,
            'actual_value': str(self.actual_value) if self.actual_value is not None else None
        }