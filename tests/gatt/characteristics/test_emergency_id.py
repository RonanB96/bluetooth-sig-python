"""Tests for EmergencyIdCharacteristic (2B2D)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.emergency_id import EmergencyIdCharacteristic
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestEmergencyId(CommonCharacteristicTests):
    """Test suite for EmergencyIdCharacteristic."""

    @pytest.fixture
    def characteristic(self) -> EmergencyIdCharacteristic:
        return EmergencyIdCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2B2D"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray(b"\x01\x02\x03\x04\x05\x06"),
                b"\x01\x02\x03\x04\x05\x06",
                "6-byte emergency ID",
            ),
            CharacteristicTestData(
                bytearray(b"\xff\xfe\xfd\xfc\xfb\xfa"),
                b"\xff\xfe\xfd\xfc\xfb\xfa",
                "High-value emergency ID",
            ),
        ]

    def test_decode_exactly_6_bytes(self, characteristic: EmergencyIdCharacteristic) -> None:
        """Test that exactly 6 bytes are decoded."""
        data = bytearray(b"\x01\x02\x03\x04\x05\x06")
        result = characteristic.parse_value(data)
        assert result == b"\x01\x02\x03\x04\x05\x06"
        assert len(result) == 6

    def test_encode_wrong_length_raises(self, characteristic: EmergencyIdCharacteristic) -> None:
        """Test that encoding non-6-byte data raises CharacteristicEncodeError."""
        with pytest.raises(CharacteristicEncodeError, match="exactly 6 bytes"):
            characteristic.build_value(b"\x01\x02\x03")

    def test_all_zeros(self, characteristic: EmergencyIdCharacteristic) -> None:
        """Test all-zero emergency ID."""
        data = bytearray(b"\x00\x00\x00\x00\x00\x00")
        result = characteristic.parse_value(data)
        assert result == b"\x00\x00\x00\x00\x00\x00"
