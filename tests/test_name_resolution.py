"""Tests for UUID registry name resolution functionality."""

from bluetooth_sig.gatt.uuid_registry import uuid_registry


class TestNameResolution:
    """Test various name resolution patterns for UUID lookup."""

    def test_battery_service_name_variations(self):
        """Test that Battery Service can be found using various name formats."""
        # Test cases: (lookup_key, should_find, expected_uuid)
        test_cases = [
            ("Battery", True, "180F"),
            ("BATTERY", True, "180F"),
            ("battery", True, "180F"),
            ("org.bluetooth.service.battery_service", True, "180F"),
            ("180F", True, "180F"),
        ]

        for lookup_key, should_find, expected_uuid in test_cases:
            info = uuid_registry.get_service_info(lookup_key)

            if should_find:
                assert info is not None, f"Should find service with key: {lookup_key}"
                assert info.uuid == expected_uuid, f"Wrong UUID for key {lookup_key}"
                assert info.name == "Battery", f"Wrong name for key {lookup_key}"
                assert (
                    info.id == "org.bluetooth.service.battery_service"
                ), f"Wrong ID for key {lookup_key}"
            else:
                assert info is None, f"Should not find service with key: {lookup_key}"

    def test_environmental_sensing_service_name_variations(self):
        """Test that Environmental Sensing Service can be found using various name formats."""
        # Test cases: (lookup_key, should_find, expected_uuid)
        test_cases = [
            ("Environmental Sensing", True, "181A"),
            ("ENVIRONMENTAL_SENSING", True, "181A"),
            ("org.bluetooth.service.environmental_sensing", True, "181A"),
            ("181A", True, "181A"),
        ]

        for lookup_key, should_find, expected_uuid in test_cases:
            info = uuid_registry.get_service_info(lookup_key)

            if should_find:
                assert info is not None, f"Should find service with key: {lookup_key}"
                assert info.uuid == expected_uuid, f"Wrong UUID for key {lookup_key}"
                assert (
                    info.name == "Environmental Sensing"
                ), f"Wrong name for key {lookup_key}"
                assert (
                    info.id == "org.bluetooth.service.environmental_sensing"
                ), f"Wrong ID for key {lookup_key}"
            else:
                assert info is None, f"Should not find service with key: {lookup_key}"

    def test_case_insensitive_lookup(self):
        """Test that name lookup is case-insensitive."""
        # Test various case combinations
        test_keys = [
            "Battery",
            "battery",
            "BATTERY",
            "bAtTeRy",
        ]

        for key in test_keys:
            info = uuid_registry.get_service_info(key)
            assert info is not None, f"Case-insensitive lookup failed for: {key}"
            assert info.uuid == "180F"
            assert info.name == "Battery"

    def test_org_bluetooth_id_format_lookup(self):
        """Test lookup using org.bluetooth.* ID format."""
        # Test org.bluetooth.service.* format
        info = uuid_registry.get_service_info("org.bluetooth.service.battery_service")
        assert info is not None
        assert info.uuid == "180F"
        assert info.name == "Battery"

        info = uuid_registry.get_service_info(
            "org.bluetooth.service.environmental_sensing"
        )
        assert info is not None
        assert info.uuid == "181A"
        assert info.name == "Environmental Sensing"

    def test_direct_uuid_lookup(self):
        """Test lookup using direct UUID strings."""
        # Test 16-bit UUID lookup
        info = uuid_registry.get_service_info("180F")
        assert info is not None
        assert info.uuid == "180F"
        assert info.name == "Battery"

        info = uuid_registry.get_service_info("181A")
        assert info is not None
        assert info.uuid == "181A"
        assert info.name == "Environmental Sensing"

    def test_invalid_service_name_lookup(self):
        """Test that invalid service names return None."""
        invalid_names = [
            "NonExistentService",
            "InvalidName",
            "0000",  # Invalid UUID
            "",  # Empty string
            "Battery Service Extra",  # Close but not exact
        ]

        for invalid_name in invalid_names:
            info = uuid_registry.get_service_info(invalid_name)
            assert (
                info is None
            ), f"Should not find service for invalid name: {invalid_name}"

    def test_characteristic_name_resolution(self):
        """Test characteristic name resolution patterns."""
        # Test Battery Level characteristic
        info = uuid_registry.get_characteristic_info("2A19")
        assert info is not None
        assert info.uuid == "2A19"
        assert info.name == "Battery Level"

        # Test Temperature characteristic
        info = uuid_registry.get_characteristic_info("2A6E")
        assert info is not None
        assert info.uuid == "2A6E"
        assert info.name == "Temperature"

        # Test Humidity characteristic
        info = uuid_registry.get_characteristic_info("2A6F")
        assert info is not None
        assert info.uuid == "2A6F"
        assert info.name == "Humidity"

    def test_name_normalization_consistency(self):
        """Test that name normalization is consistent across different formats."""
        # Get service info using different methods and ensure consistency
        battery_by_name = uuid_registry.get_service_info("Battery")
        battery_by_uuid = uuid_registry.get_service_info("180F")
        battery_by_id = uuid_registry.get_service_info(
            "org.bluetooth.service.battery_service"
        )

        assert battery_by_name is not None
        assert battery_by_uuid is not None
        assert battery_by_id is not None

        # All should return the same information
        assert battery_by_name.uuid == battery_by_uuid.uuid == battery_by_id.uuid
        assert battery_by_name.name == battery_by_uuid.name == battery_by_id.name
        assert battery_by_name.id == battery_by_uuid.id == battery_by_id.id
