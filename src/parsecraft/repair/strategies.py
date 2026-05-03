"""Repair strategies for fixing common JSON errors."""

import re
from typing import Optional


class RepairStrategies:
    """Collection of repair strategies for common JSON errors."""

    @staticmethod
    def remove_trailing_comma(json_str: str) -> Optional[str]:
        """Remove trailing commas before closing braces/brackets.
        
        Handles:
        - {"key": "value",}
        - ["item",]
        - {"a": 1, "b": 2,}
        """
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                result.append(char)
                escape_next = True
                i += 1
                continue
                
            if char == '"':
                in_string = not in_string
                result.append(char)
                i += 1
                continue
                
            if in_string:
                result.append(char)
                i += 1
                continue
            
            # Check for trailing comma pattern: ,} or ,]
            if char == ',':
                # Look ahead to find next non-whitespace character
                j = i + 1
                while j < len(json_str) and json_str[j] in ' \t\n\r':
                    j += 1
                if j < len(json_str) and json_str[j] in '}]':
                    # Skip the comma
                    i = i + 1
                    continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)

    @staticmethod
    def fix_single_quotes(json_str: str) -> Optional[str]:
        """Replace single quotes with double quotes.
        
        Handles:
        - {'key': 'value'} -> {"key": "value"}
        - ['item'] -> ["item"]
        
        Note: Only fixes quotes outside strings, not within string content.
        """
        result = []
        i = 0
        in_double_string = False
        in_single_string = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if char == '"' and not in_single_string:
                in_double_string = not in_double_string
                result.append(char)
            elif char == "'" and not in_double_string:
                # Replace single quote with double quote
                result.append('"')
            else:
                result.append(char)
            
            i += 1
        
        return ''.join(result)

    @staticmethod
    def fix_unquoted_keys(json_str: str) -> Optional[str]:
        """Quote unquoted keys.
        
        Handles:
        - {key: "value"} -> {"key": "value"}
        """
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if escape_next:
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                result.append(char)
                escape_next = True
                i += 1
                continue
            
            if char == '"':
                in_string = not in_string
                result.append(char)
                i += 1
                continue
            
            if in_string:
                result.append(char)
                i += 1
                continue
            
            # Check for unquoted key: {key: or { key:
            if char.isalpha() or char == '_':
                # This could be an unquoted key
                # Check if it's at the start of a key (after { or , or :)
                j = i - 1
                while j >= 0 and json_str[j] in ' \t\n\r':
                    j -= 1
                
                if j >= 0 and json_str[j] in '{,':
                    # This is likely an unquoted key
                    # Find the end of the key
                    key_start = i
                    while i < len(json_str) and (json_str[i].isalnum() or json_str[i] in '_-'):
                        i += 1
                    
                    # Check if followed by :
                    j = i
                    while j < len(json_str) and json_str[j] in ' \t\n\r':
                        j += 1
                    
                    if j < len(json_str) and json_str[j] == ':':
                        # Quote the key
                        result.append('"')
                        result.append(json_str[key_start:i])
                        result.append('"')
                        continue
            
            result.append(char)
            i += 1
        
        return ''.join(result)

    @staticmethod
    def fix_invalid_escape_sequences(json_str: str) -> Optional[str]:
        """Fix invalid escape sequences.
        
        Handles common invalid escapes by escaping them properly.
        Note: This is a simple approach that doesn't handle all cases.
        """
        # Common invalid escapes to fix
        invalid_escapes = [
            (r'\x', r'\\x'),  # Invalid hex escape
        ]
        
        result = json_str
        for invalid, fixed in invalid_escapes:
            # Only replace if not already escaped
            result = result.replace(invalid, fixed)
        
        return result

    @staticmethod
    def remove_trailing_newline(json_str: str) -> Optional[str]:
        """Remove trailing newlines from JSON string."""
        return json_str.rstrip()