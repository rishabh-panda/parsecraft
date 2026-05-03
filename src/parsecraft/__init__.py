"""parsecraft - A model-agnostic LLM output reliability layer.

parsecraft transforms messy, unstructured LLM responses into valid,
structured data through a robust pipeline:
Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring
"""

from parsecraft.core.config import ParserConfig
from parsecraft.core.result import ParseError, ParseResult
from parsecraft.extraction.extractor import Extractor
from parsecraft.normalization.normalizer import Normalizer
from parsecraft.parsing.parser import Parser
from parsecraft.repair.repairer import Repairer
from parsecraft.validation.validator import Validator
from parsecraft.pipeline.pipeline import Pipeline
from parsecraft.retry.retry_manager import RetryManager
from parsecraft.scoring.scorer import Scorer
from parsecraft.serialization.serializer import Serializer, PrettyPrinter

__version__ = "0.1.0"
__all__ = [
    "ParserConfig",
    "ParseResult",
    "ParseError",
    "Extractor",
    "Normalizer",
    "Parser",
    "Repairer",
    "Validator",
    "Pipeline",
    "RetryManager",
    "Scorer",
    "Serializer",
    "PrettyPrinter",
]