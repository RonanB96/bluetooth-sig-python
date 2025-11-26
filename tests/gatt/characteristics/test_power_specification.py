"""Tests for Power Specification characteristic (0x2B06)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics import PowerSpecificationCharacteristic
from bluetooth_sig.gatt.characteristics.power_specification import PowerSpecificationData

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPowerSpecificationCharacteristic(CommonCharacteristicTests):
    """Test Power Specification characteristic implementation."""

    @pytest.fixture
    def characteristic(self) -> PowerSpecificationCharacteristic:
        """Provide Power Specification characteristic for testing."""
        return PowerSpecificationCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for Power Specification characteristic."""
        return "2B06"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        """Valid power specification test data covering various powers and edge cases."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),  # 0.0 W, 0.0 W, 0.0 W
                expected_value=PowerSpecificationData(minimum=0.0, typical=0.0, maximum=0.0),
                description="Zero power specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x0A, 0x00, 0x00, 0x14, 0x00, 0x00, 0x1E, 0x00, 0x00]),  # 1.0 W, 2.0 W, 3.0 W
                expected_value=PowerSpecificationData(minimum=1.0, typical=2.0, maximum=3.0),
                description="Normal power specification (1.0-2.0-3.0 W)",
            ),
            CharacteristicTestData(
                input_data=bytearray([0xFD, 0xFF, 0xFF, 0xFD, 0xFF, 0xFF, 0xFD, 0xFF, 0xFF]),  # Max W, Max W, Max W
                expected_value=PowerSpecificationData(minimum=1677721.3, typical=1677721.3, maximum=1677721.3),
                description="Maximum power specification",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x00, 0x00, 0x01, 0x00, 0x00, 0x01, 0x00, 0x00]),  # 0.1 W, 0.1 W, 0.1 W
                expected_value=PowerSpecificationData(minimum=0.1, typical=0.1, maximum=0.1),
                description="Minimum power specification (0.1 W each)",
            ),
        ]

    # === Power Specification-Specific Tests ===
    def test_power_specification_special_values(self, characteristic: PowerSpecificationCharacteristic) -> None:
        """Test special values for power specification."""
        # Test "value is not valid" (0xFFFFFE) for all fields
        result = characteristic.decode_value(bytearray([0xFE, 0xFF, 0xFF, 0xFE, 0xFF, 0xFF, 0xFE, 0xFF, 0xFF]))
        expected = PowerSpecificationData(minimum=None, typical=None, maximum=None)
        assert result == expected

        # Test "value is not known" (0xFFFFFF) for all fields
        result = characteristic.decode_value(bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]))
        expected = PowerSpecificationData(minimum=None, typical=None, maximum=None)
        assert result == expected

        # Test mixed valid and special values
        result = characteristic.decode_value(
            bytearray([0x0A, 0x00, 0x00, 0xFE, 0xFF, 0xFF, 0x14, 0x00, 0x00])  # 1.0 W, invalid, 2.0 W
        )
        expected = PowerSpecificationData(minimum=1.0, typical=None, maximum=2.0)
        assert result == expected

    def test_power_specification_encoding(self, characteristic: PowerSpecificationCharacteristic) -> None:
        """Test encoding power specification values."""
        # Test encoding normal values
        data = PowerSpecificationData(minimum=1.0, typical=2.0, maximum=3.0)
        encoded = characteristic.encode_value(data)
        assert encoded == bytearray([0x0A, 0x00, 0x00, 0x14, 0x00, 0x00, 0x1E, 0x00, 0x00])

        # Test encoding with None values (should encode as unknown)
        data = PowerSpecificationData(minimum=1.0, typical=None, maximum=2.0)
        encoded = characteristic.encode_value(data)
        assert encoded == bytearray([0x0A, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0x14, 0x00, 0x00])

        # Test encoding zero values
        data = PowerSpecificationData(minimum=0.0, typical=0.0, maximum=0.0)
        encoded = characteristic.encode_value(data)
        assert encoded == bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def test_power_specification_precision(self, characteristic: PowerSpecificationCharacteristic) -> None:
        """Test power specification precision and rounding."""
        # Test precision (0.1 W resolution)
        data = PowerSpecificationData(minimum=1.05, typical=2.15, maximum=3.25)
        encoded = characteristic.encode_value(data)
        # Should round to nearest 0.1 W: 1.1, 2.2, 3.3
        assert encoded == bytearray([0x0B, 0x00, 0x00, 0x16, 0x00, 0x00, 0x21, 0x00, 0x00])

        # Decode back to verify
        decoded = characteristic.decode_value(encoded)
        assert decoded.minimum == 1.1
        assert decoded.typical == 2.2
        assert decoded.maximum == 3.3

    def test_power_specification_data_class(self) -> None:
        """Test PowerSpecificationData class methods."""
        data1 = PowerSpecificationData(minimum=1.0, typical=2.0, maximum=3.0)
        data2 = PowerSpecificationData(minimum=1.0, typical=2.0, maximum=3.0)
        data3 = PowerSpecificationData(minimum=1.0, typical=2.0, maximum=4.0)

        # Test equality
        assert data1 == data2
        assert data1 != data3

        # Test repr
        repr_str = repr(data1)
        assert "minimum=1.0" in repr_str
        assert "typical=2.0" in repr_str
        assert "maximum=3.0" in repr_str
        assert "maximum=3.0" in repr_str
