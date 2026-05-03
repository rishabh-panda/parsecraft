"""Unit tests for NormalizationError."""

import pytest

from parsecraft.normalization.errors import NormalizationError


class TestNormalizationError:
    """Tests for the NormalizationError exception class."""

    def test_normalization_error_with_message_and_text(self):
        """Test creating NormalizationError with message and original text."""
        original_text = '{"key": "value"}'
        error = NormalizationError("Failed to normalize", original_text)

        assert error.message == "Failed to normalize"
        assert error.original_text == original_text

    def test_normalization_error_str_representation(self):
        """Test string representation includes error message."""
        error = NormalizationError("Failed to normalize", '{"key": "value"}')

        error_str = str(error)
        assert "NormalizationError" in error_str
        assert "Failed to normalize" in error_str

    def test_normalization_error_repr_representation(self):
        """Test repr includes both message and original text."""
        original_text = '{"key": "value"}'
        error = NormalizationError("Failed to normalize", original_text)

        error_repr = repr(error)
        assert "NormalizationError" in error_repr
        assert "Failed to normalize" in error_repr
        assert original_text in error_repr

    def test_normalization_error_inherits_from_exception(self):
        """Test that NormalizationError properly inherits from Exception."""
        error = NormalizationError("Failed to normalize", '{"key": "value"}')

        assert isinstance(error, Exception)
        assert isinstance(error, NormalizationError)

    def test_normalization_error_with_empty_text(self):
        """Test creating error with empty original text."""
        error = NormalizationError("Empty text", "")

        assert error.original_text == ""
        assert error.message == "Empty text"

    def test_normalization_error_with_multiline_text(self):
        """Test creating error with multiline text."""
        original_text = """Some text before
{"key": "value"}
Some text after"""
        error = NormalizationError("Failed to normalize", original_text)

        assert error.original_text == original_text

    def test_normalization_error_can_be_raised_and_caught(self):
        """Test that NormalizationError can be raised and caught."""
        with pytest.raises(NormalizationError) as exc_info:
            raise NormalizationError("Failed to normalize", '{"key": "value"}')

        assert exc_info.value.message == "Failed to normalize"
        assert exc_info.value.original_text == '{"key": "value"}'

    def test_normalization_error_with_special_characters_in_message(self):
        """Test error with special characters in message."""
        error = NormalizationError("Error: 'invalid' \\ \"text\"", '{"key": "value"}')

        assert "Error:" in error.message
        assert "'invalid'" in error.message
        assert '"text"' in error.message

    def test_normalization_error_with_unicode_text(self):
        """Test error with unicode characters in text."""
        original_text = '{"name": "日本語", "emoji": "🎉"}'
        error = NormalizationError("Failed to normalize", original_text)

        assert error.original_text == original_text
        assert "日本語" in error.original_text
        assert "🎉" in error.original_text
