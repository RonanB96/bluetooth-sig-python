"""Example script showing GATT hierarchy."""

from gatt_hierarchy import gatt_hierarchy


def print_characteristics(service_uuid: str) -> None:
    """Print all characteristics for a service."""
    chars = gatt_hierarchy.get_service_characteristics(service_uuid)
    if not chars:
        print("  No characteristics found")
        return

    for char in sorted(chars.values(), key=lambda x: x.name):
        print(f"\n  Characteristic: {char.name}")
        print(f"  UUID: {char.uuid}")
        if char.summary:
            print(f"  Summary: {char.summary}")
        if char.properties:
            print(f"  Properties: {', '.join(sorted(char.properties))}")

        for desc in sorted(char.descriptors.values(), key=lambda x: x.name):
            print(f"\n    Descriptor: {desc.name}")
            print(f"    UUID: {desc.uuid}")
            if desc.summary:
                print(f"    Summary: {desc.summary}")


def main() -> None:
    """Print environmental service hierarchies."""
    env_services = gatt_hierarchy.get_environmental_services()

    print("Environmental Services Found:")
    print("===========================\n")

    if not env_services:
        print("No environmental services found.")
        return

    for service in sorted(env_services, key=lambda x: x.name):
        print(f"Service: {service.name}")
        print(f"UUID: {service.uuid}")
        if service.summary:
            print(f"Summary: {service.summary}")

        print_characteristics(service.uuid)
        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
