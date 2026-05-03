"""Result and error classes for parsecraft."""

import dataclasses
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclasses.dataclass
class RepairAttempt:
    """Records a single repair attempt.

    Attributes:
        strategy: Name of the repair strategy used
        success: Whether the repair was successful
        original_error: Description of the original error
        repaired_text: The repaired text (if successful)
        timestamp: When the repair was attempted
    """

    strategy: str
    success: bool
    original_error: str
    repaired_text: Optional[str] = None
    timestamp: datetime = dataclasses.field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'strategy': self.strategy,
            'success': self.success,
            'original_error': self.original_error,
            'repaired_text': self.repaired_text,
            'timestamp': self.timestamp.isoformat()
        }


@dataclasses.dataclass
class ParseResult:
    """Result object from successful parsing.

    Attributes:
        parsed_data: The parsed data (dict, list, or Pydantic model)
        reliability_score: 0.0-1.0 reliability score
        repair_history: List of repair attempts
        validation_errors: List of validation warnings
        stage_results: Results from each pipeline stage
    """

    parsed_data: Any
    reliability_score: float
    repair_history: List[RepairAttempt]
    validation_errors: List[Dict]
    stage_results: Dict[str, Any]

    def to_dict(self) -> dict:
        """Serialize to dictionary for observability."""
        return {
            'parsed_data': self.parsed_data,
            'reliability_score': self.reliability_score,
            'repair_history': [r.to_dict() for r in self.repair_history],
            'validation_errors': self.validation_errors,
            'stage_results': self.stage_results
        }


class ParseError(Exception):
    """Exception with full context on parsing failure.

    Attributes:
        message: Descriptive error message
        original_input: The original input text
        failed_stage: Which stage failed
        specific_error: The specific error that occurred
        result: Partial ParseResult if available
        repair_history: List of repair attempts
        validation_errors: List of validation errors
    """

    def __init__(
        self,
        message: str,
        original_input: str,
        failed_stage: str,
        specific_error: Exception,
        result: Optional[ParseResult] = None,
        repair_history: Optional[List[RepairAttempt]] = None,
        validation_errors: Optional[List[Dict]] = None
    ):
        self.message = message
        self.original_input = original_input
        self.failed_stage = failed_stage
        self.specific_error = specific_error
        self.result = result
        self.repair_history = repair_history or []
        self.validation_errors = validation_errors or []
        self.is_user_error = self._determine_error_type()
        super().__init__(message)

    def _determine_error_type(self) -> bool:
        """Determine if this is a user error (invalid input) or system error."""
        return self.failed_stage in ['Extraction', 'Normalization', 'Parsing']

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [f"{self.__class__.__name__}: {self.message}"]
        parts.append(f"Failed at stage: {self.failed_stage}")
        parts.append(f"Original input: {self.original_input[:100]}...")
        if self.specific_error:
            parts.append(f"Specific error: {self.specific_error}")
        if self.repair_history:
            parts.append(f"Repair attempts: {len(self.repair_history)}")
        if self.validation_errors:
            parts.append(f"Validation errors: {len(self.validation_errors)}")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """Serialize to dictionary for observability."""
        return {
            'message': self.message,
            'original_input': self.original_input,
            'failed_stage': self.failed_stage,
            'specific_error': str(self.specific_error),
            'result': self.result.to_dict() if self.result else None,
            'repair_history': [r.to_dict() for r in self.repair_history],
            'validation_errors': self.validation_errors,
            'is_user_error': self.is_user_error
        }