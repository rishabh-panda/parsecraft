"""Retry manager with exponential backoff."""

import random
import time
from typing import Any, Callable, List, Optional, Set, Type


class RetryManager:
    """Manages retry logic with exponential backoff and jitter.

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_errors: Set of exception types that should trigger a retry
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        retryable_errors: Set[Type[Exception]] = None
    ):
        """Initialize the RetryManager.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            retryable_errors: Set of exception types that should trigger a retry
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retryable_errors = retryable_errors or {
            ConnectionError,
            TimeoutError,
            OSError,
        }
        self.retry_count = 0

    def retry(
        self,
        operation: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Retry an operation with exponential backoff.

        Args:
            operation: The callable to execute
            *args: Positional arguments to pass to operation
            **kwargs: Keyword arguments to pass to operation

        Returns:
            Result from the operation

        Raises:
            The final error if all retries are exhausted
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                self.retry_count = attempt
                return operation(*args, **kwargs)
            except Exception as e:
                last_error = e

                # Check if this is a retryable error
                if not self._is_retryable(e):
                    raise

                # Check if we have retries left
                if attempt >= self.max_retries:
                    raise

                # Wait with backoff before retrying
                delay = self._calculate_delay(attempt)
                time.sleep(delay)

        # Should not reach here
        raise last_error

    def _is_retryable(self, error: Exception) -> bool:
        """Check if an error is retryable.

        Args:
            error: The exception to check

        Returns:
            True if the error should trigger a retry
        """
        for retryable_error in self.retryable_errors:
            if isinstance(error, retryable_error):
                return True
        return False

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter.

        Args:
            attempt: The current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff: base_delay * 2^attempt
        delay = self.base_delay * (2 ** attempt)

        # Apply jitter: ±10%
        jitter = delay * 0.1 * (random.random() * 2 - 1)
        delay += jitter

        # Cap at max_delay
        return min(delay, self.max_delay)

    def reset(self) -> None:
        """Reset retry count."""
        self.retry_count = 0