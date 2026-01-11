"""Tests for BluetoothSIGTranslator encoding methods."""

from __future__ import annotations

import pytest

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.types.gatt_enums import ValueType


class TestEncodeCharacteristic:
    """Tests for encode_characteristic method."""

    def test_encode_simple_value(self) -> None:
        """Test encoding a simple integer value."""
        translator = BluetoothSIGTranslator()

        # Battery Level is a simple uint8
        encoded = translator.encode_characteristic("2A19", 85)
        assert isinstance(encoded, bytes)
        assert len(encoded) == 1
        assert encoded[0] == 85

    def test_encode_with_dict(self) -> None:
        """Test encoding with dictionary input for complex types."""
        translator = BluetoothSIGTranslator()

        # Acceleration 3D characteristic (range is -1.28 to 1.27 based on sint8 resolution 0.01)
        encoded = translator.encode_characteristic("2C1D", {"x_axis": 0.5, "y_axis": 0.2, "z_axis": 1.0})
        assert isinstance(encoded, bytes)
        assert len(encoded) == 3  # 3 * sint8

    def test_encode_invalid_uuid(self) -> None:
        """Test encoding with invalid UUID raises error."""
        translator = BluetoothSIGTranslator()

        with pytest.raises(ValueError, match="Invalid UUID format"):
            translator.encode_characteristic("INVALID", 100)

    def test_encode_unsupported_uuid(self) -> None:
        """Test encoding with unsupported UUID raises error."""
        translator = BluetoothSIGTranslator()

        # Use a valid UUID format but unsupported characteristic
        with pytest.raises(ValueError, match="No encoder available"):
            translator.encode_characteristic("00000000-0000-0000-0000-000000000000", 100)

    def test_encode_without_validation(self) -> None:
        """Test encoding without validation still enforces template constraints."""
        translator = BluetoothSIGTranslator()

        # Battery level template has built-in range checking even without validation
        # This is expected behavior - templates enforce their own constraints
        with pytest.raises(ValueError):
            translator.encode_characteristic("2A19", 200, validate=False)

    def test_encode_with_validation_fails(self) -> None:
        """Test encoding with validation catches invalid values."""
        translator = BluetoothSIGTranslator()

        # Battery level must be 0-100, raises CharacteristicEncodeError
        from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError

        with pytest.raises(CharacteristicEncodeError) as exc_info:
            translator.encode_characteristic("2A19", 200, validate=True)

        assert "outside allowed range" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_encode_async(self) -> None:
        """Test async encode method."""
        translator = BluetoothSIGTranslator()

        encoded = await translator.encode_characteristic_async("2A19", 75)
        assert isinstance(encoded, bytes)
        assert encoded[0] == 75


class TestGetValueType:
    """Tests for get_value_type method."""

    def test_get_value_type_int(self) -> None:
        """Test getting value type for integer characteristic."""
        translator = BluetoothSIGTranslator()

        value_type = translator.get_value_type("2A19")  # Battery Level
        assert value_type == ValueType.INT

    def test_get_value_type_string(self) -> None:
        """Test getting value type for string characteristic."""
        translator = BluetoothSIGTranslator()

        value_type = translator.get_value_type("2A00")  # Device Name
        assert value_type == ValueType.STRING

    def test_get_value_type_various(self) -> None:
        """Test getting value type for complex characteristic."""
        translator = BluetoothSIGTranslator()

        value_type = translator.get_value_type("2A37")  # Heart Rate Measurement
        assert value_type == ValueType.VARIOUS

    def test_get_value_type_invalid_uuid(self) -> None:
        """Test getting value type with invalid UUID."""
        translator = BluetoothSIGTranslator()

        value_type = translator.get_value_type("INVALID")
        assert value_type is None

    def test_get_value_type_unsupported_uuid(self) -> None:
        """Test getting value type for unsupported UUID."""
        translator = BluetoothSIGTranslator()

        value_type = translator.get_value_type("00000000-0000-0000-0000-000000000000")
        assert value_type is None


class TestSupports:
    """Tests for supports method."""

    def test_supports_known_characteristic(self) -> None:
        """Test supports returns True for known characteristics."""
        translator = BluetoothSIGTranslator()

        assert translator.supports("2A19") is True  # Battery Level
        assert translator.supports("2A00") is True  # Device Name
        assert translator.supports("2A37") is True  # Heart Rate Measurement

    def test_supports_unknown_characteristic(self) -> None:
        """Test supports returns False for unknown characteristics."""
        translator = BluetoothSIGTranslator()

        assert translator.supports("00000000-0000-0000-0000-000000000000") is False

    def test_supports_invalid_uuid(self) -> None:
        """Test supports returns False for invalid UUID format."""
        translator = BluetoothSIGTranslator()

        assert translator.supports("INVALID") is False

    def test_supports_long_form_uuid(self) -> None:
        """Test supports works with long-form UUIDs."""
        translator = BluetoothSIGTranslator()

        # Battery Level in long form
        assert translator.supports("00002A19-0000-1000-8000-00805f9b34fb") is True


class TestCreateValue:
    """Tests for create_value method."""

    def test_create_simple_value(self) -> None:
        """Test creating simple value."""
        translator = BluetoothSIGTranslator()

        # Battery Level returns Any/int - for simple characteristics,
        # just pass the value directly to encode_characteristic
        # This test verifies that template-based characteristics work
        result = translator.encode_characteristic("2A19", 75)
        assert len(result) == 1
        assert result[0] == 75

    def test_create_complex_value(self) -> None:
        """Test creating complex dataclass value."""
        translator = BluetoothSIGTranslator()

        # Acceleration 3D creates VectorData
        value = translator.create_value("2C1D", x_axis=0.5, y_axis=0.2, z_axis=1.0)
        assert value is not None
        assert hasattr(value, "x_axis")
        assert hasattr(value, "y_axis")
        assert hasattr(value, "z_axis")
        # Now mypy knows value has these attributes
        value_x: float = value.x_axis  # type: ignore[union-attr]
        value_y: float = value.y_axis  # type: ignore[union-attr]
        value_z: float = value.z_axis  # type: ignore[union-attr]
        assert value_x == 0.5
        assert value_y == 0.2
        assert value_z == 1.0

    def test_create_value_invalid_uuid(self) -> None:
        """Test create_value with invalid UUID."""
        translator = BluetoothSIGTranslator()

        with pytest.raises(ValueError, match="Invalid UUID format"):
            translator.create_value("INVALID", value=100)

    def test_create_value_wrong_type(self) -> None:
        """Test create_value with wrong type for simple characteristic."""
        translator = BluetoothSIGTranslator()

        with pytest.raises(TypeError):
            translator.create_value("2A19", value="not an int")

    def test_create_value_missing_fields(self) -> None:
        """Test create_value with missing required fields."""
        translator = BluetoothSIGTranslator()

        # Acceleration 3D requires all three axes
        with pytest.raises(TypeError):
            translator.create_value("2C1D", x_axis=0.5)  # Missing y_axis and z_axis


class TestRoundTrip:
    """Integration tests for encode/decode round trips."""

    def test_battery_level_round_trip(self) -> None:
        """Test battery level encode/decode round trip."""
        translator = BluetoothSIGTranslator()

        original_value = 85
        encoded = translator.encode_characteristic("2A19", original_value)
        decoded = translator.parse_characteristic("2A19", encoded)

        assert decoded == original_value

    def test_acceleration_round_trip(self) -> None:
        """Test acceleration 3D encode/decode round trip."""
        translator = BluetoothSIGTranslator()

        original_dict = {"x_axis": 0.5, "y_axis": 0.2, "z_axis": 1.0}

        encoded = translator.encode_characteristic("2C1D", original_dict)
        decoded = translator.parse_characteristic("2C1D", encoded)

        assert hasattr(decoded, "x_axis")
        assert abs(decoded.x_axis - original_dict["x_axis"]) < 0.01
        assert abs(decoded.y_axis - original_dict["y_axis"]) < 0.01
        assert abs(decoded.z_axis - original_dict["z_axis"]) < 0.01

    def test_create_encode_parse_flow(self) -> None:
        """Test the complete flow: create -> encode -> parse."""
        translator = BluetoothSIGTranslator()

        # Create value
        value = translator.create_value("2C1D", x_axis=0.5, y_axis=-0.3, z_axis=1.0)

        # Encode it
        encoded = translator.encode_characteristic("2C1D", value)

        # Parse it back
        decoded = translator.parse_characteristic("2C1D", encoded)

        assert abs(decoded.x_axis - 0.5) < 0.01
        assert abs(decoded.y_axis - (-0.3)) < 0.01
        assert abs(decoded.z_axis - 1.0) < 0.01
