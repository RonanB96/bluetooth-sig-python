"""Test magnetic flux density 2D characteristic."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics import MagneticFluxDensity2DCharacteristic

from .test_characteristic_common import CommonCharacteristicTests


class TestMagneticFluxDensity2DCharacteristic(CommonCharacteristicTests):
    """Test Magnetic Flux Density 2D characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> MagneticFluxDensity2DCharacteristic:
        """Provide Magnetic Flux Density 2D characteristic for testing."""
        return MagneticFluxDensity2DCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Magnetic Flux Density 2D characteristic."""
        return "2AA0"

    @pytest.fixture
    def valid_test_data(self) -> tuple[bytearray, float]:
        """Valid magnetic flux density 2D test data."""
        return bytearray(struct.pack("<hh", 1000, -500)), 1e-4  # X=1000, Y=-500 (in 10^-7 Tesla units)

    def test_magnetic_flux_density_2d_parsing(self, characteristic: MagneticFluxDensity2DCharacteristic) -> None:
        """Test Magnetic Flux Density 2D characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "T"
        assert characteristic.value_type.value == "string"

        # Test normal parsing: X=1000, Y=-500 (in 10^-7 Tesla units)
        test_data = bytearray(struct.pack("<hh", 1000, -500))
        parsed = characteristic.decode_value(test_data)

        assert abs(parsed.x_axis - 1e-4) < 1e-10  # 1000 * 10^-7 = 1e-4
        assert abs(parsed.y_axis - (-5e-5)) < 1e-10  # -500 * 10^-7 = -5e-5
