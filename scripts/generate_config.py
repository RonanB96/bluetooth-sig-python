"""Generate Home Assistant configuration for a BLE GATT device."""

from pathlib import Path
import sys

# Adjust path to include src directory
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from gatt.gatt_sensors import gatt_sensor_translator  # noqa: E402


def generate_ha_config(device_name: str, mac_address: str) -> None:
    """Generate Home Assistant sensor configuration for a BLE device.

    Args:
        device_name: User-friendly name for the device
        mac_address: MAC address of the device
    """
    print(f"# Home Assistant configuration for {device_name}")
    print("# Add this to your configuration.yaml\n")

    print("sensor:")

    # Get all available sensors
    sensors = gatt_sensor_translator.get_sensor_characteristics()

    for uuid, (_, info) in sorted(sensors.items(), key=lambda x: x[1][1].name):
        print(f"  # {info.name}")
        print("  - platform: ble_gatt_device")
        print(f"    name: {device_name} {info.name}")
        print(f'    mac: "{mac_address}"')
        print(f'    characteristic: "{uuid}"')
        print(f"    device_class: {info.device_class.value}")
        print(f"    state_class: {info.state_class.value}")
        if info.unit_of_measurement:
            print(f'    unit_of_measurement: "{info.unit_of_measurement}"')
        if info.suggested_display_precision is not None:
            print(
                (
                    f"    suggested_display_precision: "
                    f"{info.suggested_display_precision}"
                )
            )
        print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_config.py <device_name> <mac_address>")
        print(
            "Example: python generate_config.py "
            "'Weather Station' '00:11:22:33:44:55'"
        )
        sys.exit(1)

    generate_ha_config(sys.argv[1], sys.argv[2])
