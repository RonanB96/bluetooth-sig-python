"""Tests for descriptor integration with characteristics."""

from __future__ import annotations

from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.descriptors import CCCDDescriptor
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class TestDescriptorIntegration:
    """Test descriptor integration with characteristics."""

    def test_characteristic_descriptor_support(self) -> None:
        """Test that characteristics can have descriptors added."""

        # Create a mock characteristic that supports descriptors
        class MockCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789012"),
                name="Test Characteristic",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int.from_bytes(data, "little")

            def _encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, "little"))

        char = MockCharacteristic()

        # Add a descriptor
        cccd = CCCDDescriptor()
        char.add_descriptor(cccd)

        # Check that descriptor was added
        retrieved = char.get_descriptor("2902")
        assert retrieved is cccd

        # Check descriptors collection
        descriptors = char.get_descriptors()
        assert "00002902-0000-1000-8000-00805F9B34FB" in descriptors
        assert descriptors["00002902-0000-1000-8000-00805F9B34FB"] is cccd

    def test_characteristic_notification_support(self) -> None:
        """Test characteristic notification support detection."""

        class MockCharacteristic(CustomBaseCharacteristic):
            _info = CharacteristicInfo(
                uuid=BluetoothUUID("12345678-1234-1234-1234-123456789013"),
                name="Test Characteristic 2",
                unit="",
                value_type=ValueType.INT,
            )

            def _decode_value(
                self, data: bytearray, ctx: CharacteristicContext | None = None, *, validate: bool = True
            ) -> int:
                return int.from_bytes(data, "little")

            def _encode_value(self, data: int) -> bytearray:
                return bytearray(data.to_bytes(2, "little"))

        char = MockCharacteristic()

        # Without CCCD
        assert not char.can_notify()
        assert char.get_cccd() is None

        # With CCCD
        cccd = CCCDDescriptor()
        char.add_descriptor(cccd)
        assert char.can_notify()
        assert char.get_cccd() is cccd
