#!/usr/bin/env python3
"""Advertising data parsing example using the AdvertisingPDUParser.

Demonstrates how to use the AdvertisingPDUParser and Bluetooth SIG translator to
interpret advertising PDUs and service data for examples and tests.
"""

from __future__ import annotations

import asyncio
from typing import cast

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.advertising import AdvertisingPDUParser
from bluetooth_sig.types.advertising import (
    AdvertisingData,
    AdvertisingDataStructures,
    BLEAdvertisingFlags,
    MeshAndBroadcastData,
)
from bluetooth_sig.types.appearance import AppearanceData
from bluetooth_sig.types.uuid import BluetoothUUID


def display_advertising_data(
    parsed_data: AdvertisingData,
    translator: BluetoothSIGTranslator,
    show_not_found: bool = False,
    show_debug: bool = False,
) -> None:
    """Display advertising data in a structured format showing found fields first, then not found."""
    # Collect found and not found fields
    found_fields: list[str] = []
    not_found_fields: list[str] = []

    # Basic device information
    if parsed_data.ad_structures.core.local_name:
        found_fields.append(f"Local Name: {parsed_data.ad_structures.core.local_name}")
    else:
        not_found_fields.append("Local Name")

    if parsed_data.ad_structures.core.service_uuids:
        service_lines = ["Service UUIDs:"]
        for uuid in parsed_data.ad_structures.core.service_uuids:
            service_info = translator.get_service_info_by_uuid(str(uuid))
            display_uuid = uuid.short_form  # Use short form for display
            if service_info:
                service_lines.append(f"  {display_uuid}: {service_info.name}")
            else:
                service_lines.append(f"  {display_uuid}: Unknown service")
        found_fields.extend(service_lines)
    else:
        not_found_fields.append("Service UUIDs")

    if parsed_data.ad_structures.core.manufacturer_data:
        manufacturer_lines = ["Manufacturer Data:"]
        for company_id, data in parsed_data.ad_structures.core.manufacturer_data.items():
            manufacturer_lines.append(f"  Company 0x{company_id:04X}: {data.hex()}")
        found_fields.extend(manufacturer_lines)
    else:
        not_found_fields.append("Manufacturer Data")

    if parsed_data.ad_structures.properties.tx_power != 0:
        found_fields.append(f"TX Power: {parsed_data.ad_structures.properties.tx_power} dBm")
    else:
        not_found_fields.append("TX Power")

    if parsed_data.ad_structures.properties.flags != 0:
        found_fields.append(f"Flags: 0x{parsed_data.ad_structures.properties.flags:02X}")
    else:
        not_found_fields.append("Flags")

    if parsed_data.rssi is not None:
        found_fields.append(f"RSSI: {parsed_data.rssi} dBm")
    else:
        not_found_fields.append("RSSI")

    # Appearance and service data
    if parsed_data.ad_structures.properties.appearance is not None:
        found_fields.append(f"Appearance: 0x{parsed_data.ad_structures.properties.appearance.raw_value:04X}")
    else:
        not_found_fields.append("Appearance")

    if parsed_data.ad_structures.core.service_data:
        service_data_lines = ["Service Data:"]
        for service_uuid, data in parsed_data.ad_structures.core.service_data.items():
            service_data_lines.append(f"  Service {service_uuid}: {data.hex()}")
        found_fields.extend(service_data_lines)
    else:
        not_found_fields.append("Service Data")

    # Additional legacy fields
    if parsed_data.ad_structures.core.solicited_service_uuids:
        solicited_lines = ["Solicited Service UUIDs:"]
        for uuid in parsed_data.ad_structures.core.solicited_service_uuids:
            solicited_lines.append(f"  {uuid}")
        found_fields.extend(solicited_lines)
    else:
        not_found_fields.append("Solicited Service UUIDs")

    if parsed_data.ad_structures.core.uri_data:
        uri_data = parsed_data.ad_structures.core.uri_data
        uri_info = f"URI: {uri_data.full_uri}"
        if uri_data.is_known_scheme:
            uri_info += f" (scheme: {uri_data.scheme_name})"
        found_fields.append(uri_info)
    else:
        not_found_fields.append("URI")

    # Positioning and discovery
    if parsed_data.ad_structures.location.indoor_positioning:
        found_fields.append(f"Indoor Positioning: {parsed_data.ad_structures.location.indoor_positioning.hex()}")
    else:
        not_found_fields.append("Indoor Positioning")

    if parsed_data.ad_structures.location.transport_discovery_data:
        found_fields.append(
            f"Transport Discovery Data: {parsed_data.ad_structures.location.transport_discovery_data.hex()}"
        )
    else:
        not_found_fields.append("Transport Discovery Data")

    # LE features and security
    if parsed_data.ad_structures.properties.le_supported_features:
        features = parsed_data.ad_structures.properties.le_supported_features
        feature_list: list[str] = []
        if features.le_encryption:
            feature_list.append("LE Encryption")
        if features.le_2m_phy:
            feature_list.append("LE 2M PHY")
        if features.le_coded_phy:
            feature_list.append("LE Coded PHY")
        if features.le_extended_advertising:
            feature_list.append("Extended Advertising")
        if features.le_periodic_advertising:
            feature_list.append("Periodic Advertising")

        features_display = ", ".join(feature_list) if feature_list else features.raw_value.hex()
        found_fields.append(f"LE Supported Features: {features_display}")
    else:
        not_found_fields.append("LE Supported Features")

    if parsed_data.ad_structures.security.encrypted_advertising_data:
        found_fields.append(
            f"Encrypted Advertising Data: {parsed_data.ad_structures.security.encrypted_advertising_data.hex()}"
        )
    else:
        not_found_fields.append("Encrypted Advertising Data")

    if parsed_data.ad_structures.mesh.periodic_advertising_response_timing:
        timing_hex = parsed_data.ad_structures.mesh.periodic_advertising_response_timing.hex()
        found_fields.append(f"Periodic Advertising Response Timing: {timing_hex}")
    else:
        not_found_fields.append("Periodic Advertising Response Timing")

    # Labels and 3D info
    if parsed_data.ad_structures.mesh.electronic_shelf_label:
        found_fields.append(f"Electronic Shelf Label: {parsed_data.ad_structures.mesh.electronic_shelf_label.hex()}")
    else:
        not_found_fields.append("Electronic Shelf Label")

    if parsed_data.ad_structures.location.three_d_information:
        found_fields.append(f"3D Information: {parsed_data.ad_structures.location.three_d_information.hex()}")
    else:
        not_found_fields.append("3D Information")

    if parsed_data.ad_structures.mesh.broadcast_name:
        found_fields.append(f"Broadcast Name: {parsed_data.ad_structures.mesh.broadcast_name}")
    else:
        not_found_fields.append("Broadcast Name")

    # Mesh and broadcast
    if parsed_data.ad_structures.mesh.biginfo:
        found_fields.append(f"BIGInfo: {parsed_data.ad_structures.mesh.biginfo.hex()}")
    else:
        not_found_fields.append("BIGInfo")

    if parsed_data.ad_structures.mesh.mesh_message:
        found_fields.append(f"Mesh Message: {parsed_data.ad_structures.mesh.mesh_message.hex()}")
    else:
        not_found_fields.append("Mesh Message")

    if parsed_data.ad_structures.mesh.mesh_beacon:
        found_fields.append(f"Mesh Beacon: {parsed_data.ad_structures.mesh.mesh_beacon.hex()}")
    else:
        not_found_fields.append("Mesh Beacon")

    # Target addresses
    if parsed_data.ad_structures.directed.public_target_address:
        target_lines = ["Public Target Address:"]
        for addr in parsed_data.ad_structures.directed.public_target_address:
            target_lines.append(f"  {addr}")
        found_fields.extend(target_lines)
    else:
        not_found_fields.append("Public Target Address")

    if parsed_data.ad_structures.directed.random_target_address:
        random_lines = ["Random Target Address:"]
        for addr in parsed_data.ad_structures.directed.random_target_address:
            random_lines.append(f"  {addr}")
        found_fields.extend(random_lines)
    else:
        not_found_fields.append("Random Target Address")

    # Advertising intervals
    if parsed_data.ad_structures.directed.advertising_interval is not None:
        found_fields.append(f"Advertising Interval: {parsed_data.ad_structures.directed.advertising_interval} ms")
    else:
        not_found_fields.append("Advertising Interval")

    if parsed_data.ad_structures.directed.advertising_interval_long is not None:
        found_fields.append(
            f"Advertising Interval Long: {parsed_data.ad_structures.directed.advertising_interval_long} ms"
        )
    else:
        not_found_fields.append("Advertising Interval Long")

    # Device addresses and roles
    if parsed_data.ad_structures.directed.le_bluetooth_device_address:
        found_fields.append(
            f"LE Bluetooth Device Address: {parsed_data.ad_structures.directed.le_bluetooth_device_address}"
        )
    else:
        not_found_fields.append("LE Bluetooth Device Address")

    if parsed_data.ad_structures.properties.le_role is not None:
        found_fields.append(f"LE Role: {parsed_data.ad_structures.properties.le_role}")
    else:
        not_found_fields.append("LE Role")

    if parsed_data.ad_structures.properties.class_of_device is not None:
        found_fields.append(f"Class of Device: 0x{parsed_data.ad_structures.properties.class_of_device.raw_value:06X}")
    else:
        not_found_fields.append("Class of Device")

    # OOB Pairing and security
    if parsed_data.ad_structures.oob_security.simple_pairing_hash_c:
        found_fields.append(
            f"Simple Pairing Hash C: {parsed_data.ad_structures.oob_security.simple_pairing_hash_c.hex()}"
        )
    else:
        not_found_fields.append("Simple Pairing Hash C")

    if parsed_data.ad_structures.oob_security.simple_pairing_randomizer_r:
        found_fields.append(
            f"Simple Pairing Randomizer R: {parsed_data.ad_structures.oob_security.simple_pairing_randomizer_r.hex()}"
        )
    else:
        not_found_fields.append("Simple Pairing Randomizer R")

    if parsed_data.ad_structures.oob_security.security_manager_tk_value:
        found_fields.append(
            f"Security Manager TK Value: {parsed_data.ad_structures.oob_security.security_manager_tk_value.hex()}"
        )
    else:
        not_found_fields.append("Security Manager TK Value")

    if parsed_data.ad_structures.oob_security.security_manager_oob_flags:
        oob_hex = parsed_data.ad_structures.oob_security.security_manager_oob_flags.hex()
        found_fields.append(f"Security Manager OOB Flags: {oob_hex}")
    else:
        not_found_fields.append("Security Manager OOB Flags")

    if parsed_data.ad_structures.directed.peripheral_connection_interval_range:
        range_data = parsed_data.ad_structures.directed.peripheral_connection_interval_range
        found_fields.append(
            f"Peripheral Connection Interval Range: {range_data.min_interval_ms:.2f}ms - "
            f"{range_data.max_interval_ms:.2f}ms"
        )
    else:
        not_found_fields.append("Peripheral Connection Interval Range")

    if parsed_data.ad_structures.oob_security.secure_connections_confirmation:
        confirmation = parsed_data.ad_structures.oob_security.secure_connections_confirmation
        found_fields.append(f"Secure Connections Confirmation: {confirmation.hex()}")
    else:
        not_found_fields.append("Secure Connections Confirmation")

    if parsed_data.ad_structures.oob_security.secure_connections_random:
        found_fields.append(
            f"Secure Connections Random: {parsed_data.ad_structures.oob_security.secure_connections_random.hex()}"
        )
    else:
        not_found_fields.append("Secure Connections Random")

    if parsed_data.ad_structures.location.channel_map_update_indication:
        found_fields.append(
            f"Channel Map Update Indication: {parsed_data.ad_structures.location.channel_map_update_indication.hex()}"
        )
    else:
        not_found_fields.append("Channel Map Update Indication")

    if parsed_data.ad_structures.mesh.pb_adv:
        found_fields.append(f"PB-ADV: {parsed_data.ad_structures.mesh.pb_adv.hex()}")
    else:
        not_found_fields.append("PB-ADV")

    if parsed_data.ad_structures.security.resolvable_set_identifier:
        found_fields.append(
            f"Resolvable Set Identifier: {parsed_data.ad_structures.security.resolvable_set_identifier.hex()}"
        )
    else:
        not_found_fields.append("Resolvable Set Identifier")

    # Print found fields first
    if found_fields:
        print("📋 FOUND FIELDS:")
        for field in found_fields:
            print(f"  {field}")
        print()

    # Print not found fields if flag enabled
    if show_not_found and not_found_fields:
        print("❌ NOT FOUND FIELDS:")
        for field in not_found_fields:
            print(f"  {field}")
        print()

    # Extended advertising fields (show automatically if present)
    if parsed_data.is_extended_advertising:
        extended_found: list[str] = []
        extended_not_found: list[str] = []

        if parsed_data.extended.extended_payload:
            extended_found.append(f"Extended Payload: {parsed_data.extended.extended_payload.hex()}")

        if parsed_data.extended.auxiliary_packets:
            aux_lines = ["Auxiliary Packets:"]
            for i, packet in enumerate(parsed_data.extended.auxiliary_packets):
                aux_lines.append(f"  Packet {i + 1}: {packet.pdu_name} ({len(packet.payload)} bytes)")
            extended_found.extend(aux_lines)
        else:
            extended_not_found.append("Auxiliary Packets")

        if parsed_data.extended.periodic_advertising_data:
            extended_found.append(f"Periodic Advertising Data: {parsed_data.extended.periodic_advertising_data.hex()}")

        # Broadcast code is now in mesh struct (it's an AD type, not PDU metadata)
        if parsed_data.ad_structures.mesh.broadcast_code:
            extended_found.append(f"Broadcast Code: {parsed_data.ad_structures.mesh.broadcast_code.hex()}")

        if not parsed_data.extended.extended_payload:
            extended_not_found.append("Extended Payload")

        if not parsed_data.extended.periodic_advertising_data:
            extended_not_found.append("Periodic Advertising Data")

        if not parsed_data.ad_structures.mesh.broadcast_code:
            extended_not_found.append("Broadcast Code")

        if extended_found:
            print("🔄 EXTENDED ADVERTISING - FOUND:")
            for field in extended_found:
                print(f"  {field}")
            print()

        if show_not_found and extended_not_found:
            print("🔄 EXTENDED ADVERTISING - NOT FOUND:")
            for field in extended_not_found:
                print(f"  {field}")
            print()

    # Debug output if enabled
    if show_debug:
        print(f"Is Extended Advertising: {parsed_data.is_extended_advertising}")
        print(f"Total Payload Size: {parsed_data.total_payload_size} bytes")


def demo_advertising_parsing() -> None:
    """Demonstrate advertising data parsing."""
    print("Advertising Data Parsing Example")
    print("=" * 40)

    # Create parser and translator
    # parser = AdvertisingPDUParser()  # Would be used for actual parsing
    translator = BluetoothSIGTranslator()

    # Example advertising data (this would come from BLE scanning)
    # This is mock data for demonstration
    mock_advertising_data = {
        "manufacturer_data": {
            0x004C: b"\x02\x15\xe2\xc5\x6d\xb5\xdf\xfb\x48\xd2\xb0\x60\xd0\xf5\xa7\x10\x96\xe0\x00\x00\x00\x00\xc5"
        },
        "service_data": {},
        "service_uuids": ["180F", "180A"],  # Battery and Device Info services
        "local_name": "Test Device",
    }

    # Type assertions for mypy
    manufacturer_data = mock_advertising_data["manufacturer_data"]
    service_uuids = mock_advertising_data["service_uuids"]

    print("Mock advertising data:")
    print(f"  Local name: {mock_advertising_data['local_name']}")
    print(f"  Service UUIDs: {mock_advertising_data['service_uuids']}")

    manufacturer_data = cast(dict[int, bytes], mock_advertising_data["manufacturer_data"])
    if manufacturer_data:
        for company_id, data in manufacturer_data.items():
            print(f"  Manufacturer data (0x{company_id:04X}): {data.hex()}")

    # Parse the advertising data
    print("\nParsing advertising data...")

    try:
        # The AdvertisingPDUParser would parse raw PDU data in a real scenario
        # For this demo, we'll show the API
        print("AdvertisingPDUParser methods available:")
        print("- parse_advertising_data(raw_pdu)")
        print("- parse_legacy_advertising(data)")
        print("- parse_extended_advertising(data)")

        # Show service name resolution using translator
        print("\nService name resolution:")
        service_uuids = cast(list[str], mock_advertising_data["service_uuids"])
        for uuid in service_uuids:
            service_info = translator.get_service_info_by_uuid(uuid)
            if service_info:
                print(f"  {uuid}: {service_info.name}")
            else:
                print(f"  {uuid}: Unknown service")

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error parsing advertising data: {e}")


async def main(
    data: str = "",
    mock: bool = False,
    extended_mock: bool = False,
    show_not_found: bool = False,
    show_debug: bool = False,
) -> dict[str, object]:
    """Async main entrypoint for example scripts (imported by tests).

    Prints example output and returns a small results dict for tests.
    """
    results: dict[str, object] = {}
    parsed_data = None
    translator = BluetoothSIGTranslator()

    if data:
        try:
            clean_hex = data.replace(" ", "").replace(":", "")
            raw_bytes = bytes.fromhex(clean_hex)
            advertising_parser = AdvertisingPDUParser()
            parsed_data = advertising_parser.parse_advertising_data(raw_bytes)
            print("Parsing provided advertising data:")
            print(f"Raw data: {data}")
            print("Provided Data Results with SIG Parsing:")
            print()
            display_advertising_data(parsed_data, translator, show_not_found, show_debug)
            results["provided"] = True
        except ValueError as e:
            print(f"Invalid hex data provided: {e}")
            results["error"] = "invalid_hex"
            return results
    elif mock:
        print("📝 USING MOCK LEGACY ADVERTISING DATA FOR DEMONSTRATION - No real BLE hardware required")
        print()
        print("Mock BLE Device Results with SIG Parsing:")
        print()

        from bluetooth_sig.types.advertising import CoreAdvertisingData, DeviceProperties

        parsed_data = AdvertisingData(
            raw_data=b"mock_data",
            ad_structures=AdvertisingDataStructures(
                core=CoreAdvertisingData(
                    local_name="Test Device",
                    manufacturer_data={
                        0x004C: (
                            b"\x02\x15\xe2\xc5\x6d\xb5\xdf\xfb\x48\xd2\xb0\x60\xd0\xf5\xa7\x10\x96\xe0\x00\x00\x00\x00\xc5"
                        )
                    },
                    service_uuids=[BluetoothUUID("180F"), BluetoothUUID("180A")],  # Battery and Device Info services
                    service_data={BluetoothUUID("180F"): b"\x64"},  # Battery level 100%
                ),
                properties=DeviceProperties(
                    appearance=AppearanceData(raw_value=0x03C0, info=None),  # Generic Computer
                    tx_power=-50,
                    flags=BLEAdvertisingFlags(0x06),
                ),
            ),
            rssi=-45,
        )
        display_advertising_data(parsed_data, translator, show_not_found, show_debug)
        results["used_mock"] = True
    elif extended_mock:
        print("🔄 USING MOCK EXTENDED ADVERTISING DATA FOR DEMONSTRATION - No real BLE hardware required")
        print()
        print("Mock Extended BLE Device Results with SIG Parsing:")
        print()

        from bluetooth_sig.types.advertising import (
            CoreAdvertisingData,
            DeviceProperties,
            ExtendedAdvertisingData,
        )

        parsed_data = AdvertisingData(
            raw_data=b"mock_extended_data",
            ad_structures=AdvertisingDataStructures(
                core=CoreAdvertisingData(
                    local_name="Extended Test Device",
                    manufacturer_data={
                        0x004C: (
                            b"\x02\x15\xe2\xc5\x6d\xb5\xdf\xfb\x48\xd2\xb0\x60\xd0\xf5\xa7\x10\x96\xe0\x00\x00\x00\x00\xc5"
                        )
                    },
                    service_uuids=[BluetoothUUID("180F"), BluetoothUUID("180A")],  # Battery and Device Info services
                    service_data={BluetoothUUID("180F"): b"\x64"},  # Battery level 100%
                ),
                properties=DeviceProperties(
                    appearance=AppearanceData(raw_value=0x03C1, info=None),  # Generic Computer with extended features
                    tx_power=-40,
                    flags=BLEAdvertisingFlags(0x06),
                ),
                mesh=MeshAndBroadcastData(
                    broadcast_code=b"\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff\x00",
                ),
            ),
            extended=ExtendedAdvertisingData(
                extended_payload=b"\x01\x02\x03\x04\x05",
                periodic_advertising_data=b"\xaa\xbb\xcc\xdd",
            ),
            rssi=-35,
        )
        display_advertising_data(parsed_data, translator, show_not_found, show_debug)
        results["used_extended"] = True

    if parsed_data is not None:
        results["parsed"] = {
            "local_name": parsed_data.ad_structures.core.local_name,
            "service_uuids": parsed_data.ad_structures.core.service_uuids,
            "manufacturer_data": {k: v.hex() for k, v in parsed_data.ad_structures.core.manufacturer_data.items()},
            "tx_power": parsed_data.ad_structures.properties.tx_power,
            "flags": parsed_data.ad_structures.properties.flags,
            "rssi": parsed_data.rssi,
            "extended_payload": parsed_data.extended.extended_payload.hex()
            if parsed_data.extended.extended_payload
            else "",
            "auxiliary_packets_count": len(parsed_data.extended.auxiliary_packets),
            "periodic_advertising_data": (
                parsed_data.extended.periodic_advertising_data.hex()
                if parsed_data.extended.periodic_advertising_data
                else ""
            ),
            "broadcast_code": (
                parsed_data.ad_structures.mesh.broadcast_code.hex()
                if parsed_data.ad_structures.mesh.broadcast_code
                else ""
            ),
            "is_extended_advertising": parsed_data.is_extended_advertising,
            "total_payload_size": parsed_data.total_payload_size,
        }
    else:
        results["parsed"] = None

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Advertising data parsing example using the AdvertisingPDUParser.")
    parser.add_argument("--show-not-found", action="store_true", help="Show fields not found in the advertising data")
    parser.add_argument("--show-debug", action="store_true", help="Show debug information")
    parser.add_argument("--mock", action="store_true", help="Use mock legacy advertising data")
    parser.add_argument("--extended-mock", action="store_true", help="Use mock extended advertising data")
    parser.add_argument("--data", type=str, help="Hex string of advertising data to parse")
    args = parser.parse_args()
    asyncio.run(
        main(
            data=args.data,
            mock=args.mock,
            extended_mock=args.extended_mock,
            show_not_found=args.show_not_found,
            show_debug=args.show_debug,
        )
    )
