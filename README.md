<div align="center">

# 🔧 ParseCraft

### A model-agnostic LLM output reliability layer

**Transform messy, unstructured LLM responses into valid, structured data — reliably.**

[![Python](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-155%20passing-brightgreen?style=flat-square)](#testing)
[![Pydantic](https://img.shields.io/badge/pydantic-v2-orange?style=flat-square)](https://docs.pydantic.dev/)
[![Version](https://img.shields.io/badge/version-0.1.0-blue?style=flat-square)](#installation)

</div>

---

## The Problem

LLM outputs are inherently unreliable. They may contain:

- Malformed JSON with trailing commas or single quotes
- JSON buried inside markdown code fences
- Missing required fields or type mismatches
- Inconsistent encoding, BOM sequences, or line endings
- Transient failures from rate limits or network issues

**ParseCraft solves all of this** with a fault-tolerant, 7-stage pipeline that turns raw LLM text into clean, validated, structured data — with a confidence score attached.

---

## The Pipeline

```
Raw LLM Output
      │
      ▼
┌─────────────┐
│  Extraction │  ← Strip code fences, find JSON in raw text
└──────┬──────┘
       │
       ▼
┌───────────────┐
│ Normalization │  ← Remove BOM, fix line endings, normalize whitespace
└──────┬────────┘
       │
       ▼
┌─────────┐
│ Parsing │  ← Parse JSON, validate against Pydantic or JSON Schema
└────┬────┘
     │  (fail?)
     ▼
┌────────┐
│ Repair │  ← Auto-fix trailing commas, single quotes, unquoted keys
└────┬───┘
     │
     ▼
┌────────────┐
│ Validation │  ← Check required fields, types, constraints, enums
└─────┬──────┘
      │
      ▼
┌───────┐
│ Retry │  ← Exponential backoff with jitter for transient failures
└───┬───┘
    │
    ▼
┌─────────┐
│ Scoring │  ← Reliability score 0.0–1.0
└────┬────┘
     │
     ▼
 ParseResult
```

---

## Key Features

<table>
<tr>
<td width="50%">

### 🔍 Robust Extraction
Handles JSON in any format — `\`\`\`json` fences, plain code blocks, raw text, or mixed content. Returns the first valid JSON object found.

</td>
<td width="50%">

### 🧹 Text Normalization
Strips UTF-8/UTF-16 BOM sequences, standardizes CRLF → LF line endings, and collapses excessive whitespace — without touching string content.

</td>
</tr>
<tr>
<td width="50%">

### 🔨 Automatic Repair
Fixes the most common LLM JSON mistakes in order of complexity:
- Trailing comma removal
- Single → double quote conversion
- Unquoted key quoting
- Invalid escape sequence handling

</td>
<td width="50%">

### ✅ Schema Validation
Full support for both **Pydantic v2 models** and **JSON Schema** dicts. Validates required fields, types, min/max, patterns, and enums. Collects *all* errors, not just the first.

</td>
</tr>
<tr>
<td width="50%">

### 🔁 Retry with Backoff
Exponential backoff with random jitter prevents thundering herd. Configurable max retries, retryable error types, and per-call overrides.

</td>
<td width="50%">

### 📊 Reliability Scoring
Every result carries a `reliability_score` from `0.0` to `1.0`. Perfect output scores `1.0`. Repairs, retries, and validation warnings reduce the score proportionally.

</td>
</tr>
<tr>
<td width="50%">

### 🧩 Extensible Architecture
Each pipeline stage is a separate, injectable component. Add custom repair strategies, validation modes, or observability hooks without touching core code.

</td>
<td width="50%">

### 🔭 Observability
Structured logging for every pipeline event. Each stage records its input size, output, duration, errors, and repair attempts — opt-in via config.

</td>
</tr>
</table>

---

## Installation

```bash
pip install parsecraft
```

**Requirements:** Python 3.9+, pydantic ≥ 2.5, jsonschema ≥ 4.0

---

## Quick Start

### Basic Usage

```python
from parsecraft import Pipeline, ParserConfig
from pydantic import BaseModel

# 1. Define your schema
class User(BaseModel):
    name: str
    age: int

# 2. Create a pipeline
config = ParserConfig()
pipeline = Pipeline(config)

# 3. Parse raw LLM output — fences, whitespace, and all
llm_output = """
Here is the user data you requested:

```json
{"name": "Alice", "age": 30}
"""

result = pipeline.execute(llm_output, User)

print(result.parsed_data)        # User(name='Alice', age=30)
print(result.reliability_score)  # 1.0
print(result.repair_history)     # []
```

### Handling Malformed JSON

ParseCraft automatically repairs common LLM mistakes:

```python
# LLM returned single quotes and a trailing comma — no problem
bad_output = "{'name': 'Bob', 'age': 25,}"

result = pipeline.execute(bad_output)

print(result.parsed_data)        # {'name': 'Bob', 'age': 25}
print(result.reliability_score)  # 0.85  (reduced due to repair)
print(len(result.repair_history))  # 1
```

### JSON Schema Validation

```python
schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["active", "inactive"]},
        "score":  {"type": "number", "minimum": 0, "maximum": 100}
    },
    "required": ["status", "score"]
}

result = pipeline.execute(llm_output, schema)
```

---

## API Reference

### `Pipeline`

The main entry point. Orchestrates all 7 stages.

```python
class Pipeline:
    def __init__(self, config: ParserConfig): ...

    def execute(
        self,
        text: str,
        schema: Type[BaseModel] | dict | None = None,
        config: ParserConfig | None = None,   # per-call override
    ) -> ParseResult: ...
```

---

### `ParserConfig`

Immutable configuration. All fields have sensible defaults.

```python
@dataclass(frozen=True)
class ParserConfig:
    max_retries: int = 3
    timeout: float = 30.0
    repair_enabled: bool = True
    observability_enabled: bool = False
    repair_strategies: list[str] = [
        'trailing_comma',
        'single_quotes',
        'unquoted_keys',
        'escape_sequences',
    ]
```

Create per-call overrides without mutating the original:

```python
base_config = ParserConfig(max_retries=3)
strict_config = base_config.with_overrides(max_retries=10, timeout=60.0)
```

---

### `ParseResult`

Returned on success. Contains everything you need.

```python
@dataclass
class ParseResult:
    parsed_data: Any                    # dict, list, or Pydantic model instance
    reliability_score: float            # 0.0–1.0
    repair_history: list[RepairAttempt] # what was fixed and how
    validation_errors: list[dict]       # warnings (non-fatal issues)
    stage_results: dict[str, Any]       # per-stage timing and output
```

---

### `ParseError`

Raised on failure. Carries full diagnostic context.

```python
class ParseError(Exception):
    message: str
    original_input: str
    failed_stage: str           # 'Extraction' | 'Normalization' | 'Parsing' | ...
    specific_error: Exception
    result: ParseResult | None  # partial result if available
    repair_history: list[RepairAttempt]
    validation_errors: list[dict]
    is_user_error: bool         # True = bad input, False = system failure
```

---

## Error Handling

```python
from parsecraft import Pipeline, ParserConfig
from parsecraft.core.result import ParseError

pipeline = Pipeline(ParserConfig())

try:
    result = pipeline.execute(llm_output, MySchema)
    print(f"Score: {result.reliability_score:.2f}")
    print(f"Data:  {result.parsed_data}")

except ParseError as e:
    print(f"Stage:    {e.failed_stage}")
    print(f"Cause:    {e.specific_error}")
    print(f"Repairs:  {len(e.repair_history)} attempted")
    print(f"User err: {e.is_user_error}")
    # Inspect partial result if available
    if e.result:
        print(f"Partial: {e.result.parsed_data}")
```

---

## Configuration Examples

### Production — strict, observable

```python
config = ParserConfig(
    max_retries=5,
    timeout=60.0,
    repair_enabled=True,
    observability_enabled=True,
)
```

### Fast / Low-latency — no repair, no retry

```python
config = ParserConfig(
    max_retries=0,
    repair_enabled=False,
    observability_enabled=False,
)
```

### Custom repair strategy order

```python
config = ParserConfig(
    repair_strategies=[
        'trailing_comma',   # cheapest first
        'single_quotes',
        'unquoted_keys',
        'escape_sequences', # most expensive last
    ]
)
```

---

## Pipeline Stages — Deep Dive

| Stage | Class | Responsibility |
|---|---|---|
| **Extraction** | `Extractor` | Finds JSON in raw text — code fences, inline, or bare |
| **Normalization** | `Normalizer` | Cleans encoding artifacts and whitespace |
| **Parsing** | `Parser` | `json.loads` + Pydantic / JSON Schema validation |
| **Repair** | `Repairer` | Applies fix strategies in order until JSON is valid |
| **Validation** | `Validator` | Deep schema check — collects all errors, not just first |
| **Retry** | `RetryManager` | Exponential backoff with jitter for transient errors |
| **Scoring** | `Scorer` | Computes `0.0–1.0` reliability score from pipeline metrics |

### Reliability Score Formula

```
score = 1.0
      − (repair_attempts × 0.15)   # capped at −0.50
      − (extra_parse_attempts × 0.05)
      − (validation_warnings × 0.02)  # capped at −0.10
```

A score of `1.0` means: no repairs, no retries, no warnings — perfect output.

---

## Correctness Properties

ParseCraft is validated against **21 formal correctness properties** using property-based testing (Hypothesis):

| # | Property | Stage |
|---|---|---|
| 1 | `extract(extract(x)) == extract(x)` — idempotence | Extraction |
| 2 | Extraction preserves semantic content | Extraction |
| 3 | Code fences are stripped correctly | Extraction |
| 4 | `parse(normalize(x)) == parse(x)` — round-trip equivalence | Normalization |
| 5 | Multiple whitespace forms normalize to single space | Normalization |
| 6 | `parse(serialize(parse(x))) == parse(x)` — round-trip | Parsing |
| 7 | Parsed data either matches schema or raises `ParseError` | Parsing |
| 8 | Repaired output is always valid JSON | Repair |
| 9 | Minimal change — trailing comma preferred over regeneration | Repair |
| 10 | Same input always produces same repair sequence | Repair |
| 11 | All schema constraints are checked | Validation |
| 12 | All errors collected, not just the first | Validation |
| 13 | `delay(n) ≥ delay(n−1)` — exponential backoff | Retry |
| 14 | Delays include random jitter | Retry |
| 15 | Retry count ≤ `max_retries` | Retry |
| 16 | `0.0 ≤ score ≤ 1.0` for all outputs | Scoring |
| 17 | More repairs → lower score (monotonicity) | Scoring |
| 18 | `score == 1.0` iff no repairs and no warnings | Scoring |
| 19 | All 7 stages execute in correct order | Pipeline |
| 20 | `ParseError` includes full stage context | Pipeline |
| 21 | `parse(x) == parse(x)` — idempotent parse | Pipeline |

---

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=parsecraft --cov-report=html

# Run only unit tests
python -m pytest tests/unit/
```

**Current status: 155 tests, 0 failures.**

```
tests/unit/test_extraction_errors.py        09 passed
tests/unit/test_extractor.py                44 passed
tests/unit/test_normalization_errors.py     09 passed
tests/unit/test_normalizer.py               28 passed
tests/unit/test_parser.py                   23 passed
tests/unit/test_repairer.py                 20 passed
tests/unit/test_validator.py                22 passed
──────────────────────────────────────────────────────
TOTAL                                      155 passed
──────────────────────────────────────────────────────
```

---

## Project Structure

```
parsecraft/
├── src/parsecraft/
│   ├── core/               # ParseResult, ParseError, ParserConfig
│   ├── extraction/         # Extractor + ExtractionError
│   ├── normalization/      # Normalizer + NormalizationError
│   ├── parsing/            # Parser + ParseError
│   ├── repair/             # Repairer, RepairStrategies, RepairError
│   ├── validation/         # Validator, ValidationError, FieldValidationError
│   ├── retry/              # RetryManager with exponential backoff
│   ├── scoring/            # Scorer
│   ├── pipeline/           # Pipeline orchestrator
│   └── serialization/      # Serializer, PrettyPrinter
├── tests/
│   └── unit/               # 155 unit tests
├── pyproject.toml
├── README.md
└── LICENSE.md
```

---

## Development Setup

```bash
# Clone and install in editable mode
git clone https://github.com/your-org/parsecraft.git
cd parsecraft
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Format code
black src/ tests/

# Type check
mypy src/
```

---

## License

MIT © 2026 — see [LICENSE](LICENSE) for details.

---

<div align="center">

**ParseCraft** — because LLM output shouldn't be your problem.

</div>
