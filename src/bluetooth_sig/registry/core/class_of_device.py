"""Registry for Class of Device decoding.

This module provides a registry for decoding 24-bit Class of Device (CoD)
values from Classic Bluetooth into human-readable device classifications
including major/minor device classes and service classes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import msgspec

from bluetooth_sig.registry.base import BaseRegistry
from bluetooth_sig.registry.utils import find_bluetooth_sig_path
from bluetooth_sig.types.class_of_device import (
    ClassOfDeviceInfo,
    MajorDeviceClassInfo,
    MinorDeviceClassInfo,
    ServiceClassInfo,
)


class ClassOfDeviceRegistry(BaseRegistry[ClassOfDeviceInfo]):
    """Registry for Class of Device decoding with lazy loading.

    This registry loads Class of Device mappings from the Bluetooth SIG
    assigned_numbers YAML file and provides methods to decode 24-bit CoD
    values into human-readable device classification information.

    The registry uses lazy loading - the YAML file is only parsed on the first
    decode call. This improves startup time and reduces memory usage when the
    registry is not needed.

    CoD Structure (24 bits):
        Bits 23-13: Service Class (11 bits, bit mask)
        Bits 12-8:  Major Device Class (5 bits)
        Bits 7-2:   Minor Device Class (6 bits)
        Bits 1-0:   Format Type (always 0b00)

    Thread Safety:
        This registry is thread-safe. Multiple threads can safely call
        decode_class_of_device() concurrently.

    Example:
        >>> registry = ClassOfDeviceRegistry()
        >>> info = registry.decode_class_of_device(0x02010C)
        >>> print(info.full_description)  # "Computer: Laptop (Networking)"
        >>> print(info.major_class)  # "Computer"
        >>> print(info.minor_class)  # "Laptop"
        >>> print(info.service_classes)  # ["Networking"]
    """

    def __init__(self) -> None:
        """Initialize the registry with lazy loading."""
        super().__init__()
        self._service_classes: dict[int, ServiceClassInfo] = {}
        self._major_classes: dict[int, MajorDeviceClassInfo] = {}
        self._minor_classes: dict[tuple[int, int], MinorDeviceClassInfo] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Lazy load Class of Device data from YAML on first access.

        This method is thread-safe and ensures the YAML is only loaded once,
        even when called concurrently from multiple threads.
        """

        def _load() -> None:
            """Perform the actual loading."""
            # Get path to uuids/ directory
            uuids_path = find_bluetooth_sig_path()
            if not uuids_path:
                self._loaded = True
                return

            # CoD values are in core/ directory (sibling of uuids/)
            assigned_numbers_path = uuids_path.parent
            yaml_path = assigned_numbers_path / "core" / "class_of_device.yaml"
            if not yaml_path.exists():
                self._loaded = True
                return

            self._load_yaml(yaml_path)
            self._loaded = True

        self._lazy_load(self._loaded, _load)

    def _load_yaml(self, yaml_path: Path) -> None:
        """Load and parse the class_of_device.yaml file.

        Args:
            yaml_path: Path to the class_of_device.yaml file
        """
        with yaml_path.open("r", encoding="utf-8") as f:
            data = msgspec.yaml.decode(f.read())

        if not data or not isinstance(data, dict):
            return

        self._load_service_classes(data)
        self._load_device_classes(data)

    def _load_service_classes(self, data: dict[str, Any]) -> None:
        """Load service classes from YAML data.

        Args:
            data: Parsed YAML data dictionary
        """
        cod_services = data.get("cod_services")
        if not isinstance(cod_services, list):
            return

        for item in cod_services:
            if not isinstance(item, dict):
                continue

            bit_pos = item.get("bit")
            name = item.get("name")
            if bit_pos is not None and name:
                self._service_classes[bit_pos] = ServiceClassInfo(
                    bit_position=bit_pos,
                    name=name,
                )

    def _load_device_classes(self, data: dict[str, Any]) -> None:
        """Load major and minor device classes from YAML data.

        Args:
            data: Parsed YAML data dictionary
        """
        cod_device_class = data.get("cod_device_class")
        if not isinstance(cod_device_class, list):
            return

        for item in cod_device_class:
            if not isinstance(item, dict):
                continue

            major_val = item.get("major")
            major_name = item.get("name")
            if major_val is not None and major_name:
                self._major_classes[major_val] = MajorDeviceClassInfo(
                    value=major_val,
                    name=major_name,
                )
                self._load_minor_classes(major_val, item)

    def _load_minor_classes(self, major_val: int, major_item: dict[str, Any]) -> None:
        """Load minor classes for a specific major device class.

        Args:
            major_val: Major device class value
            major_item: Dictionary containing major class data including minor classes
        """
        minor_list = major_item.get("minor")
        if not isinstance(minor_list, list):
            return

        for minor_item in minor_list:
            if not isinstance(minor_item, dict):
                continue

            minor_val = minor_item.get("value")
            minor_name = minor_item.get("name")
            if minor_val is not None and minor_name:
                self._minor_classes[(major_val, minor_val)] = MinorDeviceClassInfo(
                    value=minor_val,
                    name=minor_name,
                    major_class=major_val,
                )

    def decode_class_of_device(self, cod: int) -> ClassOfDeviceInfo:
        """Decode 24-bit Class of Device value.

        Extracts and decodes the major/minor device classes and service classes
        from a 24-bit CoD value. Lazy loads the registry data on first call.

        Args:
            cod: 24-bit Class of Device value from advertising data

        Returns:
            ClassOfDeviceInfo with decoded device classification

        Examples:
            >>> registry = ClassOfDeviceRegistry()
            >>> # Computer (major=1), Laptop (minor=3), Networking service (bit 17)
            >>> info = registry.decode_class_of_device(0x02010C)
            >>> info.major_class
            'Computer (desktop, notebook, PDA, organizer, ...)'
            >>> info.minor_class
            'Laptop'
            >>> info.service_classes
            ['Networking (LAN, Ad hoc, ...)']
        """
        self._ensure_loaded()

        # Extract fields using bit masks
        service_class_bits = (cod >> 13) & 0x7FF  # Bits 23-13 (11 bits)
        major_class = (cod >> 8) & 0x1F  # Bits 12-8 (5 bits)
        minor_class = (cod >> 2) & 0x3F  # Bits 7-2 (6 bits)

        # Decode service classes (bit mask - multiple bits can be set)
        service_classes = []
        for bit_pos in range(11):
            if service_class_bits & (1 << bit_pos):
                # Map bit position 0-10 to actual bit positions 13-23
                actual_bit_pos = bit_pos + 13
                service_info = self._service_classes.get(actual_bit_pos)
                if service_info:
                    service_classes.append(service_info.name)

        # Decode major class
        major_info = self._major_classes.get(major_class)
        major_name = major_info.name if major_info else f"Unknown (0x{major_class:02X})"

        # Decode minor class
        minor_info = self._minor_classes.get((major_class, minor_class))
        minor_name = minor_info.name if minor_info else None

        return ClassOfDeviceInfo(
            major_class=major_name,
            minor_class=minor_name,
            service_classes=service_classes,
            raw_value=cod,
        )


# Module-level singleton instance
class_of_device_registry = ClassOfDeviceRegistry()
