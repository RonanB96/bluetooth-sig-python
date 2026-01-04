"""Tests for auto-registration feature in CustomBaseCharacteristic.

This test suite verifies that custom characteristics can automatically
register themselves with the global BluetoothSIGTranslator singleton when instantiated.
"""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.types.data_types import CharacteristicInfo
from bluetooth_sig.types.uuid import BluetoothUUID


# A small self-contained test characteristic used only for these tests.
class LocalTemperatureCharacteristic(CustomBaseCharacteristic):
    """Simple custom characteristic used by auto-registration tests.

    This is intentionally minimal — it's only used to validate auto-registration
    logic (manual registration, auto-registration idempotence and parse). The
    decode/encode methods are trivial.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-5678-1234-567812345671"),
        name="Local Temperature Characteristic",
    )

    def _decode_value(self, data: bytearray, ctx: Any = None) -> float:  # noqa: ANN401
        # Expect 2-byte format: int8 (whole degrees) + uint8 decimal (00-99)
        if len(data) != 2:
            # For test, accept single byte too
            return float(int(data[0])) if data else 0.0
        whole = int(data[0])
        dec = int(data[1])
        return float(whole + dec / 100.0)

    def _encode_value(self, data: float) -> bytearray:
        whole = int(data)
        dec = int((data - whole) * 100)
        return bytearray([whole & 0xFF, dec & 0xFF])


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset the singleton translator and registry tracker between tests."""
    # Reset the singleton instance
    BluetoothSIGTranslator._instance = None
    BluetoothSIGTranslator._instance_lock = False
    # Reset the registry tracker
    CustomBaseCharacteristic._registry_tracker.clear()


class TestAutoRegistration:
    """Test auto-registration feature for custom characteristics."""

    def test_manual_registration_still_works(self) -> None:
        """Test that manual registration still works (backward compatibility)."""
        # Get the singleton translator
        translator = BluetoothSIGTranslator.get_instance()

        # Create characteristic without auto-registration
        char = LocalTemperatureCharacteristic(auto_register=False)

        # Manually register with override=True since parse_characteristic will instantiate and try to auto-register
        info = char.__class__.get_configured_info()
        assert info is not None
        translator.register_custom_characteristic_class(str(info.uuid), LocalTemperatureCharacteristic, override=True)

        # Verify it's registered
        raw_data = bytes([0x18, 0x32])  # 24.50°C (24 whole + 50 decimal)
        result = translator.parse_characteristic(str(info.uuid), raw_data)
        assert result.value == 24.5

    def test_auto_registration_on_init(self) -> None:
        """Test that characteristic auto-registers when instantiated."""
        # Create characteristic with auto-registration (uses global singleton)
        char = LocalTemperatureCharacteristic(auto_register=True)

        # Verify it's registered by parsing data using the singleton
        translator = BluetoothSIGTranslator.get_instance()
        info = char.__class__.get_configured_info()
        assert info is not None

        raw_data = bytes([0x18, 0x32])  # 24.50°C (24 whole + 50 decimal)
        result = translator.parse_characteristic(str(info.uuid), raw_data)
        assert result.value == 24.5

    def test_auto_registration_idempotent(self) -> None:
        """Test that multiple instantiations don't cause duplicate registrations."""
        # Create multiple instances with auto-registration
        char1 = LocalTemperatureCharacteristic(auto_register=True)
        LocalTemperatureCharacteristic(auto_register=True)  # char2
        LocalTemperatureCharacteristic(auto_register=True)  # char3

        # Verify parsing still works (no errors from duplicate registration)
        translator = BluetoothSIGTranslator.get_instance()
        info = char1.__class__.get_configured_info()
        assert info is not None

        raw_data = bytes([0x18, 0x32])  # 24.50°C (24 whole + 50 decimal)
        result = translator.parse_characteristic(str(info.uuid), raw_data)
        assert result.value == 24.5

    def test_default_auto_register_is_true(self) -> None:
        """Test that auto_register defaults to True."""
        # Should auto-register when no auto_register parameter provided
        char = LocalTemperatureCharacteristic()

        # Verify characteristic was created and registered
        assert char is not None
        info = char.__class__.get_configured_info()
        assert info is not None

        # Verify it's accessible via singleton
        translator = BluetoothSIGTranslator.get_instance()
        raw_data = bytes([0x18, 0x32])  # 24.50°C
        result = translator.parse_characteristic(str(info.uuid), raw_data)
        assert result.value == 24.5

    def test_dynamic_custom_characteristic_auto_registration(self) -> None:
        """Test auto-registration with dynamically created custom characteristic."""

        class DynamicCharacteristic(CustomBaseCharacteristic):
            """Test characteristic created at runtime."""

            _info = CharacteristicInfo(
                name="Dynamic Test Characteristic",
                uuid=BluetoothUUID("12345678-1234-5678-1234-567812345678"),
            )

            def _decode_value(self, data: bytearray, ctx: Any = None) -> int:  # noqa: ANN401
                """Decode single byte as integer."""
                return int(data[0]) if data else 0

        # Auto-register the dynamic characteristic
        DynamicCharacteristic(auto_register=True)  # char

        # Verify it's registered with the singleton
        translator = BluetoothSIGTranslator.get_instance()
        result = translator.parse_characteristic(
            "12345678-1234-5678-1234-567812345678",
            bytes([42]),
        )
        assert result.value == 42
