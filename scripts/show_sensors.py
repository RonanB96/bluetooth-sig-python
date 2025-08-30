"""Example script showing available GATT sensors."""

from pathlib import Path
import sys

# Adjust path to include parent directory
parent_path = str(Path(__file__).parent.parent)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

from src.gatt.gatt_sensors import gatt_sensor_translator  # noqa: E402


def main():
    """Print available sensors from the Environmental Sensing Service."""
    print("Environmental Sensors:")
    print("====================")
    gatt_sensor_translator.print_available_sensors(
        gatt_sensor_translator.ENVIRONMENTAL_SERVICE_UUID
    )

    print("\n\nBattery Sensors:")
    print("===============")
    gatt_sensor_translator.print_available_sensors(
        gatt_sensor_translator.BATTERY_SERVICE_UUID
    )

    print("\n\nAll Available Sensors:")
    print("====================")
    gatt_sensor_translator.print_available_sensors()


if __name__ == "__main__":
    main()
