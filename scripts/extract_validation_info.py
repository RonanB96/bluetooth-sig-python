#!/usr/bin/env python3
"""Extract validation information from all GATT characteristics with source tracking.

This script scans all characteristic classes and outputs their validation
constraints with clear source attribution, including:
- Validation attributes (min_value, max_value, expected_length, etc.)
- YAML-derived ranges and constraints
- Special values (sentinel mappings)
- Unit information
- Manual overrides

SOURCE ATTRIBUTION LEGEND
=========================

Each value includes a "source" field indicating where it comes from:

1. resolved_sig_info       - From Bluetooth SIG registry resolution (UUID, name)
2. yaml_or_registry        - From YAML specs or Bluetooth registry (unit, value_type)
3. yaml_spec               - From Bluetooth SIG YAML specifications
4. yaml_spec_gss           - From GSS (Generalized Specification Structure) YAML
5. class_level_or_yaml     - From characteristic class attributes or YAML defaults
6. class_override          - Explicitly set on characteristic subclass
7. class_default           - From BaseCharacteristic parent class
8. manual_override         - Explicit manual override via _manual_unit, etc.
9. manual_override_plus_yaml  - Manual + YAML combined (special values)
10. runtime_descriptor_check  - Discovered at runtime (CCCD, etc.)
11. descriptor_runtime     - From device descriptor (Valid Range at runtime)
12. exception              - Error during extraction

VALIDATION PRECEDENCE
====================

When multiple sources could provide a value, this precedence applies:

1. Descriptor Valid Range (device-reported, highest priority - runtime)
2. Class-level attributes (characteristic spec defaults)
3. YAML-derived ranges (Bluetooth SIG specification - lowest priority)

Usage:
    python scripts/extract_validation_info.py
    python scripts/extract_validation_info.py --output /custom/path/validation_info.txt
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import tempfile
from pathlib import Path
from typing import Any

# Add src to path
import sys

src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bluetooth_sig.gatt.characteristics.base import BaseCharacteristic
from bluetooth_sig.types.gatt_enums import ValueType


def get_all_characteristic_classes() -> list[type[BaseCharacteristic]]:
    """Discover all characteristic classes by scanning the characteristics module."""
    from bluetooth_sig.gatt import characteristics as char_module

    char_path = Path(char_module.__file__).parent
    characteristic_classes: list[type[BaseCharacteristic]] = []

    # Scan all Python files in characteristics directory
    for py_file in char_path.glob("*.py"):
        if py_file.name.startswith("_"):
            continue

        module_name = py_file.stem
        try:
            module = importlib.import_module(f"bluetooth_sig.gatt.characteristics.{module_name}")

            # Find all BaseCharacteristic subclasses in the module
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, BaseCharacteristic)
                    and obj is not BaseCharacteristic
                    and not name.startswith("_")
                    and not getattr(obj, "_is_base_class", False)  # Skip abstract/base helpers
                ):
                    characteristic_classes.append(obj)
        except Exception as e:
            print(f"Warning: Could not load {module_name}: {e}", file=sys.stderr)

    return characteristic_classes


def extract_class_attributes(char_class: type[BaseCharacteristic]) -> dict[str, Any]:
    """Extract validation attributes from a characteristic class with source tracking."""
    attrs = {}

    # Class-level validation attributes (check if overridden in subclass)
    for attr_name in [
        "min_value",
        "max_value",
        "expected_length",
        "min_length",
        "max_length",
        "allow_variable_length",
        "expected_type",
    ]:
        value = getattr(char_class, attr_name, None)
        if value is not None:
            # Check if defined directly on this class (not inherited from BaseCharacteristic)
            is_override = attr_name in char_class.__dict__
            source = "class_override" if is_override else "class_default"

            if attr_name == "expected_type" and value is not None:
                attrs[attr_name] = {
                    "value": value.__name__ if hasattr(value, "__name__") else str(value),
                    "source": source,
                }
            else:
                attrs[attr_name] = {
                    "value": value,
                    "source": source,
                }

    # Manual overrides
    for attr_name in ["_manual_unit", "_manual_value_type"]:
        value = getattr(char_class, attr_name, None)
        if value is not None:
            attrs[attr_name] = {
                "value": str(value),
                "source": "manual_override",
            }

    return attrs


def extract_instance_info(char_class: type[BaseCharacteristic]) -> dict[str, Any]:
    """Extract validation info from a characteristic instance with source tracking."""
    info: dict[str, Any] = {}

    try:
        instance = char_class()

        # Basic info - all from resolved info
        info["uuid"] = {
            "value": str(instance.uuid),
            "source": "resolved_sig_info",
        }
        info["name"] = {
            "value": instance.name,
            "source": "resolved_sig_info",
        }

        # Unit - could be from manual override or YAML
        unit_source = "manual_override" if instance._manual_unit else "yaml_or_registry"
        info["unit"] = {
            "value": instance.unit,
            "source": unit_source,
        }

        # Value type - could be from manual override or YAML
        value_type_source = "manual_override" if instance._manual_value_type else "yaml_or_registry"
        info["value_type"] = {
            "value": instance.value_type.name if instance.value_type else "UNKNOWN",
            "source": value_type_source,
        }

        # Validation constraints - track which one is active
        if instance.min_value is not None:
            source = "descriptor_runtime" if hasattr(instance, "_descriptor_min") else "class_level_or_yaml"
            info["min_value"] = {
                "value": instance.min_value,
                "source": source,
            }

        if instance.max_value is not None:
            source = "descriptor_runtime" if hasattr(instance, "_descriptor_max") else "class_level_or_yaml"
            info["max_value"] = {
                "value": instance.max_value,
                "source": source,
            }

        if instance.expected_length is not None:
            info["expected_length"] = {
                "value": instance.expected_length,
                "source": "class_level_or_yaml",
            }

        if instance.min_length is not None:
            info["min_length"] = {
                "value": instance.min_length,
                "source": "class_level_or_yaml",
            }

        if instance.max_length is not None:
            info["max_length"] = {
                "value": instance.max_length,
                "source": "class_level_or_yaml",
            }

        if instance.allow_variable_length:
            info["allow_variable_length"] = {
                "value": True,
                "source": "class_level_or_yaml",
            }

        # YAML-derived info - all from YAML
        yaml_data_type = instance.get_yaml_data_type()
        if yaml_data_type:
            info["yaml_data_type"] = {
                "value": yaml_data_type,
                "source": "yaml_spec",
            }

        yaml_field_size = instance.get_yaml_field_size()
        if yaml_field_size:
            info["yaml_field_size"] = {
                "value": yaml_field_size,
                "source": "yaml_spec",
            }

        yaml_unit_id = instance.get_yaml_unit_id()
        if yaml_unit_id:
            info["yaml_unit_id"] = {
                "value": yaml_unit_id,
                "source": "yaml_spec",
            }

        yaml_resolution = instance.get_yaml_resolution_text()
        if yaml_resolution:
            info["yaml_resolution"] = {
                "value": yaml_resolution,
                "source": "yaml_spec",
            }

        # Special values - from GSS (YAML) but can be overridden
        special_values = instance.gss_special_values
        if special_values:
            has_manual_override = instance._special_values is not None
            source = "manual_override_plus_yaml" if has_manual_override else "yaml_spec_gss"
            info["special_values"] = {
                "value": special_values,
                "source": source,
            }

        # Descriptor support - runtime discovery
        info["can_notify"] = {
            "value": instance.can_notify(),
            "source": "runtime_descriptor_check",
        }

        # Spec description - from YAML
        if instance.spec and instance.spec.description:
            info["description"] = {
                "value": instance.spec.description,
                "source": "yaml_spec_gss",
            }

    except Exception as e:
        info["error"] = {
            "value": str(e),
            "source": "exception",
        }

    return info


def generate_validation_report(output_file: str | Path) -> None:
    """Generate comprehensive validation information report for all characteristics."""
    characteristic_classes = get_all_characteristic_classes()

    print(f"Found {len(characteristic_classes)} characteristic classes", file=sys.stderr)

    validation_data: dict[str, Any] = {
        "metadata": {
            "total_characteristics": len(characteristic_classes),
            "script": "extract_validation_info.py",
            "validation_precedence": {
                "order": [
                    "descriptor_runtime",
                    "class_level_or_yaml",
                    "yaml_spec",
                ],
                "note": "Descriptor Valid Range (runtime) > class-level attributes > YAML defaults",
                "source": "documentation",
            },
        },
        "characteristics": {},
    }

    # Extract info for each characteristic
    for i, char_class in enumerate(sorted(characteristic_classes, key=lambda x: x.__name__), 1):
        try:
            class_name = char_class.__name__
            print(f"[{i}/{len(characteristic_classes)}] Processing {class_name}...", file=sys.stderr)

            char_info = extract_instance_info(char_class)
            validation_data["characteristics"][class_name] = char_info

        except Exception as e:
            print(f"Error processing {char_class.__name__}: {e}", file=sys.stderr)
            validation_data["characteristics"][char_class.__name__] = {"error": str(e)}

    # Write to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(validation_data, f, indent=2, default=str)

    print(f"\n✅ Validation info written to: {output_path}", file=sys.stderr)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract validation information from GATT characteristics with source tracking"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (default: /tmp/validation_info_<timestamp>.json)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )

    args = parser.parse_args()

    # Generate output filename
    if args.output is None:
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", prefix="validation_info_", suffix=".json", delete=False, dir="/tmp"
        )
        output_file = tmp_file.name
        tmp_file.close()
    else:
        output_file = args.output

    # Generate report
    try:
        generate_validation_report(output_file)
        print(f"\n📊 Report summary:")
        print(f"   Output file: {output_file}")

        # Show stats
        with open(output_file) as f:
            data = json.load(f)
            total = data["metadata"]["total_characteristics"]
            with_errors = sum(1 for v in data["characteristics"].values() if "error" in v)
            print(f"   Total characteristics: {total}")
            print(f"   Successfully processed: {total - with_errors}")
            if with_errors:
                print(f"   With errors: {with_errors}")

        print(f"\n📋 Output format:")
        print(f"   Each value includes a 'source' field indicating origin:")
        print(f"   - resolved_sig_info: From Bluetooth SIG registry")
        print(f"   - yaml_spec: From Bluetooth SIG YAML specifications")
        print(f"   - class_level_or_yaml: From characteristic class or YAML defaults")
        print(f"   - manual_override: Explicit manual override")
        print(f"   - runtime_descriptor_check: Discovered at runtime")
        print(f"   - (see script header for full source legend)")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
