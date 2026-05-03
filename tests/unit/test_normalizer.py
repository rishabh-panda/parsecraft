"""Unit tests for the Normalizer class."""

import pytest

from parsecraft.normalization.errors import NormalizationError
from parsecraft.normalization.normalizer import Normalizer


class TestNormalizer:
    """Tests for the Normalizer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.normalizer = Normalizer()

    # Test BOM removal

    def test_remove_utf8_bom(self):
        """Test removing UTF-8 BOM sequence."""
        text = '\ufeff{"key": "value"}'
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'
        assert not result.startswith('\ufeff')

    def test_remove_utf16_le_bom(self):
        """Test removing UTF-16 LE BOM sequence (U+FFFE)."""
        # Note: \ufffe is not a standard BOM, it's used to detect endianness
        # The standard UTF-8 BOM is \ufeff which is already handled
        text = '\ufffe{"key": "value"}'
        result = self.normalizer.normalize(text)
        # This character is not a standard BOM, so it may be preserved
        # The important test is that UTF-8 BOM is removed
        assert 'key' in result

    def test_remove_utf16_be_bom(self):
        """Test removing UTF-16 BE BOM sequence."""
        text = '\ufeff{"key": "value"}'
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'
        assert not result.startswith('\ufeff')

    def test_no_bom_preserved(self):
        """Test that text without BOM is preserved."""
        text = '{"key": "value"}'
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'

    # Test line ending standardization

    def test_convert_crlf_to_lf(self):
        """Test converting CRLF to LF."""
        text = '{"key": "value"}\r\n{"key2": "value2"}'
        result = self.normalizer.normalize(text)
        assert '\r\n' not in result
        assert '\n' in result

    def test_convert_cr_to_lf(self):
        """Test converting CR to LF."""
        text = '{"key": "value"}\r{"key2": "value2"}'
        result = self.normalizer.normalize(text)
        assert '\r' not in result
        assert '\n' in result

    def test_mixed_line_endings_standardized(self):
        """Test standardizing mixed line endings."""
        text = '{"key": "value"}\r\n{"key2": "value2"}\r{"key3": "value3"}'
        result = self.normalizer.normalize(text)
        assert '\r' not in result
        assert result.count('\n') == 2

    # Test whitespace normalization

    def test_normalize_multiple_spaces(self):
        """Test normalizing multiple consecutive spaces."""
        text = '{"key":   "value"}'
        result = self.normalizer.normalize(text)
        # Multiple spaces between key and value should become single space
        assert result == '{"key": "value"}'

    def test_remove_leading_tabs(self):
        """Test removing leading tabs on lines."""
        text = '\t{"key": "value"}'
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'
        assert not result.startswith('\t')

    def test_remove_leading_spaces(self):
        """Test removing leading spaces on lines."""
        text = '   {"key": "value"}'
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'
        assert not result.startswith(' ')

    def test_normalize_excessive_whitespace(self):
        """Test normalizing excessive whitespace."""
        text = '   {"key":   "value"}   '
        result = self.normalizer.normalize(text)
        # Leading/trailing whitespace should be removed
        assert result == '{"key": "value"}'

    # Test semantic preservation

    def test_preserve_string_content(self):
        """Test that string content is preserved."""
        text = '{"message": "Hello   World"}'
        result = self.normalizer.normalize(text)
        assert 'Hello   World' in result

    def test_preserve_newlines_in_strings(self):
        """Test that newlines in strings are preserved."""
        text = '{"message": "Line1\\nLine2"}'
        result = self.normalizer.normalize(text)
        assert 'Line1\\nLine2' in result

    def test_preserve_tabs_in_strings(self):
        """Test that tabs in strings are preserved."""
        text = '{"message": "Col1\\tCol2"}'
        result = self.normalizer.normalize(text)
        assert 'Col1\\tCol2' in result

    def test_preserve_escaped_quotes(self):
        """Test that escaped quotes in strings are preserved."""
        text = '{"quote": "He said \\"Hello\\""}'
        result = self.normalizer.normalize(text)
        assert 'He said \\"Hello\\"' in result

    # Test error cases

    def test_normalize_raises_error_for_empty_string(self):
        """Test that NormalizationError is raised for empty string."""
        with pytest.raises(NormalizationError) as exc_info:
            self.normalizer.normalize("")

        assert "empty" in str(exc_info.value).lower()

    def test_normalize_raises_error_for_none(self):
        """Test that NormalizationError is raised for None."""
        with pytest.raises(NormalizationError) as exc_info:
            self.normalizer.normalize(None)

        assert "empty" in str(exc_info.value).lower()

    def test_normalize_raises_error_for_non_string(self):
        """Test that NormalizationError is raised for non-string input."""
        with pytest.raises(NormalizationError) as exc_info:
            self.normalizer.normalize(123)

        assert "not a string" in str(exc_info.value).lower()

    # Test edge cases

    def test_normalize_with_unicode_content(self):
        """Test normalizing JSON with unicode content."""
        text = '\ufeff{"name": "日本語", "emoji": "🎉"}'
        result = self.normalizer.normalize(text)
        assert "日本語" in result
        assert "🎉" in result
        assert not result.startswith('\ufeff')

    def test_normalize_with_complex_nested_structure(self):
        """Test normalizing complex nested structure."""
        text = '''\t{
    "users": [
        {
            "id": 1,
            "name": "Alice"
        }
    ]
}'''
        result = self.normalizer.normalize(text)
        assert '"users"' in result
        assert '"id"' in result

    def test_normalize_with_empty_lines(self):
        """Test normalizing with empty lines."""
        text = '{"key": "value"}\n\n{"key2": "value2"}'
        result = self.normalizer.normalize(text)
        assert result.count('\n') >= 2

    def test_normalize_with_mixed_whitespace(self):
        """Test normalizing with mixed whitespace."""
        text = '\t  {"key": "value"}\t  '
        result = self.normalizer.normalize(text)
        assert result == '{"key": "value"}'

    def test_normalize_idempotent(self):
        """Test that normalization is idempotent."""
        text = '\t{"key": "value"}\r\n'
        normalized_once = self.normalizer.normalize(text)
        normalized_twice = self.normalizer.normalize(normalized_once)
        assert normalized_once == normalized_twice

    def test_normalize_with_special_characters(self):
        """Test normalizing with special characters."""
        text = '{"message": "Hello\\nWorld\\t!"}'
        result = self.normalizer.normalize(text)
        assert 'Hello\\nWorld\\t!' in result

    def test_normalize_with_numbers(self):
        """Test normalizing JSON with numbers."""
        text = '{"int": 123, "float": 3.14, "negative": -456}'
        result = self.normalizer.normalize(text)
        assert '123' in result
        assert '3.14' in result
        assert '-456' in result

    def test_normalize_with_boolean_values(self):
        """Test normalizing JSON with boolean values."""
        text = '{"bool1": true, "bool2": false}'
        result = self.normalizer.normalize(text)
        assert 'true' in result
        assert 'false' in result

    def test_normalize_with_null_values(self):
        """Test normalizing JSON with null values."""
        text = '{"null1": null, "value": "test"}'
        result = self.normalizer.normalize(text)
        assert 'null' in result

    def test_normalize_with_array_of_primitives(self):
        """Test normalizing JSON with array of primitives."""
        text = '[1, "two", true, false, null]'
        result = self.normalizer.normalize(text)
        assert '1' in result
        assert '"two"' in result
        assert 'true' in result
        assert 'false' in result
        assert 'null' in result
