# Implementation Plan: parsecraft

## Overview

parsecraft is a production-grade Python library that provides a model-agnostic LLM output reliability layer. This implementation plan breaks down the pipeline stages (Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring) into discrete coding tasks with testing requirements.

## Tasks

- [x] 1. Set up project structure and core interfaces
  - Create directory structure: `src/parsecraft/` with subdirectories for each pipeline stage
  - Define core interfaces and base classes for pipeline stages
  - Set up `pyproject.toml` with PEP 621 metadata, dependencies (pydantic>=2.5, jsonschema>=4.0)
  - Configure testing framework (pytest) and add test directory structure
  - _Requirements: 12, 15_

- [x] 2. Implement Extraction stage
  - [x] 2.1 Create `ExtractionError` exception class
    - Include descriptive error message with context
    - _Requirements: 1.4_
  
  - [x] 2.2 Implement `Extractor` class with `extract()` method
    - Handle JSON code fences (```json ... ``` and ``` ... ```)
    - Handle non-JSON code fences and extract JSON content within
    - Return entire output if no code fences but JSON-like content exists
    - Raise `ExtractionError` if no JSON-like content found
    - Return first valid JSON object when multiple present
    - _Requirements: 1.1, 1.2, 1.3, 1.5_
  
  - [x] 2.3 Write property test for extraction idempotence
    - **Property 1: Idempotence**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - `extract(extract(text)) == extract(text)`
  
  - [x] 2.4 Write property test for fence handling
    - **Property 3: Fence Handling**
    - **Validates: Requirements 1.1**
    - `extract("```json\n{...}\n```") == extract("{...}")`
  
  - [x] 2.5 Write unit tests for edge cases
    - Test code fence variations
    - Test multiple JSON objects
    - Test no JSON content
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 3. Implement Normalization stage
  - [ ] 3.1 Create `NormalizationError` exception class
    - _Requirements: 2.5_
  
  - [ ] 3.2 Implement `Normalizer` class with `normalize()` method
    - Remove BOM sequences
    - Standardize line endings to LF
    - Normalize excessive whitespace (multiple spaces, tabs at line start)
    - Preserve semantic content
    - Skip transformations that would alter semantic meaning
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 3.3 Write property test for round-trip equivalence
    - **Property 4: Round-Trip Equivalence**
    - **Validates: Requirements 2.1, 2.2**
    - `parse(normalize(text)) == parse(text)` where both succeed
  
  - [ ] 3.4 Write property test for whitespace normalization
    - **Property 5: Whitespace Normalization**
    - **Validates: Requirements 2.3**
    - `normalize("a  \t  b") == normalize("a b")`
  
  - [ ] 3.5 Write unit tests for edge cases
    - Test BOM removal
    - Test line ending standardization
    - Test whitespace normalization
    - Test semantic preservation
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 4. Implement Parsing stage
  - [ ] 4.1 Create `ParseError` exception class
    - Include original error details and schema context
    - _Requirements: 3.3, 3.4_
  
  - [ ] 4.2 Implement `Parser` class with `parse()` method
    - Parse valid JSON into Python dict
    - Validate against Pydantic models
    - Validate against JSON Schema definitions
    - Raise `ParseError` for schema mismatches
    - Raise `ParseError` for invalid JSON syntax
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 4.3 Write property test for round-trip parsing
    - **Property 6: Round-Trip Property**
    - **Validates: Requirements 3.1, 3.2**
    - `parse(serialize(parse(json))) == parse(json)` for valid JSON
  
  - [ ] 4.4 Write property test for schema validation
    - **Property 7: Schema Validation**
    - **Validates: Requirements 3.2, 3.4**
    - Either `validate(parsed, schema)` succeeds or `ParseError` is raised
  
  - [ ] 4.5 Write unit tests for edge cases
    - Test valid JSON parsing
    - Test schema validation
    - Test invalid JSON handling
    - Test Pydantic model support
    - Test JSON Schema support
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 5. Implement Repair stage
  - [ ] 5.1 Create `RepairError` exception class
    - Include attempted repair strategies and original error
    - _Requirements: 4.4_
  
  - [ ] 5.2 Implement basic repair strategies
    - Trailing comma removal
    - Single quote to double quote conversion
    - Unquoted key handling
    - Invalid escape sequence handling
    - _Requirements: 4.1_
  
  - [ ] 5.3 Implement `Repairer` class with `repair()` method
    - Try repair strategies in order of increasing complexity
    - Log original error and repair attempt for observability
    - Raise `RepairError` if all strategies fail
    - Support LLM-based repair when configured
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ] 5.4 Write property test for repair correctness
    - **Property 8: Correctness**
    - **Validates: Requirements 4.1**
    - If repair succeeds, result parses and validates successfully
  
  - [ ] 5.5 Write property test for minimal change
    - **Property 9: Minimal Change**
    - **Validates: Requirements 4.1**
    - Trailing comma removal preferred over full regeneration
  
  - [ ] 5.6 Write property test for deterministic repair
    - **Property 10: Deterministic**
    - **Validates: Requirements 4.3**
    - `repair(error1) == repair(error1)` (same error → same attempts)
  
  - [ ] 5.7 Write unit tests for edge cases
    - Test all repair strategies
    - Test multiple repair attempts
    - Test LLM-based repair configuration
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 6. Implement Validation stage
  - [ ] 6.1 Create `ValidationError` exception class
    - Include list of all validation errors
    - _Requirements: 5.4_
  
  - [ ] 6.2 Implement `Validator` class with `validate()` method
    - Check required fields are present
    - Check field types match schema
    - Validate constraints (min/max values, patterns, enums)
    - Support strict and lenient modes
    - Collect and return all validation errors
    - _Requirements: 5.1, 5.2, 5.3, 5.5_
  
  - [ ] 6.3 Write property test for validation completeness
    - **Property 11: Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.3**
    - All schema constraints are validated
  
  - [ ] 6.4 Write property test for error aggregation
    - **Property 12: Error Aggregation**
    - **Validates: Requirements 5.4**
    - Validation returns list of all errors, not just first
  
  - [ ] 6.5 Write unit tests for edge cases
    - Test required field validation
    - Test type validation
    - Test constraint validation
    - Test strict vs lenient modes
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Implement Retry stage
  - [ ] 7.1 Implement exponential backoff with jitter
    - Delay increases between retries
    - Random jitter component to prevent thundering herd
    - _Requirements: 6.2, 6.3_
  
  - [ ] 7.2 Implement `RetryManager` class
    - Retry on retryable errors (network failure, rate limit)
    - Stop after reaching max retry limit
    - Respect retry configuration for non-retryable errors
    - Raise final error with retry context when exhausted
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [ ] 7.3 Write property test for exponential backoff
    - **Property 13: Exponential Backoff**
    - **Validates: Requirements 6.2**
    - `delay(n) >= delay(n-1)` and `delay(n) > delay(n-1)` for some n
  
  - [ ] 7.4 Write property test for jitter
    - **Property 14: Jitter**
    - **Validates: Requirements 6.2**
    - Delays include random jitter component
  
  - [ ] 7.5 Write property test for retry limit
    - **Property 15: Retry Limit**
    - **Validates: Requirements 6.3**
    - Retry count ≤ max_retries for all operations
  
  - [ ] 7.6 Write unit tests for edge cases
    - Test retryable error handling
    - Test max retry limit
    - Test non-retryable error handling
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 8. Implement Scoring stage
  - [ ] 8.1 Implement `Scorer` class with `score()` method
    - Return 1.0 for perfect output (no repairs, no warnings)
    - Return 0.5-0.99 based on repair complexity
    - Reduce score based on parsing attempt count
    - Reduce score for validation warnings
    - Ensure score in range [0.0, 1.0]
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 8.2 Write property test for score bounds
    - **Property 16: Score Bounds**
    - **Validates: Requirements 7.5**
    - `0.0 <= score <= 1.0` for all outputs
  
  - [ ] 8.3 Write property test for monotonicity
    - **Property 17: Monotonicity**
    - **Validates: Requirements 7.2, 7.3**
    - If output A required fewer repairs than B, then `score(A) >= score(B)`
  
  - [ ] 8.4 Write property test for perfect score
    - **Property 18: Perfect Score**
    - **Validates: Requirements 7.1**
    - `score == 1.0` if and only if no repairs and no validation warnings
  
  - [ ] 8.5 Write unit tests for edge cases
    - Test perfect score calculation
    - Test score reduction for repairs
    - Test score reduction for multiple attempts
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 9. Implement Result object and core API
  - [ ] 9.1 Create `ParseResult` class
    - Include: parsed_data, reliability_score, repair_history, validation_errors
    - Support serialization for observability
    - _Requirements: 9.3_
  
  - [ ] 9.2 Create `ParseError` exception with Result object
    - Include full context: original input, failed stage, specific error details
    - Include all errors with context when multiple errors occur
    - Include repair history when repair attempted
    - Distinguish user errors vs system errors
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ] 9.3 Implement `OutputParser.parse()` method
    - Single entry point: `OutputParser.parse(text, schema, **options)`
    - Accept common parameters: max_retries, timeout, repair_enabled, observability_enabled
    - Return `ParseResult` on success
    - Raise `ParseError` with partial data on failure
    - Support both Pydantic models and custom schema classes
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10. Implement Configuration system
  - [ ] 10.1 Create `ParserConfig` class
    - Support: max_retries (default: 3), timeout (default: 30s), repair_enabled (default: true), observability_enabled (default: false)
    - Allow specifying repair strategies in order of preference
    - Support both global defaults and per-call overrides
    - Raise `ConfigurationError` for invalid configuration
    - Make configuration immutable after creation
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [ ] 10.2 Implement configuration validation
    - Validate all configuration parameters
    - Provide descriptive error messages
    - _Requirements: 15.4_

- [ ] 11. Implement Pipeline integration
  - [ ] 11.1 Create `Pipeline` class orchestrating all stages
    - Execute stages in order: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring
    - Invoke Repair stage when parsing fails and repair is possible
    - Raise `ParseError` with full context after all retries exhausted
    - Support observability logging
    - Support both synchronous and asynchronous operation
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 11.2 Write property test for pipeline completeness
    - **Property 19: Pipeline Completeness**
    - **Validates: Requirements 8.1**
    - Stage execution order: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring
  
  - [ ] 11.3 Write property test for error context
    - **Property 20: Error Context**
    - **Validates: Requirements 8.3**
    - ParseError includes all stage results, repair history, and scores
  
  - [ ] 11.4 Write property test for idempotent parse
    - **Property 21: Idempotent Parse**
    - **Validates: Requirements 8.5**
    - `parse(text) == parse(text)` (same input → same output)
  
  - [ ] 11.5 Write integration tests for end-to-end scenarios
    - Test complete pipeline with valid input
    - Test pipeline with malformed JSON requiring repair
    - Test pipeline with validation errors
    - Test pipeline with retry scenarios
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 12. Implement Fault-Tolerant Design
  - [ ] 12.1 Add error handling for unexpected failures
    - Catch unexpected errors in any stage
    - Attempt recovery or fail gracefully
    - _Requirements: 10.1, 10.2_
  
  - [ ] 12.2 Implement state isolation
    - Ensure no state leakage between calls
    - _Requirements: 10.4_
  
  - [ ] 12.3 Add resource limit handling
    - Raise `TimeoutError` if operation exceeds timeout
    - Raise `ResourceError` if memory limits exceeded
    - Handle deeply nested structures without stack overflow
    - _Requirements: 10.5, 10.6, 10.7_

- [ ] 13. Implement Extensible Architecture
  - [ ] 13.1 Design pipeline stages as separate, testable components
    - Each stage implements clear interface
    - _Requirements: 11.1_
  
  - [ ] 13.2 Implement dependency injection for stage components
    - _Requirements: 11.4_
  
  - [ ] 13.3 Document extension points
    - Add new repair strategies without modifying core code
    - Add new validation modes via configuration
    - _Requirements: 11.2, 11.3_

- [ ] 14. Implement Error Handling and Reporting
  - [ ] 14.1 Enhance error messages with full context
    - Include original input, failed stage, specific error details
    - List all errors with context when multiple errors occur
    - Include repair history when repair attempted
    - Distinguish user errors vs system errors
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ] 14.2 Implement structured logging for observability
    - Emit structured logs for each pipeline event
    - _Requirements: 13.5_

- [ ] 15. Implement Parser and Serializer Requirements
  - [ ] 15.1 Implement `PrettyPrinter` class
    - Format Pydantic models back into valid JSON
    - _Requirements: 14.2_
  
  - [ ] 15.2 Implement round-trip property
    - Parse → Serialize → Parse produces equivalent results
    - _Requirements: 14.3_
  
  - [ ] 15.3 Support custom encoders/decoders
    - _Requirements: 14.4_
  
  - [ ] 15.4 Handle all standard JSON types
    - null, boolean, number, string, array, object
    - _Requirements: 14.5_

- [ ] 16. Write comprehensive tests
  - [ ] 16.1 Write unit tests for each pipeline stage
    - Cover normal and edge cases
    - _Requirements: 12.1_
  
  - [ ] 16.2 Write integration tests for end-to-end scenarios
    - _Requirements: 12.2_
  
  - [ ] 16.3 Write property-based tests for correctness properties
    - Test all 21 properties defined in requirements
    - _Requirements: 12.3_
  
  - [ ] 16.4 Achieve 90% code coverage
    - _Requirements: 12.4_
  
  - [ ] 16.5 Write example tests for public API
    - Demonstrate real-world usage
    - _Requirements: 12.5_

- [ ] 17. Set up CI/CD and documentation
  - [ ] 17.1 Create GitHub Actions workflow
    - Run tests on push/PR
    - Run linters (black, flake8, mypy)
    - Publish to PyPI on release tag
    - _Requirements: 12_
  
  - [ ] 17.2 Create pyproject.toml with all metadata
    - Project name, version, description, authors
    - Dependencies and optional dependencies
    - Build system configuration
    - _Requirements: 15_
  
  - [ ] 17.3 Create README.md
    - Project overview and features
    - Installation instructions
    - Usage examples
    - API reference
    - Contribution guidelines
    - License information
    - Badges for build status and version
  
  - [ ] 17.4 Create LICENSE file
    - MIT License text
    - _Requirements: 15_
  
  - [ ] 17.5 Create .gitignore file
    - Ignore Python artifacts, virtual environments, IDE files
    - _Requirements: 15_

- [ ] 18. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The implementation follows the pipeline: Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring
- All stages must be testable and extensible per requirements