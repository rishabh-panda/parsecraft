"""Parser class for parsing and validating JSON."""

import json
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, ValidationError as PydanticValidationError

from parsecraft.parsing.errors import ParseError


class Parser:
    """Parses JSON strings and validates against schemas.

    This class handles:
    - Parsing valid JSON into Python dict
    - Validating against Pydantic models
    - Validating against JSON Schema definitions
    - Raising ParseError for schema mismatches or invalid JSON

    Attributes:
        None
    """

    def __init__(self):
        """Initialize the Parser."""
        pass

    def parse(
        self,
        json_str: str,
        schema: Optional[Union[Type[BaseModel], Dict]] = None
    ) -> Any:
        """Parse JSON string and optionally validate against schema.

        Args:
            json_str: The JSON string to parse.
            schema: Optional Pydantic model or JSON Schema dict for validation.

        Returns:
            Parsed data (dict, list, or Pydantic model instance).

        Raises:
            ParseError: If parsing fails or schema validation fails.
        """
        if not json_str or not isinstance(json_str, str):
            raise ParseError(
                "Input is empty or not a string",
                json_str if json_str else "",
                ValueError("Input must be a non-empty string")
            )

        try:
            # Parse JSON
            parsed_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ParseError(
                f"Invalid JSON: {str(e)}",
                json_str,
                e
            )

        # Validate against schema if provided
        if schema is not None:
            parsed_data = self._validate(parsed_data, schema)

        return parsed_data

    def _validate(
        self,
        data: Any,
        schema: Union[Type[BaseModel], Dict]
    ) -> Any:
        """Validate data against schema.

        Args:
            data: The parsed data to validate.
            schema: Pydantic model or JSON Schema dict.

        Returns:
            Validated data (possibly converted to Pydantic model).

        Raises:
            ParseError: If validation fails.
        """
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            # Pydantic model validation
            try:
                return schema.model_validate(data)
            except PydanticValidationError as e:
                raise ParseError(
                    f"Schema validation failed: {str(e)}",
                    json.dumps(data) if isinstance(data, (dict, list)) else str(data),
                    e
                )
        elif isinstance(schema, dict):
            # JSON Schema validation
            return self._validate_json_schema(data, schema)
        else:
            raise ParseError(
                f"Invalid schema type: {type(schema)}",
                json.dumps(data) if isinstance(data, (dict, list)) else str(data),
                ValueError(f"Schema must be a Pydantic model or JSON Schema dict, got {type(schema)}")
            )

    def _validate_json_schema(self, data: Any, schema: Dict) -> Any:
        """Validate data against JSON Schema.

        Args:
            data: The parsed data to validate.
            schema: JSON Schema dict.

        Returns:
            Validated data.

        Raises:
            ParseError: If validation fails.
        """
        try:
            import jsonschema
            from jsonschema import ValidationError as JsonSchemaValidationError
        except ImportError:
            # If jsonschema is not installed, skip validation
            return data

        try:
            jsonschema.validate(instance=data, schema=schema)
        except JsonSchemaValidationError as e:
            raise ParseError(
                f"JSON Schema validation failed: {e.message}",
                json.dumps(data),
                e
            )
        except Exception as e:
            raise ParseError(
                f"JSON Schema validation error: {str(e)}",
                json.dumps(data),
                e
            )

        return data

    def is_valid_json(self, json_str: str) -> bool:
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