"""Tests for Battery Information characteristic (0x2BEC)."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_information import (
    BatteryChemistry,
    BatteryFeatures,
    BatteryInformation,
    BatteryInformationCharacteristic,
    BatteryInformationFlags,
)
from bluetooth_sig.gatt.characteristics.utils import IEEE11073Parser
from bluetooth_sig.gatt.exceptions import CharacteristicParseError
from tests.gatt.characteristics.test_characteristic_common import (
    CharacteristicTestData,
    CommonCharacteristicTests,
)


def _sfloat_bytes(value: float) -> list[int]:
    """Encode a float to SFLOAT and return as list of ints."""
    return list(IEEE11073Parser.encode_sfloat(value))


def _uint24_le(value: int) -> list[int]:
    """Encode uint24 as 3-byte little-endian list."""
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF]


class TestBatteryInformationCharacteristic(CommonCharacteristicTests):
    """Test Battery Information characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Battery Information characteristic for testing."""
        return BatteryInformationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Battery Information characteristic."""
        return "2BEC"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid battery information test data."""
        # 19724 days since epoch = 2024-01-01 (approx)
        # 21550 days since epoch = 2029-01-01 (approx)
        return [
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0xFF,
                        0x00,  # flags: bits 0-7 all set (16-bit LE)
                        0x03,  # features: replaceable + rechargeable
                        *_uint24_le(19724),  # manufacture_date
                        *_uint24_le(21550),  # expiration_date
                        *_sfloat_bytes(10.0),  # designed_capacity: 10kWh
                        *_sfloat_bytes(2.0),  # low_energy: 2kWh
                        *_sfloat_bytes(1.0),  # critical_energy: 1kWh
                        0x05,  # chemistry: Lithium Ion
                        *_sfloat_bytes(4.0),  # nominal_voltage: 4V
                        0x01,  # aggregation_group: 1
                    ]
                ),
                expected_value=BatteryInformation(
                    flags=BatteryInformationFlags(0x00FF),
                    battery_features=BatteryFeatures(0x03),
                    battery_manufacture_date=19724,
                    battery_expiration_date=21550,
                    battery_designed_capacity=10.0,
                    battery_low_energy=2.0,
                    battery_critical_energy=1.0,
                    battery_chemistry=BatteryChemistry.LITHIUM_ION,
                    nominal_voltage=4.0,
                    battery_aggregation_group=1,
                ),
                description="All fields present",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00]),
                expected_value=BatteryInformation(
                    flags=BatteryInformationFlags(0x0000),
                    battery_features=BatteryFeatures(0x00),
                ),
                description="Mandatory fields only",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x20, 0x00, 0x02, 0x06]),
                expected_value=BatteryInformation(
                    flags=BatteryInformationFlags(0x0020),
                    battery_features=BatteryFeatures(0x02),
                    battery_chemistry=BatteryChemistry.LITHIUM_POLYMER,
                ),
                description="Chemistry only",
            ),
        ]

    def test_features_replaceable(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify replaceable feature bit."""
        data = bytearray([0x00, 0x00, 0x01])  # features: replaceable only
        result = characteristic.parse_value(data)
        assert result.battery_features & BatteryFeatures.REPLACEABLE
        assert not result.battery_features & BatteryFeatures.RECHARGEABLE

    def test_features_rechargeable(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify rechargeable feature bit."""
        data = bytearray([0x00, 0x00, 0x02])  # features: rechargeable only
        result = characteristic.parse_value(data)
        assert result.battery_features & BatteryFeatures.RECHARGEABLE
        assert not result.battery_features & BatteryFeatures.REPLACEABLE

    def test_chemistry_enum_values(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify chemistry enum maps correctly."""
        for chem_val, expected in [
            (0, BatteryChemistry.UNKNOWN),
            (5, BatteryChemistry.LITHIUM_ION),
            (8, BatteryChemistry.NICKEL_CADMIUM),
            (13, BatteryChemistry.ZINC_CARBON),
            (255, BatteryChemistry.OTHER),
        ]:
            data = bytearray([0x20, 0x00, 0x00, chem_val])
            result = characteristic.parse_value(data)
            assert result.battery_chemistry == expected

    def test_chemistry_unknown_rfu_value(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify RFU chemistry value falls back to UNKNOWN."""
        data = bytearray([0x20, 0x00, 0x00, 200])
        result = characteristic.parse_value(data)
        assert result.battery_chemistry == BatteryChemistry.UNKNOWN

    def test_dates_decode(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify date fields decode correctly."""
        data = bytearray([0x03, 0x00, 0x00, *_uint24_le(0), *_uint24_le(36524)])
        result = characteristic.parse_value(data)
        assert result.battery_manufacture_date == 0
        assert result.battery_expiration_date == 36524

    def test_aggregation_group(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify aggregation group field."""
        data = bytearray([0x80, 0x00, 0x00, 0x05])
        result = characteristic.parse_value(data)
        assert result.battery_aggregation_group == 5

    def test_roundtrip_all_fields(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with all fields."""
        original = BatteryInformation(
            flags=BatteryInformationFlags(0x00FF),
            battery_features=BatteryFeatures(0x03),
            battery_manufacture_date=19724,
            battery_expiration_date=21550,
            battery_designed_capacity=10.0,
            battery_low_energy=2.0,
            battery_critical_energy=1.0,
            battery_chemistry=BatteryChemistry.LITHIUM_ION,
            nominal_voltage=4.0,
            battery_aggregation_group=1,
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_roundtrip_minimal(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify encode/decode roundtrip with minimal fields."""
        original = BatteryInformation(
            flags=BatteryInformationFlags(0x0000),
            battery_features=BatteryFeatures(0x01),
        )
        encoded = characteristic.build_value(original)
        decoded = characteristic.parse_value(encoded)
        assert decoded == original

    def test_too_short_data(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Verify that data shorter than min_length raises error."""
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x00]))
