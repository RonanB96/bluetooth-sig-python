#!/usr/bin/env python3
"""Generate a markdown file listing all supported characteristics and services.

This script uses the registries to automatically generate documentation
of all supported GATT characteristics and services.
"""

from __future__ import annotations

import inspect
import re
import subprocess
import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from bluetooth_sig.gatt.characteristics import get_characteristic_class_map  # noqa: E402
from bluetooth_sig.gatt.resolver import NameNormalizer  # noqa: E402
from bluetooth_sig.gatt.services import get_service_class_map  # noqa: E402
from bluetooth_sig.gatt.uuid_registry import get_uuid_registry  # noqa: E402


def clean_description(description: str) -> str:
    """Clean description text for markdown display.

    Args:
        description: Raw description from YAML or docstring

    Returns:
        Cleaned description suitable for markdown table
    """
    if not description:
        return ""

    cleaned = NameNormalizer.sanitize_display_markup(description)
    cleaned = cleaned.replace(r"\autoref{", "")
    cleaned = cleaned.replace("}", "")

    # Remove newlines and extra whitespace
    cleaned = " ".join(cleaned.split())

    # Get first sentence only (up to first period followed by space or end)
    # But avoid matching decimals like "PM2.5" or "0.1"
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

    return NameNormalizer.sanitize_display_markup(name)


def get_characteristic_info(char_class: type) -> tuple[str, str, str]:
    """Get UUID, name, and description for a characteristic class.

    Args:
        char_class: The characteristic class

    Returns:
        Tuple of (uuid, name, description)

    """
    try:
        uuid_registry = get_uuid_registry()
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
        uuid_registry = get_uuid_registry()
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


def get_coverage_summary() -> tuple[int, int, list[str], int, int, list[str]]:
    """Return implementation coverage against the pinned SIG YAML registry.

    Returns:
        Tuple of implemented characteristic count, total characteristic count,
        missing characteristic names, implemented service count, total service
        count, and missing service names.
    """
    uuid_registry = get_uuid_registry()
    uuid_registry.ensure_loaded()

    characteristic_registry = uuid_registry._characteristics
    service_registry = uuid_registry._services

    implemented_characteristics = {
        uuid_obj.normalized
        for char_class in get_characteristic_class_map().values()
        if (uuid_obj := char_class.get_class_uuid()) is not None
    }
    implemented_services = {
        uuid_obj.normalized
        for service_class in get_service_class_map().values()
        if (uuid_obj := service_class.get_class_uuid()) is not None
    }

    missing_characteristics = sorted(
        characteristic_registry[uuid].name
        for uuid in characteristic_registry
        if uuid not in implemented_characteristics
    )
    missing_services = sorted(
        service_registry[uuid].name for uuid in service_registry if uuid not in implemented_services
    )

    return (
        len(implemented_characteristics),
        len(characteristic_registry),
        missing_characteristics,
        len(implemented_services),
        len(service_registry),
        missing_services,
    )


def get_sig_submodule_context() -> tuple[str, str]:
    """Return the pinned SIG submodule SHA and commit URL.

    Returns:
        Tuple of the full pinned commit SHA and a link to that upstream commit.

    Raises:
        subprocess.CalledProcessError: If git cannot resolve the submodule status.
    """
    result = subprocess.run(
        ["git", "submodule", "status", "--", "bluetooth_sig"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    sha = result.stdout.strip().split()[0].lstrip("-+")
    commit_url = f"https://bitbucket.org/bluetooth-SIG/public/commits/{sha}"
    return sha, commit_url


def generate_markdown() -> str:
    """Generate markdown documentation for characteristics and services."""
    characteristics = discover_characteristics()
    services = discover_services()
    (
        implemented_characteristic_count,
        total_characteristic_count,
        missing_characteristics,
        implemented_service_count,
        total_service_count,
        missing_services,
    ) = get_coverage_summary()
    sig_sha, sig_commit_url = get_sig_submodule_context()
    short_sig_sha = sig_sha[:7]

    md = f"""# Supported Characteristics and Services

This page lists the GATT characteristics and services currently implemented by the library.

!!! note "Auto-Generated"
    This page is automatically generated from the runtime registries and the pinned
    Bluetooth SIG YAML data by `scripts/generate_char_service_list.py`.
    The list is updated when new characteristics or services are added. See
    [Adding Characteristics](../how-to/adding-characteristics.md) to learn how to contribute
    new characteristics.

## Coverage Summary

The pinned Bluetooth SIG registry currently defines **{total_characteristic_count}** GATT characteristics and
**{total_service_count}** GATT services.

Pinned SIG data commit: [`{short_sig_sha}`]({sig_commit_url})

The library currently implements **{implemented_characteristic_count} of {total_characteristic_count}**
characteristics and **{implemented_service_count} of {total_service_count}** services.

## Implemented Characteristics

The library currently supports **{len(characteristics)}** implemented GATT characteristics:
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
                for char_name_enum in service_class.service_characteristics:
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

    if missing_characteristics:
        md += "\n## Not Yet Implemented Characteristics\n\n"
        md += (
            "The following Bluetooth SIG characteristics exist in the pinned registry but do not yet have "
            "runtime implementations in this repository:\n\n"
        )
        for name in missing_characteristics:
            md += f"- {name}\n"

    if missing_services:
        md += "\n## Not Yet Implemented Services\n\n"
        md += (
            "The following Bluetooth SIG services exist in the pinned registry but do not yet have "
            "runtime implementations:\n\n"
        )
        for name in missing_services:
            md += f"- {name}\n"

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
