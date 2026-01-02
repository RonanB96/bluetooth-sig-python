"""Tests for Acceleration 3D characteristic (0x2C1D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import Acceleration3DCharacteristic
from bluetooth_sig.gatt.characteristics.templates import VectorData
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestAcceleration3DCharacteristic(CommonCharacteristicTests):
    """Test suite for Acceleration 3D characteristic."""

    @pytest.fixture
    def characteristic(self) -> Acceleration3DCharacteristic:
        """Return an Acceleration 3D characteristic instance."""
        return Acceleration3DCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Acceleration 3D characteristic."""
        return "2C1D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for acceleration 3D."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0, 0, 0]),
                expected_value=VectorData(x_axis=0.0, y_axis=0.0, z_axis=0.0),
                description="Zero acceleration",
            ),
            CharacteristicTestData(
                input_data=bytearray([10, 20, 30]),
                expected_value=VectorData(x_axis=0.1, y_axis=0.2, z_axis=0.3),
                description="Positive acceleration",
            ),
        ]

    def test_zero_acceleration(self) -> None:
        """Test zero acceleration values."""
        char = Acceleration3DCharacteristic()
        result = char.decode_value(bytearray([0, 0, 0]))
        assert result.x_axis == 0.0
        assert result.y_axis == 0.0
        assert result.z_axis == 0.0

    def test_positive_values(self) -> None:
        """Test positive acceleration values."""
        char = Acceleration3DCharacteristic()
        result = char.decode_value(bytearray([10, 20, 30]))
        assert result.x_axis == pytest.approx(0.1)
        assert result.y_axis == pytest.approx(0.2)
        assert result.z_axis == pytest.approx(0.3)

    def test_custom_round_trip(self) -> None:
        """Test encoding and decoding preserve values."""
        char = Acceleration3DCharacteristic()
        original = VectorData(x_axis=0.5, y_axis=-0.3, z_axis=1.0)
        encoded = char.encode_value(original)
        decoded = char.decode_value(encoded)
        assert decoded.x_axis == pytest.approx(original.x_axis, abs=0.02)
        assert decoded.y_axis == pytest.approx(original.y_axis, abs=0.02)
        assert decoded.z_axis == pytest.approx(original.z_axis, abs=0.02)
