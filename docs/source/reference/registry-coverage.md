# Registry Coverage

Quick reference for Bluetooth SIG registry implementation status. Registry source files are located in `bluetooth_sig/assigned_numbers/`.

## Implementation Summary

| Folder                   | Source Files | Implemented | Status         |
| ------------------------ | ------------ | ----------- | -------------- |
| `uuids/`                 | 12           | 12          | ✅ Complete     |
| `core/`                  | 16           | 5           | 🔄 Partial      |
| `company_identifiers/`   | 1            | 1           | ✅ Complete     |
| `mesh/`                  | 15           | 0           | ❌ Out of scope |
| `profiles_and_services/` | 49           | 0           | 🔄 As needed    |
| `service_discovery/`     | 28           | 0           | ❌ Out of scope |

:::{note}
Mesh, SDP, and Classic Bluetooth registries are out of scope—this library focuses on BLE GATT. See [Limitations](../explanation/limitations.md).
:::

---

## Communication Registries

Registries used during active BLE communication: scanning, service discovery, characteristic read/write, and notifications.

### GATT Operations (Required)

These registries are **required** for core GATT functionality—service discovery, characteristic parsing, and data encoding/decoding.

| Registry Class        | Source File                       | Runtime Usage                                  |
| --------------------- | --------------------------------- | ---------------------------------------------- |
| `UuidRegistry`        | `uuids/service_uuids.yaml`        | Service discovery—resolves service UUIDs       |
| `UuidRegistry`        | `uuids/characteristic_uuids.yaml` | Characteristic lookup—UUID ↔ parser mapping    |
| `UuidRegistry`        | `uuids/descriptors.yaml`          | Descriptor identification in GATT table        |
| `UnitsRegistry`       | `uuids/units.yaml`                | Unit resolution for CPF descriptors and values |
| `FormatTypesRegistry` | `core/formattypes.yaml`           | CPF format field → type name (`uint16`, etc.)  |

### Advertising & Beacons

Essential for passive scanning and beacon-based sensors (temperature, proximity, asset tracking).

| Registry Class               | Source File                                    | Runtime Usage                                    |
| ---------------------------- | ---------------------------------------------- | ------------------------------------------------ |
| `ADTypesRegistry`            | `core/ad_types.yaml`                           | Validates AD structure types during scan parsing |
| `AppearanceValuesRegistry`   | `core/appearance_values.yaml`                  | Decodes device appearance (watch, thermometer)   |
| `CompanyIdentifiersRegistry` | `company_identifiers/company_identifiers.yaml` | Manufacturer ID → name (Apple, Nordic, etc.)     |
| `ClassOfDeviceRegistry`      | `core/class_of_device.yaml`                    | Classic BT Class of Device in dual-mode ads      |

:::{tip}
Many low-power sensors broadcast data via manufacturer-specific advertising packets. The `CompanyIdentifiersRegistry` resolves the 16-bit manufacturer ID, enabling proper routing to vendor-specific decoders.
:::

### CPF Descriptor Resolution

| Registry Class               | Source File                  | Runtime Usage                                       |
| ---------------------------- | ---------------------------- | --------------------------------------------------- |
| `NamespaceDescriptionRegistry` | `core/namespace.yaml`       | CPF description field → name (e.g., "left", "first") |

:::{tip}
The CPF (Characteristic Presentation Format) descriptor has a description field that, when namespace=0x01 (Bluetooth SIG), resolves to human-readable names. This enables automatic resolution of position indicators like "left", "right", "front" or ordinals like "first", "second" in multi-sensor devices.
:::

### URI Beacon Parsing

| Registry Class       | Source File              | Runtime Usage                                         |
| -------------------- | ------------------------ | ----------------------------------------------------- |
| `UriSchemesRegistry` | `core/uri_schemes.yaml`  | Decodes compressed URI scheme codes in advertising data |

:::{tip}
The Bluetooth SIG URI AD type (0x24) uses a compressed format where the first byte is a scheme code. For example, `0x16` = "http:" and `0x17` = "https:". The `UriSchemesRegistry` decodes these codes, enabling Eddystone URL beacon parsing and other URI-based beacon formats.
:::

### Planned Communication Registries

| Registry                       | Source File                                   | Use Case                               | Priority |
| ------------------------------ | --------------------------------------------- | -------------------------------------- | -------- |
| `CodingFormatRegistry`         | `core/coding_format.yaml`                     | LE Audio codec negotiation (LC3, etc.) | Medium   |

---

## Static Registries

Reference registries for UUID lookups, protocol identification, and metadata. Not used during active communication but useful for documentation, debugging, and completeness.

### UUID Reference Tables

| Registry Class                | Source File                           | Purpose                        |
| ----------------------------- | ------------------------------------- | ------------------------------ |
| `DeclarationsRegistry`        | `uuids/declarations.yaml`             | GATT declaration type names    |
| `MembersRegistry`             | `uuids/member_uuids.yaml`             | SIG member organisation UUIDs  |
| `ProtocolIdentifiersRegistry` | `uuids/protocol_identifiers.yaml`     | Protocol UUID reference        |
| `SdoUuidsRegistry`            | `uuids/sdo_uuids.yaml`                | Standards organisation IDs     |
| `ServiceClassesRegistry`      | `uuids/service_class.yaml`            | Classic BT service class UUIDs |
| `ObjectTypesRegistry`         | `uuids/object_types.yaml`             | Object Transfer Service types  |
| `BrowseGroupsRegistry`        | `uuids/browse_group_identifiers.yaml` | SDP browse group identifiers   |
| `MeshProfilesRegistry`        | `uuids/mesh_profile_uuids.yaml`       | Mesh profile UUID mappings     |

### Out of Scope

| Folder               | Files | Reason                                   |
| -------------------- | ----- | ---------------------------------------- |
| `mesh/`              | 15    | Mesh networking—different protocol stack |
| `service_discovery/` | 28    | SDP for Classic Bluetooth, not BLE       |

---

## Profile-Triggered Registries

Registries in `profiles_and_services/` are loaded on-demand when corresponding GATT characteristics are implemented:

| Profile  | Files | Trigger Characteristics         |
| -------- | ----- | ------------------------------- |
| LE Audio | 26    | ASCS, PACS, BAP service parsing |
| ESL      | 1     | Electronic Shelf Label GATT     |
| TBS      | 1     | Telephone Bearer Service        |
| TDS      | 1     | Transport Discovery Service     |

---

## Priority Roadmap

### LE Audio Foundation

**Coding Format Registry** — 9-entry registry for codec identification. Required foundation before implementing LE Audio characteristics (LC3, vendor codecs).

### As Needed

Profile registries added when corresponding characteristics are implemented. No preemptive loading to minimise startup overhead.

**Legend:** ✅ Implemented | 🔄 Planned | ❌ Out of scope

---

## See Also

- [Registry System Architecture](../explanation/architecture/registry-system.md) — Implementation details
- [Supported Characteristics](characteristics.md) — Full characteristic list
- [Limitations](../explanation/limitations.md) — Scope boundaries
