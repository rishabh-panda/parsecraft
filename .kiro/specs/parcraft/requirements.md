# Requirements Document: parsecraft

## Introduction

parsecraft is a production-grade Python library that provides a model-agnostic LLM output reliability layer. It transforms messy, unstructured LLM responses into valid, structured data through a robust pipeline: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring.

The library addresses the fundamental challenge that LLM outputs are inherently unreliable - they may contain malformed JSON, missing fields, type mismatches, or be completely invalid. parsecraft provides a fault-tolerant, extensible framework that handles these failures gracefully while exposing a clean, simple API for developers.

## Glossary

- **parsecraft**: The library itself - a model-agnostic LLM output reliability layer
- **LLM**: Large Language Model - the source of unstructured output
- **Raw Output**: The unprocessed text returned by an LLM
- **Structured Data**: Valid JSON or Pydantic model instance
- **Schema**: A validation schema (Pydantic model or JSON Schema) defining expected output structure
- **Pipeline Stage**: A discrete step in the reliability layer (Extraction, Normalization, Parsing, Repair, Validation, Retry, Scoring)
- **Repair**: The process of attempting to fix invalid output using heuristics or LLM-based methods
- **Reliability Score**: A numeric confidence metric (0.0-1.0) indicating output quality

## Requirements

### Requirement 1: Extract Raw LLM Output

**User Story:** As a developer, I want to extract structured content from raw LLM output, so that I can work with clean data regardless of formatting.

#### Acceptance Criteria

1. WHEN raw LLM output contains JSON code fences (```json ... ``` or ``` ... ```), THE Extractor SHALL remove the fences and return the inner content
2. WHEN raw LLM output contains non-JSON code fences (```python ... ```, ```markdown ... ```, etc.), THE Extractor SHALL attempt to find and extract any JSON content within the output
3. WHEN raw LLM output contains no code fences but appears to contain JSON, THE Extractor SHALL return the entire output
4. IF no JSON-like content is found in the raw output, THEN THE Extractor SHALL raise an ExtractionError with a descriptive message
5. WHERE multiple JSON objects are present, THE Extractor SHALL return the first valid JSON object found

### Requirement 2: Normalize Text Format

**User Story:** As a developer, I want to normalize text formatting issues, so that parsing can proceed reliably regardless of encoding or whitespace problems.

#### Acceptance Criteria

1. WHEN raw text contains BOM (Byte Order Mark) sequences, THE Normalizer SHALL remove them
2. WHEN raw text contains inconsistent line endings (CRLF vs LF), THE Normalizer SHALL standardize to LF
3. WHEN raw text contains excessive whitespace (multiple consecutive spaces, tabs at line start), THE Normalizer SHALL normalize to single spaces and trim
4. WHILE normalizing, THE Normalizer SHALL preserve the semantic content of the text
5. IF normalization would alter semantic meaning (e.g., removing spaces within strings), THEN THE Normalizer SHALL skip that transformation

### Requirement 3: Parse Structured Data

**User Story:** As a developer, I want to parse normalized text into structured data, so that I can work with validated Python objects.

#### Acceptance Criteria

1. WHEN normalized text is valid JSON, THE Parser SHALL parse it into a Python dict
2. WHEN parsed JSON does not match the target schema, THE Parser SHALL raise a ParseError with details about the mismatch
3. IF parsing fails due to invalid JSON syntax, THEN THE Parser SHALL raise a ParseError with the underlying JSON error
4. WHERE a schema is provided, THE Parser SHALL validate the parsed data against the schema
5. THE Parser SHALL support both Pydantic models and JSON Schema definitions

### Requirement 4: Repair Invalid Output

**User Story:** As a developer, I want to automatically repair invalid output, so that I can recover from common LLM mistakes without manual intervention.

#### Acceptance Criteria

1. WHEN parsing fails due to common JSON errors (trailing commas, single quotes, unquoted keys), THE Repairer SHALL attempt automatic fixes
2. WHEN repair is attempted, THE Repairer SHALL log the original error and repair attempt for observability
3. WHERE multiple repair strategies are available, THE Repairer SHALL try them in order of increasing complexity
4. IF all repair strategies fail, THEN THE Repairer SHALL raise a RepairError with details about attempted fixes
5. WHERE LLM-based repair is configured, THE Repairer SHALL use the configured LLM to regenerate valid output

### Requirement 5: Validate Against Schema

**User Story:** As a developer, I want to validate parsed data against a schema, so that I can ensure output conforms to my expectations.

#### Acceptance Criteria

1. WHEN data is provided with a schema, THE Validator SHALL check that all required fields are present
2. WHEN data is provided with a schema, THE Validator SHALL check that field types match the schema
3. WHEN data is provided with a schema, THE Validator SHALL validate constraints (min/max values, patterns, enums)
4. IF validation fails, THEN THE Validator SHALL raise a ValidationError with a list of all validation errors
5. WHERE optional validation modes exist (strict vs lenient), THE Validator SHALL support both modes

### Requirement 6: Retry with Backoff

**User Story:** As a developer, I want automatic retry with exponential backoff, so that transient failures don't immediately cause errors.

#### Acceptance Criteria

1. WHEN a retryable error occurs (network failure, rate limit), THE RetryManager SHALL retry the operation
2. WHILE retrying, THE RetryManager SHALL use exponential backoff with jitter
3. WHERE a maximum retry count is configured, THE RetryManager SHALL stop retrying after reaching the limit
4. IF all retries are exhausted, THEN THE RetryManager SHALL raise the final error with retry context
5. WHERE specific errors should not be retried, THE RetryManager SHALL respect the retry configuration

### Requirement 7: Score Output Reliability

**User Story:** As a developer, I want a reliability score for each output, so that I can make informed decisions about output quality.

#### Acceptance Criteria

1. WHEN output is successfully parsed and validated, THE Scorer SHALL return a reliability score of 1.0
2. WHEN output required repair to become valid, THE Scorer SHALL return a score between 0.5 and 0.99 based on repair complexity
3. WHEN output required multiple parsing attempts, THE Scorer SHALL reduce the score based on attempt count
4. WHERE validation warnings exist (optional fields missing, type coercion), THE Scorer SHALL reduce the score appropriately
5. THE Scorer SHALL return a score in the range [0.0, 1.0] where 1.0 indicates perfect reliability

### Requirement 8: Core Pipeline Integration

**User Story:** As a developer, I want the pipeline stages to work together seamlessly, so that I can get reliable output with minimal configuration.

#### Acceptance Criteria

1. WHEN parse() is called, THE Pipeline SHALL execute all stages in order: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring
2. WHERE a stage fails and repair is possible, THE Pipeline SHALL invoke the Repair stage and retry subsequent stages
3. IF the entire pipeline fails after all retries, THEN THE Pipeline SHALL raise a ParseError with full context
4. WHERE observability is enabled, THE Pipeline SHALL log each stage execution and outcome
5. THE Pipeline SHALL support both synchronous and asynchronous operation

### Requirement 9: Clean Developer API

**User Story:** As a developer, I want a simple, intuitive API, so that I can integrate parsecraft with minimal code changes.

#### Acceptance Criteria

1. THE Main API SHALL provide a single entry point: `OutputParser.parse(text, schema, **options)`
2. WHERE options are provided, THE API SHALL accept common parameters: max_retries, timeout, repair_enabled, observability_enabled
3. THE API SHALL return a Result object containing: parsed_data, reliability_score, repair_history, validation_errors
4. IF parsing fails, THE API SHALL raise a ParseError that includes the Result object with partial data
5. THE API SHALL support both Pydantic models and custom schema classes

### Requirement 10: Fault-Tolerant Design

**User Story:** As a developer, I want the library to handle unexpected failures gracefully, so that my application remains stable.

#### Acceptance Criteria

1. WHEN an unexpected error occurs in any stage, THE Pipeline SHALL catch it and attempt recovery or fail gracefully
2. IF a repair attempt causes additional errors, THE Pipeline SHALL discard the repair and try the next strategy
3. WHERE external dependencies fail (LLM API, network), THE Pipeline SHALL provide clear error messages
4. THE Pipeline SHALL NOT leak internal state between calls
5. WHERE resource limits are exceeded (memory, time), THE Pipeline SHALL raise a TimeoutError or ResourceError

### Requirement 11: Extensible Architecture

**User Story:** As a library maintainer, I want to add new pipeline stages and strategies, so that the library can evolve.

#### Acceptance Criteria

1. EACH pipeline stage SHALL be implemented as a separate, testable component
2. WHERE new repair strategies are needed, THE Architecture SHALL allow adding them without modifying core code
3. WHERE new validation modes are needed, THE Architecture SHALL allow adding them via configuration
4. THE Pipeline SHALL use dependency injection for stage components
5. EACH extension point SHALL have clear documentation and example implementations

### Requirement 12: Testability

**User Story:** As a developer, I want the library to be thoroughly tested, so that I can trust its reliability.

#### Acceptance Criteria

1. EACH pipeline stage SHALL have unit tests covering normal and edge cases
2. THE Pipeline SHALL have integration tests covering end-to-end scenarios
3. WHERE property-based testing is applicable, THE Tests SHALL use property-based approaches
4. THE Test Suite SHALL achieve at least 90% code coverage
5. EACH public API SHALL have example tests demonstrating real-world usage

### Requirement 13: Error Handling and Reporting

**User Story:** As a developer, I want clear error messages, so that I can debug issues quickly.

#### Acceptance Criteria

1. WHEN parsing fails, THE Error Message SHALL include: original input, failed stage, specific error details
2. WHERE multiple errors occur, THE Error Message SHALL list all errors with context
3. IF a repair attempt is made, THE Error Message SHALL include the repair history
4. THE Error Message SHALL distinguish between user errors (invalid input) and system errors (internal failure)
5. WHERE observability is enabled, THE System SHALL emit structured logs for each pipeline event

### Requirement 14: Parser and Serializer Requirements

**User Story:** As a developer, I want to parse and serialize data reliably, so that round-trip operations work correctly.

#### Acceptance Criteria

1. WHEN valid JSON is parsed into a Pydantic model, THE Parser SHALL produce a valid model instance
2. THE PrettyPrinter SHALL format Pydantic models back into valid JSON
3. FOR ALL valid model instances, parsing then printing then parsing SHALL produce an equivalent model (round-trip property)
4. WHERE custom serializers are needed, THE System SHALL support custom encoder/decoder configuration
5. THE Parser SHALL handle all standard JSON types: null, boolean, number, string, array, object

### Requirement 15: Configuration and Options

**User Story:** As a developer, I want configurable behavior, so that I can tune the library for my use case.

#### Acceptance Criteria

1. THE Configuration SHALL support: max_retries (default: 3), timeout (default: 30s), repair_enabled (default: true), observability_enabled (default: false)
2. WHERE repair is enabled, THE Configuration SHALL allow specifying repair strategies in order of preference
3. THE Configuration SHALL support both global defaults and per-call overrides
4. IF invalid configuration is provided, THE System SHALL raise a ConfigurationError with descriptive message
5. THE Configuration SHALL be immutable after creation to prevent race conditions

## Correctness Properties for Property-Based Testing

### Extraction Stage Properties

1. **Idempotence**: Extracting from already-extracted content returns the same result
   - `extract(extract(text)) == extract(text)`

2. **Content Preservation**: Extraction does not alter the semantic content
   - The extracted JSON string, when parsed, equals the original intended structure

3. **Fence Handling**: Code fences are properly stripped
   - `extract("```json\n{...}\n```") == extract("{...}")`

### Normalization Stage Properties

1. **Round-Trip Equivalence**: Normalization preserves parseability
   - `parse(normalize(text)) == parse(text)` where both succeed

2. **Whitespace Normalization**: Multiple whitespace forms normalize to single space
   - `normalize("a  \t  b") == normalize("a b")`

### Parsing Stage Properties

1. **Round-Trip Property**: Parse → Serialize → Parse produces equivalent results
   - `parse(serialize(parse(json))) == parse(json)` for valid JSON

2. **Schema Validation**: Parsed data either matches schema or raises error
   - Either `validate(parsed, schema)` succeeds or `ParseError` is raised

### Repair Stage Properties

1. **Correctness**: Repaired output is valid
   - If repair succeeds, the result parses and validates successfully

2. **Minimal Change**: Repairs make the smallest possible change to fix errors
   - Trailing comma removal is preferred over full regeneration

3. **Deterministic**: Same input always produces same repair attempt sequence
   - `repair(error1) == repair(error1)` (same error → same attempts)

### Validation Stage Properties

1. **Completeness**: All schema constraints are checked
   - Required fields, types, and constraints are all validated

2. **Error Aggregation**: All validation errors are collected, not just the first
   - Validation returns a list of all errors, not just the first one found

### Retry Stage Properties

1. **Exponential Backoff**: Delay increases between retries
   - `delay(n) >= delay(n-1)` and `delay(n) > delay(n-1)` for some n

2. **Jitter**: Randomization prevents thundering herd
   - Delays include random jitter component

3. **Retry Limit**: Never exceeds configured maximum retries
   - Retry count ≤ max_retries for all operations

### Scoring Stage Properties

1. **Score Bounds**: Reliability score is always in [0.0, 1.0]
   - `0.0 <= score <= 1.0` for all outputs

2. **Monotonicity**: More repair attempts → lower score
   - If output A required fewer repairs than B, then `score(A) >= score(B)`

3. **Perfect Score**: No repairs, no warnings → score of 1.0
   - `score == 1.0` if and only if no repairs and no validation warnings

### Pipeline Integration Properties

1. **Pipeline Completeness**: All stages execute in correct order
   - Stage execution order: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring

2. **Error Context**: Final error includes full pipeline context
   - ParseError includes all stage results, repair history, and scores

3. **Idempotent Parse**: Calling parse twice on same input produces same result
   - `parse(text) == parse(text)` (same input → same output)

## Edge Cases and Failure Modes

### Malformed JSON Edge Cases

1. **Trailing commas**: `{"a": 1, "b": 2,}` → Should be repairable
2. **Single quotes**: `{'a': 1}` → Should be repairable
3. **Unquoted keys**: `{a: 1}` → Should be repairable
4. **Invalid escape sequences**: `"\x"` → Should be repairable or error
5. **Nested structure issues**: Missing closing braces/brackets → Should attempt repair

### Type Coercion Edge Cases

1. **String to number**: `"123"` → `123` → Should coerce if schema allows
2. **Boolean strings**: `"true"` → `true` → Should coerce if schema allows
3. **Null handling**: `null` fields → Should handle per schema definition
4. **Array type mismatches**: `[1, "two", 3]` → Should validate per schema

### Schema Edge Cases

1. **Missing required fields**: Should raise ValidationError with field name
2. **Extra fields**: Should handle per schema strictness setting
3. **Nested schema validation**: Should validate all nested structures
4. **Circular references**: Should detect and handle gracefully

### Network/External Failure Edge Cases

1. **Rate limiting**: Should retry with backoff
2. **Connection timeouts**: Should retry with backoff
3. **Server errors (5xx)**: Should retry with backoff
4. **Client errors (4xx)**: Should not retry (except 429 rate limit)

### Resource Limit Edge Cases

1. **Memory limits**: Should raise ResourceError if parsing large payloads
2. **Timeout limits**: Should raise TimeoutError if operation exceeds timeout
3. **Stack depth**: Should handle deeply nested structures without stack overflow

### Concurrency Edge Cases

1. **Thread safety**: Pipeline state should not leak between concurrent calls
2. **Async safety**: Async and sync modes should not interfere
3. **Configuration isolation**: Per-call config should not affect other calls
