"""Core module for parsecraft.

This module contains core data models and configuration.
"""

from parsecraft.core.config import ParserConfig
from parsecraft.core.result import ParseError, ParseResult

__all__ = ["ParserConfig", "ParseResult", "ParseError"]