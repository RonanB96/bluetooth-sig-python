"""Base class for GATT descriptors."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Protocol

from ...types import DescriptorData, DescriptorInfo
from ...types.uuid import BluetoothUUID
from ..exceptions import UUIDResolutionError
from ..resolver import NameVariantGenerator
from ..uuid_registry import uuid_registry

logger = logging.getLogger(__name__)


class BaseDescriptor(ABC):
    """Base class for all GATT descriptors.

    Automatically resolves UUID and name from Bluetooth SIG registry.
    Provides parsing capabilities for descriptor values.

    Attributes:
        _descriptor_name: Optional explicit descriptor name for registry lookup.
        _writable: Whether this descriptor type supports write operations.
            Override to True in writable descriptor subclasses (CCCD, SCCD).

    Note:
        Most descriptors are read-only per Bluetooth SIG specification.
        Some like CCCD (0x2902) and SCCD (0x2903) support writes.
    """

    # Class attributes for explicit overrides
    _descriptor_name: str | None = None
    _writable: bool = False  # Override to True in writable descriptor subclasses
    _info: DescriptorInfo  # Populated in __post_init__

    def __init__(self) -> None:
        """Initialize descriptor with resolved information."""
        self.__post_init__()

    def __post_init__(self) -> None:
        """Initialize descriptor with resolved information."""
        self._info = self._resolve_info()

    def _resolve_info(self) -> DescriptorInfo:
        """Resolve descriptor information from registry using sophisticated name resolution."""
        # Generate name variants using the same logic as characteristics
        descriptor_name = getattr(self.__class__, "_descriptor_name", None)
        variants = NameVariantGenerator.generate_descriptor_variants(self.__class__.__name__, descriptor_name)

        # Try each variant
        for variant in variants:
            info = uuid_registry.get_descriptor_info(variant)
            if info:
                return info

        # No resolution found
        raise UUIDResolutionError(self.__class__.__name__, [self.__class__.__name__])

    def _has_structured_data(self) -> bool:
        """Check if this descriptor contains structured data."""
        return False

    def _get_data_format(self) -> str:
        """Get the data format for this descriptor."""
        return "bytes"

    @property
    def uuid(self) -> BluetoothUUID:
        """Get the descriptor UUID."""
        return self._info.uuid

    @property
    def name(self) -> str:
        """Get the descriptor name."""
        return self._info.name

    @property
    def info(self) -> DescriptorInfo:
        """Get the descriptor information."""
        return self._info

    def parse_value(self, data: bytes) -> DescriptorData:
        """Parse raw descriptor data into structured format.

        Args:
            data: Raw bytes from the descriptor read

        Returns:
            DescriptorData object with parsed value and metadata
        """
        try:
            parsed_value = self._parse_descriptor_value(data)
            return DescriptorData(
                info=self._info,
                value=parsed_value,
                raw_data=data,
                parse_success=True,
                error_message="",
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to parse descriptor %s: %s", self.name, e)
            return DescriptorData(
                info=self._info,
                value=None,
                raw_data=data,
                parse_success=False,
                error_message=str(e),
            )

    def is_writable(self) -> bool:
        """Check if descriptor type supports write operations.

        Returns:
            True if descriptor type supports writes, False otherwise.

        Note:
            Only checks descriptor type, not runtime permissions or security.
            Example writable descriptors (CCCD, SCCD) override `_writable = True`.
        """
        return self._writable

    @abstractmethod
    def _parse_descriptor_value(self, data: bytes) -> Any:  # noqa: ANN401  # Descriptors can return various types
        """Parse the specific descriptor value format.

        Args:
            data: Raw bytes from the descriptor

        Returns:
            Parsed value in appropriate format

        Raises:
            NotImplementedError: If subclass doesn't implement parsing
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement _parse_descriptor_value()")


class _RangeValue(Protocol):
    """Protocol for parsed descriptor values with min/max fields."""

    @property
    def min_value(self) -> int | float: ...

    @property
    def max_value(self) -> int | float: ...


class RangeDescriptorMixin(ABC):
    """Mixin for descriptors that provide min/max value validation.

    Concrete subclasses must also inherit from BaseDescriptor (which provides
    ``_parse_descriptor_value``).  The abstract stub below declares the
    dependency so that mypy recognises it without ``type: ignore[attr-defined]``.
    """

    @abstractmethod
    def _parse_descriptor_value(self, data: bytes) -> _RangeValue:
        """Parse the descriptor value — implemented by BaseDescriptor."""

    def get_min_value(self, data: bytes) -> int | float:
        """Get the minimum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Minimum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)
        return parsed.min_value

    def get_max_value(self, data: bytes) -> int | float:
        """Get the maximum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Maximum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)
        return parsed.max_value

    def is_value_in_range(self, data: bytes, value: float) -> bool:
        """Check if a value is within the valid range.

        Args:
            data: Raw descriptor data
            value: Value to check

        Returns:
            True if value is within [min_value, max_value] range
        """
        parsed = self._parse_descriptor_value(data)
        min_val = parsed.min_value
        max_val = parsed.max_value
        return bool(min_val <= value <= max_val)
