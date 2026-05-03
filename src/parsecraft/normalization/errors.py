"""Error classes for the normalization stage."""


class NormalizationError(Exception):
    """Raised when normalization of text fails.

    This exception is raised when the Normalizer encounters an issue
    while attempting to normalize text, such as removing BOM sequences,
    standardizing line endings, or normalizing whitespace.

    Attributes:
        message: Descriptive error message explaining why normalization failed.
        original_text: The text that was attempted to be normalized.
    """

    def __init__(self, message: str, original_text: str):
        """
        Initialize NormalizationError.

        Args:
            message: Descriptive error message explaining why normalization failed.
            original_text: The text that was attempted to be normalized.
        """
        self.message = message
        self.original_text = original_text
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"original_text={self.original_text!r})"
        )
