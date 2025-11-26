"""Tests for Battery Critical Status characteristic (0x2BE9)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_critical_status import (
    BatteryCriticalStatus,
    BatteryCriticalStatusCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


class TestBatteryCriticalStatusCharacteristic(CommonCharacteristicTests):
    """Test Battery Critical Status characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic:
        """Provide Battery Critical Status characteristic for testing."""
        return BatteryCriticalStatusCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Critical Status characteristic."""
        return "2BE9"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery critical status test data covering various bit combinations."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00]),
                expected_value=BatteryCriticalStatus(
                    critical_power_state=False,
                    immediate_service_required=False,
                ),
                description="All bits clear (no critical states)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01]),
                expected_value=BatteryCriticalStatus(
                    critical_power_state=True,
                    immediate_service_required=False,
                ),
                description="Critical power state set",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02]),
                expected_value=BatteryCriticalStatus(
                    critical_power_state=False,
                    immediate_service_required=True,
                ),
                description="Immediate service required set",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x03]),
                expected_value=BatteryCriticalStatus(
                    critical_power_state=True,
                    immediate_service_required=True,
                ),
                description="Both bits set",
            ),
        ]

    # === Battery Critical Status-Specific Tests ===
    def test_battery_critical_status_bit_parsing(self, characteristic: BaseCharacteristic) -> None:
        """Test individual bit parsing for battery critical status."""
        # Test each bit individually
        bits = [
            ("critical_power_state", 0x01),
            ("immediate_service_required", 0x02),
        ]

        for bit_name, bit_mask in bits:
            # Test bit set
            result = characteristic.decode_value(bytearray([bit_mask]))
            assert getattr(result, bit_name) is True, f"Bit {bit_name} should be True when set"

            # Test bit clear (all other bits set)
            inverted_mask = 0xFF ^ bit_mask
            result = characteristic.decode_value(bytearray([inverted_mask]))
            assert getattr(result, bit_name) is False, f"Bit {bit_name} should be False when clear"

    def test_battery_critical_status_multiple_bits(self, characteristic: BaseCharacteristic) -> None:
        """Test multiple bits set simultaneously."""
        # Test combination of bits
        test_cases = [
            (0x03, ["critical_power_state", "immediate_service_required"]),
        ]

        for mask, expected_bits in test_cases:
            result = characteristic.decode_value(bytearray([mask]))
            for bit_name in expected_bits:
                assert getattr(result, bit_name) is True, f"Bit {bit_name} should be True in mask {mask:02X}"

            # Check other bits are False
            all_bits = ["critical_power_state", "immediate_service_required"]
            for bit_name in all_bits:
                if bit_name not in expected_bits:
                    assert getattr(result, bit_name) is False, f"Bit {bit_name} should be False in mask {mask:02X}"

    def test_battery_critical_status_encoding(self, characteristic: BatteryCriticalStatusCharacteristic) -> None:
        """Test encoding BatteryCriticalStatus to bytes."""
        # Test all bits clear
        status = BatteryCriticalStatus(
            critical_power_state=False,
            immediate_service_required=False,
        )
        encoded = characteristic.encode_value(status)
        assert encoded == bytearray([0x00])

        # Test all bits set
        status = BatteryCriticalStatus(
            critical_power_state=True,
            immediate_service_required=True,
        )
        encoded = characteristic.encode_value(status)
        assert encoded == bytearray([0x03])

        # Test alternating pattern
        status = BatteryCriticalStatus(
            critical_power_state=False,
            immediate_service_required=True,
        )
        encoded = characteristic.encode_value(status)
        assert encoded == bytearray([0x02])

    def test_battery_critical_status_round_trip(self, characteristic: BatteryCriticalStatusCharacteristic) -> None:
        """Test round-trip encoding/decoding preserves values."""
        test_values = [0x00, 0x01, 0x02, 0x03]

        for value in test_values:
            decoded = characteristic.decode_value(bytearray([value]))
            encoded = characteristic.encode_value(decoded)
            assert encoded == bytearray([value]), f"Round-trip failed for value {value:02X}"

    def test_characteristic_metadata(self, characteristic: BatteryCriticalStatusCharacteristic) -> None:
        """Test characteristic metadata."""
        assert characteristic.name == "Battery Critical Status"
        assert characteristic.unit is None
        assert characteristic.uuid == "2BE9"  # type: ignore[unreachable]
