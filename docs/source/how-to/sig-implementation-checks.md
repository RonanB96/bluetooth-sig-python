# SIG Implementation Checks

Maintainers use two repository scripts to cross-check GATT implementations against Bluetooth SIG sources. These are optional, local checks—not part of the contributor quality gates in [Contributing](contributing.md).

## Scope and backlog

What is implemented, planned, and out of scope is documented in [Registry Coverage](../reference/registry-coverage.md). Use that reference when deciding whether a gap belongs in this repository.

## Spec table validation

`scripts/validate_service_characteristics_from_specs.py` compares characteristics tables from extracted spec text to classes under `src/bluetooth_sig/gatt/services/`.

1. Fetch spec HTML and prepare text extracts using **Fetching SIG Specs** in [`.github/copilot-instructions.md`](https://github.com/RonanB96/bluetooth-sig-python/blob/main/.github/copilot-instructions.md#fetching-sig-specs).
1. Save extracts under `.tmp/` as `*_spec.txt` (gitignored).
1. Run the script; see its module docstring and `python scripts/validate_service_characteristics_from_specs.py --help` for file layout, options, and exit codes.

## YAML coverage report

`scripts/gatt_coverage_report.py` reports YAML-defined UUIDs versus Python implementations for characteristics, services, and descriptors. See `python scripts/gatt_coverage_report.py --help` for usage.

## Runtime validation (applications)

For checking a concrete device service at runtime, use `validate_service()` on service classes—see [Service Validation](services.md#service-validation). That API is separate from the maintainer spec-table script above.

## See Also

- [Adding Characteristics](adding-characteristics.md) — Implement new characteristics and services
- [Registry Coverage](../reference/registry-coverage.md) — Implementation status and roadmap
- [Contributing](contributing.md) — Pull requests and quality gates
