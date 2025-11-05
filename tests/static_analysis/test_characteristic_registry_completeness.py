"""Static analysis tests to catch common bugs at development time.

These tests verify:
1. All implemented SIG characteristics are in CharacteristicName enum
2. All implemented SIG services are in ServiceName enum
3. Characteristic classes have proper UUID resolution
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.registry import _CharacteristicClassDiscovery
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types.gatt_enums import CharacteristicName


class TestCharacteristicEnumCompleteness:
    """Test that CharacteristicName enum contains all implemented characteristics."""

    def test_all_sig_characteristics_have_enum_entries(self) -> None:
        """CRITICAL: Verify every SIG characteristic class has a corresponding enum entry.

        This test catches the bug where RSC Feature and CSC Feature were implemented
        but missing from CharacteristicName enum, causing them to not be registered
        and failing in batch parsing scenarios.

        Without this test, characteristics can be:
        - Implemented in code
        - Have proper decode/encode methods
        - Pass unit tests
        BUT still fail in integration because they're not discoverable by the registry!
        """
        # Discover all characteristic classes
        discovered_classes = _CharacteristicClassDiscovery.discover_classes()

        # Get all UUID->name mappings from the enum
        enum_uuids = set()
        for enum_member in CharacteristicName:
            # Try to resolve UUID for this enum member
            info = uuid_registry.get_characteristic_info(enum_member.value)
            if info:
                enum_uuids.add(info.uuid.normalized)

        # Check each discovered class
        missing_from_enum = []
        for char_cls in discovered_classes:
            uuid_obj = char_cls.get_class_uuid()
            if uuid_obj is None:
                continue

            # Check if this is a SIG characteristic (16-bit UUID)
            if not uuid_obj.is_sig_characteristic():
                continue  # Custom characteristics don't need enum entries

            # Check if UUID is in enum
            if uuid_obj.normalized not in enum_uuids:
                char_name = char_cls.__name__
                # Try to get the name from YAML
                yaml_info = uuid_registry.get_characteristic_info(str(uuid_obj))
                yaml_name = yaml_info.name if yaml_info else "Unknown"

                missing_from_enum.append(
                    {
                        "class": char_name,
                        "uuid": str(uuid_obj),
                        "yaml_name": yaml_name,
                    }
                )

        # Report all missing characteristics
        if missing_from_enum:
            error_msg = "The following SIG characteristics are implemented but missing from CharacteristicName enum:\n"
            for item in missing_from_enum:
                error_msg += (
                    f"\n  - {item['class']} (UUID: {item['uuid']})"
                    f"\n    YAML name: '{item['yaml_name']}'"
                    f"\n    Add to CharacteristicName enum as:"
                    f'\n    {item["yaml_name"].upper().replace(" ", "_").replace("-", "_")} = "{item["yaml_name"]}"'
                    f"\n"
                )
            error_msg += (
                "\nWhy this matters:"
                "\n- Characteristics without enum entries are not auto-registered"
                "\n- They will fail in batch parsing (translator.parse_characteristics)"
                "\n- Dependencies on them will not work"
                "\n- Integration tests will fail even if unit tests pass"
            )
            pytest.fail(error_msg)

    def test_characteristic_enum_names_match_yaml(self) -> None:
        """Verify CharacteristicName enum values match YAML registry names.

        This catches typos and ensures enum→UUID resolution works correctly.
        """
        mismatches = []

        for enum_member in CharacteristicName:
            # Try to resolve this enum value in YAML
            info = uuid_registry.get_characteristic_info(enum_member.value)

            if info is None:
                mismatches.append(
                    {
                        "enum_name": enum_member.name,
                        "enum_value": enum_member.value,
                        "issue": "No matching entry in YAML registry",
                    }
                )
            elif info.name != enum_member.value:
                mismatches.append(
                    {
                        "enum_name": enum_member.name,
                        "enum_value": enum_member.value,
                        "yaml_name": info.name,
                        "issue": "Enum value doesn't match YAML name",
                    }
                )

        if mismatches:
            error_msg = "CharacteristicName enum has entries that don't match YAML registry:\n"
            for item in mismatches:
                error_msg += f'\n  - {item["enum_name"]} = "{item["enum_value"]}"'
                error_msg += f"\n    Issue: {item['issue']}"
                if "yaml_name" in item:
                    error_msg += f'\n    YAML has: "{item["yaml_name"]}"'
                error_msg += "\n"
            pytest.fail(error_msg)

    def test_no_duplicate_uuids_in_characteristic_classes(self) -> None:
        """Verify no two characteristic classes resolve to the same UUID.

        This catches copy-paste errors where someone duplicates a class
        but forgets to update the UUID.
        """
        discovered_classes = _CharacteristicClassDiscovery.discover_classes()

        uuid_to_classes: dict[str, list[str]] = {}
        for char_cls in discovered_classes:
            uuid_obj = char_cls.get_class_uuid()
            if uuid_obj is None:
                continue

            uuid_str = str(uuid_obj)
            if uuid_str not in uuid_to_classes:
                uuid_to_classes[uuid_str] = []
            uuid_to_classes[uuid_str].append(char_cls.__name__)

        # Find duplicates
        duplicates = {uuid: classes for uuid, classes in uuid_to_classes.items() if len(classes) > 1}

        if duplicates:
            error_msg = "Multiple characteristic classes resolve to the same UUID:\n"
            for uuid, classes in duplicates.items():
                error_msg += f"\n  UUID {uuid}:"
                for cls_name in classes:
                    error_msg += f"\n    - {cls_name}"
                error_msg += "\n"
            error_msg += "\nThis likely indicates a copy-paste error where UUID wasn't updated."
            pytest.fail(error_msg)


class TestCharacteristicRegistryIntegrity:
    """Test that characteristic registry can handle all implemented characteristics."""

    def test_all_sig_characteristics_can_be_instantiated(self) -> None:
        """Verify all SIG characteristics can be created without errors.

        This catches issues like:
        - Missing __init__ parameters
        - Broken UUID resolution
        - Missing dependencies in __init__
        """
        discovered_classes = _CharacteristicClassDiscovery.discover_classes()

        instantiation_failures = []
        for char_cls in discovered_classes:
            uuid_obj = char_cls.get_class_uuid()
            if uuid_obj is None or not uuid_obj.is_sig_characteristic():
                continue  # Skip non-SIG characteristics

            try:
                instance = char_cls()
                assert instance is not None
                assert instance.uuid is not None
            except Exception as e:
                instantiation_failures.append(
                    {
                        "class": char_cls.__name__,
                        "uuid": str(uuid_obj),
                        "error": str(e),
                    }
                )

        if instantiation_failures:
            error_msg = "The following SIG characteristics cannot be instantiated:\n"
            for item in instantiation_failures:
                error_msg += f"\n  - {item['class']} (UUID: {item['uuid']})"
                error_msg += f"\n    Error: {item['error']}\n"
            pytest.fail(error_msg)

    def test_all_sig_characteristics_have_valid_uuids(self) -> None:
        """Verify all SIG characteristic UUIDs follow Bluetooth SIG format.

        SIG UUIDs should be in format: 0000XXXX-0000-1000-8000-00805F9B34FB
        where XXXX is a 16-bit assigned number.
        """
        discovered_classes = _CharacteristicClassDiscovery.discover_classes()

        invalid_uuids = []
        for char_cls in discovered_classes:
            uuid_obj = char_cls.get_class_uuid()
            if uuid_obj is None:
                continue

            # Check if claiming to be SIG but doesn't follow format
            if uuid_obj.is_sig_characteristic():
                # SIG UUIDs must follow specific format
                uuid_str = str(uuid_obj).upper()
                if not (uuid_str.startswith("0000") and uuid_str.endswith("-0000-1000-8000-00805F9B34FB")):
                    invalid_uuids.append(
                        {
                            "class": char_cls.__name__,
                            "uuid": str(uuid_obj),
                            "issue": "Claims to be SIG UUID but doesn't follow format",
                        }
                    )

        if invalid_uuids:
            error_msg = "The following characteristics have invalid SIG UUIDs:\n"
            for item in invalid_uuids:
                error_msg += f"\n  - {item['class']}: {item['uuid']}"
                error_msg += f"\n    {item['issue']}\n"
            pytest.fail(error_msg)
