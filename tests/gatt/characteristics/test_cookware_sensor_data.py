from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.battery_level import BatteryLevelCharacteristic
from bluetooth_sig.gatt.characteristics.cooking_common import COOKING_TEMPERATURE, HUMIDITY
from bluetooth_sig.gatt.characteristics.cooking_sensor_common import CookingSensorValue
from bluetooth_sig.gatt.characteristics.cookware_sensor_data import (  # type: ignore[import-untyped]
    CookwareSensorDataCharacteristic,
    CookwareSensorDataValue,
    CookwareSensorStatus,
)
from bluetooth_sig.gatt.characteristics.pressure import PressureCharacteristic
from bluetooth_sig.gatt.constants import SIZE_UUID16
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.gatt.descriptors.cooking_sensor_info import CookingSensorInfoDescriptor
from bluetooth_sig.gatt.exceptions import CharacteristicEncodeError, CharacteristicParseError, SpecialValueDetectedError
from bluetooth_sig.types import SpecialValueType
from bluetooth_sig.types.uuid import BluetoothUUID

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests

# Permitted Cookware Sensor Data formats resolve their UUIDs from the canonical
# characteristics rather than hardcoding hex values.
_TEMPERATURE_SENSOR_UUID = COOKING_TEMPERATURE.uuid
_HUMIDITY_SENSOR_UUID = HUMIDITY.uuid
_PRESSURE_SENSOR_UUID = PressureCharacteristic().uuid
# A real SIG characteristic that is NOT a permitted cookware sensor format.
_UNPERMITTED_SENSOR_UUID = BatteryLevelCharacteristic().uuid


class TestCookwareSensorDataCharacteristic(CommonCharacteristicTests):
    @pytest.fixture
    def characteristic(self) -> CookwareSensorDataCharacteristic:
        return CookwareSensorDataCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2C2C"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        # Sensor data is context-dependent; all entries use the temperature sensor
        # so the overridden parse/round-trip tests can supply a single descriptor context.
        return [
            CharacteristicTestData(
                bytearray([0x00, 0xC8, 0x00]),
                CookwareSensorDataValue(
                    sensor_status=CookwareSensorStatus.NO_ERROR,
                    sensor_data=CookingSensorValue(sensor_uuid=_TEMPERATURE_SENSOR_UUID, value=20.0),
                ),
                "temperature 20.0C",
            ),
            CharacteristicTestData(
                bytearray([0x00, 0x2C, 0x01]),
                CookwareSensorDataValue(
                    sensor_status=CookwareSensorStatus.NO_ERROR,
                    sensor_data=CookingSensorValue(sensor_uuid=_TEMPERATURE_SENSOR_UUID, value=30.0),
                ),
                "temperature 30.0C",
            ),
        ]

    def test_parse_valid_data_succeeds(
        self, characteristic: BaseCharacteristic[Any], valid_test_data: list[CharacteristicTestData]
    ) -> None:
        ctx = _sensor_context(_TEMPERATURE_SENSOR_UUID)
        for test_case in valid_test_data:
            result = characteristic.parse_value(test_case.input_data, ctx)
            self._assert_values_equal(result, test_case.expected_value, test_case.description)

    def test_decode_valid_data_returns_expected_value(
        self, characteristic: BaseCharacteristic[Any], valid_test_data: list[CharacteristicTestData]
    ) -> None:
        ctx = _sensor_context(_TEMPERATURE_SENSOR_UUID)
        for test_case in valid_test_data:
            result = characteristic.parse_value(test_case.input_data, ctx)
            self._assert_values_equal(result, test_case.expected_value, test_case.description)

    def test_parse_decode_consistency(
        self, characteristic: BaseCharacteristic[Any], valid_test_data: list[CharacteristicTestData]
    ) -> None:
        ctx = _sensor_context(_TEMPERATURE_SENSOR_UUID)
        test_case = valid_test_data[0]
        parse_result = characteristic.parse_value(test_case.input_data, ctx)
        decode_result = characteristic._decode_value(test_case.input_data, ctx)
        self._assert_values_equal(parse_result, decode_result, "parse vs decode consistency")

    def test_round_trip(
        self, characteristic: BaseCharacteristic[Any], valid_test_data: list[CharacteristicTestData]
    ) -> None:
        ctx = _sensor_context(_TEMPERATURE_SENSOR_UUID)
        for test_case in valid_test_data:
            parsed = characteristic.parse_value(test_case.input_data, ctx)
            encoded = characteristic.build_value(parsed)
            assert encoded == test_case.input_data, f"Round trip failed for {test_case.description}"

    def test_uuid_resolution(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        assert characteristic.uuid.short_form == "2C2C"

    def test_short_payload_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray())

    def test_missing_sensor_info_context_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([int(CookwareSensorStatus.NO_ERROR), 0xC8, 0x00]))

    def test_rfu_status_bits_parse_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x04, 0xC8, 0x00]), _sensor_context(_TEMPERATURE_SENSOR_UUID))

    def test_rfu_status_bits_build_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicEncodeError):
            characteristic.build_value(
                CookwareSensorDataValue(
                    sensor_status=CookwareSensorStatus(0x04),
                    sensor_data=CookingSensorValue(sensor_uuid=_TEMPERATURE_SENSOR_UUID, value=20.0),
                )
            )

    def test_temperature_sensor_data_uses_cooking_sensor_info_context(
        self, characteristic: CookwareSensorDataCharacteristic
    ) -> None:
        sensor_uuid = _TEMPERATURE_SENSOR_UUID
        parsed = characteristic.parse_value(bytearray([0x00, 0xC8, 0x00]), _sensor_context(sensor_uuid))
        assert parsed == CookwareSensorDataValue(
            sensor_status=CookwareSensorStatus.NO_ERROR,
            sensor_data=CookingSensorValue(sensor_uuid=sensor_uuid, value=20.0),
        )
        assert characteristic.build_value(parsed) == bytearray([0x00, 0xC8, 0x00])

    def test_humidity_sensor_data_uses_cooking_sensor_info_context(
        self, characteristic: CookwareSensorDataCharacteristic
    ) -> None:
        sensor_uuid = _HUMIDITY_SENSOR_UUID
        parsed = characteristic.parse_value(bytearray([0x00, 0xD2, 0x0F]), _sensor_context(sensor_uuid))
        assert parsed == CookwareSensorDataValue(
            sensor_status=CookwareSensorStatus.NO_ERROR,
            sensor_data=CookingSensorValue(sensor_uuid=sensor_uuid, value=40.5),
        )
        assert characteristic.build_value(parsed) == bytearray([0x00, 0xD2, 0x0F])

    def test_pressure_sensor_data_uses_cooking_sensor_info_context(
        self, characteristic: CookwareSensorDataCharacteristic
    ) -> None:
        sensor_uuid = _PRESSURE_SENSOR_UUID
        parsed = characteristic.parse_value(bytearray([0x00, 0x02, 0x76, 0x0F, 0x00]), _sensor_context(sensor_uuid))
        assert parsed == CookwareSensorDataValue(
            sensor_status=CookwareSensorStatus.NO_ERROR,
            sensor_data=CookingSensorValue(sensor_uuid=sensor_uuid, value=101325.0),
        )
        assert characteristic.build_value(parsed) == bytearray([0x00, 0x02, 0x76, 0x0F, 0x00])

    def test_unpermitted_sensor_uuid_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0x64]), _sensor_context(_UNPERMITTED_SENSOR_UUID))

    def test_context_sensor_data_length_mismatch_fails(self, characteristic: CookwareSensorDataCharacteristic) -> None:
        with pytest.raises(CharacteristicParseError):
            characteristic.parse_value(bytearray([0x00, 0xC8]), _sensor_context(_TEMPERATURE_SENSOR_UUID))

    def test_temperature_unknown_sentinel_raises_special_value(
        self, characteristic: CookwareSensorDataCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x00, 0x80]), _sensor_context(_TEMPERATURE_SENSOR_UUID))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN

    def test_humidity_unknown_sentinel_raises_special_value(
        self, characteristic: CookwareSensorDataCharacteristic
    ) -> None:
        with pytest.raises(SpecialValueDetectedError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0xFF, 0xFF]), _sensor_context(_HUMIDITY_SENSOR_UUID))
        assert exc_info.value.special_value.value_type == SpecialValueType.UNKNOWN


def _sensor_context(sensor_uuid: BluetoothUUID) -> CharacteristicContext:
    descriptor = CookingSensorInfoDescriptor()
    descriptor_data = descriptor.parse_value(
        int(sensor_uuid.short_form, 16).to_bytes(SIZE_UUID16, byteorder="little") + bytes([0x00, 0xFF, 0x00])
    )
    return CharacteristicContext(descriptors={str(descriptor.uuid): descriptor_data})
