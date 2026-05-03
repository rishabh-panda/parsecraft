"""Extractor class for extracting JSON content from raw LLM output."""

import json
import re
from typing import Optional


class Extractor:
    """Extracts JSON content from raw LLM output.

    This class handles various formats of LLM output including:
    - JSON code fences (```json ... ``` or ``` ... ```)
    - Non-JSON code fences with embedded JSON
    - Raw JSON in text
    - Multiple JSON objects (returns first valid one)

    Attributes:
        None
    """

    def __init__(self):
        """Initialize the Extractor."""
        pass

    def extract(self, text: str) -> str:
        """Extract JSON content from raw text.

        Args:
            text: Raw LLM output text to extract from.

        Returns:
            Extracted JSON string.

        Raises:
            ExtractionError: If no JSON-like content is found.
        """
        if not text or not isinstance(text, str):
            from parsecraft.extraction.errors import ExtractionError
            raise ExtractionError(
                "Input text is empty or not a string",
                str(text) if text else ""
            )

        # Try to extract from JSON code fences first
        json_content = self._extract_from_json_fence(text)
        if json_content is not None:
            return json_content

        # Try to extract from any code fence
        json_content = self._extract_from_any_fence(text)
        if json_content is not None:
            return json_content

        # Try to extract JSON from raw text
        json_content = self._extract_from_raw_text(text)
        if json_content is not None:
            return json_content

        # No JSON found
        from parsecraft.extraction.errors import ExtractionError
        raise ExtractionError(
            "No JSON-like content found in the output",
            text
        )

    def _extract_from_json_fence(self, text: str) -> Optional[str]:
        """Extract JSON from JSON code fences.

        Matches patterns like:
        ```json
        {"key": "value"}
        ```
        or
        ```json{"key": "value"}```
        """
        # Pattern for ```json ... ```
        pattern = r'```json\s*(.*?)\s*```'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            content = match.group(1).strip()
            if self._is_valid_json_like(content):
                return content

        return None

    def _extract_from_any_fence(self, text: str) -> Optional[str]:
        """Extract JSON from any code fence (python, markdown, etc.).

        Searches for code fences and extracts any JSON content within.
        """
        # Match any code fence: ```language ... ``` or ```...```
        # Try multiple patterns to be flexible
        patterns = [
            r'```(?:\w+)?\s*\n?(.*?)\n?\s*```',  # Multiline with optional language
            r'```\s*(.*?)\s*```',  # Inline or simple fences
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.DOTALL)
            for match in matches:
                content = match.group(1).strip()
                if self._is_valid_json_like(content):
                    return content

        return None

    def _extract_from_raw_text(self, text: str) -> Optional[str]:
        """Extract JSON from raw text without code fences.

        Returns the entire text if it appears to be JSON, or finds JSON in text.
        """
        # Try to find JSON pattern anywhere in the text
        import json
        
        # Look for potential JSON objects or arrays
        start_patterns = [
            (r'\{', r'\}'),  # Object
            (r'\[', r'\]'),  # Array
        ]
        
        for start_re, end_re in start_patterns:
            # Find all occurrences
            for start_match in re.finditer(start_re, text):
                idx = start_match.start()
                # Try from this position
                result = self._extract_json_at_position(text, idx)
                if result:
                    return result
        
        text = text.strip()
        # If the entire text looks like JSON, return it
        if self._is_valid_json_like(text):
            return text

        return None
    
    def _extract_json_at_position(self, text: str, start_idx: int) -> Optional[str]:
        """Extract JSON starting at a specific position."""
        if start_idx < 0 or start_idx >= len(text):
            return None
            
        text_to_parse = text[start_idx:]
        
        if text_to_parse.startswith('{'):
            return self._extract_object(text_to_parse)
        elif text_to_parse.startswith('['):
            return self._extract_array(text_to_parse)
        
        return None
    
    def _extract_object(self, text: str) -> Optional[str]:
        """Extract a complete JSON object."""
        if not text.startswith('{'):
            return None
            
        brace_count = 0
        in_string = False
        escape_next = False
        start_idx = None
        end_idx = None
        
        for i, char in enumerate(text):
            if start_idx is None:
                if char == '{':
                    start_idx = i
                    
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"':
                in_string = not in_string
                continue
                
            if in_string:
                continue
                
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx is not None:
                    end_idx = i + 1
                    break
                    
        if start_idx is not None and end_idx is not None:
            candidate = text[start_idx:end_idx]
            if self._is_valid_json_like(candidate):
                return candidate
                
        return None
    
    def _extract_array(self, text: str) -> Optional[str]:
        """Extract a complete JSON array."""
        if not text.startswith('['):
            return None
            
        bracket_count = 0
        in_string = False
        escape_next = False
        start_idx = None
        end_idx = None
        
        for i, char in enumerate(text):
            if start_idx is None:
                if char == '[':
                    start_idx = i
                    
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"':
                in_string = not in_string
                continue
                
            if in_string:
                continue
                
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and start_idx is not None:
                    end_idx = i + 1
                    break
                    
        if start_idx is not None and end_idx is not None:
            candidate = text[start_idx:end_idx]
            if self._is_valid_json_like(candidate):
                return candidate
                
        return None

    def _is_valid_json_like(self, content: str) -> bool:
        """Check if content appears to be valid JSON-like.

        This is a heuristic check that doesn't require full parsing.
        """
        if not content:
            return False

        content = content.strip()

        # Must start with { or [
        if not (content.startswith('{') or content.startswith('[')):
            return False

        # Must end with } or ]
        if not (content.endswith('}') or content.endswith(']')):
            return False

        # Check for basic JSON structure
        # Count braces/brackets to ensure they're balanced
        brace_count = 0
        bracket_count = 0
        in_string = False
        escape_next = False

        for char in content:
            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            # Check for single quotes (not valid JSON)
            if char == "'":
                return False

            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1

        return brace_count == 0 and bracket_count == 0
