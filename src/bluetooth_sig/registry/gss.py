"""GSS (GATT Service Specification) registry.

This module provides a registry for Bluetooth SIG GSS YAML files,
extracting characteristic specifications with field metadata including
units, resolutions, value ranges, and presence conditions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

import msgspec

from bluetooth_sig.registry.base import BaseGenericRegistry
from bluetooth_sig.registry.uuids.units import UnitsRegistry
from bluetooth_sig.types.gatt_enums import DataType
from bluetooth_sig.types.registry.gss_characteristic import (
    FieldSpec,
    GssCharacteristicSpec,
)


class GssRegistry(BaseGenericRegistry[GssCharacteristicSpec]):
    """Registry for GSS (GATT Service Specification) characteristic definitions.

    Parses Bluetooth SIG GSS YAML files and extracts typed characteristic
    specifications with full field metadata. Implements singleton pattern
    with thread-safe lazy loading.

    Example:
        registry = GssRegistry.get_instance()
        spec = registry.get_spec("Battery Level")
        if spec:
            for field in spec.structure:
                print(f"{field.python_name}: {field.unit_id}")

    """

    _instance: GssRegistry | None = None

    def __init__(self) -> None:
        """Initialize the GSS registry."""
        super().__init__()
        self._specs: dict[str, GssCharacteristicSpec] = {}
        self._units_registry: UnitsRegistry | None = None

    @classmethod
    def get_instance(cls) -> GssRegistry:
        """Get the singleton instance of the GSS registry."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _get_units_registry(self) -> UnitsRegistry:
        """Get or lazily initialize the units registry.

        Returns:
            The UnitsRegistry singleton instance
        """
        if self._units_registry is None:
            # Cast needed because get_instance returns base class type
            self._units_registry = UnitsRegistry.get_instance()  # type: ignore[assignment]
        return self._units_registry  # type: ignore[return-value]

    def _load(self) -> None:
        """Load GSS specifications from YAML files."""
        gss_path = self._find_gss_path()
        if gss_path:
            for yaml_file in gss_path.glob("org.bluetooth.characteristic.*.yaml"):
                self._process_gss_file(yaml_file)
        self._loaded = True

    def _find_gss_path(self) -> Path | None:
        """Find the GSS specifications directory."""
        # Try project root location
        project_root = Path(__file__).parent.parent.parent.parent
        gss_path = project_root / "bluetooth_sig" / "gss"

        if gss_path.exists():
            return gss_path

        # Try package root location
        pkg_root = Path(__file__).parent.parent
        gss_path = pkg_root / "bluetooth_sig" / "gss"

        return gss_path if gss_path.exists() else None

    def _process_gss_file(self, yaml_file: Path) -> None:
        """Process a single GSS YAML file and store as typed GssCharacteristicSpec."""
        try:
            with yaml_file.open("r", encoding="utf-8") as f:
                data = msgspec.yaml.decode(f.read())

            if not data or "characteristic" not in data:
                return

            char_data = data["characteristic"]
            char_name = char_data.get("name")
            char_id = char_data.get("identifier")

            if not char_name or not char_id:
                return

            # Parse structure into typed FieldSpec list
            raw_structure = char_data.get("structure", [])
            typed_structure: list[FieldSpec] = []
            for raw_field in raw_structure:
                if isinstance(raw_field, dict):
                    typed_structure.append(
                        FieldSpec(
                            field=raw_field.get("field", ""),
                            type=raw_field.get("type", ""),
                            size=str(raw_field.get("size", "")),
                            description=raw_field.get("description", ""),
                        )
                    )

            # Create typed GssCharacteristicSpec
            gss_spec = GssCharacteristicSpec(
                identifier=char_id,
                name=char_name,
                description=char_data.get("description", ""),
                structure=typed_structure,
            )

            # Store by both ID and name for lookup flexibility
            if char_id:
                self._specs[char_id] = gss_spec
            if char_name:
                self._specs[char_name] = gss_spec

        except (msgspec.DecodeError, OSError, KeyError) as e:
            logging.warning("Failed to parse GSS YAML file %s: %s", yaml_file, e)

    def get_spec(self, identifier: str) -> GssCharacteristicSpec | None:
        """Get a GSS specification by name or ID.

        Args:
            identifier: Characteristic name or ID

        Returns:
            GssCharacteristicSpec if found, None otherwise
        """
        self._ensure_loaded()
        with self._lock:
            return self._specs.get(identifier)

    def get_all_specs(self) -> dict[str, GssCharacteristicSpec]:
        """Get all loaded GSS specifications.

        Returns:
            Dictionary of all specifications keyed by name and ID
        """
        self._ensure_loaded()
        with self._lock:
            return dict(self._specs)

    def extract_info_from_gss(self, char_data: dict[str, Any]) -> tuple[str | None, str | None]:
        """Extract unit and value_type from GSS characteristic structure.

        Args:
            char_data: Raw characteristic data from YAML

        Returns:
            Tuple of (unit_symbol, value_type) or (None, None) if not found
        """
        structure = char_data.get("structure", [])
        if not isinstance(structure, list) or not structure:
            return None, None

        typed_structure: list[dict[str, Any]] = []
        for raw_field in structure:
            if isinstance(raw_field, dict):
                typed_structure.append(cast(dict[str, Any], raw_field))

        if not typed_structure:
            return None, None

        unit = None
        value_type = None

        for field in typed_structure:
            field_dict: dict[str, Any] = field

            if not value_type and isinstance(field_dict.get("type"), str):
                yaml_type_value = cast(str, field_dict["type"])
                value_type = self._convert_yaml_type_to_python_type(yaml_type_value)

            description_value = field_dict.get("description", "")
            if not isinstance(description_value, str):
                continue

            # Extract unit from either "Base Unit:" or "Unit:" format
            if not unit and ("Base Unit:" in description_value or "Unit:" in description_value):
                unit = self._extract_unit_from_description(description_value)

        return unit, value_type

    def _extract_unit_from_description(self, description: str) -> str | None:
        """Extract unit symbol from GSS field description.

        Handles both "Base Unit:" (unit on next line) and "Unit:" (inline) formats.
        Strips all spaces from unit IDs to handle YAML formatting issues.

        Args:
            description: Field description text from GSS YAML

        Returns:
            Human-readable unit symbol, or None if no unit found
        """
        unit_id, _ = self._extract_unit_id_and_line(description)
        if unit_id:
            return self._convert_bluetooth_unit_to_readable(unit_id)
        return None

    def _extract_unit_id_and_line(self, description: str) -> tuple[str | None, str | None]:
        """Extract raw unit ID and line from GSS field description.

        Handles both "Base Unit:" (unit on next line) and "Unit:" (inline) formats.
        Strips all spaces from unit IDs to handle YAML formatting issues.

        Args:
            description: Field description text from GSS YAML

        Returns:
            Tuple of (unit_id without org.bluetooth.unit prefix, full unit line)
            Returns (None, None) if no unit found
        """
        unit_line = None

        if "Base Unit:" in description:
            # Format: "Base Unit:\norg.bluetooth.unit.xxx" or "Base Unit: org.bluetooth.unit.xxx"
            parts = description.split("Base Unit:")[1].split("\n")
            unit_line = parts[0].strip()
            if not unit_line and len(parts) > 1:  # Unit is on next line
                unit_line = parts[1].strip()
        elif "Unit:" in description:
            # Format: "Unit: org.bluetooth.unit.xxx" (inline)
            unit_line = description.split("Unit:")[1].split("\n")[0].strip()

        if unit_line and "org.bluetooth.unit." in unit_line:
            # Remove all spaces (handles YAML formatting issues)
            cleaned_line = unit_line.replace(" ", "")
            unit_spec = cleaned_line.split("org.bluetooth.unit.")[1].strip()
            return unit_spec, cleaned_line

        return None, None

    def _convert_yaml_type_to_python_type(self, yaml_type: str) -> str:
        """Convert YAML type to Python type string."""
        return DataType.from_string(yaml_type).to_python_type()

    def _convert_bluetooth_unit_to_readable(self, unit_spec: str) -> str:
        """Convert Bluetooth SIG unit specification to human-readable symbol.

        Args:
            unit_spec: Unit specification from GSS YAML (e.g., "thermodynamic_temperature.degree_celsius")

        Returns:
            Human-readable unit symbol (e.g., "°C"), or unit_spec if no mapping found
        """
        unit_spec = unit_spec.rstrip(".").lower()
        unit_id = f"org.bluetooth.unit.{unit_spec}"

        units_registry = self._get_units_registry()
        unit_info = units_registry.get_info(unit_id)
        if unit_info and unit_info.symbol:
            return unit_info.symbol

        return unit_spec


# Singleton instance for convenient access
gss_registry = GssRegistry.get_instance()
