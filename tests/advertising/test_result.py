"""Tests for InterpretationResult and InterpretationStatus."""

from __future__ import annotations

from bluetooth_sig.advertising.result import InterpretationResult, InterpretationStatus
from bluetooth_sig.advertising.state import DeviceAdvertisingState


class TestInterpretationStatus:
    """Tests for InterpretationStatus enum."""

    def test_success_value(self) -> None:
        """Test SUCCESS status value."""
        assert InterpretationStatus.SUCCESS.value == "success"

    def test_encryption_required_value(self) -> None:
        """Test ENCRYPTION_REQUIRED status value."""
        assert InterpretationStatus.ENCRYPTION_REQUIRED.value == "encryption_required"

    def test_decryption_failed_value(self) -> None:
        """Test DECRYPTION_FAILED status value."""
        assert InterpretationStatus.DECRYPTION_FAILED.value == "decryption_failed"

    def test_replay_detected_value(self) -> None:
        """Test REPLAY_DETECTED status value."""
        assert InterpretationStatus.REPLAY_DETECTED.value == "replay_detected"

    def test_duplicate_packet_value(self) -> None:
        """Test DUPLICATE_PACKET status value."""
        assert InterpretationStatus.DUPLICATE_PACKET.value == "duplicate_packet"

    def test_parse_error_value(self) -> None:
        """Test PARSE_ERROR status value."""
        assert InterpretationStatus.PARSE_ERROR.value == "parse_error"

    def test_unsupported_version_value(self) -> None:
        """Test UNSUPPORTED_VERSION status value."""
        assert InterpretationStatus.UNSUPPORTED_VERSION.value == "unsupported_version"


class TestInterpretationResult:
    """Tests for InterpretationResult struct."""

    def test_default_success(self) -> None:
        """Test default result is SUCCESS with no data."""
        result: InterpretationResult[str] = InterpretationResult()
        assert result.status == InterpretationStatus.SUCCESS
        assert result.data is None
        assert result.is_success is True
        assert result.is_error is False

    def test_success_with_data(self) -> None:
        """Test successful result with data."""
        result: InterpretationResult[dict[str, float]] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data={"temperature": 25.5, "humidity": 60.0},
        )
        assert result.status == InterpretationStatus.SUCCESS
        assert result.data == {"temperature": 25.5, "humidity": 60.0}
        assert result.is_success is True

    def test_encryption_required(self) -> None:
        """Test ENCRYPTION_REQUIRED status."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.ENCRYPTION_REQUIRED,
            error_message="Bindkey required for decryption",
        )
        assert result.status == InterpretationStatus.ENCRYPTION_REQUIRED
        assert result.is_success is False
        assert result.is_error is True
        assert result.error_message == "Bindkey required for decryption"

    def test_parse_error_with_message(self) -> None:
        """Test PARSE_ERROR with error message."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.PARSE_ERROR,
            error_message="Invalid payload length",
        )
        assert result.status == InterpretationStatus.PARSE_ERROR
        assert result.is_error is True
        assert result.error_message == "Invalid payload length"

    def test_duplicate_packet_not_error(self) -> None:
        """Test DUPLICATE_PACKET is not considered an error."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.DUPLICATE_PACKET,
        )
        assert result.status == InterpretationStatus.DUPLICATE_PACKET
        assert result.is_success is False
        assert result.is_error is False  # Duplicate is not an error

    def test_warnings(self) -> None:
        """Test result with warnings."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            warnings=["Low battery", "Weak signal"],
        )
        assert len(result.warnings) == 2
        assert "Low battery" in result.warnings
        assert "Weak signal" in result.warnings


class TestInterpretationResultStateUpdates:
    """Tests for InterpretationResult state update fields."""

    def test_updated_encryption_counter(self) -> None:
        """Test setting updated encryption counter."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_encryption_counter=42,
        )
        assert result.updated_encryption_counter == 42

    def test_updated_packet_id(self) -> None:
        """Test setting updated packet ID."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_packet_id=99,
        )
        assert result.updated_packet_id == 99

    def test_updated_bindkey_verified(self) -> None:
        """Test setting bindkey verification status."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_bindkey_verified=True,
        )
        assert result.updated_bindkey_verified is True

    def test_updated_device_type(self) -> None:
        """Test setting updated device type."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_device_type="BTHome sensor",
        )
        assert result.updated_device_type == "BTHome sensor"

    def test_updated_protocol_version(self) -> None:
        """Test setting updated protocol version."""
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_protocol_version="v2",
        )
        assert result.updated_protocol_version == "v2"


class TestApplyToState:
    """Tests for InterpretationResult.apply_to_state method."""

    def test_apply_no_updates(self) -> None:
        """Test apply with no updates does not change state."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        state.encryption.encryption_counter = 10

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
        )

        result.apply_to_state(state)
        assert state.encryption.encryption_counter == 10  # Unchanged

    def test_apply_encryption_counter(self) -> None:
        """Test applying encryption counter update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        state.encryption.encryption_counter = 10

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_encryption_counter=42,
        )

        result.apply_to_state(state)
        assert state.encryption.encryption_counter == 42

    def test_apply_packet_id(self) -> None:
        """Test applying packet ID update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_packet_id=99,
        )

        result.apply_to_state(state)
        assert state.packets.packet_id == 99

    def test_apply_bindkey_verified(self) -> None:
        """Test applying bindkey verified update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        assert state.encryption.bindkey_verified is False

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_bindkey_verified=True,
        )

        result.apply_to_state(state)
        assert state.encryption.bindkey_verified is True

    def test_apply_device_type(self) -> None:
        """Test applying device type update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_device_type="BTHome sensor",
        )

        result.apply_to_state(state)
        assert state.device_type == "BTHome sensor"

    def test_apply_protocol_version(self) -> None:
        """Test applying protocol version update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_protocol_version="v2",
        )

        result.apply_to_state(state)
        assert state.protocol_version == "v2"

    def test_apply_sleepy_device(self) -> None:
        """Test applying sleepy device update."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_is_sleepy_device=True,
        )

        result.apply_to_state(state)
        assert state.is_sleepy_device is True

    def test_apply_multiple_updates(self) -> None:
        """Test applying multiple updates at once."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data="test",
            updated_encryption_counter=42,
            updated_packet_id=99,
            updated_bindkey_verified=True,
            updated_device_type="BTHome sensor",
            updated_protocol_version="v2",
        )

        returned_state = result.apply_to_state(state)

        # Verify all updates applied
        assert state.encryption.encryption_counter == 42
        assert state.packets.packet_id == 99
        assert state.encryption.bindkey_verified is True
        assert state.device_type == "BTHome sensor"
        assert state.protocol_version == "v2"

        # Verify returns same state for chaining
        assert returned_state is state

    def test_apply_returns_state_for_chaining(self) -> None:
        """Test apply returns state for method chaining."""
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")
        result: InterpretationResult[str] = InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            updated_encryption_counter=1,
        )

        returned = result.apply_to_state(state)
        assert returned is state
