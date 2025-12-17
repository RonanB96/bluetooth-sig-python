"""Tests for advertising data interpreter base classes and registry."""

from __future__ import annotations

import msgspec

from bluetooth_sig.advertising import (
    AdvertisingDataInterpreter,
    AdvertisingInterpreterInfo,
    AdvertisingPDUParser,
    DataSource,
    DictKeyProvider,
)
from bluetooth_sig.types.uuid import BluetoothUUID


class TestSensorData(msgspec.Struct, kw_only=True, frozen=True):
    """Test sensor data type."""

    device_type: str = ""
    temperature: float | None = None
    raw_data: bytes = b""


class TestDictKeyProvider:
    """Tests for DictKeyProvider."""

    def test_get_key_found(self) -> None:
        """Test getting an existing key."""
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider = DictKeyProvider({"AA:BB:CC:DD:EE:FF": key})
        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key

    def test_get_key_case_insensitive(self) -> None:
        """Test MAC address case insensitivity."""
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider = DictKeyProvider({"aa:bb:cc:dd:ee:ff": key})
        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key

    def test_get_key_not_found(self) -> None:
        """Test getting a missing key returns None."""
        provider = DictKeyProvider({})
        assert provider.get_key("AA:BB:CC:DD:EE:FF") is None

    def test_set_key(self) -> None:
        """Test setting a key."""
        provider = DictKeyProvider()
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider.set_key("AA:BB:CC:DD:EE:FF", key)
        assert provider.get_key("AA:BB:CC:DD:EE:FF") == key

    def test_remove_key(self) -> None:
        """Test removing a key."""
        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        provider = DictKeyProvider({"AA:BB:CC:DD:EE:FF": key})
        provider.remove_key("AA:BB:CC:DD:EE:FF")
        assert provider.get_key("AA:BB:CC:DD:EE:FF") is None


class TestAdvertisingDataInterpreter:
    """Tests for AdvertisingDataInterpreter."""

    def test_interpreter_instance_attributes(self) -> None:
        """Test interpreter instance has mac_address and bindkey."""

        class SimpleInterpreter(AdvertisingDataInterpreter[TestSensorData]):
            _info = AdvertisingInterpreterInfo(company_id=0x1234, name="Test")

            @classmethod
            def supports(
                cls,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
            ) -> bool:
                return 0x1234 in manufacturer_data

            def interpret(
                self,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
                rssi: int,
            ) -> TestSensorData:
                return TestSensorData(device_type="Test")

        key = bytes.fromhex("0123456789abcdef0123456789abcdef")
        interpreter = SimpleInterpreter("AA:BB:CC:DD:EE:FF", bindkey=key)

        assert interpreter.mac_address == "AA:BB:CC:DD:EE:FF"
        assert interpreter.bindkey == key
        assert interpreter.state == {}
        assert interpreter.info.company_id == 0x1234

    def test_interpreter_state_persistence(self) -> None:
        """Test interpreter state persists across calls."""

        class StatefulInterpreter(AdvertisingDataInterpreter[TestSensorData]):
            _info = AdvertisingInterpreterInfo(company_id=0x5678, name="Stateful")

            @classmethod
            def supports(
                cls,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
            ) -> bool:
                return 0x5678 in manufacturer_data

            def interpret(
                self,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
                rssi: int,
            ) -> TestSensorData:
                counter = self.state.get("counter", 0) + 1
                self.state["counter"] = counter
                return TestSensorData(device_type=f"call_{counter}")

        interpreter = StatefulInterpreter("AA:BB:CC:DD:EE:FF")

        result1 = interpreter.interpret({0x5678: b"\x01"}, {}, None, -65)
        assert result1.device_type == "call_1"

        result2 = interpreter.interpret({0x5678: b"\x02"}, {}, None, -60)
        assert result2.device_type == "call_2"

        assert interpreter.state["counter"] == 2


class TestAdvertisingInterpreterRegistry:
    """Tests for AdvertisingInterpreterRegistry."""

    def test_find_interpreter_class(self) -> None:
        """Test finding an interpreter class by advertisement."""
        from bluetooth_sig.advertising.registry import AdvertisingInterpreterRegistry

        registry = AdvertisingInterpreterRegistry()

        class TestInterpreter(AdvertisingDataInterpreter[TestSensorData]):
            _info = AdvertisingInterpreterInfo(
                company_id=0x9999,
                name="Test",
                data_source=DataSource.MANUFACTURER,
            )

            @classmethod
            def supports(
                cls,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
            ) -> bool:
                return 0x9999 in manufacturer_data

            def interpret(
                self,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
                rssi: int,
            ) -> TestSensorData:
                return TestSensorData(device_type="Test")

        registry.register(TestInterpreter)

        interpreter_class = registry.find_interpreter_class(
            manufacturer_data={0x9999: b"\x01\x02\x03"},
            service_data={},
            local_name=None,
        )
        assert interpreter_class is TestInterpreter

    def test_find_all_interpreter_classes(self) -> None:
        """Test finding all matching interpreter classes."""
        from bluetooth_sig.advertising.registry import AdvertisingInterpreterRegistry

        registry = AdvertisingInterpreterRegistry()

        class Interpreter1(AdvertisingDataInterpreter[TestSensorData]):
            _info = AdvertisingInterpreterInfo(company_id=0xAAAA, name="I1")

            @classmethod
            def supports(
                cls,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
            ) -> bool:
                return 0xAAAA in manufacturer_data

            def interpret(
                self,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
                rssi: int,
            ) -> TestSensorData:
                return TestSensorData(device_type="I1")

        class Interpreter2(AdvertisingDataInterpreter[TestSensorData]):
            _info = AdvertisingInterpreterInfo(company_id=0xAAAA, name="I2")

            @classmethod
            def supports(
                cls,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
            ) -> bool:
                return 0xAAAA in manufacturer_data

            def interpret(
                self,
                manufacturer_data: dict[int, bytes],
                service_data: dict[BluetoothUUID, bytes],
                local_name: str | None,
                rssi: int,
            ) -> TestSensorData:
                return TestSensorData(device_type="I2")

        registry.register(Interpreter1)
        registry.register(Interpreter2)

        classes = registry.find_all_interpreter_classes(
            manufacturer_data={0xAAAA: b"\x01"},
            service_data={},
            local_name=None,
        )
        assert len(classes) == 2
        assert Interpreter1 in classes
        assert Interpreter2 in classes

    def test_no_matching_interpreter(self) -> None:
        """Test when no interpreter matches."""
        from bluetooth_sig.advertising.registry import AdvertisingInterpreterRegistry

        registry = AdvertisingInterpreterRegistry()

        result = registry.find_interpreter_class(
            manufacturer_data={0x1111: b"\x01\x02\x03"},
            service_data={},
            local_name=None,
        )
        assert result is None


class TestAdvertisingPDUParser:
    """Tests for the PDU parser (AdvertisingPDUParser)."""

    def test_parse_manufacturer_data(self) -> None:
        """Test parsing manufacturer data from PDU."""
        parser = AdvertisingPDUParser()

        # AD structure: length=4, type=0xFF (manufacturer), company_id=0x1234, data=0x56
        ad_data = bytes([0x04, 0xFF, 0x34, 0x12, 0x56])
        result = parser.parse_advertising_data(ad_data)

        assert 0x1234 in result.ad_structures.core.manufacturer_data
        assert result.ad_structures.core.manufacturer_data[0x1234] == b"\x56"

    def test_parse_service_data(self) -> None:
        """Test parsing service data from PDU."""
        parser = AdvertisingPDUParser()

        # AD structure: length=4, type=0x16 (service data 16-bit), uuid=0xFCD2, data=0x40
        ad_data = bytes([0x04, 0x16, 0xD2, 0xFC, 0x40])
        result = parser.parse_advertising_data(ad_data)

        fcd2_uuid = BluetoothUUID("FCD2")
        assert fcd2_uuid in result.ad_structures.core.service_data
        assert result.ad_structures.core.service_data[fcd2_uuid] == b"\x40"

    def test_parse_local_name(self) -> None:
        """Test parsing local name from PDU."""
        parser = AdvertisingPDUParser()

        # AD structure: length=5, type=0x09 (complete local name), name="Test"
        ad_data = bytes([0x05, 0x09]) + b"Test"
        result = parser.parse_advertising_data(ad_data)

        assert result.ad_structures.core.local_name == "Test"
