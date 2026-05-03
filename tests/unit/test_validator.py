"""Unit tests for the Validator class."""

import pytest
from pydantic import BaseModel

from parsecraft.validation.errors import FieldValidationError, ValidationError
from parsecraft.validation.validator import Validator


class TestValidator:
    """Tests for the Validator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = Validator()

    # Test Pydantic model validation

    def test_validate_pydantic_valid_data(self):
        """Test validating valid data against Pydantic model."""
        class User(BaseModel):
            name: str
            age: int

        data = {"name": "Alice", "age": 30}
        errors = self.validator.validate(data, User)
        assert len(errors) == 0

    def test_validate_pydantic_missing_required_field(self):
        """Test that missing required field is detected."""
        class User(BaseModel):
            name: str
            age: int

        data = {"name": "Alice"}  # missing age
        errors = self.validator.validate(data, User)
        assert len(errors) == 1
        assert errors[0].field == "age"

    def test_validate_pydantic_wrong_type(self):
        """Test that wrong type is detected."""
        class User(BaseModel):
            name: str
            age: int

        data = {"name": "Alice", "age": "thirty"}  # age should be int
        errors = self.validator.validate(data, User)
        assert len(errors) >= 1

    def test_validate_pydantic_extra_field_strict_mode(self):
        """Test that extra fields are rejected in strict mode."""
        class User(BaseModel):
            name: str

        data = {"name": "Alice", "extra": "value"}
        errors = self.validator.validate(data, User, mode="strict")
        assert len(errors) == 1
        assert errors[0].field == "extra"

    def test_validate_pydantic_extra_field_lenient_mode(self):
        """Test that extra fields are allowed in lenient mode."""
        class User(BaseModel):
            name: str

        data = {"name": "Alice", "extra": "value"}
        errors = self.validator.validate(data, User, mode="lenient")
        assert len(errors) == 0

    def test_validate_pydantic_none_value(self):
        """Test that None value is handled correctly."""
        class User(BaseModel):
            name: str
            age: int | None = None

        data = {"name": "Alice", "age": None}
        errors = self.validator.validate(data, User)
        # None is valid for Optional[int]
        assert len(errors) == 0

    # Test JSON Schema validation

    def test_validate_json_schema_valid_data(self):
        """Test validating valid data against JSON Schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        data = {"name": "Alice", "age": 30}
        errors = self.validator.validate(data, schema)
        assert len(errors) == 0

    def test_validate_json_schema_missing_required_field(self):
        """Test that missing required field is detected."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        data = {"name": "Alice"}  # missing age
        errors = self.validator.validate(data, schema)
        assert len(errors) == 1
        assert errors[0].field == "age"

    def test_validate_json_schema_wrong_type(self):
        """Test that wrong type is detected."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        data = {"name": "Alice", "age": "thirty"}  # age should be integer
        errors = self.validator.validate(data, schema)
        assert len(errors) >= 1

    def test_validate_json_schema_extra_field_strict_mode(self):
        """Test that extra fields are rejected in strict mode."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        data = {"name": "Alice", "extra": "value"}
        errors = self.validator.validate(data, schema, mode="strict")
        assert len(errors) == 1

    def test_validate_json_schema_enum(self):
        """Test enum validation."""
        schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["active", "inactive"]}
            }
        }
        data = {"status": "pending"}  # not in enum
        errors = self.validator.validate(data, schema)
        assert len(errors) == 1

    def test_validate_json_schema_min_max(self):
        """Test min/max validation."""
        schema = {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        }
        data = {"age": 200}  # exceeds maximum
        errors = self.validator.validate(data, schema)
        assert len(errors) == 1

    def test_validate_json_schema_min_length(self):
        """Test minLength validation."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 2}
            }
        }
        data = {"name": "A"}  # too short
        errors = self.validator.validate(data, schema)
        assert len(errors) == 1

    # Test is_valid method

    def test_is_valid_true(self):
        """Test is_valid returns True for valid data."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        assert self.validator.is_valid({"name": "Alice"}, schema) is True

    def test_is_valid_false(self):
        """Test is_valid returns False for invalid data."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        assert self.validator.is_valid({"name": 123}, schema) is False

    # Test error aggregation

    def test_aggregates_multiple_errors(self):
        """Test that all errors are collected, not just the first."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age", "email"]
        }
        data = {}  # all required fields missing
        errors = self.validator.validate(data, schema)
        assert len(errors) >= 3

    # Test edge cases

    def test_validate_empty_object(self):
        """Test validating empty object."""
        schema = {"type": "object", "properties": {}}
        errors = self.validator.validate({}, schema)
        assert len(errors) == 0

    def test_validate_nested_object(self):
        """Test validating nested objects."""
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }
        data = {"user": {"name": "Alice"}}
        errors = self.validator.validate(data, schema)
        assert len(errors) == 0

    def test_validate_array(self):
        """Test validating arrays."""
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"type": "integer"}
                }
            }
        }
        data = {"items": [1, 2, 3]}
        errors = self.validator.validate(data, schema)
        assert len(errors) == 0

    def test_validate_field_error_to_dict(self):
        """Test FieldValidationError to_dict method."""
        error = FieldValidationError(
            field="name",
            message="Required field",
            expected_type="string",
            actual_value=None
        )
        error_dict = error.to_dict()
        assert error_dict["field"] == "name"
        assert error_dict["message"] == "Required field"
        assert error_dict["expected_type"] == "string"
        assert error_dict["actual_value"] is None

    def test_validate_invalid_schema_type(self):
        """Test that invalid schema type raises ValidationError."""
        with pytest.raises(ValidationError):
            self.validator.validate({"key": "value"}, "not_a_schema")

    def test_validate_complex_nested_structure(self):
        """Test validating complex nested structure."""
        schema = {
            "type": "object",
            "properties": {
                "users": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"}
                        },
                        "required": ["name"]
                    }
                }
            }
        }
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob"}
            ]
        }
        errors = self.validator.validate(data, schema)
        assert len(errors) == 0