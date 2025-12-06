#!/usr/bin/env python3
"""Generate a markdown file listing all supported characteristics and services.

This script uses the registries to automatically generate documentation
of all supported GATT characteristics and services.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from bluetooth_sig.gatt.characteristics import get_characteristic_class_map  # noqa: E402
from bluetooth_sig.gatt.resolver import NameNormalizer  # noqa: E402
from bluetooth_sig.gatt.services import get_service_class_map  # noqa: E402
from bluetooth_sig.gatt.uuid_registry import uuid_registry  # noqa: E402


def clean_description(description: str) -> str:
    """Clean description text for markdown display.

    Args:
        description: Raw description from YAML or docstring

    Returns:
        Cleaned description suitable for markdown table
    """
    if not description:
        return ""

    # Replace LaTeX formatting with Unicode/HTML equivalents
    replacements = {
        r"\textsubscript{2}": "₂",
        r"\textsubscript{3}": "₃",
        r"\textsubscript{1}": "₁",
        r"\textsubscript{0}": "₀",
        r"\textsubscript{": "<sub>",
        r"}": "</sub>",  # Only for subscripts
        r"\autoref{": "",  # Remove LaTeX reference commands
    }

    cleaned = description
    for pattern, replacement in replacements.items():
        cleaned = cleaned.replace(pattern, replacement)

    # Remove newlines and extra whitespace
    cleaned = " ".join(cleaned.split())

    # Get first sentence only (up to first period followed by space or end)
    # But avoid matching decimals like "PM2.5" or "0.1"
    import re

    match = re.search(r"^(.*?)\.\s", cleaned)  # Period followed by space
    if match:
        cleaned = match.group(1).strip() + "."
    elif cleaned and not cleaned.endswith("."):
        # If no sentence-ending period found, add one
        cleaned = cleaned + "."

    return cleaned


def clean_name(name: str) -> str:
    """Clean name text for markdown display (LaTeX only, no sentence extraction).

    Args:
        name: Raw name from YAML

    Returns:
        Cleaned name suitable for markdown
    """
    if not name:
        return ""

    # Replace LaTeX formatting with Unicode/HTML equivalents
    replacements = {
        r"\textsubscript{2}": "₂",
        r"\textsubscript{3}": "₃",
        r"\textsubscript{1}": "₁",
        r"\textsubscript{0}": "₀",
        r"\textsubscript{": "<sub>",
        r"}": "</sub>",
    }

    cleaned = name
    for pattern, replacement in replacements.items():
        cleaned = cleaned.replace(pattern, replacement)

    return cleaned


def get_characteristic_info(char_class: type) -> tuple[str, str, str]:
    """Get UUID, name, and description for a characteristic class.

    Args:
        char_class: The characteristic class

    Returns:
        Tuple of (uuid, name, description)

    """
    try:
        # Get UUID from the class method
        uuid_obj = char_class.get_class_uuid()
        uuid = str(uuid_obj).upper() if uuid_obj else "N/A"

        # Try to get name from registry first (most accurate)
        registry_info = uuid_registry.get_characteristic_info(uuid_obj) if uuid_obj else None
        if registry_info:
            name = clean_name(registry_info.name)  # Clean LaTeX from name (no sentence extraction)
            # Try to get description from YAML via resolve_characteristic_spec
            char_spec = uuid_registry.resolve_characteristic_spec(registry_info.name)
            raw_description = char_spec.description.strip() if char_spec and char_spec.description else ""
            description = clean_description(raw_description)
        else:
            # Fallback to class name processing
            base_name = NameNormalizer.remove_suffix(char_class.__name__, "Characteristic")
            name = NameNormalizer.camel_case_to_display_name(base_name)
            description = ""

        return uuid, name, description
    except Exception as e:
        print(f"Warning: Error processing {char_class.__name__}: {e}", file=sys.stderr)
        return "N/A", char_class.__name__, ""


def get_service_info(service_class: type) -> tuple[str, str, str]:
    """Get UUID, name, and description for a service class.

    Args:
        service_class: The service class

    Returns:
        Tuple of (uuid, name, description)

    """
    try:
        # Get UUID from the class method
        uuid_obj = service_class.get_class_uuid()
        uuid = str(uuid_obj).upper() if uuid_obj else "N/A"

        # Try to get name from registry first (most accurate)
        registry_info = uuid_registry.get_service_info(uuid_obj) if uuid_obj else None
        if registry_info:
            name = clean_name(registry_info.name)  # Clean LaTeX from name (no sentence extraction)
            doc = inspect.getdoc(service_class)
            raw_description = doc.split("\n")[0].strip() if doc else ""
            description = clean_description(raw_description)
        else:
            # Fallback to class name processing
            base_name = NameNormalizer.remove_suffix(service_class.__name__, "Service")
            name = NameNormalizer.camel_case_to_display_name(base_name)
            description = ""

        return uuid, name, description
    except Exception as e:
        print(f"Warning: Error processing {service_class.__name__}: {e}", file=sys.stderr)
        return "N/A", service_class.__name__, ""


def discover_characteristics() -> list[tuple[str, str, str, str]]:
    """Discover all characteristic classes from the registry.

    Returns:
        List of tuples: (class_name, uuid, name, description)

    """
    characteristics = []

    try:
        # Use the characteristic class map directly
        for _char_name, char_class in get_characteristic_class_map().items():
            uuid, name, description = get_characteristic_info(char_class)
            characteristics.append((char_class.__name__, uuid, name, description))

    except Exception as e:
        print(f"Error discovering characteristics: {e}", file=sys.stderr)

    # Sort by name
    characteristics.sort(key=lambda x: x[2])
    return characteristics


def discover_services() -> list[tuple[str, str, str, str]]:
    """Discover all service classes from the registry.

    Returns:
        List of tuples: (class_name, uuid, name, description)

    """
    services = []

    try:
        # Use the service class map directly
        for _service_name, service_class in get_service_class_map().items():
            uuid, name, description = get_service_info(service_class)
            services.append((service_class.__name__, uuid, name, description))

    except Exception as e:
        print(f"Error discovering services: {e}", file=sys.stderr)

    # Sort by name
    services.sort(key=lambda x: x[2])
    return services


def generate_markdown() -> str:
    """Generate markdown documentation for characteristics and services."""
    characteristics = discover_characteristics()
    services = discover_services()

    md = f"""# Supported Characteristics and Services

This page lists all GATT characteristics and services currently supported by the library.

!!! note "Auto-Generated"
    This page is automatically generated from the codebase by `scripts/generate_char_service_list.py`.
    The list is updated when new characteristics or services are added. See
    [Adding Characteristics](../how-to/adding-characteristics.md) to learn how to contribute
    new characteristics.

## Characteristics

The library currently supports **{len(characteristics)}** GATT characteristics:
"""

    # Build a mapping of characteristic names to the services they belong to
    # char_name -> [(service_name, service_uuid, service_class)]
    char_to_services: dict[str, list[tuple[str, str, str]]] = {}

    for service_class_name, service_uuid, service_name, _service_description in services:
        # Get the actual service class to access its service_characteristics
        try:
            service_class = get_service_class_map().get(service_name.replace(" ", "").upper())
            if service_class is None:
                # Try alternative lookup
                for _key, cls in get_service_class_map().items():
                    if cls.__name__ == service_class_name:
                        service_class = cls
                        break

            if service_class and hasattr(service_class, "service_characteristics"):
                # Get the characteristics defined in this service
                for char_name_enum in service_class.service_characteristics.keys():
                    # Convert enum to readable name
                    char_display_name = char_name_enum.value.replace("_", " ").title()

                    if char_display_name not in char_to_services:
                        char_to_services[char_display_name] = []

                    char_to_services[char_display_name].append((service_name, service_uuid, service_class_name))
        except Exception as e:
            print(f"Warning: Could not process service {service_class_name}: {e}", file=sys.stderr)
            continue

    # Group characteristics by service
    # service_name -> [(class_name, uuid, name, description)]
    service_groups: dict[str, list[tuple[str, str, str, str]]] = {}
    ungrouped_chars: list[tuple[str, str, str, str]] = []

    for class_name, uuid, name, description in characteristics:
        if name in char_to_services:
            # Add to each service that uses this characteristic
            for service_name, _service_uuid, _service_class_name in char_to_services[name]:
                if service_name not in service_groups:
                    service_groups[service_name] = []
                service_groups[service_name].append((class_name, uuid, name, description))
        else:
            ungrouped_chars.append((class_name, uuid, name, description))

    # Output characteristics grouped by service
    # Sort services alphabetically
    for service_name in sorted(service_groups.keys()):
        chars_in_service = service_groups[service_name]
        if not chars_in_service:
            continue

        md += f"\n### {service_name}\n\n"
        md += "| Characteristic | UUID | Description |\n"
        md += "|----------------|------|-------------|\n"

        for _class_name, uuid, name, description in sorted(chars_in_service, key=lambda x: x[2]):
            md += f"| **{name}** | `{uuid}` | {description} |\n"

    # Add ungrouped characteristics if any
    if ungrouped_chars:
        md += "\n### Other Characteristics\n\n"
        md += "| Characteristic | UUID | Description |\n"
        md += "|----------------|------|-------------|\n"

        for _class_name, uuid, name, description in sorted(ungrouped_chars, key=lambda x: x[2]):
            md += f"| **{name}** | `{uuid}` | {description} |\n"

    md += "\n## Services\n\n"
    md += f"The library currently supports **{len(services)}** GATT services:\n\n"
    md += "| Service | UUID | Description |\n"
    md += "|---------|------|-------------|\n"

    for _class_name, uuid, name, description in services:
        md += f"| **{name}** | `{uuid}` | {description} |\n"

    md += """
## Adding Support for New Characteristics

To add support for a new characteristic:

1. See the [Adding Characteristics](../how-to/adding-characteristics.md) guide
2. Follow the existing patterns in `src/bluetooth_sig/gatt/characteristics/`
3. Add tests for your new characteristic in `tests/gatt/characteristics/`
4. Submit a pull request

## Official Bluetooth SIG Registry

This library is based on the official [Bluetooth SIG Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/)
registry. The UUID registry is loaded from YAML files in the `bluetooth_sig` submodule.
"""

    return md


def main() -> None:
    """Main entry point."""
    output_file = repo_root / "docs" / "source" / "reference" / "characteristics.md"

    # Create directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print("Generating characteristics and services list...")
    markdown = generate_markdown()

    print(f"Writing to {output_file}...")
    output_file.write_text(markdown)

    print("✓ Successfully generated documentation")


if __name__ == "__main__":
    main()
