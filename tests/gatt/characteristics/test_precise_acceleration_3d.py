"""Tests for Precise Acceleration 3D characteristic (0x2C1E)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PreciseAcceleration3DCharacteristic
from bluetooth_sig.gatt.characteristics.templates import VectorData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPreciseAcceleration3DCharacteristic(CommonCharacteristicTests):
    """Test suite for Precise Acceleration 3D characteristic."""

    @pytest.fixture
    def characteristic(self) -> PreciseAcceleration3DCharacteristic:
        return PreciseAcceleration3DCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C1E"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                expected_value=VectorData(x_axis=0.0, y_axis=0.0, z_axis=0.0),
                description="Zero acceleration",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xE8, 0x03, 0x00, 0x00, 0x00, 0x00]),
                expected_value=VectorData(x_axis=1.0, y_axis=0.0, z_axis=0.0),
                description="1.0 gn on x-axis (raw 1000 * 0.001)",
            ),
        ]

    def test_encode_round_trip(self) -> None:
        """Verify encode/decode round-trip."""
        char = PreciseAcceleration3DCharacteristic()
        original = VectorData(x_axis=0.5, y_axis=-0.25, z_axis=1.0)
        encoded = char.build_value(original)
        decoded = char.parse_value(encoded)
        assert decoded == original
