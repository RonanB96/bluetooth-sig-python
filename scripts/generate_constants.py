"""Generate GATT UUID constants from Bluetooth SIG specifications."""

from gatt_uuids import gatt_uuid_manager


def main():
    """Generate and save GATT UUID constants."""
    constants = gatt_uuid_manager.get_uuid_constants()

    # Save to constants file
    with open("gatt_constants.py", "w", encoding="utf-8") as f:
        f.write(constants)

    print("Generated GATT UUID constants from Bluetooth SIG specifications")

    # Print detailed information about environmental characteristics
    gatt_uuid_manager.print_environmental_info()


if __name__ == "__main__":
    main()
