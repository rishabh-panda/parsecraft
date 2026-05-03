"""Error classes for the extraction stage."""


class ExtractionError(Exception):
    """Raised when extraction of JSON content from raw LLM output fails.

    This exception is raised when no JSON-like content can be found in the
    raw output, after attempting to extract from code fences and checking
    for JSON-like patterns in the text.

    Attributes:
        message: Descriptive error message explaining why extraction failed.
        raw_text: The raw text that was attempted to be extracted from.
    """

    def __init__(self, message: str, raw_text: str):
        """
        Initialize ExtractionError.

        Args:
            message: Descriptive error message explaining why extraction failed.
            raw_text: The raw text that was attempted to be extracted from.
        """
        self.message = message
        self.raw_text = raw_text
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"raw_text={self.raw_text!r})"
        )
