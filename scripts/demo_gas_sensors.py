#!/usr/bin/env python3
"""
Gas Sensor Characteristics Demo

Demonstrates the parsing and functionality of all implemented gas sensor characteristics
for air quality monitoring.
"""

import sys
from pathlib import Path

# Configure path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
from path_config import configure_for_scripts
configure_for_scripts()

from ble_gatt_device.gatt.characteristics import (
    AmmoniaConcentrationCharacteristic,
    CO2ConcentrationCharacteristic,
    MethaneConcentrationCharacteristic,
    NitrogenDioxideConcentrationCharacteristic,
    OzoneConcentrationCharacteristic,
    PM10ConcentrationCharacteristic,
    PM1ConcentrationCharacteristic,
    PM25ConcentrationCharacteristic,
    SulfurDioxideConcentrationCharacteristic,
    TVOCConcentrationCharacteristic,
)


def demonstrate_gas_sensor_parsing():
    """Demonstrate parsing of simulated gas sensor data."""
    print("🌬️ Gas Sensor Characteristics Demo")
    print("=" * 60)
    print("Demonstrating air quality monitoring with BLE GATT framework")
    print()

    # Simulated air quality sensor data (realistic values)
    sensor_data = {
        # Core air quality sensors
        "CO2 (Indoor)": (
            CO2ConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x90, 0x01]),  # 400 ppm (good indoor air)
        ),
        "CO2 (Poor)": (
            CO2ConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x70, 0x17]),  # 6000 ppm (poor indoor air)
        ),
        "TVOC (Normal)": (
            TVOCConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0xF4, 0x01]),  # 500 ppb (normal)
        ),
        "TVOC (High)": (
            TVOCConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x10, 0x27]),  # 10000 ppb (high)
        ),
        # Extended gas sensors
        "Ammonia": (
            AmmoniaConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x19, 0x00]),  # 25 ppm
        ),
        "Methane": (
            MethaneConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x64, 0x00]),  # 100 ppm
        ),
        "NO2 (Urban)": (
            NitrogenDioxideConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x28, 0x00]),  # 40 ppb (typical urban)
        ),
        "Ozone": (
            OzoneConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x32, 0x00]),  # 50 ppb
        ),
        "SO2": (
            SulfurDioxideConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x0A, 0x00]),  # 10 ppb
        ),
        # Particulate matter sensors
        "PM1 (Good)": (
            PM1ConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x0F, 0x00]),  # 15 µg/m³
        ),
        "PM2.5 (Moderate)": (
            PM25ConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x19, 0x00]),  # 25 µg/m³
        ),
        "PM10 (Poor)": (
            PM10ConcentrationCharacteristic(uuid="", properties=set()),
            bytearray([0x37, 0x00]),  # 55 µg/m³
        ),
    }

    # Parse and display all sensor readings
    print("📊 Simulated Air Quality Readings:")
    print("-" * 60)

    for sensor_name, (characteristic, data) in sensor_data.items():
        try:
            parsed_value = characteristic.parse_value(data)
            unit = characteristic.unit
            device_class = characteristic.device_class
            uuid = characteristic.CHAR_UUID

            # Color code based on sensor type
            if "CO2" in sensor_name:
                emoji = "🏭"
            elif "TVOC" in sensor_name:
                emoji = "🧪"
            elif "PM" in sensor_name:
                emoji = "💨"
            else:
                emoji = "🌬️"

            print(
                f"{emoji} {sensor_name:15} | "
                f"{parsed_value:>6} {unit:>6} | "
                f"UUID: 0x{uuid} | "
                f"HA: {device_class}"
            )

        except ValueError as e:
            print(f"❌ {sensor_name:15} | Error: {e}")

    print("-" * 60)
    print()

    # Demonstrate special values
    print("⚠️ Special Value Handling:")
    print("-" * 40)

    co2_char = CO2ConcentrationCharacteristic(uuid="", properties=set())

    # Test special values
    special_cases = [
        ("Unknown value", bytearray([0xFF, 0xFF])),
        ("Exceeds range", bytearray([0xFE, 0xFF])),
    ]

    for case_name, data in special_cases:
        try:
            value = co2_char.parse_value(data)
            print(f"✅ {case_name}: {value} ppm")
        except ValueError as e:
            print(f"⚠️ {case_name}: {e}")

    print()

    # Show Home Assistant integration details
    print("🏠 Home Assistant Integration:")
    print("-" * 40)

    example_chars = [
        CO2ConcentrationCharacteristic(uuid="", properties=set()),
        TVOCConcentrationCharacteristic(uuid="", properties=set()),
        PM25ConcentrationCharacteristic(uuid="", properties=set()),
    ]

    for char in example_chars:
        print(
            f"• {char.__class__.__name__:30} | "
            f"device_class: {char.device_class:20} | "
            f"state_class: {char.state_class}"
        )

    print()
    print("✅ All 10 gas sensor characteristics implemented successfully!")
    print("🌟 Ready for comprehensive air quality monitoring!")


if __name__ == "__main__":
    demonstrate_gas_sensor_parsing()