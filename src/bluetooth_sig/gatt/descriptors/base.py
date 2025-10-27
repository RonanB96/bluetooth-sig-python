"""Base class for GATT descriptors."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from ...types import DescriptorData, DescriptorInfo
from ...types.uuid import BluetoothUUID
from ..exceptions import UUIDResolutionError
from ..resolver import NameVariantGenerator
from ..uuid_registry import uuid_registry

logger = logging.getLogger(__name__)


class BaseDescriptor(ABC):
    """Base class for all GATT descriptors.

    Automatically resolves UUID and name from Bluetooth SIG specifications.
    Provides parsing capabilities for descriptor values.
    """

    # Class attributes for explicit overrides
    _descriptor_name: str | None = None
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
                return DescriptorInfo(
                    uuid=info.uuid,
                    name=info.name,
                    description=info.summary or "",
                    has_structured_data=self._has_structured_data(),
                    data_format=self._get_data_format(),
                )

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


class RangeDescriptorMixin:
    """Mixin for descriptors that provide min/max value validation."""

    def get_min_value(self, data: bytes) -> int | float:
        """Get the minimum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Minimum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)  # type: ignore[attr-defined]
        return parsed.min_value  # type: ignore[no-any-return]

    def get_max_value(self, data: bytes) -> int | float:
        """Get the maximum valid value.

        Args:
            data: Raw descriptor data

        Returns:
            Maximum valid value for the characteristic
        """
        parsed = self._parse_descriptor_value(data)  # type: ignore[attr-defined]
        return parsed.max_value  # type: ignore[no-any-return]

    def is_value_in_range(self, data: bytes, value: int | float) -> bool:
        """Check if a value is within the valid range.

        Args:
            data: Raw descriptor data
            value: Value to check

        Returns:
            True if value is within [min_value, max_value] range
        """
        parsed = self._parse_descriptor_value(data)  # type: ignore[attr-defined]
        min_val = parsed.min_value
        max_val = parsed.max_value
        return bool(min_val <= value <= max_val)
