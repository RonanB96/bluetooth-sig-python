"""Simple test script to verify UUID loading."""

from pathlib import Path
import yaml


def load_yaml(file_path: Path) -> dict:
    """Load a YAML file."""
    with file_path.open("r") as f:
        return yaml.safe_load(f)


def test_uuid_loading():
    """Test loading UUIDs from YAML files."""
    base_path = (
        Path(__file__).parent.parent / "bluetooth_sig" / "assigned_numbers" / "uuids"
    )

    # Test Service UUIDs
    print("Testing Service UUID Loading:")
    print("-" * 50)

    service_data = load_yaml(base_path / "service_uuids.yaml")
    battery_service = None
    env_service = None

    for service in service_data["uuids"]:
        if isinstance(service["uuid"], str):
            uuid = service["uuid"].replace("0x", "")
        else:
            uuid = hex(service["uuid"])[2:].upper()

        if uuid == "180F":  # Battery Service
            battery_service = service
            print("Found Battery Service:")
            print(f"  UUID: {uuid}")
            print(f"  Name: {service['name']}")
            print(f"  ID: {service['id']}\n")

        elif uuid == "181A":  # Environmental Sensing
            env_service = service
            print("Found Environmental Sensing Service:")
            print(f"  UUID: {uuid}")
            print(f"  Name: {service['name']}")
            print(f"  ID: {service['id']}\n")

    assert battery_service is not None, "Failed to find Battery Service"
    assert env_service is not None, "Failed to find Environmental Service"
    assert battery_service["name"] == "Battery", "Wrong Battery Service name"
    assert (
        env_service["name"] == "Environmental Sensing"
    ), "Wrong Environmental Service name"

    # Test Characteristic UUIDs
    print("\nTesting Characteristic UUID Loading:")
    print("-" * 50)

    char_data = load_yaml(base_path / "characteristic_uuids.yaml")
    battery_level = None
    temperature = None
    humidity = None

    for char in char_data["uuids"]:
        if isinstance(char["uuid"], str):
            uuid = char["uuid"].replace("0x", "")
        else:
            uuid = hex(char["uuid"])[2:].upper()

        if uuid == "2A19":  # Battery Level
            battery_level = char
            print("Found Battery Level Characteristic:")
            print(f"  UUID: {uuid}")
            print(f"  Name: {char['name']}")
            print(f"  ID: {char['id']}\n")

        elif uuid == "2A6E":  # Temperature
            temperature = char
            print("Found Temperature Characteristic:")
            print(f"  UUID: {uuid}")
            print(f"  Name: {char['name']}")
            print(f"  ID: {char['id']}\n")

        elif uuid == "2A6F":  # Humidity
            humidity = char
            print("Found Humidity Characteristic:")
            print(f"  UUID: {uuid}")
            print(f"  Name: {char['name']}")
            print(f"  ID: {char['id']}\n")

    assert battery_level is not None, "Failed to find Battery Level characteristic"
    assert temperature is not None, "Failed to find Temperature characteristic"
    assert humidity is not None, "Failed to find Humidity characteristic"


def main():
    """Run the test."""
    try:
        test_uuid_loading()
        print("\nAll tests passed successfully! ✅")
    except AssertionError as e:
        print(f"\nTest failed: {e} ❌")
    except Exception as e:
        print(f"\nUnexpected error: {e} ❌")


if __name__ == "__main__":
    main()
