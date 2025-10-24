"""Test magnetic flux density 3D characteristic."""

from __future__ import annotations

import struct

import pytest

from bluetooth_sig.gatt.characteristics.magnetic_flux_density_3d import MagneticFluxDensity3DCharacteristic
from bluetooth_sig.gatt.characteristics.templates import VectorData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestMagneticFluxDensity3DCharacteristic(CommonCharacteristicTests):
    """Test Magnetic Flux Density 3D characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> MagneticFluxDensity3DCharacteristic:
        """Provide Magnetic Flux Density 3D characteristic for testing."""
        return MagneticFluxDensity3DCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Magnetic Flux Density 3D characteristic."""
        return "2AA1"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Valid magnetic flux density 3D test data."""
        return CharacteristicTestData(
            input_data=bytearray(struct.pack("<hhh", 1000, -500, 2000)),
            expected_value=VectorData(x_axis=1e-4, y_axis=-5e-5, z_axis=2e-4),
            description="Magnetic flux density 3D X=1000, Y=-500, Z=2000",
        )

    def test_magnetic_flux_density_3d_parsing(self, characteristic: MagneticFluxDensity3DCharacteristic) -> None:
        """Test Magnetic Flux Density 3D characteristic parsing."""
        # Test metadata
        assert characteristic.unit == "T"
        assert characteristic.value_type.value == "string"

        # Test normal parsing: X=1000, Y=-500, Z=2000
        test_data = bytearray(struct.pack("<hhh", 1000, -500, 2000))
        parsed = characteristic.decode_value(test_data)

        assert abs(parsed.x_axis - 1e-4) < 1e-10
        assert abs(parsed.y_axis - (-5e-5)) < 1e-10
        assert abs(parsed.z_axis - 2e-4) < 1e-10
