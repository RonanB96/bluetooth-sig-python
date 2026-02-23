"""Test magnetic flux density 2D characteristic."""

from __future__ import annotations

import struct
from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import MagneticFluxDensity2DCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.templates import Vector2DData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMagneticFluxDensity2DCharacteristic(CommonCharacteristicTests):
    """Test Magnetic Flux Density 2D characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        """Provide Magnetic Flux Density 2D characteristic for testing."""
        return MagneticFluxDensity2DCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Magnetic Flux Density 2D characteristic."""
        return "2AA0"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid magnetic flux density 2D test data."""
        return [
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<hh", 0, 0)),
                expected_value=Vector2DData(x_axis=0.0, y_axis=0.0),
                description="Zero magnetic flux density",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<hh", 1000, -500)),
                expected_value=Vector2DData(x_axis=1e-4, y_axis=-5e-5),
                description="Magnetic flux density 2D X=1000, Y=-500",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<hh", 32767, 32767)),
                expected_value=Vector2DData(x_axis=32767 * 1e-7, y_axis=32767 * 1e-7),
                description="Maximum positive magnetic flux density",
            ),
            CharacteristicTestData(
                input_data=bytearray(struct.pack("<hh", -32768, -32768)),
                expected_value=Vector2DData(x_axis=-32768 * 1e-7, y_axis=-32768 * 1e-7),
                description="Minimum negative magnetic flux density",
            ),
        ]

    def test_magnetic_flux_density_2d_parsing(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test Magnetic Flux Density 2D characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "T"
        assert characteristic.python_type is str

        # Test normal parsing: X=1000, Y=-500 (in 10^-7 Tesla units)
        test_data = bytearray(struct.pack("<hh", 1000, -500))
        parsed = characteristic.parse_value(test_data)

        assert abs(parsed.x_axis - 1e-4) < 1e-10  # 1000 * 10^-7 = 1e-4
        assert abs(parsed.y_axis - (-5e-5)) < 1e-10  # -500 * 10^-7 = -5e-5
