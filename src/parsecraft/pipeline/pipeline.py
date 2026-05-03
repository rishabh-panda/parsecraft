"""Pipeline orchestrator for parsecraft."""

import logging
import time
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from parsecraft.core.config import ParserConfig
from parsecraft.core.result import ParseError, ParseResult, RepairAttempt
from parsecraft.extraction.extractor import Extractor
from parsecraft.normalization.normalizer import Normalizer
from parsecraft.parsing.parser import Parser
from parsecraft.repair.repairer import Repairer
from parsecraft.scoring.scorer import Scorer
from parsecraft.validation.validator import Validator


class Pipeline:
    """Orchestrates all pipeline stages.

    Executes stages in order:
    Extraction → Normalization → Parsing → Repair → Validation → Retry → Scoring

    Attributes:
        config: ParserConfig for this pipeline
    """

    def __init__(self, config: ParserConfig):
        """Initialize the Pipeline.

        Args:
            config: ParserConfig for this pipeline
        """
        self.config = config
        self.extractor = Extractor()
        self.normalizer = Normalizer()
        self.parser = Parser()
        self.repairer = Repairer(strategies=config.repair_strategies)
        self.validator = Validator(strict_mode=True)
        self.scorer = Scorer()
        self.logger = logging.getLogger(__name__)

    def execute(
        self,
        text: str,
        schema: Optional[Union[Type[BaseModel], Dict]] = None,
        config: Optional[ParserConfig] = None
    ) -> ParseResult:
        """Execute the full pipeline.

        Args:
            text: Raw LLM output
            schema: Pydantic model or JSON Schema for validation
            config: Optional config overrides

        Returns:
            ParseResult with parsed data and reliability score

        Raises:
            ParseError: If pipeline fails after all retries
        """
        config = config or self.config
        stage_results: Dict[str, Any] = {}
        repair_history: List[RepairAttempt] = []
        validation_errors: List[Dict] = []

        # Retry loop
        for attempt in range(config.max_retries + 1):
            try:
                result = self._execute_once(text, schema, stage_results, repair_history, validation_errors)
                return result
            except ParseError as e:
                if attempt < config.max_retries:
                    # Retry
                    self.logger.info(f"Retry {attempt + 1}/{config.max_retries}")
                    continue
                else:
                    # All retries exhausted
                    raise ParseError(
                        f"Pipeline failed after {config.max_retries + 1} attempts",
                        text,
                        e.failed_stage,
                        e.specific_error,
                        e.result,
                        repair_history,
                        validation_errors
                    )

        # Should not reach here
        raise ParseError(
            "Pipeline failed unexpectedly",
            text,
            "Unknown",
            RuntimeError("Pipeline failed unexpectedly"),
            None,
            repair_history,
            validation_errors
        )

    def _execute_once(
        self,
        text: str,
        schema: Optional[Union[Type[BaseModel], Dict]],
        stage_results: Dict[str, Any],
        repair_history: List[RepairAttempt],
        validation_errors: List[Dict]
    ) -> ParseResult:
        """Execute the pipeline once without retry.

        Args:
            text: Raw LLM output
            schema: Pydantic model or JSON Schema
            stage_results: Dict to store stage results
            repair_history: List to store repair attempts
            validation_errors: List to store validation errors

        Returns:
            ParseResult

        Raises:
            ParseError: If any stage fails
        """
        start_time = time.time()

        # Stage 1: Extraction
        try:
            extracted = self.extractor.extract(text)
            stage_results['extraction'] = {'success': True, 'output': extracted}
        except Exception as e:
            stage_results['extraction'] = {'success': False, 'error': str(e)}
            raise ParseError(
                "Extraction failed",
                text,
                "Extraction",
                e,
                None,
                repair_history,
                validation_errors
            )

        # Stage 2: Normalization
        try:
            normalized = self.normalizer.normalize(extracted)
            stage_results['normalization'] = {'success': True, 'output': normalized}
        except Exception as e:
            stage_results['normalization'] = {'success': False, 'error': str(e)}
            raise ParseError(
                "Normalization failed",
                text,
                "Normalization",
                e,
                None,
                repair_history,
                validation_errors
            )

        # Stage 3: Parsing
        try:
            parsed = self.parser.parse(normalized, schema)
            stage_results['parsing'] = {'success': True, 'output': parsed}
        except Exception as e:
            stage_results['parsing'] = {'success': False, 'error': str(e)}

            # Try repair if enabled
            if self.config.repair_enabled:
                try:
                    repaired = self.repairer.repair(normalized, e)
                    repair_history.append(RepairAttempt(
                        strategy='repair',
                        success=True,
                        original_error=str(e),
                        repaired_text=repaired
                    ))
                    parsed = self.parser.parse(repaired, schema)
                    stage_results['repair'] = {'success': True, 'output': repaired}
                    stage_results['parsing'] = {'success': True, 'output': parsed}
                except Exception as repair_error:
                    repair_history.append(RepairAttempt(
                        strategy='repair',
                        success=False,
                        original_error=str(e),
                        repaired_text=None
                    ))
                    stage_results['repair'] = {'success': False, 'error': str(repair_error)}
                    raise ParseError(
                        "Parsing failed and repair unsuccessful",
                        text,
                        "Parsing",
                        e,
                        None,
                        repair_history,
                        validation_errors
                    )
            else:
                raise ParseError(
                    "Parsing failed",
                    text,
                    "Parsing",
                    e,
                    None,
                    repair_history,
                    validation_errors
                )

        # Stage 4: Validation
        try:
            if schema:
                v_errors = self.validator.validate(parsed, schema)
                if v_errors:
                    validation_errors.extend([e.to_dict() for e in v_errors])
                    stage_results['validation'] = {
                        'success': True,
                        'warnings': len(v_errors),
                        'errors': [e.to_dict() for e in v_errors]
                    }
                else:
                    stage_results['validation'] = {'success': True, 'warnings': 0}
            else:
                stage_results['validation'] = {'success': True, 'warnings': 0}
        except Exception as e:
            stage_results['validation'] = {'success': False, 'error': str(e)}
            raise ParseError(
                "Validation failed",
                text,
                "Validation",
                e,
                None,
                repair_history,
                validation_errors
            )

        # Stage 5: Scoring
        try:
            score = self.scorer.score(
                parsed=parsed,
                repair_history=repair_history,
                validation_warnings=len(validation_errors)
            )
            stage_results['scoring'] = {'success': True, 'score': score}
        except Exception as e:
            stage_results['scoring'] = {'success': False, 'error': str(e)}
            score = 0.5  # Default score on scoring failure

        total_time = time.time() - start_time
        stage_results['total_time'] = total_time

        return ParseResult(
            parsed_data=parsed,
            reliability_score=score,
            repair_history=repair_history,
            validation_errors=validation_errors,
            stage_results=stage_results
        )