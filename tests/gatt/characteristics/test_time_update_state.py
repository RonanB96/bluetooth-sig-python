"""Tests for Time Update State characteristic (0x2A17)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.time_update_state import (
    TimeUpdateCurrentState,
    TimeUpdateResult,
    TimeUpdateState,
    TimeUpdateStateCharacteristic,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestTimeUpdateStateCharacteristic(CommonCharacteristicTests):
    """Test suite for Time Update State characteristic.

    Inherits behavioural tests from CommonCharacteristicTests.
    Adds time update state-specific validation and edge cases.
    """

    @pytest.fixture
    def characteristic(self) -> TimeUpdateStateCharacteristic:
        """Return a Time Update State characteristic instance."""
        return TimeUpdateStateCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        """Return the expected UUID for Time Update State characteristic."""
        return "2A17"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        """Return valid test data for time update state."""
        return [
            CharacteristicTestData(
                input_data=bytearray([0x00, 0x00]),
                expected_value=TimeUpdateState(
                    current_state=TimeUpdateCurrentState.IDLE,
                    result=TimeUpdateResult.SUCCESSFUL,
                ),
                description="Idle state with successful result",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x01, 0x01]),
                expected_value=TimeUpdateState(
                    current_state=TimeUpdateCurrentState.PENDING,
                    result=TimeUpdateResult.CANCELED,
                ),
                description="Pending state with canceled result",
            ),
            CharacteristicTestData(
                input_data=bytearray([0x02, 0x02]),
                expected_value=TimeUpdateState(
                    current_state=TimeUpdateCurrentState.UPDATING,
                    result=TimeUpdateResult.NO_CONNECTION_TO_REFERENCE,
                ),
                description="Updating state with no connection result",
            ),
        ]

    def test_idle_state_successful_result(self) -> None:
        """Test IDLE state with SUCCESSFUL result."""
        char = TimeUpdateStateCharacteristic()
        state = TimeUpdateState(
            current_state=TimeUpdateCurrentState.IDLE,
            result=TimeUpdateResult.SUCCESSFUL,
        )

        # Test encoding
        encoded = char.build_value(state)
        assert encoded == bytearray([0x00, 0x00])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded == state

    def test_pending_state_canceled_result(self) -> None:
        """Test PENDING state with CANCELED result."""
        char = TimeUpdateStateCharacteristic()
        state = TimeUpdateState(
            current_state=TimeUpdateCurrentState.PENDING,
            result=TimeUpdateResult.CANCELED,
        )

        # Test encoding
        encoded = char.build_value(state)
        assert encoded == bytearray([0x01, 0x01])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded == state

    def test_updating_state_timeout_result(self) -> None:
        """Test UPDATING state with TIMEOUT result."""
        char = TimeUpdateStateCharacteristic()
        state = TimeUpdateState(
            current_state=TimeUpdateCurrentState.UPDATING,
            result=TimeUpdateResult.TIMEOUT,
        )

        # Test encoding
        encoded = char.build_value(state)
        assert encoded == bytearray([0x02, 0x04])

        # Test decoding
        decoded = char.parse_value(encoded)
        assert decoded == state

    def test_invalid_length_raises_error(self) -> None:
        """Test that invalid data lengths result in parse failure."""
        char = TimeUpdateStateCharacteristic()

        # Test too short - parse_value returns parse_success=False
        result = char.parse_value(bytearray([0x00]))
        assert result.parse_success is False
        assert result.error_message == "Time Update State requires 2 bytes, got 1"

        # Test too long - also returns parse_success=False
        result = char.parse_value(bytearray([0x00, 0x00, 0x00]))
        assert result.parse_success is False
        assert result.error_message == "Time Update State requires 2 bytes, got 3"

    def test_invalid_current_state_raises_error(self) -> None:
        """Test that invalid current state values result in parse failure."""
        char = TimeUpdateStateCharacteristic()

        # Test invalid current state - parse_value returns parse_success=False
        result = char.parse_value(bytearray([0xFF, 0x00]))
        assert result.parse_success is False

    def test_invalid_result_raises_error(self) -> None:
        """Test that invalid result values result in parse failure."""
        char = TimeUpdateStateCharacteristic()

        # Test invalid result - parse_value returns parse_success=False
        result = char.parse_value(bytearray([0x00, 0xFF]))
        assert result.parse_success is False

    def test_current_state_enum_values(self) -> None:
        """Test that current state enum has expected values."""
        assert TimeUpdateCurrentState.IDLE.value == 0x00
        assert TimeUpdateCurrentState.PENDING.value == 0x01
        assert TimeUpdateCurrentState.UPDATING.value == 0x02

    def test_result_enum_values(self) -> None:
        """Test that result enum has expected values."""
        assert TimeUpdateResult.SUCCESSFUL.value == 0x00
        assert TimeUpdateResult.CANCELED.value == 0x01
        assert TimeUpdateResult.NO_CONNECTION_TO_REFERENCE.value == 0x02
        assert TimeUpdateResult.REFERENCE_RESPONDED_WITH_ERROR.value == 0x03
        assert TimeUpdateResult.TIMEOUT.value == 0x04
        assert TimeUpdateResult.UPDATE_NOT_ATTEMPTED_AFTER_RESET.value == 0x05
