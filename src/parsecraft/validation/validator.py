"""Validator class for validating data against schemas."""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from parsecraft.validation.errors import FieldValidationError, ValidationError


class Validator:
    """Validates data against Pydantic models or JSON Schema.

    This class provides comprehensive validation including:
    - Required field validation
    - Type validation
    - Constraint validation (min/max, patterns, enums)
    - Support for strict and lenient modes

    Attributes:
        strict_mode: If True, extra fields are not allowed.
    """

    def __init__(self, strict_mode: bool = True):
        """Initialize the Validator.

        Args:
            strict_mode: If True, extra fields not in schema are not allowed.
        """
        self.strict_mode = strict_mode

    def validate(
        self,
        data: Any,
        schema: Union[type, Dict],
        mode: str = None
    ) -> List[FieldValidationError]:
        """Validate data against schema.

        Args:
            data: The data to validate.
            schema: Pydantic model class or JSON Schema dict.
            mode: Validation mode ('strict' or 'lenient'). Defaults to self.strict_mode.

        Returns:
            List of validation errors (empty if valid).

        Raises:
            ValidationError: If validation fails.
        """
        mode = mode or ('strict' if self.strict_mode else 'lenient')
        
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return self._validate_pydantic(data, schema, mode)
        elif isinstance(schema, dict):
            return self._validate_json_schema(data, schema, mode)
        else:
            raise ValidationError(
                f"Invalid schema type: {type(schema)}",
                [FieldValidationError(
                    field="schema",
                    message=f"Schema must be a Pydantic model or JSON Schema dict, got {type(schema)}"
                )]
            )

    def _validate_pydantic(
        self,
        data: Any,
        schema: type,
        mode: str
    ) -> List[FieldValidationError]:
        """Validate using Pydantic model."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append(FieldValidationError(
                field="root",
                message="Data must be a dictionary",
                expected_type="object",
                actual_value=type(data).__name__
            ))
            return errors

        # Get field definitions from Pydantic model
        field_definitions = {}
        for name, field in schema.model_fields.items():
            field_definitions[name] = {
                'type': field.annotation,
                'required': field.is_required(),
                'default': field.default,
                'json_schema_extra': field.json_schema_extra
            }

        # Check for required fields
        for name, field_info in field_definitions.items():
            if field_info['required'] and name not in data:
                errors.append(FieldValidationError(
                    field=name,
                    message="Required field is missing",
                    expected_type=str(field_info['type'])
                ))

        # Check for extra fields in strict mode
        if mode == 'strict':
            for key in data.keys():
                if key not in field_definitions:
                    errors.append(FieldValidationError(
                        field=key,
                        message="Extra fields are not allowed in strict mode",
                        actual_value=data[key]
                    ))

        # Validate field types and constraints
        for name, value in data.items():
            if name in field_definitions:
                field_errors = self._validate_field_type(
                    name, value, field_definitions[name]
                )
                errors.extend(field_errors)

        return errors

    def _validate_field_type(
        self,
        field_name: str,
        value: Any,
        field_info: Dict
    ) -> List[FieldValidationError]:
        """Validate a single field's type and constraints."""
        errors = []
        expected_type = field_info.get('type')
        
        if expected_type is None:
            return errors

        # Check if value is None when field is required
        if value is None and field_info.get('required', False):
            errors.append(FieldValidationError(
                field=field_name,
                message="Field cannot be null",
                expected_type=str(expected_type)
            ))
            return errors

        # Basic type checking
        type_map = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict
        }

        expected_type_str = str(expected_type)
        
        # Handle Optional types
        if 'Optional' in expected_type_str or 'None' in expected_type_str:
            if value is None:
                return errors
        
        # Handle List types
        if 'List' in expected_type_str or 'list' in expected_type_str:
            if not isinstance(value, list):
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"Expected list, got {type(value).__name__}",
                    expected_type="list",
                    actual_value=value
                ))
            return errors

        # Handle Dict types
        if 'Dict' in expected_type_str or 'dict' in expected_type_str:
            if not isinstance(value, dict):
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"Expected dict, got {type(value).__name__}",
                    expected_type="dict",
                    actual_value=value
                ))
            return errors

        # Handle basic types
        for type_name, type_class in type_map.items():
            if type_name in expected_type_str.lower():
                if not isinstance(value, type_class):
                    errors.append(FieldValidationError(
                        field=field_name,
                        message=f"Expected {type_name}, got {type(value).__name__}",
                        expected_type=type_name,
                        actual_value=value
                    ))
                break

        return errors

    def _validate_json_schema(
        self,
        data: Any,
        schema: Dict,
        mode: str
    ) -> List[FieldValidationError]:
        """Validate using JSON Schema."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append(FieldValidationError(
                field="root",
                message="Data must be a dictionary for JSON Schema validation",
                expected_type="object"
            ))
            return errors

        schema_type = schema.get('type')
        
        # Check type
        if schema_type == 'object':
            # Validate required fields
            required = schema.get('required', [])
            for field_name in required:
                if field_name not in data:
                    errors.append(FieldValidationError(
                        field=field_name,
                        message="Required field is missing"
                    ))

            # Check for extra fields in strict mode
            if mode == 'strict':
                properties = schema.get('properties', {})
                for key in data.keys():
                    if key not in properties:
                        errors.append(FieldValidationError(
                            field=key,
                            message="Extra fields are not allowed in strict mode",
                            actual_value=data[key]
                        ))

            # Validate properties
            properties = schema.get('properties', {})
            for field_name, value in data.items():
                if field_name in properties:
                    field_schema = properties[field_name]
                    field_errors = self._validate_json_schema_field(
                        field_name, value, field_schema
                    )
                    errors.extend(field_errors)

        return errors

    def _validate_json_schema_field(
        self,
        field_name: str,
        value: Any,
        field_schema: Dict
    ) -> List[FieldValidationError]:
        """Validate a single field against JSON Schema."""
        errors = []
        field_type = field_schema.get('type')
        
        if field_type == 'string' and not isinstance(value, str):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected string, got {type(value).__name__}",
                expected_type="string",
                actual_value=value
            ))
        elif field_type == 'number' and not isinstance(value, (int, float)):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected number, got {type(value).__name__}",
                expected_type="number",
                actual_value=value
            ))
        elif field_type == 'integer' and not isinstance(value, int):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected integer, got {type(value).__name__}",
                expected_type="integer",
                actual_value=value
            ))
        elif field_type == 'boolean' and not isinstance(value, bool):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected boolean, got {type(value).__name__}",
                expected_type="boolean",
                actual_value=value
            ))
        elif field_type == 'array' and not isinstance(value, list):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected array, got {type(value).__name__}",
                expected_type="array",
                actual_value=value
            ))
        elif field_type == 'object' and not isinstance(value, dict):
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Expected object, got {type(value).__name__}",
                expected_type="object",
                actual_value=value
            ))

        # Check enum
        if 'enum' in field_schema and value not in field_schema['enum']:
            errors.append(FieldValidationError(
                field=field_name,
                message=f"Value must be one of {field_schema['enum']}",
                expected_type=f"enum: {field_schema['enum']}",
                actual_value=value
            ))

        # Check minimum/maximum for numbers
        if field_type in ('number', 'integer'):
            if 'minimum' in field_schema and value < field_schema['minimum']:
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"Value {value} is less than minimum {field_schema['minimum']}",
                    expected_type=f"minimum: {field_schema['minimum']}",
                    actual_value=value
                ))
            if 'maximum' in field_schema and value > field_schema['maximum']:
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"Value {value} is greater than maximum {field_schema['maximum']}",
                    expected_type=f"maximum: {field_schema['maximum']}",
                    actual_value=value
                ))

        # Check minLength/maxLength for strings
        if field_type == 'string':
            if 'minLength' in field_schema and len(value) < field_schema['minLength']:
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"String length {len(value)} is less than minLength {field_schema['minLength']}",
                    expected_type=f"minLength: {field_schema['minLength']}",
                    actual_value=value
                ))
            if 'maxLength' in field_schema and len(value) > field_schema['maxLength']:
                errors.append(FieldValidationError(
                    field=field_name,
                    message=f"String length {len(value)} is greater than maxLength {field_schema['maxLength']}",
                    expected_type=f"maxLength: {field_schema['maxLength']}",
                    actual_value=value
                ))

        return errors

    def is_valid(
        self,
        data: Any,
        schema: Union[type, Dict],
        mode: str = None
    ) -> bool:
        """Check if data is valid without raising exception.

        Args:
            data: The data to validate.
            schema: Pydantic model or JSON Schema.
            mode: Validation mode.

        Returns:
            True if valid, False otherwise.
        """
        try:
            errors = self.validate(data, schema, mode)
            return len(errors) == 0
        except Exception:
            return False