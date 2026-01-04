from __future__ import annotations

import msgspec

from bluetooth_sig.gatt.characteristics.base import CharacteristicData
from bluetooth_sig.gatt.characteristics.custom import CustomBaseCharacteristic
from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext, DeviceInfo
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


class DummyCalibration(msgspec.Struct, kw_only=True):
    value: float


class CalibrationCharacteristic(CustomBaseCharacteristic):
    """Test calibration characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789001"),
        name="Test Calibration",
        unit="",
        value_type=ValueType.INT,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> int:
        # simple calibration: single uint8
        return int(data[0])

    def _encode_value(self, data: int) -> bytearray:
        return bytearray([int(data)])


class MeasurementCharacteristic(CustomBaseCharacteristic):
    """Test measurement characteristic."""

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("12345678-1234-1234-1234-123456789002"),
        name="Test Measurement",
        unit="",
        value_type=ValueType.FLOAT,
    )

    def _decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        raw = int.from_bytes(data[0:2], byteorder="little", signed=True)
        scale = 1.0
        if ctx and ctx.other_characteristics:
            calib = ctx.other_characteristics.get("calib")
            if calib and calib.value is not None:
                scale = float(calib.value)
        return raw * scale

    def _encode_value(self, data: int) -> bytearray:
        # not used in test
        return bytearray(int(data).to_bytes(2, byteorder="little", signed=True))


def test_context_parsing_simple() -> None:
    # Create fake parsed calibration using a mock characteristic

    calib_info = CharacteristicInfo(
        uuid=BluetoothUUID("2A19"),  # Use a valid UUID format
        name="Calibration",
        value_type=ValueType.INT,
        unit="",
    )
    calib_char = UnknownCharacteristic(info=calib_info)
    calib_data = CharacteristicData(characteristic=calib_char, value=2, raw_data=b"\x02", parse_success=True)

    ctx = CharacteristicContext(
        device_info=DeviceInfo(address="00:11:22:33:44:55"),
        other_characteristics={"calib": calib_data},  # type: ignore[dict-item]
    )

    meas = MeasurementCharacteristic()
    raw_meas = (123).to_bytes(2, byteorder="little", signed=True)

    parsed = meas.parse_value(bytearray(raw_meas), ctx)

    assert parsed.value == 123 * 2
