"""Verify all characteristic UUIDs match the Bluetooth SIG YAML source of truth.

This test ensures that every implemented characteristic has a UUID that exactly
matches the canonical source: bluetooth_sig/assigned_numbers/uuids/characteristic_uuids.yaml
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pytest
import yaml

from bluetooth_sig.gatt.characteristics.registry import CharacteristicRegistry
from bluetooth_sig.types.uuid import BluetoothUUID

logger = logging.getLogger(__name__)


def load_uuid_spec() -> dict[str, str]:
    """Load canonical UUID ↔ name mapping from characteristic_uuids.yaml.

    Returns:
        Dict mapping normalized_uuid (e.g., "0x2a00") to name (e.g., "Device Name")
    """
    # Find the YAML file in the installation
    yaml_path = (
        Path(__file__).resolve().parents[2]
        / "bluetooth_sig"
        / "assigned_numbers"
        / "uuids"
        / "characteristic_uuids.yaml"
    )

    if not yaml_path.exists():
        pytest.skip(f"Could not find characteristic_uuids.yaml at {yaml_path}")

    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Build mapping: normalized_uuid -> (name, id)
    uuid_spec: dict[str, tuple[str, str]] = {}
    for entry in data.get("uuids", []):
        uuid = entry.get("uuid")
        name = entry.get("name")
        uuid_id = entry.get("id")

        if uuid and name:
            # Normalize to lowercase hex without '0x'
            normalized = BluetoothUUID(uuid).normalized.lower()
            uuid_spec[normalized] = (name, uuid_id or "")

    logger.info(f"Loaded {len(uuid_spec)} UUIDs from characteristic_uuids.yaml")
    return uuid_spec


@pytest.fixture(scope="session")
def uuid_spec() -> dict[str, tuple[str, str]]:
    """Load UUID spec once per session."""
    return load_uuid_spec()


@pytest.fixture(scope="session")
def char_registry() -> CharacteristicRegistry:
    """Get the characteristic registry."""
    return CharacteristicRegistry()


class TestUuidSpecCompliance:
    """Test that all characteristics have UUIDs matching the spec."""

    def test_all_characteristics_have_resolvable_uuids(self, char_registry: CharacteristicRegistry) -> None:
        """Verify every characteristic class can resolve a UUID."""
        enum_map = char_registry._get_enum_map()  # pylint: disable=protected-access
        all_chars = list(enum_map.values())
        failing_chars = []

        for char_class in all_chars:
            uuid = char_class.get_class_uuid()
            if uuid is None:
                failing_chars.append(char_class.__name__)

        assert not failing_chars, f"{len(failing_chars)} characteristics could not resolve UUIDs: {failing_chars}"

    def test_characteristic_uuids_match_spec(
        self, char_registry: CharacteristicRegistry, uuid_spec: dict[str, tuple[str, str]]
    ) -> None:
        """Verify each characteristic's UUID matches characteristic_uuids.yaml."""
        enum_map = char_registry._get_enum_map()  # pylint: disable=protected-access
        all_chars = list(enum_map.values())
        mismatches: list[dict[str, Any]] = []
        unresolvable: list[str] = []

        for char_class in all_chars:
            class_uuid = char_class.get_class_uuid()

            if class_uuid is None:
                unresolvable.append(char_class.__name__)
                continue

            normalized_uuid = class_uuid.normalized.lower()

            if normalized_uuid not in uuid_spec:
                mismatches.append(
                    {
                        "class": char_class.__name__,
                        "uuid": str(class_uuid),
                        "issue": "UUID not found in characteristic_uuids.yaml",
                    }
                )
                continue

            spec_name, spec_id = uuid_spec[normalized_uuid]
            logger.debug(f"✓ {char_class.__name__:50s} → {normalized_uuid:8s} ({spec_name})")

        if mismatches:
            logger.error(f"UUID verification failed for {len(mismatches)} characteristics:")
            for mismatch in mismatches[:20]:  # Show first 20
                logger.error(f"  {mismatch['class']}: {mismatch['issue']}")

        if unresolvable:
            logger.warning(f"{len(unresolvable)} characteristics had unresolvable UUIDs")

        assert not mismatches, f"{len(mismatches)} characteristics have UUIDs not in the spec"

    def test_characteristic_count_matches_expectations(
        self, char_registry: CharacteristicRegistry, uuid_spec: dict[str, tuple[str, str]]
    ) -> None:
        """Verify the number of implemented characteristics is reasonable."""
        enum_map = char_registry._get_enum_map()  # pylint: disable=protected-access
        all_chars = list(enum_map.values())
        resolvable = sum(1 for c in all_chars if c.get_class_uuid() is not None)

        logger.info(f"Total characteristics in registry: {len(all_chars)}")
        logger.info(f"Characteristics with resolvable UUIDs: {resolvable}")
        logger.info(f"UUIDs in characteristic_uuids.yaml: {len(uuid_spec)}")

        # Should have at least 400 characteristics (481 expected)
        assert resolvable >= 400, f"Expected at least 400 characteristics, got {resolvable}"

    def test_no_duplicate_uuids_across_characteristics(self, char_registry: CharacteristicRegistry) -> None:
        """Ensure no two different characteristic classes map to the same UUID."""
        enum_map = char_registry._get_enum_map()  # pylint: disable=protected-access
        all_chars = list(enum_map.values())
        uuid_to_classes: dict[str, list[str]] = {}

        for char_class in all_chars:
            uuid = char_class.get_class_uuid()
            if uuid is not None:
                normalized = uuid.normalized.lower()
                if normalized not in uuid_to_classes:
                    uuid_to_classes[normalized] = []
                uuid_to_classes[normalized].append(char_class.__name__)

        duplicates = {uuid: classes for uuid, classes in uuid_to_classes.items() if len(classes) > 1}

        assert not duplicates, f"Found {len(duplicates)} duplicate UUIDs: {duplicates}"
