#!/usr/bin/env python3
"""Generate a markdown file listing all supported characteristics and services.

This script scans the codebase to automatically generate documentation
of all supported GATT characteristics and services.
"""

import importlib
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.gatt.services.base import BaseGattService


def get_characteristic_info(cls: type) -> Tuple[str, str, str]:
    """Get UUID, name, and description for a characteristic class."""
    try:
        # Try to get info from _info attribute
        if hasattr(cls, '_info') and cls._info is not None:
            uuid = getattr(cls._info, 'uuid', 'N/A')
            name = getattr(cls._info, 'name', cls.__name__)
            # Convert UUID object to string if needed
            uuid = str(uuid).upper() if uuid != 'N/A' else 'N/A'
        else:
            # Fallback to class attributes
            uuid = 'N/A'
            name = cls.__name__.replace('Characteristic', '').replace('_', ' ')
        
        # Get description from docstring
        doc = inspect.getdoc(cls)
        if doc:
            # Get first line as description
            description = doc.split('\n')[0].strip()
        else:
            description = ""
        
        return uuid, name, description
    except Exception as e:
        print(f"Warning: Error processing {cls.__name__}: {e}", file=sys.stderr)
        return 'N/A', cls.__name__, ""


def discover_characteristics() -> List[Tuple[str, str, str, str]]:
    """Discover all characteristic classes.
    
    Returns:
        List of tuples: (class_name, uuid, name, description)
    """
    characteristics = []
    
    try:
        import bluetooth_sig.gatt.characteristics as chars_module
        
        # Get the package path
        package_path = Path(chars_module.__file__).parent
        
        # Iterate through all Python files in the characteristics directory
        for file_path in package_path.glob("*.py"):
            if file_path.name.startswith('_') or file_path.name in ['base.py', 'utils.py']:
                continue
            
            module_name = f"bluetooth_sig.gatt.characteristics.{file_path.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Find all classes that inherit from BaseCharacteristic
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseCharacteristic) and 
                        obj is not BaseCharacteristic and
                        obj.__module__ == module_name):
                        
                        uuid, char_name, description = get_characteristic_info(obj)
                        characteristics.append((name, uuid, char_name, description))
            except Exception as e:
                print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error discovering characteristics: {e}", file=sys.stderr)
    
    # Sort by name
    characteristics.sort(key=lambda x: x[2])
    return characteristics


def discover_services() -> List[Tuple[str, str, str]]:
    """Discover all service classes.
    
    Returns:
        List of tuples: (class_name, name, description)
    """
    services = []
    
    try:
        import bluetooth_sig.gatt.services as services_module
        
        # Get the package path
        package_path = Path(services_module.__file__).parent
        
        # Iterate through all Python files in the services directory
        for file_path in package_path.glob("*.py"):
            if file_path.name.startswith('_') or file_path.name == 'base.py':
                continue
            
            module_name = f"bluetooth_sig.gatt.services.{file_path.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Find all classes that inherit from BaseGattService
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseGattService) and 
                        obj is not BaseGattService and
                        obj.__module__ == module_name):
                        
                        # Get description from docstring
                        doc = inspect.getdoc(obj)
                        description = doc.split('\n')[0].strip() if doc else ""
                        
                        service_name = name.replace('Service', '').replace('_', ' ')
                        services.append((name, service_name, description))
            except Exception as e:
                print(f"Warning: Could not import {module_name}: {e}", file=sys.stderr)
    
    except Exception as e:
        print(f"Error discovering services: {e}", file=sys.stderr)
    
    # Sort by name
    services.sort(key=lambda x: x[1])
    return services


def generate_markdown() -> str:
    """Generate markdown documentation for characteristics and services."""
    
    characteristics = discover_characteristics()
    services = discover_services()
    
    md = """# Supported Characteristics and Services

This page lists all GATT characteristics and services currently supported by the library.

!!! note "Auto-Generated"
    This page is automatically generated from the codebase. The list is updated when new characteristics or services are added.

## Characteristics

The library currently supports **{num_chars}** GATT characteristics:

""".format(num_chars=len(characteristics))
    
    # Group by category based on common prefixes
    categories: Dict[str, List[Tuple[str, str, str, str]]] = {}
    
    for class_name, uuid, name, description in characteristics:
        # Try to categorize
        category = "Other"
        
        if any(x in name.lower() for x in ['battery', 'power']):
            category = "Power & Battery"
        elif any(x in name.lower() for x in ['temperature', 'humidity', 'pressure', 'uv', 'co2', 'pm', 'air']):
            category = "Environmental Sensing"
        elif any(x in name.lower() for x in ['heart', 'blood', 'glucose', 'weight', 'body']):
            category = "Health & Fitness"
        elif any(x in name.lower() for x in ['cycling', 'running', 'rsc', 'csc']):
            category = "Sports & Activity"
        elif any(x in name.lower() for x in ['manufacturer', 'model', 'serial', 'firmware', 'hardware', 'software']):
            category = "Device Information"
        elif any(x in name.lower() for x in ['current', 'voltage', 'electric']):
            category = "Electrical"
        
        if category not in categories:
            categories[category] = []
        categories[category].append((class_name, uuid, name, description))
    
    # Sort categories
    category_order = [
        "Power & Battery",
        "Environmental Sensing", 
        "Health & Fitness",
        "Sports & Activity",
        "Device Information",
        "Electrical",
        "Other"
    ]
    
    for category in category_order:
        if category not in categories or not categories[category]:
            continue
        
        md += f"\n### {category}\n\n"
        md += "| Characteristic | UUID | Description |\n"
        md += "|----------------|------|-------------|\n"
        
        for class_name, uuid, name, description in sorted(categories[category], key=lambda x: x[2]):
            # Truncate long descriptions
            if len(description) > 80:
                description = description[:77] + "..."
            md += f"| **{name}** | `{uuid}` | {description} |\n"
    
    md += "\n## Services\n\n"
    md += f"The library currently supports **{len(services)}** GATT services:\n\n"
    md += "| Service | Description |\n"
    md += "|---------|-------------|\n"
    
    for class_name, name, description in services:
        if len(description) > 100:
            description = description[:97] + "..."
        md += f"| **{name}** | {description} |\n"
    
    md += """

## Adding Support for New Characteristics

To add support for a new characteristic:

1. See the [Adding New Characteristics](guides/adding-characteristics.md) guide
2. Follow the existing patterns in `src/bluetooth_sig/gatt/characteristics/`
3. Add tests for your new characteristic
4. Submit a pull request

## Official Bluetooth SIG Registry

This library is based on the official [Bluetooth SIG Assigned Numbers](https://www.bluetooth.com/specifications/assigned-numbers/) registry. The UUID registry is loaded from YAML files in the `bluetooth_sig` submodule.
"""
    
    return md


def main():
    """Main entry point."""
    output_file = repo_root / "docs" / "supported-characteristics.md"
    
    print(f"Generating characteristics and services list...")
    markdown = generate_markdown()
    
    print(f"Writing to {output_file}...")
    output_file.write_text(markdown)
    
    print(f"✓ Successfully generated documentation")


if __name__ == "__main__":
    main()
