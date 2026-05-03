# parsecraft

A model-agnostic LLM output reliability layer.

parsecraft transforms messy, unstructured LLM responses into valid, structured data through a robust pipeline:

```
Raw LLM Output
    ↓
[Extraction]    → Extract JSON from code fences or raw text
    ↓
[Normalization] → Remove BOM, standardize line endings, normalize whitespace
    ↓
[Parsing]       → Parse JSON into Python objects, validate against schema
    ↓
[Repair]        → Attempt automatic fixes for common JSON errors
    ↓
[Validation]    → Validate parsed data against schema constraints
    ↓
[Retry]         → Retry with exponential backoff for transient failures
    ↓
[Scoring]       → Calculate reliability score (0.0-1.0)
    ↓
ParseResult (or ParseError)
```

## Features

- **Model-agnostic**: Works with any LLM output
- **Robust extraction**: Handles code fences, raw JSON, and mixed content
- **Text normalization**: Removes BOM, standardizes line endings, normalizes whitespace
- **Automatic repair**: Fixes common JSON errors (trailing commas, single quotes, etc.)
- **Schema validation**: Supports Pydantic models and JSON Schema
- **Retry with backoff**: Handles transient failures with exponential backoff
- **Reliability scoring**: Get confidence scores for parsed output
- **Extensible**: Easy to add custom repair strategies and validation modes

## Installation

```bash
pip install parsecraft
```

## Quick Start

```python
from parsecraft import OutputParser
from pydantic import BaseModel

# Define your schema
class User(BaseModel):
    name: str
    age: int

# Create parser
parser = OutputParser()

# Parse LLM output
llm_output = '''```json
{"name": "Alice", "age": 30}
```'''

result = parser.parse(llm_output, User)

print(result.parsed_data)  # User(name='Alice', age=30)
print(result.reliability_score)  # 1.0
```

## API Reference

### OutputParser

```python
class OutputParser:
    def parse(
        self,
        text: str,
        schema: Union[Type[BaseModel], dict, None] = None,
        **options
    ) -> ParseResult:
        """Parse LLM output and return structured data."""
```

### Options

- `max_retries`: Maximum retry attempts (default: 3)
- `timeout`: Timeout in seconds (default: 30)
- `repair_enabled`: Enable automatic repair (default: true)
- `observability_enabled`: Enable observability logging (default: false)

### ParseResult

```python
@dataclass
class ParseResult:
    parsed_data: Any  # The parsed data
    reliability_score: float  # 0.0-1.0
    repair_history: List[RepairAttempt]  # History of repair attempts
    validation_errors: List[Dict]  # Validation warnings
    stage_results: Dict[str, Any]  # Results from each stage
```

### ParseError

```python
class ParseError(Exception):
    message: str
    original_input: str
    failed_stage: str
    specific_error: Exception
    result: Optional[ParseResult]
    repair_history: List[RepairAttempt]
    validation_errors: List[Dict]
    is_user_error: bool
```

## Pipeline Stages

### 1. Extraction

Extracts JSON content from raw LLM output:
- JSON code fences (```json ... ```)
- Non-JSON code fences with embedded JSON
- Raw JSON in text
- Multiple JSON objects (returns first valid)

### 2. Normalization

Cleans text formatting:
- Removes BOM sequences
- Standardizes line endings to LF
- Normalizes excessive whitespace
- Preserves semantic content

### 3. Parsing

Parses and validates:
- Parses valid JSON into Python objects
- Validates against Pydantic models
- Validates against JSON Schema
- Raises ParseError for schema mismatches

### 4. Repair

Automatically fixes common errors:
- Trailing comma removal
- Single quote to double quote conversion
- Unquoted key handling
- Invalid escape sequence handling

### 5. Validation

Validates against schema:
- Required field validation
- Type validation
- Constraint validation (min/max, patterns, enums)
- Strict and lenient modes

### 6. Retry

Handles transient failures:
- Exponential backoff with jitter
- Configurable retry limit
- Retryable error types

### 7. Scoring

Calculates reliability score:
- 1.0 for perfect output
- Reduced for repairs, multiple attempts, validation warnings
- Range: 0.0-1.0

## Error Handling

parsecraft provides detailed error information:

```python
try:
    result = parser.parse(llm_output, User)
except ParseError as e:
    print(f"Failed at stage: {e.failed_stage}")
    print(f"Original input: {e.original_input}")
    print(f"Repair attempts: {len(e.repair_history)}")
    print(f"Is user error: {e.is_user_error}")
```

## Configuration

```python
from parsecraft import ParserConfig

config = ParserConfig(
    max_retries=5,
    timeout=60.0,
    repair_enabled=True,
    observability_enabled=True,
    repair_strategies=[
        'trailing_comma',
        'single_quotes',
        'unquoted_keys',
        'escape_sequences',
    ]
)

parser = OutputParser(config)
```

## License

MIT License