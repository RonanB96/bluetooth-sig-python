"""Test RSC measurement characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.rsc_measurement import (
    RSCMeasurementCharacteristic,
    RSCMeasurementData,
)

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestRSCMeasurementCharacteristic(CommonCharacteristicTests):
    """Test RSC Measurement characteristic functionality."""

    @pytest.fixture
    def characteristic(self) -> RSCMeasurementCharacteristic:
        """Fixture providing an RSC measurement characteristic."""
        return RSCMeasurementCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Expected UUID for RSC measurement characteristic."""
        return "2A53"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Valid test data for RSC measurement characteristic covering various flag combinations."""
        return [
            # Test 1: Basic RSC measurement (no optional fields)
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0x80,
                        0x02,  # speed = 2.5 m/s (640 * 1/256)
                        0xB4,  # cadence = 180 steps/min
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=0x00,
                    instantaneous_stride_length=None,
                    total_distance=None,
                ),
                description="Basic RSC measurement",
            ),
            # Test 2: RSC with stride length
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: stride length present
                        0x80,
                        0x02,  # speed = 2.5 m/s (640 * 1/256)
                        0xB4,  # cadence = 180 steps/min
                        0x55,
                        0x00,  # stride length = 0.85 m (85 * 0.01)
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=0x01,
                    instantaneous_stride_length=0.85,
                    total_distance=None,
                ),
                description="RSC measurement with stride length",
            ),
            # Test 3: RSC with total distance
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x02,  # flags: total distance present
                        0x80,
                        0x02,  # speed = 2.5 m/s
                        0xB4,  # cadence = 180 steps/min
                        0x10,
                        0x27,
                        0x00,
                        0x00,  # total distance = 1000.0 m (10000 * 0.1)
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=0x02,
                    instantaneous_stride_length=None,
                    total_distance=1000.0,
                ),
                description="RSC measurement with total distance",
            ),
            # Test 4: RSC with both optional fields
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x03,  # flags: stride length + total distance (0x01 | 0x02)
                        0x80,
                        0x02,  # speed = 2.5 m/s
                        0xB4,  # cadence = 180 steps/min
                        0x55,
                        0x00,  # stride length = 0.85 m
                        0x10,
                        0x27,
                        0x00,
                        0x00,  # total distance = 1000.0 m
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=0x03,
                    instantaneous_stride_length=0.85,
                    total_distance=1000.0,
                ),
                description="RSC measurement with both optional fields",
            ),
            # Test 5: Fast running speed
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x00,  # flags: no optional fields
                        0x80,
                        0x05,  # speed = 5.5 m/s (1408 * 1/256)
                        0xDC,  # cadence = 220 steps/min
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=5.5,
                    instantaneous_cadence=220,
                    flags=0x00,
                    instantaneous_stride_length=None,
                    total_distance=None,
                ),
                description="Fast running speed",
            ),
            # Test 6: Walking pace with long stride
            CharacteristicTestData(
                input_data=bytearray(
                    [
                        0x01,  # flags: stride length present
                        0x9A,
                        0x01,  # speed = 1.6015625 m/s (410 * 1/256)
                        0x78,  # cadence = 120 steps/min
                        0x50,
                        0x00,  # stride length = 0.80 m (80 * 0.01)
                    ]
                ),
                expected_value=RSCMeasurementData(
                    instantaneous_speed=1.6015625,  # 410/256 exact value
                    instantaneous_cadence=120,
                    flags=0x01,
                    instantaneous_stride_length=0.80,
                    total_distance=None,
                ),
                description="Walking pace with long stride",
            ),
        ]

    def test_rsc_measurement_invalid_data(self, characteristic: RSCMeasurementCharacteristic) -> None:
        """Test RSC measurement error handling."""
        # Too short data
        with pytest.raises(ValueError, match="RSC Measurement data must be at least 4 bytes"):
            characteristic.decode_value(bytearray([0x00, 0x01, 0x02]))

        # Missing required data
        with pytest.raises(ValueError, match="RSC Measurement data must be at least 4 bytes"):
            characteristic.decode_value(bytearray([0x00]))

    def test_rsc_measurement_encoding_units(self, characteristic: RSCMeasurementCharacteristic) -> None:
        """Test RSC measurement encoding units and precision."""
        # Test speed encoding (1/256 m/s resolution)
        test_data = bytearray([0x00, 0x01, 0x00, 0x00])  # speed = 1/256 m/s (1 * 1/256)
        result = characteristic.decode_value(test_data)
        assert abs(result.instantaneous_speed - (1 / 256)) < 1e-10

        # Test stride length encoding (0.01 m resolution)
        test_data = bytearray([0x01, 0x00, 0x01, 0x00, 0x01, 0x00])  # stride = 0.01 m
        result = characteristic.decode_value(test_data)
        assert result.instantaneous_stride_length == 0.01

        # Test total distance encoding (0.1 m resolution)
        test_data = bytearray([0x02, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00])  # distance = 0.1 m
        result = characteristic.decode_value(test_data)
        assert result.total_distance == 0.1
