"""Normalizer class for normalizing text formatting issues."""

import re
from typing import Optional


class Normalizer:
    """Normalizes text formatting issues.

    This class handles various text normalization tasks including:
    - Removing BOM (Byte Order Mark) sequences
    - Standardizing line endings to LF
    - Normalizing excessive whitespace (multiple spaces, tabs at line start)
    - Preserving semantic content

    Attributes:
        None
    """

    def __init__(self):
        """Initialize the Normalizer."""
        pass

    def normalize(self, text: str) -> str:
        """Normalize text formatting.

        Args:
            text: Raw text to normalize.

        Returns:
            Normalized text with standardized formatting.

        Raises:
            NormalizationError: If normalization fails.
        """
        if not text or not isinstance(text, str):
            from parsecraft.normalization.errors import NormalizationError
            raise NormalizationError(
                "Input text is empty or not a string",
                str(text) if text else ""
            )

        try:
            # Step 1: Remove BOM sequences
            normalized = self._remove_bom(text)

            # Step 2: Standardize line endings to LF
            normalized = self._standardize_line_endings(normalized)

            # Step 3: Normalize excessive whitespace
            normalized = self._normalize_whitespace(normalized)

            return normalized

        except Exception as e:
            from parsecraft.normalization.errors import NormalizationError
            raise NormalizationError(
                f"Failed to normalize text: {str(e)}",
                text
            )

    def _remove_bom(self, text: str) -> str:
        """Remove BOM (Byte Order Mark) sequences.

        Handles common BOM sequences:
        - UTF-8 BOM: \ufeff
        - UTF-16 LE BOM: \ufffe
        - UTF-16 BE BOM: \ufeff
        """
        # Remove UTF-8 BOM
        if text.startswith('\ufeff'):
            return text[1:]
        # Remove UTF-16 LE BOM
        if text.startswith('\ufffe'):
            return text[2:]
        # Remove UTF-16 BE BOM
        if text.startswith('\ufeff'):
            return text[2:]

        return text

    def _standardize_line_endings(self, text: str) -> str:
        """Standardize line endings to LF.

        Converts:
        - CRLF (\\r\\n) to LF (\\n)
        - CR (\\r) to LF (\\n)
        """
        # First convert CRLF to LF
        normalized = text.replace('\r\n', '\n')
        # Then convert remaining CR to LF
        normalized = normalized.replace('\r', '\n')

        return normalized

    def _normalize_whitespace(self, text: str) -> str:
        """Normalize excessive whitespace.

        - Multiple consecutive spaces become single space
        - Tabs at line start are removed
        - Trailing whitespace on each line is removed
        - Preserves whitespace inside strings
        """
        lines = text.split('\n')
        normalized_lines = []

        for line in lines:
            # Remove tabs at line start
            line = line.lstrip('\t')

            # Normalize multiple spaces to single space
            # But preserve spaces inside strings by tracking quote state
            normalized_line = self._normalize_spaces_in_line(line)
            normalized_lines.append(normalized_line)

        return '\n'.join(normalized_lines)

    def _normalize_spaces_in_line(self, line: str) -> str:
        """Normalize spaces in a single line, preserving string content."""
        result = []
        in_string = False
        escape_next = False

        prev_char = None
        for char in line:
            if escape_next:
                result.append(char)
                escape_next = False
                prev_char = char
                continue

            if char == '\\':
                result.append(char)
                escape_next = True
                prev_char = char
                continue

            if char == '"':
                in_string = not in_string
                result.append(char)
                prev_char = char
                continue

            if in_string:
                # Preserve all whitespace inside strings
                result.append(char)
                prev_char = char
                continue

            # Outside strings: normalize whitespace
            if char == ' ':
                # Skip multiple spaces, but keep one
                if prev_char != ' ':
                    result.append(char)
            elif char == '\t':
                # Replace tabs with space (but not at line start - already handled)
                if prev_char != ' ' and prev_char is not None:
                    result.append(' ')
            else:
                result.append(char)

            prev_char = char

        # Remove trailing whitespace
        return ''.join(result).rstrip()

    def normalize_preserve_strings(self, text: str) -> str:
        """Normalize whitespace while preserving semantic content.

        This method is more conservative and preserves whitespace
        inside strings and other semantic content.
        """
        if not text:
            return text

        # Remove BOM
        normalized = self._remove_bom(text)

        # Standardize line endings
        normalized = self._standardize_line_endings(normalized)

        # Only normalize leading whitespace on lines (tabs/spaces)
        lines = normalized.split('\n')
        normalized_lines = []

        for line in lines:
            # Remove leading tabs and spaces
            normalized_line = line.lstrip('\t ')
            normalized_lines.append(normalized_line)

        return '\n'.join(normalized_lines)
