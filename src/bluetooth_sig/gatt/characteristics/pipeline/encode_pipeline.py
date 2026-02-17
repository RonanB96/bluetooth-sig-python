"""Encode pipeline for GATT characteristic values.

Orchestrates the multi-stage encoding process: type validation → range
validation → value encoding → length validation.
"""

from __future__ import annotations

import os
from typing import Any

from ....types import SpecialValueResult
from ....types.data_types import ValidationAccumulator
from ...exceptions import CharacteristicEncodeError
from ..utils.extractors import get_extractor
from .validation import CharacteristicValidator


class EncodePipeline:
    """Multi-stage encode pipeline for characteristic values.

    Stages:
        1. Type validation
        2. Range validation (numeric types only)
        3. Value encoding (via template or subclass ``_encode_value``)
        4. Length validation (post-encode)

    Uses a back-reference to the owning characteristic for:
    - ``_encode_value()`` dispatch (Template Method pattern)
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

    def run(  # pylint: disable=too-many-branches
        self,
        data: Any,  # noqa: ANN401  # T | SpecialValueResult
        validate: bool = True,
    ) -> bytearray:
        """Execute the full encode pipeline.

        Args:
            data: Value to encode (type T) or ``SpecialValueResult``.
            validate: Enable validation (type, range, length checks).
                      Special values bypass validation.

        Returns:
            Encoded bytes ready for BLE write.

        Raises:
            CharacteristicEncodeError: If encoding or validation fails.

        """
        char = self._char
        enable_trace = self._is_trace_enabled()
        build_trace: list[str] = ["Starting build"] if enable_trace else []
        validation = ValidationAccumulator()

        # Special value encoding — bypass validation
        if isinstance(data, SpecialValueResult):
            if enable_trace:
                build_trace.append(f"Encoding special value: {data.meaning}")
            try:
                return self._pack_raw_int(data.raw_value)
            except Exception as e:
                raise CharacteristicEncodeError(
                    message=f"Failed to encode special value: {e}",
                    name=char.name,
                    uuid=char.uuid,
                    value=data,
                    validation=None,
                ) from e

        try:
            # Type validation
            if validate:
                if enable_trace:
                    build_trace.append("Validating type")
                type_validation = self._validator.validate_type(data)
                validation.errors.extend(type_validation.errors)
                validation.warnings.extend(type_validation.warnings)
                if not type_validation.valid:
                    raise TypeError("; ".join(type_validation.errors))  # noqa: TRY301

            # Range validation for numeric types
            if validate and isinstance(data, (int, float)):
                if enable_trace:
                    build_trace.append("Validating range")
                range_validation = self._validator.validate_range(data, ctx=None)
                validation.errors.extend(range_validation.errors)
                validation.warnings.extend(range_validation.warnings)
                if not range_validation.valid:
                    raise ValueError("; ".join(range_validation.errors))  # noqa: TRY301

            # Encode
            if enable_trace:
                build_trace.append("Encoding value")
            encoded: bytearray = char._encode_value(data)

            # Length validation
            if validate:
                if enable_trace:
                    build_trace.append("Validating encoded length")
                length_validation = self._validator.validate_length(encoded)
                validation.errors.extend(length_validation.errors)
                validation.warnings.extend(length_validation.warnings)
                if not length_validation.valid:
                    raise ValueError("; ".join(length_validation.errors))  # noqa: TRY301

            if enable_trace:
                build_trace.append("Build completed successfully")

        except Exception as e:
            if enable_trace:
                build_trace.append(f"Build failed: {type(e).__name__}: {e}")

            raise CharacteristicEncodeError(
                message=str(e),
                name=char.name,
                uuid=char.uuid,
                value=data,
                validation=validation,
            ) from e
        else:
            return encoded

    # ------------------------------------------------------------------
    # Special value encoding helpers
    # ------------------------------------------------------------------

    def encode_special(self, value_type: Any) -> bytearray:  # noqa: ANN401  # SpecialValueType
        """Encode a special value type to bytes (reverse lookup).

        Args:
            value_type: ``SpecialValueType`` enum member.

        Returns:
            Encoded bytes for the special value.

        Raises:
            ValueError: If no raw value of that type is defined.

        """
        raw = self._char._special_resolver.get_raw_for_type(value_type)
        if raw is None:
            raise ValueError(f"No special value of type {value_type.name} defined for this characteristic")
        return self._pack_raw_int(raw)

    def encode_special_by_meaning(self, meaning: str) -> bytearray:
        """Encode a special value by a partial meaning string match.

        Args:
            meaning: Partial meaning string to match.

        Returns:
            Encoded bytes for the matching special value.

        Raises:
            ValueError: If no matching special value is found.

        """
        raw = self._char._special_resolver.get_raw_for_meaning(meaning)
        if raw is None:
            raise ValueError(f"No special value matching '{meaning}' defined for this characteristic")
        return self._pack_raw_int(raw)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _pack_raw_int(self, raw: int) -> bytearray:
        """Pack a raw integer to bytes using template extractor or YAML extractor."""
        char = self._char
        # Priority 1: template extractor
        if char._template is not None:
            extractor = getattr(char._template, "extractor", None)
            if extractor is not None:
                return bytearray(extractor.pack(raw))

        # Priority 2: YAML-derived extractor
        yaml_type = char.get_yaml_data_type()
        if yaml_type is not None:
            extractor = get_extractor(yaml_type)
            if extractor is not None:
                return bytearray(extractor.pack(raw))

        raise ValueError("No extractor available to pack raw integer for this characteristic")

    def _is_trace_enabled(self) -> bool:
        """Check if build trace is enabled."""
        env_value = os.getenv("BLUETOOTH_SIG_ENABLE_PARSE_TRACE", "").lower()
        if env_value in ("0", "false", "no"):
            return False
        return self._char._enable_parse_trace is not False
