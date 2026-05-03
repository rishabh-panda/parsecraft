"""Repairer class for attempting to fix invalid JSON."""

import json
import logging
from typing import Any, Callable, List, Optional

from parsecraft.repair.errors import RepairError
from parsecraft.repair.strategies import RepairStrategies


class Repairer:
    """Attempts to repair invalid JSON using various strategies.

    This class tries multiple repair strategies in order of increasing
    complexity to fix common JSON errors.

    Attributes:
        strategies: List of repair strategy functions to try.
    """

    def __init__(self, strategies: List[str] = None):
        """Initialize the Repairer.

        Args:
            strategies: List of strategy names to use. If None, uses defaults.
        """
        self.strategies = strategies or [
            'trailing_comma',
            'single_quotes',
            'unquoted_keys',
            'escape_sequences',
        ]
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    def repair(
        self,
        json_str: str,
        original_error: Exception = None,
        max_iterations: int = 5
    ) -> str:
        """Attempt to repair invalid JSON.

        Args:
            json_str: The invalid JSON string to repair.
            original_error: The original exception that caused parsing to fail.
            max_iterations: Maximum number of repair iterations.

        Returns:
            Repaired JSON string.

        Raises:
            RepairError: If all repair strategies fail.
        """
        if not json_str:
            raise RepairError(
                "Cannot repair empty string",
                original_error or ValueError("Empty string"),
                self.strategies
            )

        # If already valid, return as-is
        if self._is_valid_json(json_str):
            return json_str

        attempted = []
        current = json_str
        
        for iteration in range(max_iterations):
            found_fix = False
            
            for strategy_name in self.strategies:
                try:
                    repaired = self._apply_strategy(strategy_name, current)
                    if repaired and repaired != current and self._is_valid_json(repaired):
                        self.logger.info(f"Successfully repaired using {strategy_name} (iteration {iteration + 1})")
                        return repaired
                    elif repaired and repaired != current:
                        # Strategy made a change but still not valid
                        # Try other strategies on this result
                        current = repaired
                        found_fix = True
                except Exception as e:
                    self.logger.debug(f"Strategy {strategy_name} failed: {e}")
                
                attempted.append(strategy_name)
            
            if not found_fix:
                break
        
        # All strategies failed
        raise RepairError(
            f"Failed to repair JSON after trying {len(set(attempted))} strategies",
            original_error or ValueError("Unknown error"),
            list(set(attempted))
        )

    def _apply_strategy(self, strategy_name: str, json_str: str) -> Optional[str]:
        """Apply a specific repair strategy.

        Args:
            strategy_name: Name of the strategy to apply.
            json_str: The JSON string to repair.

        Returns:
            Repaired string, or None if strategy doesn't apply.
        """
        strategy_map = {
            'trailing_comma': RepairStrategies.remove_trailing_comma,
            'single_quotes': RepairStrategies.fix_single_quotes,
            'unquoted_keys': RepairStrategies.fix_unquoted_keys,
            'escape_sequences': RepairStrategies.fix_invalid_escape_sequences,
            'trailing_newline': RepairStrategies.remove_trailing_newline,
        }
        
        strategy_func = strategy_map.get(strategy_name)
        if strategy_func:
            return strategy_func(json_str)
        
        return None

    def _is_valid_json(self, json_str: str) -> bool:
        """Check if a string is valid JSON.

        Args:
            json_str: The string to check.

        Returns:
            True if valid JSON, False otherwise.
        """
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def add_strategy(self, strategy_name: str, strategy_func: Callable[[str], Optional[str]]) -> None:
        """Add a custom repair strategy.

        Args:
            strategy_name: Name of the strategy.
            strategy_func: Function that takes a string and returns repaired string or None.
        """
        if strategy_name not in self.strategies:
            self.strategies.append(strategy_name)
        
        # Store custom strategy (would need to modify _apply_strategy to use it)
        setattr(RepairStrategies, strategy_name, staticmethod(strategy_func))