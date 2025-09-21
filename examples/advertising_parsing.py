#!/usr/bin/env python3
"""Advertising data parsing example using AdvertisingParser."""

from bluetooth_sig import BluetoothSIGTranslator


def demo_advertising_parsing() -> None:
    """Demonstrate advertising data parsing."""
    print("Advertising Data Parsing Example")
    print("=" * 40)

    # Create parser and translator
    # parser = AdvertisingParser()  # Would be used for actual parsing
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

    print("Mock advertising data:")
    print(f"  Local name: {mock_advertising_data['local_name']}")
    print(f"  Service UUIDs: {mock_advertising_data['service_uuids']}")

    if mock_advertising_data["manufacturer_data"]:
        for company_id, data in mock_advertising_data["manufacturer_data"].items():
            print(f"  Manufacturer data (0x{company_id:04X}): {data.hex()}")

    # Parse the advertising data
    print("\nParsing advertising data...")

    try:
        # The AdvertisingParser would parse raw PDU data in a real scenario
        # For this demo, we'll show the API
        print("AdvertisingParser methods available:")
        print("- parse_advertising_data(raw_pdu)")
        print("- parse_legacy_advertising(data)")
        print("- parse_extended_advertising(data)")

        # Show service name resolution using translator
        print("\nService name resolution:")
        for uuid in mock_advertising_data["service_uuids"]:
            service_info = translator.get_service_info_by_uuid(uuid)
            if service_info:
                print(f"  {uuid}: {service_info.name}")
            else:
                print(f"  {uuid}: Unknown service")

    except (ValueError, KeyError, AttributeError) as e:
        print(f"Error parsing advertising data: {e}")


if __name__ == "__main__":
    demo_advertising_parsing()
