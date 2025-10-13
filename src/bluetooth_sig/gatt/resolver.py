"""Shared SIG resolver utilities for characteristics and services.

This module provides common name resolution and normalization logic to avoid
duplication between characteristic and service resolvers.
"""

from __future__ import annotations

import re
from typing import Generic, TypeVar

from ..types import CharacteristicInfo, ServiceInfo
from ..types.gatt_enums import ValueType
from .uuid_registry import UuidInfo, uuid_registry

# Generic type variables for resolver return types
TInfo = TypeVar("TInfo", CharacteristicInfo, ServiceInfo)


class NameNormalizer:
    """Utilities for normalizing class names to various Bluetooth SIG formats.

    This class provides name transformation functions that are common to both
    characteristic and service resolution.
    """

    @staticmethod
    def camel_case_to_display_name(name: str) -> str:
        """Convert camelCase class name to space-separated display name.

        Uses industry-standard two-step regex pattern to handle acronyms correctly:
        - Step 1: Handle consecutive capitals followed by lowercase (VOCConcentration -> VOC Concentration)
        - Step 2: Handle lowercase/digit followed by capital (camelCase -> camel Case)

        Args:
            name: CamelCase name (e.g., "VOCConcentration", "BatteryLevel")

        Returns:
            Space-separated display name (e.g., "VOC Concentration", "Battery Level")

        Examples:
            >>> NameNormalizer.camel_case_to_display_name("VOCConcentration")
            "VOC Concentration"
            >>> NameNormalizer.camel_case_to_display_name("CO2Concentration")
            "CO2 Concentration"
            >>> NameNormalizer.camel_case_to_display_name("BatteryLevel")
            "Battery Level"
        """
        # Step 1: Handle consecutive capitals followed by lowercase
        # e.g., "VOCConcentration" -> "VOC Concentration"
        s1 = re.sub("([A-Z]+)([A-Z][a-z])", r"\1 \2", name)
        # Step 2: Handle lowercase/digit followed by capital
        # e.g., "camelCase" -> "camel Case", "PM25Concentration" -> "PM25 Concentration"
        return re.sub("([a-z0-9])([A-Z])", r"\1 \2", s1)

    @staticmethod
    def remove_suffix(name: str, suffix: str) -> str:
        """Remove suffix from name if present.

        Args:
            name: Original name
            suffix: Suffix to remove (e.g., "Characteristic", "Service")

        Returns:
            Name without suffix, or original name if suffix not present
        """
        if name.endswith(suffix):
            return name[: -len(suffix)]
        return name

    @staticmethod
    def to_org_format(words: list[str], entity_type: str) -> str:
        """Convert words to org.bluetooth format.

        Args:
            words: List of words from name split
            entity_type: Type of entity ("characteristic" or "service")

        Returns:
            Org format string (e.g., "org.bluetooth.characteristic.battery_level")
        """
        return f"org.bluetooth.{entity_type}." + "_".join(word.lower() for word in words)


class NameVariantGenerator:
    """Generates name variants for registry lookups.

    Produces all possible name formats that might match registry entries,
    ordered by likelihood of success.
    """

    @staticmethod
    def generate_characteristic_variants(class_name: str, explicit_name: str | None = None) -> list[str]:
        """Generate all name variants to try for characteristic resolution.

        Args:
            class_name: The __name__ of the characteristic class
            explicit_name: Optional explicit name override

        Returns:
            List of name variants ordered by likelihood of success
        """
        variants: list[str] = []

        # If explicit name provided, try it first
        if explicit_name:
            variants.append(explicit_name)

        # Remove 'Characteristic' suffix if present
        base_name = NameNormalizer.remove_suffix(class_name, "Characteristic")

        # Convert to space-separated display name
        display_name = NameNormalizer.camel_case_to_display_name(base_name)

        # Generate org format
        words = display_name.split()
        org_name = NameNormalizer.to_org_format(words, "characteristic")

        # Order by hit rate (based on testing):
        # 1. Space-separated display name
        # 2. Base name without suffix
        # 3. Org ID format (~0% hit rate but spec-compliant)
        # 4. Full class name (fallback)
        variants.extend(
            [
                display_name,
                base_name,
                org_name,
                class_name,
            ]
        )

        # Remove duplicates while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for v in variants:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result

    @staticmethod
    def generate_service_variants(class_name: str, explicit_name: str | None = None) -> list[str]:
        """Generate all name variants to try for service resolution.

        Args:
            class_name: The __name__ of the service class
            explicit_name: Optional explicit name override

        Returns:
            List of name variants ordered by likelihood of success
        """
        variants: list[str] = []

        # If explicit name provided, try it first
        if explicit_name:
            variants.append(explicit_name)

        # Remove 'Service' suffix if present
        base_name = NameNormalizer.remove_suffix(class_name, "Service")

        # Split on camelCase and convert to space-separated
        words = re.findall("[A-Z][^A-Z]*", base_name)
        display_name = " ".join(words)

        # Generate org format
        org_name = NameNormalizer.to_org_format(words, "service")

        # Order by likelihood:
        # 1. Space-separated display name
        # 2. Base name without suffix
        # 3. Display name with " Service" suffix
        # 4. Full class name
        # 5. Org ID format
        variants.extend(
            [
                display_name,
                base_name,
                display_name + " Service",
                class_name,
                org_name,
            ]
        )

        # Remove duplicates while preserving order
        seen: set[str] = set()
        result: list[str] = []
        for v in variants:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result


class RegistrySearchStrategy(Generic[TInfo]):  # pylint: disable=too-few-public-methods
    """Base strategy for searching registry with name variants.

    This class implements the Template Method pattern, allowing subclasses
    to customize the search behavior for different entity types.
    """

    def search(self, class_obj: type, explicit_name: str | None = None) -> TInfo | None:
        """Search registry using name variants.

        Args:
            class_obj: The class to resolve info for
            explicit_name: Optional explicit name override

        Returns:
            Resolved info object or None if not found
        """
        variants = self._generate_variants(class_obj.__name__, explicit_name)

        for variant in variants:
            info = self._lookup_in_registry(variant)
            if info:
                return self._create_info(info, class_obj)

        return None

    def _generate_variants(self, class_name: str, explicit_name: str | None) -> list[str]:
        """Generate name variants for this entity type."""
        raise NotImplementedError

    def _lookup_in_registry(self, name: str) -> UuidInfo | None:
        """Lookup name in registry."""
        raise NotImplementedError

    def _create_info(self, uuid_info: UuidInfo, class_obj: type) -> TInfo:
        """Create Info object from registry UuidInfo."""
        raise NotImplementedError


class CharacteristicRegistrySearch(RegistrySearchStrategy[CharacteristicInfo]):  # pylint: disable=too-few-public-methods
    """Registry search strategy for characteristics."""

    def _generate_variants(self, class_name: str, explicit_name: str | None) -> list[str]:
        return NameVariantGenerator.generate_characteristic_variants(class_name, explicit_name)

    def _lookup_in_registry(self, name: str) -> UuidInfo | None:
        return uuid_registry.get_characteristic_info(name)

    def _create_info(self, uuid_info: UuidInfo, class_obj: type) -> CharacteristicInfo:
        return CharacteristicInfo(
            uuid=uuid_info.uuid,
            name=uuid_info.name,
            unit=uuid_info.unit or "",
            value_type=ValueType(uuid_info.value_type) if uuid_info.value_type else ValueType.UNKNOWN,
            properties=[],
        )


class ServiceRegistrySearch(RegistrySearchStrategy[ServiceInfo]):  # pylint: disable=too-few-public-methods
    """Registry search strategy for services."""

    def _generate_variants(self, class_name: str, explicit_name: str | None) -> list[str]:
        return NameVariantGenerator.generate_service_variants(class_name, explicit_name)

    def _lookup_in_registry(self, name: str) -> UuidInfo | None:
        return uuid_registry.get_service_info(name)

    def _create_info(self, uuid_info: UuidInfo, class_obj: type) -> ServiceInfo:
        return ServiceInfo(
            uuid=uuid_info.uuid,
            name=uuid_info.name,
            description=uuid_info.summary or "",
        )
