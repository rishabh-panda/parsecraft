"""Unit tests for the Parser class."""

import json
import pytest
from pydantic import BaseModel

from parsecraft.parsing.errors import ParseError
from parsecraft.parsing.parser import Parser


class TestParser:
    """Tests for the Parser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = Parser()

    # Test basic JSON parsing

    def test_parse_valid_json_object(self):
        """Test parsing valid JSON object."""
        json_str = '{"key": "value", "number": 123}'
        result = self.parser.parse(json_str)
        assert result == {"key": "value", "number": 123}

    def test_parse_valid_json_array(self):
        """Test parsing valid JSON array."""
        json_str = '[1, 2, 3, "four", true]'
        result = self.parser.parse(json_str)
        assert result == [1, 2, 3, "four", True]

    def test_parse_nested_json(self):
        """Test parsing nested JSON."""
        json_str = '{"outer": {"inner": {"deep": "value"}}}'
        result = self.parser.parse(json_str)
        assert result == {"outer": {"inner": {"deep": "value"}}}

    def test_parse_empty_object(self):
        """Test parsing empty object."""
        json_str = '{}'
        result = self.parser.parse(json_str)
        assert result == {}

    def test_parse_empty_array(self):
        """Test parsing empty array."""
        json_str = '[]'
        result = self.parser.parse(json_str)
        assert result == []

    def test_parse_with_special_values(self):
        """Test parsing JSON with special values."""
        json_str = '{"null": null, "true": true, "false": false, "float": 3.14}'
        result = self.parser.parse(json_str)
        assert result == {"null": None, "true": True, "false": False, "float": 3.14}

    # Test error cases

    def test_parse_invalid_json(self):
        """Test that ParseError is raised for invalid JSON."""
        json_str = '{"key": "value"'  # Missing closing brace
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(json_str)
        assert "Invalid JSON" in str(exc_info.value)

    def test_parse_empty_string(self):
        """Test that ParseError is raised for empty string."""
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse("")
        assert "empty" in str(exc_info.value).lower()

    def test_parse_none(self):
        """Test that ParseError is raised for None."""
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(None)
        assert "empty" in str(exc_info.value).lower()

    def test_parse_non_string(self):
        """Test that ParseError is raised for non-string input."""
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(123)
        assert "empty" in str(exc_info.value).lower()

    # Test Pydantic model validation

    def test_parse_with_pydantic_model(self):
        """Test parsing with Pydantic model validation."""
        class User(BaseModel):
            name: str
            age: int

        json_str = '{"name": "Alice", "age": 30}'
        result = self.parser.parse(json_str, schema=User)
        assert isinstance(result, User)
        assert result.name == "Alice"
        assert result.age == 30

    def test_parse_pydantic_validation_error(self):
        """Test that ParseError is raised for Pydantic validation failure."""
        class User(BaseModel):
            name: str
            age: int

        json_str = '{"name": "Alice", "age": "not_an_int"}'  # age should be int
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(json_str, schema=User)
        assert "Schema validation failed" in str(exc_info.value)

    def test_parse_pydantic_missing_required_field(self):
        """Test that ParseError is raised for missing required field."""
        class User(BaseModel):
            name: str
            age: int

        json_str = '{"name": "Alice"}'  # missing age
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(json_str, schema=User)
        assert "Schema validation failed" in str(exc_info.value)

    # Test JSON Schema validation

    def test_parse_with_json_schema(self):
        """Test parsing with JSON Schema validation."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        json_str = '{"name": "Alice", "age": 30}'
        result = self.parser.parse(json_str, schema=schema)
        assert result == {"name": "Alice", "age": 30}

    def test_parse_json_schema_validation_error(self):
        """Test that ParseError is raised for JSON Schema validation failure."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        json_str = '{"name": "Alice", "age": "not_an_int"}'  # age should be integer
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(json_str, schema=schema)
        assert "JSON Schema validation failed" in str(exc_info.value)

    # Test is_valid_json

    def test_is_valid_json_true(self):
        """Test is_valid_json returns True for valid JSON."""
        assert self.parser.is_valid_json('{"key": "value"}') is True
        assert self.parser.is_valid_json('[1, 2, 3]') is True
        assert self.parser.is_valid_json('"string"') is True
        assert self.parser.is_valid_json('123') is True

    def test_is_valid_json_false(self):
        """Test is_valid_json returns False for invalid JSON."""
        assert self.parser.is_valid_json('{"key": "value"') is False
        assert self.parser.is_valid_json('{key: value}') is False
        assert self.parser.is_valid_json('') is False
        assert self.parser.is_valid_json(None) is False
        assert self.parser.is_valid_json(123) is False

    # Test edge cases

    def test_parse_with_unicode(self):
        """Test parsing JSON with unicode content."""
        json_str = '{"name": "日本語", "emoji": "🎉"}'
        result = self.parser.parse(json_str)
        assert result == {"name": "日本語", "emoji": "🎉"}

    def test_parse_with_escaped_characters(self):
        """Test parsing JSON with escaped characters."""
        json_str = '{"message": "Hello\\nWorld\\t!"}'
        result = self.parser.parse(json_str)
        assert result == {"message": "Hello\nWorld\t!"}

    def test_parse_large_numbers(self):
        """Test parsing JSON with large numbers."""
        json_str = '{"big": 12345678901234567890, "float": 3.14159}'
        result = self.parser.parse(json_str)
        assert result["big"] == 12345678901234567890
        assert result["float"] == 3.14159

    def test_parse_without_schema(self):
        """Test that parsing without schema works."""
        json_str = '{"key": "value"}'
        result = self.parser.parse(json_str)
        assert result == {"key": "value"}
        assert type(result) == dict

    def test_parse_with_none_schema(self):
        """Test that passing None as schema is handled."""
        json_str = '{"key": "value"}'
        result = self.parser.parse(json_str, schema=None)
        assert result == {"key": "value"}

    def test_roundtrip_parsing(self):
        """Test that parse → serialize → parse produces equivalent results."""
        original = {"key": "value", "number": 123, "nested": {"a": 1, "b": 2}}
        json_str = json.dumps(original)
        parsed = self.parser.parse(json_str)
        serialized = json.dumps(parsed)
        reparsed = self.parser.parse(serialized)
        assert parsed == original
        assert reparsed == original