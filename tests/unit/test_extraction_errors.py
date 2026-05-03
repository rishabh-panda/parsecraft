"""Unit tests for ExtractionError."""

import pytest

from parsecraft.extraction.errors import ExtractionError


class TestExtractionError:
    """Tests for the ExtractionError exception class."""

    def test_extraction_error_with_message_and_raw_text(self):
        """Test creating ExtractionError with message and raw text."""
        raw_text = '{"key": "value"}'
        error = ExtractionError("No JSON found", raw_text)

        assert error.message == "No JSON found"
        assert error.raw_text == raw_text

    def test_extraction_error_str_representation(self):
        """Test string representation includes error message."""
        error = ExtractionError("No JSON found", '{"key": "value"}')

        error_str = str(error)
        assert "ExtractionError" in error_str
        assert "No JSON found" in error_str

    def test_extraction_error_repr_representation(self):
        """Test repr includes both message and raw text."""
        raw_text = '{"key": "value"}'
        error = ExtractionError("No JSON found", raw_text)

        error_repr = repr(error)
        assert "ExtractionError" in error_repr
        assert "No JSON found" in error_repr
        assert raw_text in error_repr

    def test_extraction_error_inherits_from_exception(self):
        """Test that ExtractionError properly inherits from Exception."""
        error = ExtractionError("No JSON found", '{"key": "value"}')

        assert isinstance(error, Exception)
        assert isinstance(error, ExtractionError)

    def test_extraction_error_with_empty_raw_text(self):
        """Test creating error with empty raw text."""
        error = ExtractionError("No content found", "")

        assert error.raw_text == ""
        assert error.message == "No content found"

    def test_extraction_error_with_multiline_raw_text(self):
        """Test creating error with multiline raw text."""
        raw_text = """Some text before
```json
{"key": "value"}
```
Some text after"""
        error = ExtractionError("No JSON found", raw_text)

        assert error.raw_text == raw_text

    def test_extraction_error_can_be_raised_and_caught(self):
        """Test that ExtractionError can be raised and caught."""
        with pytest.raises(ExtractionError) as exc_info:
            raise ExtractionError("No JSON found", '{"key": "value"}')

        assert exc_info.value.message == "No JSON found"
        assert exc_info.value.raw_text == '{"key": "value"}'

    def test_extraction_error_with_special_characters_in_message(self):
        """Test error with special characters in message."""
        error = ExtractionError("Error: 'invalid' \\ \"json\"", '{"key": "value"}')

        assert "Error:" in error.message
        assert "'invalid'" in error.message
        assert '"json"' in error.message

    def test_extraction_error_with_unicode_raw_text(self):
        """Test error with unicode characters in raw text."""
        raw_text = '{"name": "日本語", "emoji": "🎉"}'
        error = ExtractionError("No JSON found", raw_text)

        assert error.raw_text == raw_text
        assert "日本語" in error.raw_text
        assert "🎉" in error.raw_text
