"""Tests for DeviceAdvertising class."""

from __future__ import annotations

from unittest.mock import Mock

import msgspec
import pytest

from bluetooth_sig.advertising.base import AdvertisingData, InterpreterInfo, PayloadInterpreter
from bluetooth_sig.advertising.exceptions import AdvertisingParseError
from bluetooth_sig.advertising.registry import PayloadInterpreterRegistry
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.device.advertising import DeviceAdvertising
from bluetooth_sig.types.company import ManufacturerData


class SensorDataStub(msgspec.Struct, kw_only=True, frozen=True):
    """Stub sensor data for testing."""

    temperature: float
    humidity: float | None = None


class MockInterpreter(PayloadInterpreter[SensorDataStub]):
    """Mock interpreter for testing."""

    _info = InterpreterInfo(
        company_id=0x1234,
        name="MockInterpreter",
    )
    _is_base_class = True  # Prevent auto-registration

    @classmethod
    def supports(cls, advertising_data: AdvertisingData) -> bool:
        return 0x1234 in advertising_data.manufacturer_data

    def interpret(
        self,
        advertising_data: AdvertisingData,
        state: DeviceAdvertisingState,
    ) -> SensorDataStub:
        manufacturer_data = advertising_data.manufacturer_data.get(0x1234)
        if manufacturer_data is None or len(manufacturer_data.payload) < 2:
            raise AdvertisingParseError(
                message="Payload too short",
                interpreter_name="MockInterpreter",
            )

        temp = int.from_bytes(manufacturer_data.payload[0:2], "little", signed=True) / 100.0
        # Update state with device type
        state.device_type = "Mock Sensor"
        return SensorDataStub(temperature=temp)


class TestDeviceAdvertisingInit:
    """Tests for DeviceAdvertising initialization."""

    def test_init_with_mac_address(self) -> None:
        """Test initialization with MAC address."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        assert adv.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_init_creates_empty_state(self) -> None:
        """Test initialization creates empty state."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        assert isinstance(adv.state, DeviceAdvertisingState)
        assert adv.state.address == "AA:BB:CC:DD:EE:FF"

    def test_init_no_interpreters(self) -> None:
        """Test initialization with no interpreters."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        assert adv.get_interpreter("nonexistent") is None


class TestDeviceAdvertisingBindkey:
    """Tests for DeviceAdvertising bindkey management."""

    def test_set_bindkey(self) -> None:
        """Test setting bindkey."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        key = bytes.fromhex("0102030405060708090a0b0c0d0e0f10")

        adv.set_bindkey(key)

        assert adv.state.encryption.bindkey == key


class TestDeviceAdvertisingInterpreterRegistration:
    """Tests for interpreter registration."""

    def test_register_interpreter(self) -> None:
        """Test registering an interpreter."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        interpreter = MockInterpreter("AA:BB:CC:DD:EE:FF")

        # Variance: MockInterpreter[SensorDataStub] not directly assignable to PayloadInterpreter[object]
        adv.register_interpreter("mock", interpreter)  # type: ignore[arg-type]

        assert adv.get_interpreter("mock") is interpreter

    def test_get_nonexistent_interpreter(self) -> None:
        """Test getting a nonexistent interpreter returns None."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        assert adv.get_interpreter("nonexistent") is None


class TestDeviceAdvertisingProcess:
    """Tests for process method."""

    def test_process_with_interpreter_class(self) -> None:
        """Test processing with a specific interpreter class (type-safe)."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)

        # Temperature: 2550 = 25.50°C
        payload = b"\xf6\x09"
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, payload)},
            service_data={},
        )
        result = adv.process(ad_data, interpreter=MockInterpreter)

        assert result is not None
        assert result.temperature == 25.50

    def test_process_auto_select_interpreter(self) -> None:
        """Test automatic interpreter selection."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        interpreter = MockInterpreter("AA:BB:CC:DD:EE:FF")
        adv.register_interpreter("mock", interpreter)  # type: ignore[arg-type]

        payload = b"\xf6\\x09"
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, payload)},
            service_data={},
        )
        result = adv.process(ad_data)

        assert result is not None

    def test_process_no_matching_interpreter(self) -> None:
        """Test processing with no matching interpreter raises error."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)

        ad_data = AdvertisingData(
            manufacturer_data={0x5678: ManufacturerData.from_id_and_payload(0x5678, b"\x00\x00")},
            service_data={},
        )

        with pytest.raises(AdvertisingParseError) as exc_info:
            adv.process(ad_data)

        assert "No interpreter found" in str(exc_info.value)

    def test_process_with_registry_auto_detection(self) -> None:
        """Test auto-detection via registry."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)

        # Create and set registry
        registry = PayloadInterpreterRegistry()
        registry.register(MockInterpreter)
        adv.set_registry(registry)

        payload = b"\xf6\\x09"
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, payload)},
            service_data={},
        )
        result = adv.process(ad_data)

        assert result is not None

    def test_process_updates_state_on_success(self) -> None:
        """Test that successful processing updates state."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        interpreter = MockInterpreter("AA:BB:CC:DD:EE:FF")
        adv.register_interpreter("mock", interpreter)  # type: ignore[arg-type]

        payload = b"\xf6\\x09"
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, payload)},
            service_data={},
        )
        adv.process(ad_data)

        # MockInterpreter sets device_type
        assert adv.state.device_type == "Mock Sensor"

    def test_process_with_parse_error(self) -> None:
        """Test processing that results in parse error."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        interpreter = MockInterpreter("AA:BB:CC:DD:EE:FF")
        adv.register_interpreter("mock", interpreter)  # type: ignore[arg-type]

        # Too short payload
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"\x00")},
            service_data={},
        )

        with pytest.raises(AdvertisingParseError):
            adv.process(ad_data)


class TestDeviceAdvertisingStateManagement:
    """Tests for state management."""

    def test_state_is_accessible(self) -> None:
        """Test state is accessible and modifiable."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)

        adv.state.encryption.encryption_counter = 42
        assert adv.state.encryption.encryption_counter == 42

    def test_state_persists_across_calls(self) -> None:
        """Test state persists across multiple process calls."""
        mock_cm = Mock()
        adv = DeviceAdvertising("AA:BB:CC:DD:EE:FF", mock_cm)
        interpreter = MockInterpreter("AA:BB:CC:DD:EE:FF")
        adv.register_interpreter("mock", interpreter)  # type: ignore[arg-type]

        # First call
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"\xf6\x09")},
            service_data={},
        )
        adv.process(ad_data)

        assert adv.state.device_type == "Mock Sensor"

        # Manually update state
        adv.state.encryption.encryption_counter = 10

        # Second call - state should still have counter
        ad_data2 = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"\xf6\x09")},
            service_data={},
        )
        adv.process(ad_data2)

        assert adv.state.encryption.encryption_counter == 10
