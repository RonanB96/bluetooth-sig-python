"""Test Altitude characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import AltitudeCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAltitudeCharacteristic(CommonCharacteristicTests):
    """Test Altitude characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> AltitudeCharacteristic:
        """Provide Altitude characteristic for testing."""
        return AltitudeCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Altitude characteristic."""
        return "2AB3"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid Altitude test data.

        IPS spec §3.7: decoded metres = (raw_uint16 − 1000) × 0.1.
        """
        return [
            # raw=1005: (1005−1000)×0.1 = 0.5 m
            CharacteristicTestData(
                input_data=bytearray([0xED, 0x03]), expected_value=0.5, description="5 dm above WGS84 ellipsoid"
            ),
            # raw=1000: (1000−1000)×0.1 = 0.0 m (on ellipsoid)
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03]), expected_value=0.0, description="On WGS84 ellipsoid (0.0 m)"
            ),
            # raw=2000: (2000−1000)×0.1 = 100.0 m
            CharacteristicTestData(
                input_data=bytearray([0xD0, 0x07]), expected_value=100.0, description="100.0 m above ellipsoid"
            ),
        ]

    def test_altitude_parsing(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "m"
        assert characteristic.python_type is float

        # raw=1005: (1005−1000)×0.1 = 0.5 m  (IPS spec §3.7)
        test_data = bytearray([0xED, 0x03])
        parsed = characteristic.parse_value(test_data)
        assert parsed == 0.5

    def test_altitude_error_handling(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude error handling."""
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x12]))

        assert "Length validation failed" in str(exc_info.value)
        assert "expected exactly 2 bytes" in str(exc_info.value)

    def test_altitude_boundary_values(self, characteristic: AltitudeCharacteristic) -> None:
        """Test Altitude boundary values per IPS spec §3.7.

        raw uint16 x; decoded metres = (x − 1000) × 0.1.
        """
        # On ellipsoid (x=1000 → 0 dm = 0.0 m)
        data_zero = bytearray([0xE8, 0x03])  # 1000
        result = characteristic.parse_value(data_zero)
        assert abs(result - 0.0) < 0.01

        # Spec maximum (x=65534 → 64534 dm = 6453.4 m; “≥65534 dm” per spec Table 3.3)
        data_max = bytearray([0xFE, 0xFF])  # 65534
        result = characteristic.parse_value(data_max)
        assert abs(result - 6453.4) < 0.1

        # Spec minimum (x=0 → −1000 dm = −100.0 m; “≤−1000 dm” per spec Table 3.3)
        data_min = bytearray([0x00, 0x00])  # 0
        result = characteristic.parse_value(data_min)
        assert abs(result - (-100.0)) < 0.01

    def test_altitude_round_trip(self, characteristic: AltitudeCharacteristic) -> None:
        """Test encode/decode round trip."""
        test_value = 123.4
        encoded = characteristic.build_value(test_value)
        decoded = characteristic.parse_value(encoded)
        assert decoded == test_value
