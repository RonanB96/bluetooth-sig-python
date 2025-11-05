"""Static analysis tests for service registry completeness.

These tests verify:
1. All implemented SIG services are in ServiceName enum
2. Service enum values match YAML registry names
3. No duplicate UUIDs in service classes
"""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.services.registry import _ServiceClassDiscovery
from bluetooth_sig.gatt.uuid_registry import uuid_registry
from bluetooth_sig.types.gatt_enums import ServiceName


class TestServiceEnumCompleteness:
    """Test that ServiceName enum contains all implemented services."""

    def test_all_sig_services_have_enum_entries(self) -> None:
        """CRITICAL: Verify every SIG service class has a corresponding enum entry.

        This test ensures services are discoverable by the registry system.
        Without enum entries, services:
        - Won't be auto-registered
        - Will fail in service discovery scenarios
        - Cannot be referenced by name in code
        """
        # Discover all service classes
        discovered_classes = _ServiceClassDiscovery.discover_classes()

        # Get all UUID->name mappings from the enum
        enum_uuids = set()
        for enum_member in ServiceName:
            # Try to resolve UUID for this enum member
            info = uuid_registry.get_service_info(enum_member.value)
            if info:
                enum_uuids.add(info.uuid.normalized)

        # Check each discovered class
        missing_from_enum = []
        for service_cls in discovered_classes:
            uuid_obj = service_cls.get_class_uuid()

            # Check if this is a SIG service (16-bit UUID)
            if not uuid_obj.is_sig_service():
                continue  # Custom services don't need enum entries

            # Check if UUID is in enum
            if uuid_obj.normalized not in enum_uuids:
                service_name = service_cls.__name__
                # Try to get the name from YAML
                yaml_info = uuid_registry.get_service_info(str(uuid_obj))
                yaml_name = yaml_info.name if yaml_info else "Unknown"

                missing_from_enum.append(
                    {
                        "class": service_name,
                        "uuid": str(uuid_obj),
                        "yaml_name": yaml_name,
                    }
                )

        # Report all missing services
        if missing_from_enum:
            error_msg = "The following SIG services are implemented but missing from ServiceName enum:\n"
            for item in missing_from_enum:
                error_msg += (
                    f"\n  - {item['class']} (UUID: {item['uuid']})"
                    f"\n    YAML name: '{item['yaml_name']}'"
                    f"\n    Add to ServiceName enum as:"
                    f'\n    {item["yaml_name"].upper().replace(" ", "_").replace("-", "_")} = "{item["yaml_name"]}"'
                    f"\n"
                )
            error_msg += (
                "\nWhy this matters:"
                "\n- Services without enum entries are not auto-registered"
                "\n- They will fail in service discovery operations"
                "\n- They cannot be referenced by name in application code"
                "\n- Integration tests will fail even if unit tests pass"
            )
            pytest.fail(error_msg)

    def test_service_enum_names_match_yaml(self) -> None:
        """Verify ServiceName enum values match YAML registry names.

        This catches typos and ensures enum→UUID resolution works correctly.
        """
        mismatches = []

        for enum_member in ServiceName:
            # Try to resolve this enum value in YAML
            info = uuid_registry.get_service_info(enum_member.value)

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
            error_msg = "ServiceName enum has entries that don't match YAML registry:\n"
            for item in mismatches:
                error_msg += f'\n  - {item["enum_name"]} = "{item["enum_value"]}"'
                error_msg += f"\n    Issue: {item['issue']}"
                if "yaml_name" in item:
                    error_msg += f'\n    YAML has: "{item["yaml_name"]}"'
                error_msg += "\n"
            pytest.fail(error_msg)

    def test_no_duplicate_uuids_in_service_classes(self) -> None:
        """Verify no two service classes resolve to the same UUID.

        This catches copy-paste errors where someone duplicates a class
        but forgets to update the UUID.
        """
        discovered_classes = _ServiceClassDiscovery.discover_classes()

        uuid_to_classes: dict[str, list[str]] = {}
        for service_cls in discovered_classes:
            uuid_obj = service_cls.get_class_uuid()

            uuid_str = str(uuid_obj)
            if uuid_str not in uuid_to_classes:
                uuid_to_classes[uuid_str] = []
            uuid_to_classes[uuid_str].append(service_cls.__name__)

        # Find duplicates
        duplicates = {uuid: classes for uuid, classes in uuid_to_classes.items() if len(classes) > 1}

        if duplicates:
            error_msg = "Multiple service classes resolve to the same UUID:\n"
            for uuid, classes in duplicates.items():
                error_msg += f"\n  UUID {uuid}:"
                for cls_name in classes:
                    error_msg += f"\n    - {cls_name}"
                error_msg += "\n"
            error_msg += "\nThis likely indicates a copy-paste error where UUID wasn't updated."
            pytest.fail(error_msg)


class TestServiceRegistryIntegrity:
    """Test that service registry can handle all implemented services."""

    def test_all_sig_services_can_be_instantiated(self) -> None:
        """Verify all SIG services can be created without errors.

        This catches issues like:
        - Missing __init__ parameters
        - Broken UUID resolution
        - Missing dependencies in __init__
        """
        discovered_classes = _ServiceClassDiscovery.discover_classes()

        instantiation_failures = []
        for service_cls in discovered_classes:
            uuid_obj = service_cls.get_class_uuid()
            if not uuid_obj.is_sig_service():
                continue  # Skip non-SIG services

            try:
                instance = service_cls()
                assert instance is not None
                assert instance.uuid is not None
            except Exception as e:
                instantiation_failures.append(
                    {
                        "class": service_cls.__name__,
                        "uuid": str(uuid_obj),
                        "error": str(e),
                    }
                )

        if instantiation_failures:
            error_msg = "The following SIG services cannot be instantiated:\n"
            for item in instantiation_failures:
                error_msg += f"\n  - {item['class']} (UUID: {item['uuid']})"
                error_msg += f"\n    Error: {item['error']}\n"
            pytest.fail(error_msg)

    def test_all_sig_services_have_valid_uuids(self) -> None:
        """Verify all SIG service UUIDs follow Bluetooth SIG format.

        SIG UUIDs should be in format: 0000XXXX-0000-1000-8000-00805F9B34FB
        where XXXX is a 16-bit assigned number.
        """
        discovered_classes = _ServiceClassDiscovery.discover_classes()

        invalid_uuids = []
        for service_cls in discovered_classes:
            uuid_obj = service_cls.get_class_uuid()

            # Check if claiming to be SIG but doesn't follow format
            if uuid_obj.is_sig_service():
                # SIG UUIDs must follow specific format
                uuid_str = str(uuid_obj).upper()
                if not (uuid_str.startswith("0000") and uuid_str.endswith("-0000-1000-8000-00805F9B34FB")):
                    invalid_uuids.append(
                        {
                            "class": service_cls.__name__,
                            "uuid": str(uuid_obj),
                            "issue": "Claims to be SIG UUID but doesn't follow format",
                        }
                    )

        if invalid_uuids:
            error_msg = "The following services have invalid SIG UUIDs:\n"
            for item in invalid_uuids:
                error_msg += f"\n  - {item['class']}: {item['uuid']}"
                error_msg += f"\n    {item['issue']}\n"
            pytest.fail(error_msg)
