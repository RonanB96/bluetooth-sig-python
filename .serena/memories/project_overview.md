______________________________________________________________________

## applyTo: '\*\*'

# Bluetooth SIG Standards Library Overview

- Purpose: Provide a pure-Python library that loads the official Bluetooth SIG assigned-number registry and offers standards-compliant, type-safe parsing for 70+ GATT services/characteristics with automatic UUID resolution.
- Tech stack: Python 3.9+, dataclasses, typing; relies on bundled Bluetooth SIG YAML registry via git submodule. Framework-agnostic for BLE integrations (bleak, simplepyble, etc.).
- Structure: `src/bluetooth_sig/` contains core translator, device utilities, GATT characteristics/services, registry loaders, and type helpers; `bluetooth_sig/assigned_numbers/` holds upstream YAML data; `examples/` showcases integrations; `tests/` provides comprehensive validation; `scripts/` exposes lint/format helpers.
- Key practices: Strict type hints everywhere, dataclass-based data modelling, no hardcoded UUIDs, raise precise errors, maintain SIG compliance.
- Docs: See README and `docs/AGENT_GUIDE.md` plus `.github/copilot-instructions.md` for agent workflow.
