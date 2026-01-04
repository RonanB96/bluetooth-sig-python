from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import BodySensorLocation, HeartRateMeasurementCharacteristic
from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.characteristics.heart_rate_measurement import (
    HeartRateData,
    HeartRateMeasurementFlags,
    SensorContactState,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestHeartRateMeasurementCharacteristic(CommonCharacteristicTests):
    characteristic_cls = HeartRateMeasurementCharacteristic

    @pytest.fixture
    def characteristic(self) -> BaseCharacteristic[Any]:
        return HeartRateMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2A37"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData | list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x50]),  # Flags=0, HR=80 BPM (8-bit)
                expected_value=HeartRateData(
                    heart_rate=80,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags(0),
                ),
                description="Basic 8-bit heart rate",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0xC8, 0x00]),  # Flags=1 (16-bit HR), HR=200 BPM
                expected_value=HeartRateData(
                    heart_rate=200,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags.HEART_RATE_VALUE_FORMAT_UINT16,
                ),
                description="16-bit heart rate",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x0E, 0x4B, 0x80, 0x00]
                ),  # Flags=14 (sensor contact detected + energy), HR=75, Energy=128 kJ
                expected_value=HeartRateData(
                    heart_rate=75,
                    sensor_contact=SensorContactState.DETECTED,
                    energy_expended=128,
                    rr_intervals=(),
                    flags=HeartRateMeasurementFlags.SENSOR_CONTACT_SUPPORTED
                    | HeartRateMeasurementFlags.SENSOR_CONTACT_DETECTED
                    | HeartRateMeasurementFlags.ENERGY_EXPENDED_PRESENT,
                ),
                description="Sensor contact detected with energy expended",
            ),
            CharacteristicTestData(
                input_data=bytearray(
                    [0x10, 0x5A, 0x00, 0x08, 0x00, 0x10]
                ),  # Flags=16 (RR intervals), HR=90, RR=2.0s (2048/1024), 4.0s (4096/1024)
                expected_value=HeartRateData(
                    heart_rate=90,
                    sensor_contact=SensorContactState.NOT_SUPPORTED,
                    energy_expended=None,
                    rr_intervals=(2.0, 4.0),
                    flags=HeartRateMeasurementFlags.RR_INTERVAL_PRESENT,
                ),
                description="Heart rate with RR intervals",
            ),
        ]

    def test_heart_rate_without_context_backward_compatibility(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that parsing works without context (backward compatibility)."""
        hr_data = bytearray([0x00, 0x3C])  # 60 BPM
        result = characteristic.parse_value(hr_data, ctx=None)

        assert isinstance(result, HeartRateData)
        assert result.heart_rate == 60
        assert result.sensor_location is None  # No context available

    def test_heart_rate_with_sensor_location_context(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test heart rate parsing with sensor location from context."""
        from typing import cast

        from bluetooth_sig.gatt.characteristics.base import CharacteristicData
        from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
        from bluetooth_sig.gatt.context import CharacteristicContext
        from bluetooth_sig.types import CharacteristicDataProtocol, CharacteristicInfo
        from bluetooth_sig.types.uuid import BluetoothUUID

        # Mock context with sensor location (Body Sensor Location = 0x2A38)
        # Use full UUID format as that's what get_context_characteristic expects
        sensor_location_char = UnknownCharacteristic(
            info=CharacteristicInfo(
                uuid=BluetoothUUID("2A38"),
                name="Body Sensor Location",
            )
        )
        sensor_location = CharacteristicData(
            characteristic=sensor_location_char,
            value=2,  # 2 = Wrist
            raw_data=bytes([0x02]),
            parse_success=True,
            error_message="",
        )

        # Store with full UUID format to match how translator builds context
        sensor_location_uuid = BluetoothUUID("2A38").dashed_form
        ctx = CharacteristicContext(
            other_characteristics={sensor_location_uuid: cast(CharacteristicDataProtocol, sensor_location)}
        )

        # Parse with context
        hr_data = bytearray([0x00, 0x3C])  # 60 BPM
        result = characteristic.parse_value(hr_data, ctx)

        assert result.heart_rate == 60
        assert result.sensor_location == BodySensorLocation.WRIST

    def test_heart_rate_with_different_sensor_locations(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test heart rate with various sensor locations."""
        from typing import cast

        from bluetooth_sig.gatt.characteristics.base import CharacteristicData
        from bluetooth_sig.gatt.characteristics.unknown import UnknownCharacteristic
        from bluetooth_sig.gatt.context import CharacteristicContext
        from bluetooth_sig.types import CharacteristicDataProtocol, CharacteristicInfo
        from bluetooth_sig.types.uuid import BluetoothUUID

        location_map = {
            0: BodySensorLocation.OTHER,
            1: BodySensorLocation.CHEST,
            2: BodySensorLocation.WRIST,
            3: BodySensorLocation.FINGER,
            4: BodySensorLocation.HAND,
            5: BodySensorLocation.EAR_LOBE,
            6: BodySensorLocation.FOOT,
        }

        for location_value, expected_enum in location_map.items():
            sensor_location_char = UnknownCharacteristic(
                info=CharacteristicInfo(
                    uuid=BluetoothUUID("2A38"),
                    name="Body Sensor Location",
                )
            )
            sensor_location = CharacteristicData(
                characteristic=sensor_location_char,
                value=location_value,
                raw_data=bytes([location_value]),
                parse_success=True,
                error_message="",
            )

            # Use full UUID format to match translator behaviour
            sensor_location_uuid = BluetoothUUID("2A38").dashed_form
            ctx = CharacteristicContext(
                other_characteristics={sensor_location_uuid: cast(CharacteristicDataProtocol, sensor_location)}
            )

            hr_data = bytearray([0x00, 0x46])  # 70 BPM
            result = characteristic.parse_value(hr_data, ctx)

            assert result.heart_rate == 70
            assert result.sensor_location == expected_enum

    def test_heart_rate_context_with_missing_sensor_location(self, characteristic: BaseCharacteristic[Any]) -> None:
        """Test that heart rate works when context exists but sensor location doesn't."""
        from bluetooth_sig.gatt.context import CharacteristicContext

        # Context without sensor location
        ctx = CharacteristicContext(other_characteristics={})

        hr_data = bytearray([0x00, 0x50])  # 80 BPM
        result = characteristic.parse_value(hr_data, ctx)

        assert result.heart_rate == 80
        assert result.sensor_location is None  # Graceful handling of missing context data
