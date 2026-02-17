"""Characteristic encoding, value creation, and data validation.

Provides encode_characteristic, create_value, validate_characteristic_data,
and type introspection for characteristic value types.
"""

from __future__ import annotations

import inspect
import logging
import struct
import typing
from typing import Any, TypeVar, overload

from ..gatt.characteristics import templates
from ..gatt.characteristics.base import BaseCharacteristic
from ..gatt.characteristics.registry import CharacteristicRegistry
from ..gatt.exceptions import (
    CharacteristicError,
    CharacteristicParseError,
)
from ..types import (
    ValidationResult,
)
from ..types.gatt_enums import ValueType
from ..types.uuid import BluetoothUUID
from .parser import CharacteristicParser

T = TypeVar("T")

logger = logging.getLogger(__name__)


class CharacteristicEncoder:
    """Handles characteristic encoding, value creation, and data validation.

    Takes a CharacteristicParser reference for validate_characteristic_data,
    which needs to attempt a parse to check data format validity.
    """

    def __init__(self, parser: CharacteristicParser) -> None:
        """Initialise with a parser reference for validation support.

        Args:
            parser: CharacteristicParser instance for data validation

        """
        self._parser = parser

    @overload
    def encode_characteristic(
        self,
        char: type[BaseCharacteristic[T]],
        value: T,
        validate: bool = ...,
    ) -> bytes: ...

    @overload
    def encode_characteristic(
        self,
        char: str,
        value: Any,  # noqa: ANN401  # Runtime UUID dispatch cannot be type-safe
        validate: bool = ...,
    ) -> bytes: ...

    def encode_characteristic(
        self,
        char: str | type[BaseCharacteristic[T]],
        value: T | Any,  # Runtime UUID dispatch cannot be type-safe
        validate: bool = True,
    ) -> bytes:
        r"""Encode a value for writing to a characteristic.

        Args:
            char: Characteristic class (type-safe) or UUID string (not type-safe).
            value: The value to encode. Type is checked when using characteristic class.
            validate: If True, validates the value before encoding (default: True)

        Returns:
            Encoded bytes ready to write to the characteristic

        Raises:
            ValueError: If UUID is invalid, characteristic not found, or value is invalid
            TypeError: If value type doesn't match characteristic's expected type
            CharacteristicEncodeError: If encoding fails

        """
        # Handle characteristic class input (type-safe path)
        if isinstance(char, type) and issubclass(char, BaseCharacteristic):
            char_instance = char()
            logger.debug("Encoding characteristic class=%s, value=%s", char.__name__, value)
            try:
                if validate:
                    encoded = char_instance.build_value(value)
                    logger.debug("Successfully encoded %s with validation", char_instance.name)
                else:
                    encoded = char_instance._encode_value(value)  # pylint: disable=protected-access
                    logger.debug("Successfully encoded %s without validation", char_instance.name)
                return bytes(encoded)
            except Exception:
                logger.exception("Encoding failed for %s", char_instance.name)
                raise

        # Handle string UUID input (not type-safe path)
        logger.debug("Encoding characteristic UUID=%s, value=%s", char, value)

        characteristic = CharacteristicRegistry.get_characteristic(char)
        if not characteristic:
            raise ValueError(f"No encoder available for characteristic UUID: {char}")

        logger.debug("Found encoder for UUID=%s: %s", char, type(characteristic).__name__)

        # Handle dict input - convert to proper type
        if isinstance(value, dict):
            value_type = self._get_characteristic_value_type_class(characteristic)
            if value_type and hasattr(value_type, "__init__") and not isinstance(value_type, str):
                try:
                    value = value_type(**value)
                    logger.debug("Converted dict to %s", value_type.__name__)
                except (TypeError, ValueError) as e:
                    type_name = getattr(value_type, "__name__", str(value_type))
                    raise TypeError(f"Failed to convert dict to {type_name} for characteristic {char}: {e}") from e

        # Encode using build_value (with validation) or encode_value (without)
        try:
            if validate:
                encoded = characteristic.build_value(value)
                logger.debug("Successfully encoded %s with validation", characteristic.name)
            else:
                encoded = characteristic._encode_value(value)  # pylint: disable=protected-access
                logger.debug("Successfully encoded %s without validation", characteristic.name)
            return bytes(encoded)
        except Exception:
            logger.exception("Encoding failed for %s", characteristic.name)
            raise

    def _get_characteristic_value_type_class(  # pylint: disable=too-many-return-statements,too-many-branches
        self, characteristic: BaseCharacteristic[Any]
    ) -> type[Any] | None:
        """Get the Python type class that a characteristic expects.

        Args:
            characteristic: The characteristic instance

        Returns:
            The type class, or None if it can't be determined

        """
        # Try to infer from decode_value return type annotation
        if hasattr(characteristic, "_decode_value"):
            try:
                module = inspect.getmodule(characteristic.__class__)
                globalns = getattr(module, "__dict__", {}) if module else {}
                type_hints = typing.get_type_hints(characteristic._decode_value, globalns=globalns)  # pylint: disable=protected-access
                return_type = type_hints.get("return")
                if return_type and return_type is not type(None):
                    return return_type  # type: ignore[no-any-return]
            except (TypeError, AttributeError, NameError):
                return_type = inspect.signature(characteristic._decode_value).return_annotation  # pylint: disable=protected-access
                sig = inspect.signature(characteristic._decode_value)  # pylint: disable=protected-access
                return_annotation = sig.return_annotation
                if (
                    return_annotation
                    and return_annotation != inspect.Parameter.empty
                    and not isinstance(return_annotation, str)
                ):
                    return return_annotation  # type: ignore[no-any-return]

        # Try to get from _manual_value_type attribute
        if hasattr(characteristic, "_manual_value_type"):
            manual_type = characteristic._manual_value_type  # pylint: disable=protected-access
            if manual_type and isinstance(manual_type, str) and hasattr(templates, manual_type):
                return getattr(templates, manual_type)  # type: ignore[no-any-return]

        # Try to get from template
        if hasattr(characteristic, "_template") and characteristic._template:  # pylint: disable=protected-access
            template = characteristic._template  # pylint: disable=protected-access
            if hasattr(template, "__orig_class__"):
                args = typing.get_args(template.__orig_class__)
                if args:
                    return args[0]  # type: ignore[no-any-return]

        # For simple types, check info.value_type
        info = characteristic.info
        if info.value_type == ValueType.INT:
            return int
        if info.value_type == ValueType.FLOAT:
            return float
        if info.value_type == ValueType.STRING:
            return str
        if info.value_type == ValueType.BOOL:
            return bool
        if info.value_type == ValueType.BYTES:
            return bytes

        return None

    def validate_characteristic_data(self, uuid: str, data: bytes) -> ValidationResult:
        """Validate characteristic data format against SIG specifications.

        Args:
            uuid: The characteristic UUID
            data: Raw data bytes to validate

        Returns:
            ValidationResult with validation details

        """
        try:
            self._parser.parse_characteristic(uuid, data)
            try:
                bt_uuid = BluetoothUUID(uuid)
                char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
                expected = char_class.expected_length if char_class else None
            except (ValueError, AttributeError):
                expected = None
            return ValidationResult(
                is_valid=True,
                actual_length=len(data),
                expected_length=expected,
                error_message="",
            )
        except (CharacteristicParseError, ValueError, TypeError, struct.error, CharacteristicError) as e:
            try:
                bt_uuid = BluetoothUUID(uuid)
                char_class = CharacteristicRegistry.get_characteristic_class_by_uuid(bt_uuid)
                expected = char_class.expected_length if char_class else None
            except (ValueError, AttributeError):
                expected = None
            return ValidationResult(
                is_valid=False,
                actual_length=len(data),
                expected_length=expected,
                error_message=str(e),
            )

    def create_value(self, uuid: str, **kwargs: Any) -> Any:  # noqa: ANN401
        """Create a properly typed value instance for a characteristic.

        Args:
            uuid: The characteristic UUID
            **kwargs: Field values for the characteristic's type

        Returns:
            Properly typed value instance

        Raises:
            ValueError: If UUID is invalid or characteristic not found
            TypeError: If kwargs don't match the characteristic's expected fields

        """
        characteristic = CharacteristicRegistry.get_characteristic(uuid)
        if not characteristic:
            raise ValueError(f"No characteristic found for UUID: {uuid}")

        value_type = self._get_characteristic_value_type_class(characteristic)

        if not value_type:
            if len(kwargs) == 1:
                return next(iter(kwargs.values()))
            raise ValueError(
                f"Cannot determine value type for characteristic {uuid}. "
                "Try passing a dict to encode_characteristic() instead."
            )

        # Handle simple primitive types
        if value_type in (int, float, str, bool, bytes):
            if len(kwargs) == 1:
                value = next(iter(kwargs.values()))
                if not isinstance(value, value_type):
                    type_name = getattr(value_type, "__name__", str(value_type))
                    raise TypeError(f"Expected {type_name}, got {type(value).__name__}")
                return value
            type_name = getattr(value_type, "__name__", str(value_type))
            raise TypeError(f"Simple type {type_name} expects a single value")

        # Construct complex type from kwargs
        try:
            return value_type(**kwargs)
        except (TypeError, ValueError) as e:
            type_name = getattr(value_type, "__name__", str(value_type))
            raise TypeError(f"Failed to create {type_name} for characteristic {uuid}: {e}") from e
