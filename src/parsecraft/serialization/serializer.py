"""Serializer class for parsecraft."""

import json
from typing import Any, Type

from pydantic import BaseModel


class Serializer:
    """Handles serialization and deserialization of data.

    Supports:
    - JSON serialization
    - Pydantic model serialization
    - Custom encoders
    """

    def __init__(self, custom_encoders: dict = None):
        """Initialize the Serializer.

        Args:
            custom_encoders: Dict of custom encoder functions
        """
        self.custom_encoders = custom_encoders or {}

    def serialize(self, data: Any) -> str:
        """Serialize data to JSON string.

        Args:
            data: The data to serialize

        Returns:
            JSON string representation
        """
        return json.dumps(data, default=self._default_encoder)

    def deserialize(self, json_str: str) -> Any:
        """Deserialize JSON string to Python object.

        Args:
            json_str: The JSON string to parse

        Returns:
            Python object
        """
        return json.loads(json_str)

    def _default_encoder(self, obj: Any) -> Any:
        """Default encoder for JSON serialization.

        Args:
            obj: The object to encode

        Returns:
            JSON-serializable representation
        """
        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            return obj.model_dump()

        # Handle custom encoders
        for type_class, encoder in self.custom_encoders.items():
            if isinstance(obj, type_class):
                return encoder(obj)

        # Handle common types
        if hasattr(obj, '__dict__'):
            return obj.__dict__

        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def to_dict(self, data: Any) -> dict:
        """Convert data to dictionary.

        Args:
            data: The data to convert

        Returns:
            Dictionary representation
        """
        if isinstance(data, BaseModel):
            return data.model_dump()
        elif isinstance(data, dict):
            return data
        elif hasattr(data, '__dict__'):
            return data.__dict__
        else:
            return str(data)


class PrettyPrinter:
    """Formats Pydantic models back into valid JSON."""

    def __init__(self, indent: int = 2):
        """Initialize the PrettyPrinter.

        Args:
            indent: Number of spaces for indentation
        """
        self.indent = indent

    def format(self, data: Any) -> str:
        """Format data as pretty-printed JSON.

        Args:
            data: The data to format

        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(data, indent=self.indent, default=self._default_encoder)

    def _default_encoder(self, obj: Any) -> Any:
        """Default encoder for JSON serialization."""
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")