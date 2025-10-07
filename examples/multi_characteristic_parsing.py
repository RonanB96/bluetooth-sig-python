#!/usr/bin/env python3
"""Example demonstrating multi-characteristic parsing with dependencies.

This example shows how to implement characteristics that depend on data from
other characteristics, following Bluetooth SIG specification patterns like:
- Glucose Measurement Context (depends on Glucose Measurement sequence number)
- Blood Pressure measurements (depends on feature flags)
- Environmental Sensing (multiple sensors sharing descriptors)

The multi-characteristic parsing pattern enables:
1. Calibration data applied to raw measurements
2. Sequence number matching between related characteristics
3. Feature flags controlling interpretation of measurement data
"""

import struct
import sys
from pathlib import Path

# Set up paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bluetooth_sig.core import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.base import CustomBaseCharacteristic
from bluetooth_sig.gatt.context import CharacteristicContext
from bluetooth_sig.types import CharacteristicInfo
from bluetooth_sig.types.gatt_enums import GattProperty, ValueType
from bluetooth_sig.types.uuid import BluetoothUUID


# Define custom characteristics demonstrating the pattern
class CalibrationCharacteristic(CustomBaseCharacteristic):
    """Calibration factor characteristic (independent).

    This characteristic stores a calibration factor that will be
    applied to sensor readings.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("CA11B001-0000-1000-8000-00805F9B34FB"),
        name="Calibration Factor",
        unit="unitless",
        value_type=ValueType.FLOAT,
        properties=[GattProperty.READ],
    )

    def decode_value(self, data: bytearray, ctx=None) -> float:
        """Parse calibration factor as float32."""
        return struct.unpack("<f", bytes(data))[0]

    def encode_value(self, data: float) -> bytearray:
        """Encode calibration factor."""
        return bytearray(struct.pack("<f", data))


class SensorReadingCharacteristic(CustomBaseCharacteristic):
    """Sensor reading that depends on calibration (dependent).

    SIG Pattern:
    This demonstrates optional context enrichment - the characteristic works
    standalone but provides more accurate values when calibration is available.
    """

    _info = CharacteristicInfo(
        uuid=BluetoothUUID("5E450001-0000-1000-8000-00805F9B34FB"),
        name="Sensor Reading",
        unit="calibrated units",
        value_type=ValueType.FLOAT,
        properties=[GattProperty.READ, GattProperty.NOTIFY],
    )

    # Declare dependency on calibration characteristic
    dependencies = ["CA11B001-0000-1000-8000-00805F9B34FB"]

    def decode_value(self, data: bytearray, ctx: CharacteristicContext | None = None) -> float:
        """Parse sensor reading and apply calibration if available.

        Args:
            data: Raw sensor reading as int16
            ctx: Optional context providing access to calibration

        Returns:
            Calibrated sensor reading
        """
        # Parse raw sensor value
        raw_value = int.from_bytes(bytes(data[:2]), byteorder="little", signed=True)

        # Default calibration factor
        calibration_factor = 1.0

        # Enhance with context if available (SIG pattern)
        if ctx is not None:
            calib_char = ctx.get_characteristic_by_uuid("CA11B001-0000-1000-8000-00805F9B34FB")
            if calib_char and calib_char.parse_success:
                calibration_factor = calib_char.value

        return raw_value * calibration_factor

    def encode_value(self, data: float) -> bytearray:
        """Encode sensor reading."""
        raw = int(data)
        return bytearray(raw.to_bytes(2, byteorder="little", signed=True))


def demonstrate_independent_parsing():
    """Show how independent characteristics are parsed normally."""
    print("=" * 70)
    print("Example 1: Independent Characteristic Parsing")
    print("=" * 70)

    translator = BluetoothSIGTranslator()

    # Register custom characteristic
    translator.register_custom_characteristic_class(
        str(CalibrationCharacteristic._info.uuid),
        CalibrationCharacteristic,
        override=True,
    )

    # Create test data: calibration factor = 2.5
    calib_data = struct.pack("<f", 2.5)

    # Parse calibration characteristic
    result = translator.parse_characteristic(
        str(CalibrationCharacteristic._info.uuid),
        calib_data,
    )

    print(f"✅ Parsed calibration factor: {result.value}")
    print(f"   Parse success: {result.parse_success}")
    print(f"   Characteristic: {result.name}")
    print()


def demonstrate_dependent_parsing_without_context():
    """Show how dependent characteristics work without context (standalone mode)."""
    print("=" * 70)
    print("Example 2: Dependent Characteristic Without Context (Standalone)")
    print("=" * 70)

    translator = BluetoothSIGTranslator()

    # Register custom characteristic
    translator.register_custom_characteristic_class(
        str(SensorReadingCharacteristic._info.uuid),
        SensorReadingCharacteristic,
        override=True,
    )

    # Create test data: raw sensor reading = 100
    sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

    # Parse sensor reading WITHOUT context
    result = translator.parse_characteristic(
        str(SensorReadingCharacteristic._info.uuid),
        sensor_data,
    )

    print(f"✅ Parsed sensor reading: {result.value}")
    print(f"   Parse success: {result.parse_success}")
    print("   Note: Used default calibration factor (1.0) since no context provided")
    print()


def demonstrate_dependent_parsing_with_context():
    """Show how dependent characteristics use context for enriched results."""
    print("=" * 70)
    print("Example 3: Dependent Characteristic With Context (Enhanced)")
    print("=" * 70)

    translator = BluetoothSIGTranslator()

    # Register custom characteristics
    translator.register_custom_characteristic_class(
        str(CalibrationCharacteristic._info.uuid),
        CalibrationCharacteristic,
        override=True,
    )
    translator.register_custom_characteristic_class(
        str(SensorReadingCharacteristic._info.uuid),
        SensorReadingCharacteristic,
        override=True,
    )

    # Create test data
    calib_data = struct.pack("<f", 2.5)
    sensor_data = (100).to_bytes(2, byteorder="little", signed=True)

    # Parse calibration first
    calib_result = translator.parse_characteristic(
        str(CalibrationCharacteristic._info.uuid),
        calib_data,
    )
    print(f"📊 Step 1: Parsed calibration factor: {calib_result.value}")

    # Parse sensor WITH context containing calibration
    ctx = CharacteristicContext(other_characteristics={str(CalibrationCharacteristic._info.uuid): calib_result})

    sensor_result = translator.parse_characteristic(
        str(SensorReadingCharacteristic._info.uuid),
        sensor_data,
        ctx=ctx,
    )

    print(f"✅ Step 2: Parsed sensor reading: {sensor_result.value}")
    print("   Raw value: 100")
    print("   Calibration factor: 2.5")
    print(f"   Calibrated value: 100 × 2.5 = {sensor_result.value}")
    print()


def demonstrate_batch_parsing_with_dependencies():
    """Show how batch parsing handles dependencies automatically."""
    print("=" * 70)
    print("Example 4: Automatic Dependency-Aware Batch Parsing")
    print("=" * 70)

    translator = BluetoothSIGTranslator()

    # Register custom characteristics
    translator.register_custom_characteristic_class(
        str(CalibrationCharacteristic._info.uuid),
        CalibrationCharacteristic,
        override=True,
    )
    translator.register_custom_characteristic_class(
        str(SensorReadingCharacteristic._info.uuid),
        SensorReadingCharacteristic,
        override=True,
    )

    # Create test data (order doesn't matter - dependencies handled automatically)
    char_data = {
        # Dependent characteristic (will be parsed AFTER calibration)
        str(SensorReadingCharacteristic._info.uuid): (100).to_bytes(2, byteorder="little", signed=True),
        # Independent characteristic (will be parsed FIRST)
        str(CalibrationCharacteristic._info.uuid): struct.pack("<f", 2.5),
    }

    print("📦 Input characteristics (in arbitrary order):")
    print(f"   1. {SensorReadingCharacteristic._info.name}")
    print(f"   2. {CalibrationCharacteristic._info.name}")
    print()

    # Parse all characteristics - dependencies handled automatically!
    results = translator.parse_characteristics(char_data)

    print("🔄 Parsing order (determined by dependencies):")
    print(f"   1. {CalibrationCharacteristic._info.name} (no dependencies)")
    print(f"   2. {SensorReadingCharacteristic._info.name} (depends on calibration)")
    print()

    print("✅ Results:")
    for uuid, result in results.items():
        if uuid == str(CalibrationCharacteristic._info.uuid):
            print(f"   {result.name}: {result.value}")
        else:
            print(f"   {result.name}: {result.value} (with calibration applied)")

    print()
    print("💡 Key Insight: The translator automatically:")
    print("   - Detected the dependency declaration")
    print("   - Sorted characteristics by dependencies (topological sort)")
    print("   - Parsed independent characteristics first")
    print("   - Provided context to dependent characteristics")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("Multi-Characteristic Parsing Examples")
    print("Following Bluetooth SIG Specification Patterns")
    print("=" * 70 + "\n")

    demonstrate_independent_parsing()
    demonstrate_dependent_parsing_without_context()
    demonstrate_dependent_parsing_with_context()
    demonstrate_batch_parsing_with_dependencies()

    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print("""
This pattern is used in official SIG specifications:

1. Glucose Service (0x1808):
   - Glucose Measurement Context depends on Glucose Measurement
   - Uses sequence number matching

2. Blood Pressure (0x1810):
   - Blood Pressure Measurement depends on Feature characteristic
   - Uses feature flags for interpretation

3. Cycling Power (0x1818):
   - Power Measurement depends on Feature and Sensor Location
   - Uses feature flags and location context

Key Benefits:
✅ Characteristics work standalone when context unavailable
✅ Enhanced accuracy/interpretation when context provided
✅ Automatic dependency resolution in batch parsing
✅ SIG specification compliance
    """)


if __name__ == "__main__":
    main()
