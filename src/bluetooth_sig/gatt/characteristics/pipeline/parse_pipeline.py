"""Parse pipeline for GATT characteristic values.

Orchestrates the multi-stage parsing process: length validation → raw integer
extraction → special value detection → value decoding → range/type validation.
"""

from __future__ import annotations

import os
from typing import Any, TypeVar

from ....types import ParseFieldError as FieldError
from ....types import SpecialValueResult
from ....types.data_types import ValidationAccumulator
from ...exceptions import (
    CharacteristicParseError,
    ParseFieldError,
    SpecialValueDetectedError,
)
from ..utils.extractors import get_extractor
from .validation import CharacteristicValidator

T = TypeVar("T")


class ParsePipeline:
    """Multi-stage parse pipeline for characteristic values.

    Stages:
        1. Length validation (pre-decode)
        2. Raw integer extraction (little-endian per Bluetooth spec)
        3. Special value detection (sentinel values like 0x8000)
        4. Value decoding (via template or subclass ``_decode_value``)
        5. Range validation (post-decode)
        6. Type validation

    Uses a back-reference to the owning characteristic for:
    - ``_decode_value()`` dispatch (Template Method pattern)
    - Metadata access (``name``, ``uuid``, ``_template``, ``_spec``)
    - Special value resolver
    """

    def __init__(self, char: Any, validator: CharacteristicValidator) -> None:  # noqa: ANN401
        """Initialise with back-reference to the owning characteristic.

        Args:
            char: BaseCharacteristic instance.
            validator: Shared validator instance.

        """
        self._char = char
        self._validator = validator

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(
        self,
        data: bytes | bytearray,
        ctx: Any | None = None,  # noqa: ANN401  # CharacteristicContext
        validate: bool = True,
    ) -> Any:  # noqa: ANN401  # Returns T (generic of owning char)
        """Execute the full parse pipeline.

        Args:
            data: Raw bytes from BLE read.
            ctx: Optional ``CharacteristicContext`` for dependency-aware parsing.
            validate: Whether to run validation stages.

        Returns:
            Parsed value of type T.

        Raises:
            SpecialValueDetectedError: If a sentinel value is detected.
            CharacteristicParseError: If parsing or validation fails.

        """
        char = self._char
        data_bytes = bytearray(data)
        enable_trace = self._is_trace_enabled()
        parse_trace: list[str] = ["Starting parse"] if enable_trace else []
        field_errors: list[FieldError] = []
        validation = ValidationAccumulator()
        raw_int: int | None = None

        try:
            self._perform_length_validation(data_bytes, enable_trace, parse_trace, validation, validate)
            raw_int, parsed_value = self._extract_and_check_special(data_bytes, enable_trace, parse_trace, ctx)
        except Exception as e:
            if enable_trace:
                parse_trace.append(f"Parse failed: {type(e).__name__}: {e}")
            raise CharacteristicParseError(
                message=str(e),
                name=char.name,
                uuid=char.uuid,
                raw_data=bytes(data),
                raw_int=raw_int,
                field_errors=field_errors,
                parse_trace=parse_trace,
                validation=validation,
            ) from e

        if isinstance(parsed_value, SpecialValueResult):
            if enable_trace:
                parse_trace.append(f"Detected special value: {parsed_value.meaning}")
            raise SpecialValueDetectedError(
                special_value=parsed_value,
                name=char.name,
                uuid=char.uuid,
                raw_data=bytes(data),
                raw_int=raw_int,
            )

        try:
            decoded_value = self._decode_and_validate(data_bytes, enable_trace, parse_trace, ctx, validation, validate)
        except Exception as e:
            if enable_trace:
                parse_trace.append(f"Parse failed: {type(e).__name__}: {e}")
            if isinstance(e, ParseFieldError):
                field_errors.append(
                    FieldError(
                        field=e.field,
                        reason=e.field_reason,
                        offset=e.offset,
                        raw_slice=bytes(e.data) if hasattr(e, "data") else None,
                    )
                )
            raise CharacteristicParseError(
                message=str(e),
                name=char.name,
                uuid=char.uuid,
                raw_data=bytes(data),
                raw_int=raw_int,
                field_errors=field_errors,
                parse_trace=parse_trace,
                validation=validation,
            ) from e

        if enable_trace:
            parse_trace.append("Parse completed successfully")

        return decoded_value

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------

    def _perform_length_validation(
        self,
        data_bytes: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
        validation: ValidationAccumulator,
        validate: bool,
    ) -> None:
        """Stage 1: validate data length before parsing."""
        if not validate:
            return
        if enable_trace:
            parse_trace.append(f"Validating data length (got {len(data_bytes)} bytes)")
        length_validation = self._validator.validate_length(data_bytes)
        validation.errors.extend(length_validation.errors)
        validation.warnings.extend(length_validation.warnings)
        if not length_validation.valid:
            raise ValueError("; ".join(length_validation.errors))

    def _extract_and_check_special(  # pylint: disable=unused-argument
        self,
        data_bytes: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
        ctx: Any | None,  # noqa: ANN401  # CharacteristicContext
    ) -> tuple[int | None, int | SpecialValueResult | None]:
        """Stage 2+3: extract raw int and check for special values."""
        raw_int = self._extract_raw_int(data_bytes, enable_trace, parse_trace)

        parsed_value = None
        if raw_int is not None:
            if enable_trace:
                parse_trace.append("Checking for special values")
            parsed_value = self._check_special_value(raw_int)
            if enable_trace:
                if isinstance(parsed_value, SpecialValueResult):
                    parse_trace.append(f"Found special value: {parsed_value}")
                else:
                    parse_trace.append("Not a special value, proceeding with decode")

        return raw_int, parsed_value

    def _decode_and_validate(
        self,
        data_bytes: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
        ctx: Any | None,  # noqa: ANN401  # CharacteristicContext
        validation: ValidationAccumulator,
        validate: bool,
    ) -> Any:  # noqa: ANN401  # Returns T
        """Stage 4+5+6: decode value via template/subclass, then validate."""
        if enable_trace:
            parse_trace.append("Decoding value")
        decoded_value = self._char._decode_value(data_bytes, ctx, validate=validate)

        if validate:
            if enable_trace:
                parse_trace.append("Validating range")
            range_validation = self._validator.validate_range(decoded_value, ctx)
            validation.errors.extend(range_validation.errors)
            validation.warnings.extend(range_validation.warnings)
            if not range_validation.valid:
                raise ValueError("; ".join(range_validation.errors))
            if enable_trace:
                parse_trace.append("Validating type")
            type_validation = self._validator.validate_type(decoded_value)
            validation.errors.extend(type_validation.errors)
            validation.warnings.extend(type_validation.warnings)
            if not type_validation.valid:
                raise ValueError("; ".join(type_validation.errors))
        return decoded_value

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_raw_int(
        self,
        data: bytearray,
        enable_trace: bool,
        parse_trace: list[str],
    ) -> int | None:
        """Extract raw integer from bytes using template or YAML extractors."""
        char = self._char

        # Priority 1: Template extractor
        if char._template is not None and char._template.extractor is not None:
            if enable_trace:
                parse_trace.append("Extracting raw integer via template extractor")
            raw_int: int = char._template.extractor.extract(data, offset=0)
            if enable_trace:
                parse_trace.append(f"Extracted raw_int: {raw_int}")
            return raw_int

        # Priority 2: YAML data type extractor
        yaml_type = char.get_yaml_data_type()
        if yaml_type is not None:
            extractor = get_extractor(yaml_type)
            if extractor is not None:
                if enable_trace:
                    parse_trace.append(f"Extracting raw integer via YAML type '{yaml_type}'")
                raw_int = extractor.extract(data, offset=0)
                if enable_trace:
                    parse_trace.append(f"Extracted raw_int: {raw_int}")
                return raw_int

        # No extractor available
        if enable_trace:
            parse_trace.append("No extractor available for raw_int extraction")
        return None

    def _check_special_value(self, raw_value: int) -> int | SpecialValueResult:
        """Check if raw value is a special sentinel value."""
        res: SpecialValueResult | None = self._char._special_resolver.resolve(raw_value)
        if res is not None:
            return res
        return raw_value

    def _is_trace_enabled(self) -> bool:
        """Check if parse trace is enabled via environment variable or instance attribute."""
        env_value = os.getenv("BLUETOOTH_SIG_ENABLE_PARSE_TRACE", "").lower()
        if env_value in ("0", "false", "no"):
            return False
        return self._char._enable_parse_trace is not False
