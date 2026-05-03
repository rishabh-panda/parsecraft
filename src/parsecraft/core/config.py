"""Configuration class for the parser."""

import dataclasses
from typing import List, Optional


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass


@dataclasses.dataclass(frozen=True)
class ParserConfig:
    """Immutable configuration for the parser.

    Attributes:
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Timeout in seconds (default: 30.0)
        repair_enabled: Whether to enable automatic repair (default: True)
        observability_enabled: Whether to enable observability logging (default: False)
        repair_strategies: List of repair strategies in order of preference
    """

    max_retries: int = 3
    timeout: float = 30.0
    repair_enabled: bool = True
    observability_enabled: bool = False
    repair_strategies: List[str] = dataclasses.field(
        default_factory=lambda: [
            'trailing_comma',
            'single_quotes',
            'unquoted_keys',
            'escape_sequences',
        ]
    )

    def __post_init__(self):
        """Validate configuration after creation."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration and raise ConfigurationError if invalid."""
        if self.max_retries < 0:
            raise ConfigurationError("max_retries must be non-negative")
        if self.timeout <= 0:
            raise ConfigurationError("timeout must be positive")
        if not isinstance(self.repair_strategies, list):
            raise ConfigurationError("repair_strategies must be a list")
        for strategy in self.repair_strategies:
            if not isinstance(strategy, str):
                raise ConfigurationError(f"repair_strategies must contain strings, got {type(strategy)}")

    def with_overrides(self, **kwargs) -> 'ParserConfig':
        """Create new config with overrides (for per-call configuration)."""
        return dataclasses.replace(self, **kwargs)