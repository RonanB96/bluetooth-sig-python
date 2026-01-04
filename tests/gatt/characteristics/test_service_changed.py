"""Tests for Service Changed characteristic (0x2A05)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import ServiceChangedCharacteristic, ServiceChangedData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestServiceChangedCharacteristic(CommonCharacteristicTests):
    """Test suite for Service Changed characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds service changed-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> ServiceChangedCharacteristic:
        """Return a Service Changed characteristic instance."""
        return ServiceChangedCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Service Changed characteristic."""
        return "2A05"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for service changed."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x05, 0x00]),
                expected_value=ServiceChangedData(start_handle=0x0001, end_handle=0x0005),
                description="Service range 0x0001 to 0x0005",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x10, 0x00, 0x20, 0x00]),
                expected_value=ServiceChangedData(start_handle=0x0010, end_handle=0x0020),
                description="Service range 0x0010 to 0x0020",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFF, 0xFF, 0xFF, 0xFF]),
                expected_value=ServiceChangedData(start_handle=0xFFFF, end_handle=0xFFFF),
                description="Maximum handle values",
            ),
        ]

    def test_single_service_changed(self) -> None:
        """Test service changed with a single service."""
        char = ServiceChangedCharacteristic()
        service_changed = ServiceChangedData(start_handle=0x0020, end_handle=0x0025)

        # Test encoding
        encoded = char.build_value(service_changed)
        assert encoded == bytearray([0x20, 0x00, 0x25, 0x00])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded.value == service_changed

    def test_multiple_services_changed(self) -> None:
        """Test service changed with multiple services in range."""
        char = ServiceChangedCharacteristic()
        service_changed = ServiceChangedData(start_handle=0x0010, end_handle=0x0050)

        # Test encoding
        encoded = char.build_value(service_changed)
        assert encoded == bytearray([0x10, 0x00, 0x50, 0x00])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded.value == service_changed

    def test_invalid_length_raises_error(self) -> None:
        """Test that invalid data lengths result in parse failure."""
        char = ServiceChangedCharacteristic()

        # Test too short - parse_value returns parse_success=False
        result = char.parse_value(bytearray([0x00, 0x00]))
        assert result.parse_success is False
        assert result.error_message == (
            "Length validation failed for Service Changed: expected exactly 4 bytes, got 2 "
            "(class-level constraint for ServiceChangedCharacteristic)"
        )

        # Test too long - should also fail with exact length validation
        result = char.parse_value(bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
        assert result.parse_success is False
        assert result.error_message == (
            "Length validation failed for Service Changed: expected exactly 4 bytes, got 6 "
            "(class-level constraint for ServiceChangedCharacteristic)"
        )

    def test_round_trip_encoding(self) -> None:
        """Test that encoding and decoding preserve data."""
        char = ServiceChangedCharacteristic()
        original = ServiceChangedData(start_handle=0xABCD, end_handle=0xEF01)

        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)

        assert decoded.value == original
        assert encoded == bytearray([0xCD, 0xAB, 0x01, 0xEF])  # Little endian
