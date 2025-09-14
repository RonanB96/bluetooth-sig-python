from __future__ import annotations

from dataclasses import dataclass

from bluetooth_sig.gatt.context import CharacteristicContext, DeviceInfo
from bluetooth_sig.types import CharacteristicData


@dataclass
class DummyCalibration:
    value: float


class CalibrationCharacteristic:
    def __init__(self, uuid: str = "calib", properties: set[str] | None = None):
        self._char_uuid = uuid

    def decode_value(self, data: bytearray, ctx=None):
        # simple calibration: single uint8
        return int(data[0])

    def encode_value(self, value):
        return bytearray([int(value)])


class MeasurementCharacteristic:
    def __init__(self, uuid: str = "meas", properties: set[str] | None = None):
        self._char_uuid = uuid

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None):
        raw = int.from_bytes(data[0:2], byteorder="little", signed=True)
        scale = 1.0
        if ctx and ctx.other_characteristics:
            calib = ctx.other_characteristics.get("calib")
            if calib and calib.value is not None:
                scale = float(calib.value)
        return raw * scale

    def encode_value(self, value):
        # not used in test
        return bytearray(int(value).to_bytes(2, byteorder="little", signed=True))


def test_context_parsing_simple():
    # Create fake parsed calibration
    calib_data = CharacteristicData(
        uuid="calib", name="Calibration", value=2, raw_data=b"\x02"
    )

    ctx = CharacteristicContext(
        device_info=DeviceInfo(address="00:11:22:33:44:55"),
        other_characteristics={"calib": calib_data},
    )

    meas = MeasurementCharacteristic()
    raw_meas = (123).to_bytes(2, byteorder="little", signed=True)

    parsed_val = meas.decode_value(bytearray(raw_meas), ctx)

    assert parsed_val == 123 * 2
