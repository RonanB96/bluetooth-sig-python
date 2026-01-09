"""Test RSC measurement characteristic."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.rsc_feature import RSCFeatureCharacteristic
from bluetooth_sig.gatt.characteristics.rsc_measurement import (
    RSCMeasurementCharacteristic,
    RSCMeasurementData,
    RSCMeasurementFlags,
)
from bluetooth_sig.gatt.exceptions import CharacteristicParseError

from .test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests, DependencyTestData


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
    def dependency_test_data(self) -> list[DependencyTestData]:
        """Test data for optional RSC Feature dependency."""
        measurement_data = bytearray(
            [
                0x00,  # flags: no optional fields
                0x80,
                0x02,  # speed = 2.5 m/s (640 * 1/256)
                0xB4,  # cadence = 180 steps/min
            ]
        )

        return [
            DependencyTestData(
                with_dependency_data={
                    str(RSCMeasurementCharacteristic.get_class_uuid()): measurement_data,  # RSC Measurement
                    str(RSCFeatureCharacteristic.get_class_uuid()): bytearray(
                        [0x01, 0x00]
                    ),  # RSC Feature: instantaneous stride length supported
                },
                without_dependency_data=measurement_data,
                expected_with=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=RSCMeasurementFlags(0x00),
                    instantaneous_stride_length=None,
                    total_distance=None,
                ),
                expected_without=RSCMeasurementData(
                    instantaneous_speed=2.5,
                    instantaneous_cadence=180,
                    flags=RSCMeasurementFlags(0x00),
                    instantaneous_stride_length=None,
                    total_distance=None,
                ),
                description="RSC measurement with optional feature characteristic present",
            ),
        ]

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
                    flags=RSCMeasurementFlags(0x00),
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
                    flags=RSCMeasurementFlags.INSTANTANEOUS_STRIDE_LENGTH_PRESENT,
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
                    flags=RSCMeasurementFlags.TOTAL_DISTANCE_PRESENT,
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
                    flags=(
                        RSCMeasurementFlags.INSTANTANEOUS_STRIDE_LENGTH_PRESENT
                        | RSCMeasurementFlags.TOTAL_DISTANCE_PRESENT
                    ),
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
                    flags=RSCMeasurementFlags(0x00),
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
                    flags=RSCMeasurementFlags.INSTANTANEOUS_STRIDE_LENGTH_PRESENT,
                    instantaneous_stride_length=0.80,
                    total_distance=None,
                ),
                description="Walking pace with long stride",
            ),
        ]

    def test_rsc_measurement_invalid_data(self, characteristic: RSCMeasurementCharacteristic) -> None:
        """Test RSC measurement error handling."""
        # Too short data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00, 0x01, 0x02]))
        assert "at least 4 bytes" in str(exc_info.value)

        # Missing required data
        with pytest.raises(CharacteristicParseError) as exc_info:
            characteristic.parse_value(bytearray([0x00]))
        assert "at least 4 bytes" in str(exc_info.value)

    def test_rsc_measurement_encoding_units(self, characteristic: RSCMeasurementCharacteristic) -> None:
        """Test RSC measurement encoding units and precision."""
        # Test speed encoding (1/256 m/s resolution)
        test_data = bytearray([0x00, 0x01, 0x00, 0x00])  # speed = 1/256 m/s (1 * 1/256)
        result = characteristic.parse_value(test_data)
        assert result is not None
        assert abs(result.instantaneous_speed - (1 / 256)) < 1e-10

        # Test stride length encoding (0.01 m resolution)
        test_data = bytearray([0x01, 0x00, 0x01, 0x00, 0x01, 0x00])  # stride = 0.01 m
        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.instantaneous_stride_length == 0.01

        # Test total distance encoding (0.1 m resolution)
        test_data = bytearray([0x02, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00])  # distance = 0.1 m
        result = characteristic.parse_value(test_data)
        assert result is not None
        assert result.total_distance == 0.1

    def test_rsc_measurement_declares_dependencies(self) -> None:
        """Test that RSC Measurement declares RSC Feature as optional dependency.

        This is critical for ensuring proper parsing order in batch operations.
        Without this declaration, RSC Feature might be parsed AFTER RSC Measurement,
        preventing cross-validation.
        """
        from bluetooth_sig.gatt.characteristics.rsc_feature import RSCFeatureCharacteristic

        char = RSCMeasurementCharacteristic()
        feature_uuid = str(RSCFeatureCharacteristic.get_class_uuid())

        # Verify optional dependency is declared
        assert char.optional_dependencies, "RSC Measurement should declare optional dependencies"
        assert feature_uuid.upper() in [dep.upper() for dep in char.optional_dependencies], (
            f"RSC Measurement should declare dependency on RSC Feature ({feature_uuid})"
        )

        # Verify it's optional, not required (measurement can work without feature)
        assert not char.required_dependencies or feature_uuid.upper() not in [
            dep.upper() for dep in char.required_dependencies
        ], "RSC Feature should be optional, not required"
