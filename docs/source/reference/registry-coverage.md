# Registry Coverage

Quick reference for Bluetooth SIG registry implementation status. Registry source files are located in `bluetooth_sig/assigned_numbers/`.

## Implementation Summary

| Folder                   | Source Files | Implemented | Status          |
| ------------------------ | ------------ | ----------- | --------------- |
| `uuids/`                 | 12           | 12          | ✅ Complete      |
| `core/`                  | 16           | 3           | 🔄 Partial |
| `company_identifiers/`   | 1            | 1           | ✅ Complete      |
| `mesh/`                  | 15           | 0           | ❌ Out of scope  |
| `profiles_and_services/` | 49           | 0           | 🔄 As needed     |
| `service_discovery/`     | 28           | 0           | ❌ Out of scope  |

:::{note}
Mesh, SDP, and Classic Bluetooth registries are out of scope—this library focuses on BLE GATT. See [Limitations](../explanation/limitations.md).
:::

## uuids/

All 12 UUID registry files are implemented. Core GATT UUIDs (services, characteristics, descriptors) are loaded by `UuidRegistry`; others have dedicated registry classes.

| File                            | Registry Class                | Notes                      |
| ------------------------------- | ----------------------------- | -------------------------- |
| `service_uuids.yaml`            | `UuidRegistry`                | GATT services              |
| `characteristic_uuids.yaml`     | `UuidRegistry`                | GATT characteristics       |
| `descriptors.yaml`              | `UuidRegistry`                | GATT descriptors           |
| `units.yaml`                    | `UnitsRegistry`               | Measurement units          |
| `browse_group_identifiers.yaml` | `BrowseGroupsRegistry`        | SDP browse groups          |
| `declarations.yaml`             | `DeclarationsRegistry`        | GATT declaration types     |
| `member_uuids.yaml`             | `MembersRegistry`             | SIG member UUIDs           |
| `mesh_profile_uuids.yaml`       | `MeshProfilesRegistry`        | Mesh profile mappings      |
| `object_types.yaml`             | `ObjectTypesRegistry`         | OTS type definitions       |
| `protocol_identifiers.yaml`     | `ProtocolIdentifiersRegistry` | Protocol UUIDs             |
| `sdo_uuids.yaml`                | `SdoUuidsRegistry`            | SDO identifiers            |
| `service_class.yaml`            | `ServiceClassesRegistry`      | Classic BT service classes |

## core/

3 of 16 files implemented. Priority items marked.

| File                     | Status | Notes                         |
| ------------------------ | ------ | ----------------------------- |
| `ad_types.yaml`          | ✅      | Advertising data types        |
| `appearance_values.yaml` | ✅      | Device appearance codes       |
| `class_of_device.yaml`   | ✅      | Classic BT CoD decoding       |
| `formattypes.yaml`       | 🔄      | **Priority**: GSS field types |
| `coding_format.yaml`     | ❌      | Audio codecs                  |
| `uri_schemes.yaml`       | ❌      | URI beacon parsing            |
| Others (10 files)        | ❌      | Out of scope for GATT         |

## company_identifiers/

| File                       | Status | Notes            |
| -------------------------- | ------ | ---------------- |
| `company_identifiers.yaml` | ✅      | Manufacturer IDs |

## Priority Roadmap

**Format Types** (`core/formattypes.yaml`) - GATT Specification Supplement field parsing. Defines data types (`uint8`, `sint16`, `float32`, etc.) used in characteristic definitions.

### Profile-Triggered Additions

Registries in `profiles_and_services/` will be added when corresponding GATT characteristics are implemented:

| Profile  | Files | Trigger                     |
| -------- | ----- | --------------------------- |
| LE Audio | 26    | LE Audio characteristics    |
| ESL      | 1     | Electronic Shelf Label GATT |
| TBS      | 1     | Telephone Bearer Service    |

**Legend:** ✅ Implemented | 🔄 Planned | ❌ Out of scope

## See Also

- [Registry System Architecture](../explanation/architecture/registry-system.md) - Implementation details
- [Supported Characteristics](characteristics.md) - Full characteristic list
- [Limitations](../explanation/limitations.md) - Scope boundaries
