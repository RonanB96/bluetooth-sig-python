"""Tests for PayloadInterpreter and PayloadInterpreterRegistry."""

from __future__ import annotations

import msgspec
import pytest

from bluetooth_sig.advertising.base import (
    AdvertisingData,
    DataSource,
    InterpreterInfo,
    PayloadInterpreter,
)
from bluetooth_sig.advertising.registry import PayloadInterpreterRegistry
from bluetooth_sig.advertising.result import InterpretationResult, InterpretationStatus
from bluetooth_sig.advertising.state import DeviceAdvertisingState
from bluetooth_sig.types import ManufacturerData
from bluetooth_sig.types.uuid import BluetoothUUID


class SensorDataStub(msgspec.Struct, kw_only=True, frozen=True):
    """Stub sensor data type for testing."""

    temperature: float
    humidity: float | None = None


class TestInterpreterInfo:
    """Tests for InterpreterInfo struct."""

    def test_default_values(self) -> None:
        """Test default values are correct."""
        info = InterpreterInfo()
        assert info.company_id is None
        assert info.service_uuid is None
        assert info.name == ""
        assert info.data_source == DataSource.MANUFACTURER

    def test_with_company_id(self) -> None:
        """Test with company ID for manufacturer data."""
        info = InterpreterInfo(
            company_id=0x0499,  # RuuviTag
            name="RuuviTag",
            data_source=DataSource.MANUFACTURER,
        )
        assert info.company_id == 0x0499
        assert info.name == "RuuviTag"
        assert info.data_source == DataSource.MANUFACTURER

    def test_with_service_uuid(self) -> None:
        """Test with service UUID for service data."""
        uuid = BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb")
        info = InterpreterInfo(
            service_uuid=uuid,
            name="BTHome",
            data_source=DataSource.SERVICE,
        )
        assert info.service_uuid == uuid
        assert info.name == "BTHome"
        assert info.data_source == DataSource.SERVICE

    def test_frozen(self) -> None:
        """Test info struct is immutable."""
        info = InterpreterInfo(name="Test")
        with pytest.raises(AttributeError):
            info.name = "Changed"  # type: ignore[misc]


class SimpleTestInterpreter(PayloadInterpreter[SensorDataStub]):
    """Simple test interpreter for unit tests."""

    _info = InterpreterInfo(
        company_id=0x1234,
        name="TestInterpreter",
        data_source=DataSource.MANUFACTURER,
    )
    _is_base_class = True  # Prevent auto-registration

    @classmethod
    def supports(cls, advertising_data: AdvertisingData) -> bool:
        """Check if manufacturer data contains our company ID."""
        return 0x1234 in advertising_data.manufacturer_data

    def interpret(
        self,
        advertising_data: AdvertisingData,
        state: DeviceAdvertisingState,
    ) -> InterpretationResult[SensorDataStub]:
        """Parse test sensor data."""
        mfr_data = advertising_data.manufacturer_data.get(0x1234)
        data = mfr_data.payload if mfr_data else b""
        if len(data) < 4:
            return InterpretationResult(
                status=InterpretationStatus.PARSE_ERROR,
                error_message="Payload too short",
            )

        temperature = int.from_bytes(data[0:2], "little", signed=True) / 100.0
        humidity = int.from_bytes(data[2:4], "little") / 100.0

        return InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data=SensorDataStub(temperature=temperature, humidity=humidity),
            updated_device_type="Test Sensor",
        )


class TestPayloadInterpreter:
    """Tests for PayloadInterpreter base class."""

    def test_init_with_mac_address(self) -> None:
        """Test interpreter initialization with MAC address."""
        interpreter = SimpleTestInterpreter("AA:BB:CC:DD:EE:FF")
        assert interpreter.mac_address == "AA:BB:CC:DD:EE:FF"

    def test_info_property(self) -> None:
        """Test info property returns correct metadata."""
        interpreter = SimpleTestInterpreter("AA:BB:CC:DD:EE:FF")
        assert interpreter.info.company_id == 0x1234
        assert interpreter.info.name == "TestInterpreter"
        assert interpreter.info.data_source == DataSource.MANUFACTURER

    def test_supports_classmethod(self) -> None:
        """Test supports classmethod."""
        # Should support
        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"\x00")})
        assert SimpleTestInterpreter.supports(ad_data) is True

        # Should not support
        ad_data2 = AdvertisingData(manufacturer_data={0x5678: ManufacturerData.from_id_and_payload(0x5678, b"\x00")})
        assert SimpleTestInterpreter.supports(ad_data2) is False

        ad_data3 = AdvertisingData()
        assert SimpleTestInterpreter.supports(ad_data3) is False

    def test_interpret_success(self) -> None:
        """Test successful interpretation."""
        interpreter = SimpleTestInterpreter("AA:BB:CC:DD:EE:FF")
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        # Temperature: 2550 (25.50°C), Humidity: 6000 (60.00%)
        payload = b"\xf6\x09\x70\x17"
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, payload)}, rssi=-60
        )
        result = interpreter.interpret(ad_data, state)

        assert result.status == InterpretationStatus.SUCCESS
        assert result.data is not None
        assert result.data.temperature == 25.50
        assert result.data.humidity == 60.00
        assert result.updated_device_type == "Test Sensor"

    def test_interpret_parse_error(self) -> None:
        """Test interpretation with parse error."""
        interpreter = SimpleTestInterpreter("AA:BB:CC:DD:EE:FF")
        state = DeviceAdvertisingState(address="AA:BB:CC:DD:EE:FF")

        # Too short payload
        ad_data = AdvertisingData(
            manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"\x00")}, rssi=-60
        )
        result = interpreter.interpret(ad_data, state)

        assert result.status == InterpretationStatus.PARSE_ERROR
        assert result.data is None
        assert result.error_message == "Payload too short"


class TestPayloadInterpreterRegistry:
    """Tests for PayloadInterpreterRegistry."""

    def test_empty_registry(self) -> None:
        """Test empty registry returns no matches."""
        registry = PayloadInterpreterRegistry()
        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"")})
        result = registry.find_interpreter_class(ad_data)
        assert result is None

    def test_register_and_find_by_company_id(self) -> None:
        """Test registering and finding by company ID."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"")})
        result = registry.find_interpreter_class(ad_data)
        assert result is SimpleTestInterpreter

    def test_find_no_match(self) -> None:
        """Test finding with no matching company ID."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        ad_data = AdvertisingData(manufacturer_data={0x5678: ManufacturerData.from_id_and_payload(0x5678, b"")})
        result = registry.find_interpreter_class(ad_data)
        assert result is None

    def test_unregister(self) -> None:
        """Test unregistering an interpreter."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        # Verify registered
        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"")})
        assert registry.find_interpreter_class(ad_data) is SimpleTestInterpreter

        # Unregister
        registry.unregister(SimpleTestInterpreter)

        # Verify unregistered
        assert registry.find_interpreter_class(ad_data) is None

    def test_get_registered_interpreters(self) -> None:
        """Test getting all registered interpreters."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        interpreters = registry.get_registered_interpreters()
        assert SimpleTestInterpreter in interpreters

    def test_clear(self) -> None:
        """Test clearing all registrations."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        registry.clear()

        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"")})
        assert registry.find_interpreter_class(ad_data) is None
        assert registry.get_registered_interpreters() == []

    def test_find_all_interpreter_classes(self) -> None:
        """Test finding all matching interpreters."""
        registry = PayloadInterpreterRegistry()
        registry.register(SimpleTestInterpreter)

        # Create another interpreter for same company ID
        class AnotherInterpreter(SimpleTestInterpreter):
            _info = InterpreterInfo(
                company_id=0x1234,
                name="Another",
                data_source=DataSource.MANUFACTURER,
            )
            _is_base_class = True

        registry.register(AnotherInterpreter)

        ad_data = AdvertisingData(manufacturer_data={0x1234: ManufacturerData.from_id_and_payload(0x1234, b"")})
        results = registry.find_all_interpreter_classes(ad_data)
        assert len(results) == 2
        assert SimpleTestInterpreter in results
        assert AnotherInterpreter in results


class ServiceDataInterpreter(PayloadInterpreter[SensorDataStub]):
    """Test interpreter for service data."""

    _info = InterpreterInfo(
        service_uuid=BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb"),
        name="ServiceDataTest",
        data_source=DataSource.SERVICE,
    )
    _is_base_class = True

    @classmethod
    def supports(cls, advertising_data: AdvertisingData) -> bool:
        uuid = BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb")
        return uuid in advertising_data.service_data

    def interpret(
        self,
        advertising_data: AdvertisingData,
        state: DeviceAdvertisingState,
    ) -> InterpretationResult[SensorDataStub]:
        return InterpretationResult(
            status=InterpretationStatus.SUCCESS,
            data=SensorDataStub(temperature=22.0),
        )


class TestServiceDataRouting:
    """Tests for service data routing in registry."""

    def test_register_and_find_by_service_uuid(self) -> None:
        """Test registering and finding by service UUID."""
        registry = PayloadInterpreterRegistry()
        registry.register(ServiceDataInterpreter)

        uuid = BluetoothUUID("0000fcd2-0000-1000-8000-00805f9b34fb")
        ad_data = AdvertisingData(service_data={uuid: b""})
        result = registry.find_interpreter_class(ad_data)
        assert result is ServiceDataInterpreter

    def test_uuid_case_insensitive(self) -> None:
        """Test UUID matching is case-insensitive."""
        registry = PayloadInterpreterRegistry()
        registry.register(ServiceDataInterpreter)

        # Use lowercase UUID
        uuid = BluetoothUUID("0000FCD2-0000-1000-8000-00805F9B34FB")
        ad_data = AdvertisingData(service_data={uuid: b""})
        result = registry.find_interpreter_class(ad_data)
        assert result is ServiceDataInterpreter
