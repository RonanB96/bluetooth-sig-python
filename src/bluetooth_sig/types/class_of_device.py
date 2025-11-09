"""Class of Device data structures for Classic Bluetooth.

This module provides data structures for representing and decoding the 24-bit
Class of Device (CoD) field used in Classic Bluetooth for device classification.
"""

from __future__ import annotations

import msgspec


class ServiceClassInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Service class information from Class of Device field.

    Attributes:
        bit_position: Bit position in the CoD field (13-23)
        name: Human-readable service class name
    """

    bit_position: int
    name: str


class MajorDeviceClassInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Major device class information from Class of Device field.

    Attributes:
        value: Major device class value (0-31, 5 bits)
        name: Human-readable major device class name
    """

    value: int
    name: str


class MinorDeviceClassInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Minor device class information from Class of Device field.

    Attributes:
        value: Minor device class value (0-63, 6 bits)
        name: Human-readable minor device class name
        major_class: Major device class this minor class belongs to
    """

    value: int
    name: str
    major_class: int


class ClassOfDeviceInfo(msgspec.Struct, frozen=True, kw_only=True):
    """Decoded Class of Device information.

    Represents the decoded classification information from a 24-bit CoD field,
    including major/minor device classes and service classes.

    Attributes:
        major_class: Major device class name (e.g., "Computer", "Phone")
        minor_class: Minor device class name (e.g., "Laptop", "Smartphone"), or None
        service_classes: List of service class names (e.g., ["Networking", "Audio"])
        raw_value: Original 24-bit CoD value
    """

    major_class: str
    minor_class: str | None
    service_classes: list[str]
    raw_value: int

    @property
    def full_description(self) -> str:
        """Get full device description combining major, minor, and services.

        Returns:
            Human-readable description like "Computer: Laptop (Networking, Audio)"

        Examples:
            >>> info = ClassOfDeviceInfo(
            ...     major_class="Computer", minor_class="Laptop", service_classes=["Networking"], raw_value=0x02010C
            ... )
            >>> info.full_description
            'Computer: Laptop (Networking)'
        """
        desc = self.major_class
        if self.minor_class:
            desc += f": {self.minor_class}"
        if self.service_classes:
            desc += f" ({', '.join(self.service_classes)})"
        return desc
