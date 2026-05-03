"""Unit tests for the Repairer class."""

import json
import pytest

from parsecraft.repair.errors import RepairError
from parsecraft.repair.repairer import Repairer
from parsecraft.repair.strategies import RepairStrategies


class TestRepairStrategies:
    """Tests for individual repair strategies."""

    def test_remove_trailing_comma_in_object(self):
        """Test removing trailing comma in object."""
        input_str = '{"key": "value",}'
        result = RepairStrategies.remove_trailing_comma(input_str)
        assert result == '{"key": "value"}'
        assert json.loads(result) == {"key": "value"}

    def test_remove_trailing_comma_in_array(self):
        """Test removing trailing comma in array."""
        input_str = '[1, 2, 3,]'
        result = RepairStrategies.remove_trailing_comma(input_str)
        assert result == '[1, 2, 3]'
        assert json.loads(result) == [1, 2, 3]

    def test_remove_trailing_comma_nested(self):
        """Test removing trailing comma in nested structure."""
        input_str = '{"items": [1, 2,],}'
        result = RepairStrategies.remove_trailing_comma(input_str)
        assert result == '{"items": [1, 2]}'
        assert json.loads(result) == {"items": [1, 2]}

    def test_fix_single_quotes(self):
        """Test fixing single quotes."""
        input_str = "{'key': 'value'}"
        result = RepairStrategies.fix_single_quotes(input_str)
        assert result == '{"key": "value"}'
        assert json.loads(result) == {"key": "value"}

    def test_fix_single_quotes_in_array(self):
        """Test fixing single quotes in array."""
        input_str = "['item1', 'item2']"
        result = RepairStrategies.fix_single_quotes(input_str)
        assert json.loads(result) == ["item1", "item2"]

    def test_fix_unquoted_keys(self):
        """Test fixing unquoted keys."""
        input_str = '{key: "value"}'
        result = RepairStrategies.fix_unquoted_keys(input_str)
        assert result == '{"key": "value"}'
        assert json.loads(result) == {"key": "value"}

    def test_fix_unquoted_keys_complex(self):
        """Test fixing unquoted keys in complex structure."""
        input_str = '{name: "Alice", age: 30}'
        result = RepairStrategies.fix_unquoted_keys(input_str)
        parsed = json.loads(result)
        assert parsed == {"name": "Alice", "age": 30}

    def test_remove_trailing_newline(self):
        """Test removing trailing newlines."""
        input_str = '{"key": "value"}\n\n'
        result = RepairStrategies.remove_trailing_newline(input_str)
        assert result == '{"key": "value"}'


class TestRepairer:
    """Tests for the Repairer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.repairer = Repairer()

    def test_repair_trailing_comma(self):
        """Test repairing trailing comma."""
        json_str = '{"key": "value",}'
        result = self.repairer.repair(json_str)
        assert json.loads(result) == {"key": "value"}

    def test_repair_single_quotes(self):
        """Test repairing single quotes."""
        json_str = "{'key': 'value'}"
        result = self.repairer.repair(json_str)
        assert json.loads(result) == {"key": "value"}

    def test_repair_unquoted_keys(self):
        """Test repairing unquoted keys."""
        json_str = '{key: "value"}'
        result = self.repairer.repair(json_str)
        assert json.loads(result) == {"key": "value"}

    def test_repair_multiple_issues(self):
        """Test repairing multiple issues (order matters)."""
        # First fix single quotes, then trailing comma
        json_str = "{'key': 'value',}"
        result = self.repairer.repair(json_str)
        # Should succeed: trailing_comma -> single_quotes
        assert json.loads(result) == {"key": "value"}

    def test_repair_empty_string_raises_error(self):
        """Test that repair raises error for empty string."""
        with pytest.raises(RepairError):
            self.repairer.repair("")

    def test_repair_already_valid_json(self):
        """Test that valid JSON is returned as-is."""
        json_str = '{"key": "value"}'
        result = self.repairer.repair(json_str)
        assert result == '{"key": "value"}'

    def test_repair_unrecoverable_error(self):
        """Test that unrecoverable JSON raises RepairError."""
        # This JSON has a fundamental issue that can't be fixed
        json_str = '{"key": }'  # Missing value
        with pytest.raises(RepairError) as exc_info:
            self.repairer.repair(json_str)
        assert len(exc_info.value.attempted_strategies) > 0

    def test_repair_with_custom_strategies(self):
        """Test repairing with custom strategy list."""
        repairer = Repairer(strategies=['trailing_comma'])
        json_str = '{"key": "value",}'
        result = repairer.repair(json_str)
        assert json.loads(result) == {"key": "value"}

    def test_is_valid_json(self):
        """Test _is_valid_json method."""
        assert self.repairer._is_valid_json('{"key": "value"}') is True
        assert self.repairer._is_valid_json('[1, 2, 3]') is True
        assert self.repairer._is_valid_json('invalid') is False
        assert self.repairer._is_valid_json('') is False

    def test_repair_preserves_valid_json(self):
        """Test that repair doesn't break already valid JSON."""
        json_str = '{"name": "Alice", "age": 30, "active": true}'
        result = self.repairer.repair(json_str)
        parsed = json.loads(result)
        assert parsed["name"] == "Alice"
        assert parsed["age"] == 30
        assert parsed["active"] is True

    def test_repair_complex_nested_structure(self):
        """Test repairing complex nested structure."""
        json_str = '{"users": [{"name": "Alice",}, {"name": "Bob",}],}'
        result = self.repairer.repair(json_str)
        parsed = json.loads(result)
        assert "users" in parsed
        assert len(parsed["users"]) == 2

    def test_strategy_order(self):
        """Test that strategies are tried in order."""
        # This should fail at the first strategy (trailing_comma)
        # because the JSON has an issue that trailing_comma can't fix
        json_str = "{'key': 'value'}"
        
        # It should eventually succeed with single_quotes
        result = self.repairer.repair(json_str)
        assert json.loads(result) == {"key": "value"}