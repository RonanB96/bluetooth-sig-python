"""Characteristic User Description Descriptor implementation."""

from __future__ import annotations

import msgspec

from .base import BaseDescriptor


class CharacteristicUserDescriptionData(msgspec.Struct, frozen=True, kw_only=True):
    """Characteristic User Description descriptor data."""

    description: str


class CharacteristicUserDescriptionDescriptor(BaseDescriptor):
    """Characteristic User Description Descriptor (0x2901).

    Contains a user-readable description of the characteristic.
    UTF-8 encoded string describing the characteristic's purpose.
    """

    def _has_structured_data(self) -> bool:
        return True

    def _get_data_format(self) -> str:
        return "utf8"

    def _parse_descriptor_value(self, data: bytes) -> CharacteristicUserDescriptionData:
        """Parse Characteristic User Description value.

        Args:
            data: Raw UTF-8 bytes

        Returns:
            CharacteristicUserDescriptionData with the description string
        """
        try:
            description = data.decode("utf-8")
            return CharacteristicUserDescriptionData(description=description)
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 data in Characteristic User Description: {e}") from e

    def get_description(self, data: bytes) -> str:
        """Get the user description string."""
        parsed = self._parse_descriptor_value(data)
        return parsed.description
