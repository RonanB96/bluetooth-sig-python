"""Tests for Position Quality characteristic."""

from __future__ import annotations

from typing import Any

import pytest

from bluetooth_sig.gatt.characteristics import PositionQualityCharacteristic
from bluetooth_sig.gatt.characteristics.position_quality import (
    PositionQualityData,
    PositionQualityFlags,
    PositionStatus,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestPositionQualityCharacteristic(CommonCharacteristicTests):
    """Test suite for Position Quality characteristic.

    Inherits behavioral tests from CommonCharacteristicTests.
    Only adds position quality-specific edge cases and domain validation.
    """

    @pytest.fixture
    def characteristic(self) -> PositionQualityCharacteristic:
        """Return a Position Quality characteristic instance."""
        return PositionQualityCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Position Quality characteristic."""
        return "2A69"

    @pytest.fixture
    def valid_test_data(self) -> CharacteristicTestData:
        """Return valid test data for position quality (basic quality metrics)."""
        # Position quality data: flags(2) + time_to_first_fix(2) + hdop(1) + vdop(1)
        data = bytearray(
            [
                0x64,
                0x00,  # flags (time_to_first_fix, hdop, vdop present)
                0x10,
                0x27,  # time_to_first_fix (1000 seconds)
                0x04,  # hdop (2.0)
                0x06,  # vdop (3.0)
            ]
        )
        return CharacteristicTestData(
            input_data=data,
            expected_value=PositionQualityData(
                flags=PositionQualityFlags(0x0064),
                number_of_beacons_in_solution=None,
                number_of_beacons_in_view=None,
                time_to_first_fix=1000.0,  # 10000 / 10
                ehpe=None,
                evpe=None,
                hdop=2.0,
                vdop=3.0,
                position_status=PositionStatus.NO_POSITION,
            ),
            description="Position Quality with HDOP, VDOP, and time to first fix",
        )

    # === Position Quality-Specific Tests ===
    @pytest.mark.parametrize(
        "flags,data,expected",
        [
            # Basic: time to first fix, HDOP, VDOP
            (
                0x0064,  # TIME_TO_FIRST_FIX_PRESENT | HDOP_PRESENT | VDOP_PRESENT
                bytearray([0x64, 0x00, 0x10, 0x27, 0x04, 0x06]),  # ttff=1000, hdop=2.0, vdop=3.0
                {
                    "number_of_beacons_in_solution": None,
                    "number_of_beacons_in_view": None,
                    "time_to_first_fix": 1000.0,  # 10000 / 10
                    "ehpe": None,
                    "evpe": None,
                    "hdop": 2.0,
                    "vdop": 3.0,
                },
            ),
            # Beacon counts
            (
                0x0003,  # NUMBER_OF_BEACONS_IN_SOLUTION_PRESENT | NUMBER_OF_BEACONS_IN_VIEW_PRESENT
                bytearray([0x03, 0x00, 0x05, 0x0A]),  # beacons_sol=5, beacons_view=10
                {
                    "number_of_beacons_in_solution": 5,
                    "number_of_beacons_in_view": 10,
                    "time_to_first_fix": None,
                    "ehpe": None,
                    "evpe": None,
                    "hdop": None,
                    "vdop": None,
                },
            ),
            # Position errors
            (
                0x0018,  # EHPE_PRESENT | EVPE_PRESENT
                bytearray([0x18, 0x00, 0xC8, 0x00, 0x00, 0x00, 0x2C, 0x01, 0x00, 0x00]),  # ehpe=2.0, evpe=3.0
                {
                    "number_of_beacons_in_solution": None,
                    "number_of_beacons_in_view": None,
                    "time_to_first_fix": None,
                    "ehpe": 2.0,
                    "evpe": 3.0,
                    "hdop": None,
                    "vdop": None,
                },
            ),
            # DOP values only
            (
                0x0060,  # HDOP_PRESENT | VDOP_PRESENT
                bytearray([0x60, 0x00, 0x08, 0x0A]),  # hdop=4.0, vdop=5.0
                {
                    "number_of_beacons_in_solution": None,
                    "number_of_beacons_in_view": None,
                    "time_to_first_fix": None,
                    "ehpe": None,
                    "evpe": None,
                    "hdop": 4.0,
                    "vdop": 5.0,
                },
            ),
        ],
    )
    def test_position_quality_flag_combinations(
        self, characteristic: PositionQualityCharacteristic, flags: int, data: bytearray, expected: dict[str, Any]
    ) -> None:
        """Test position quality with various flag combinations."""
        result = characteristic.decode_value(data)
        for field, expected_value in expected.items():
            actual_value = getattr(result, field)
            assert actual_value == expected_value, f"Field {field}: expected {expected_value}, got {actual_value}"

    def test_position_quality_all_fields(self, characteristic: PositionQualityCharacteristic) -> None:
        """Test position quality with all optional fields present."""
        # All fields present
        data = bytearray(
            [
                0xFF,
                0x00,  # flags (all fields present)
                0x05,  # number_of_beacons_in_solution (5)
                0x0A,  # number_of_beacons_in_view (10)
                0xE8,
                0x03,  # time_to_first_fix (1000)
                0xC8,
                0x00,
                0x00,
                0x00,  # ehpe (2.0)
                0x2C,
                0x01,
                0x00,
                0x00,  # evpe (3.0)
                0x08,  # hdop (4.0)
                0x0A,  # vdop (5.0)
            ]
        )

        result = characteristic.decode_value(data)
        assert result.number_of_beacons_in_solution == 5
        assert result.number_of_beacons_in_view == 10
        assert result.time_to_first_fix == 100.0
        assert result.ehpe == 2.0
        assert result.evpe == 3.0
        assert result.hdop == 4.0
        assert result.vdop == 5.0

    def test_position_quality_minimal_data(self, characteristic: PositionQualityCharacteristic) -> None:
        """Test position quality with minimal data (only flags)."""
        data = bytearray([0x00, 0x00])  # No fields present

        result = characteristic.decode_value(data)
        assert result.number_of_beacons_in_solution is None
        assert result.number_of_beacons_in_view is None
        assert result.time_to_first_fix is None
        assert result.ehpe is None
        assert result.evpe is None
        assert result.hdop is None
        assert result.vdop is None

    def test_position_quality_precision_values(self, characteristic: PositionQualityCharacteristic) -> None:
        """Test position quality precision values."""
        # Test maximum precision (0.1 for DOP values)
        data = bytearray(
            [
                0xC0,
                0x00,  # flags (ehpe, evpe, hdop, vdop present)
                0x01,  # ehpe (0.1)
                0x01,  # evpe (0.1)
                0x01,  # hdop (0.1)
                0x01,  # vdop (0.1)
            ]
        )

        result = characteristic.decode_value(data)
        assert result.ehpe is None
        assert result.evpe is None
        assert result.hdop is None
        assert result.vdop == 0.5
