"""Scorer class for calculating reliability scores."""

from typing import Any, Dict, List

from parsecraft.core.result import RepairAttempt


class Scorer:
    """Calculates reliability score for parsed output.

    Score is calculated based on:
    - Repair complexity (fewer repairs = higher score)
    - Number of parsing attempts
    - Validation warnings

    Score range: 0.0 - 1.0
    """

    def __init__(self):
        """Initialize the Scorer."""
        pass

    def score(
        self,
        parsed: Any,
        repair_history: List[RepairAttempt],
        validation_warnings: int = 0
    ) -> float:
        """Calculate reliability score.

        Args:
            parsed: The parsed data
            repair_history: List of repair attempts
            validation_warnings: Number of validation warnings

        Returns:
            Reliability score between 0.0 and 1.0
        """
        score = 1.0

        # Deduct for repair attempts
        repair_attempts = len(repair_history)
        if repair_attempts > 0:
            # Calculate repair complexity based on attempts
            repair_complexity = min(repair_attempts * 0.15, 0.5)
            score -= repair_complexity

        # Deduct for validation warnings
        if validation_warnings > 0:
            score -= min(validation_warnings * 0.05, 0.2)

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return score

    def calculate_score(
        self,
        parsed: Any,
        repair_history: List[RepairAttempt],
        validation_warnings: int = 0,
        parsing_attempts: int = 1
    ) -> float:
        """Calculate reliability score with more detailed metrics.

        Args:
            parsed: The parsed data
            repair_history: List of repair attempts
            validation_warnings: Number of validation warnings
            parsing_attempts: Number of parsing attempts

        Returns:
            Reliability score between 0.0 and 1.0
        """
        score = 1.0

        # Deduct for repair attempts
        repair_attempts = len(repair_history)
        if repair_attempts > 0:
            repair_complexity = min(repair_attempts * 0.15, 0.5)
            score -= repair_complexity

        # Deduct for parsing attempts
        if parsing_attempts > 1:
            score -= (parsing_attempts - 1) * 0.05

        # Deduct for validation warnings
        if validation_warnings > 0:
            score -= min(validation_warnings * 0.02, 0.1)

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return score