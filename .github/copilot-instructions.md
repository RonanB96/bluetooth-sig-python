# Bluetooth SIG Standards Library

Pure Python library for Bluetooth SIG standards interpretation (GATT characteristics, services, advertisements).

## Project Layout

```
bluetooth_sig/          ← READ-ONLY submodule (SIG YAML data). Never modify.
  gss/                  ← Characteristic YAML definitions (source of truth)
  assigned_numbers/     ← Company IDs, UUIDs, service discovery data
  dp/                   ← Device properties
src/bluetooth_sig/      ← Implementation code (framework-agnostic, no BLE backend imports)
  core/                 ← Public API facade and engines
  gatt/characteristics/ ← Characteristic modules
    base.py             ← BaseCharacteristic[T] — uses composition via _template, NOT inheritance
    templates/          ← Reusable coding templates (numeric, scaled, string, composite, etc.)
    pipeline/           ← Parse/encode pipelines + validation
  registry/             ← Thread-safe singleton registries (lazy-load from YAML)
  advertising/          ← BLE advertising packet parsing
  device/               ← Device abstraction layer
  stream/               ← Stream parsing
  types/                ← Type definitions & enums
tests/                  ← Mirrors src/ structure; primary location: gatt/characteristics/
```

## Non-Negotiable Rules

1. **YAML is read-only.** If Python and YAML disagree, fix the Python.
2. **No framework imports** (`homeassistant`, `bleak`, `simplepyble`) in `src/bluetooth_sig/`.
3. **No hardcoded UUIDs** in implementation — use registry resolution.
4. **No `Optional`** — use `Type | None`.
5. **No `TYPE_CHECKING` blocks** or lazy imports in core logic.
6. **No raw `dict`/`tuple` returns** — use `msgspec.Struct`.
7. **No bare `except:`** or silent `pass`.
8. **No `hasattr`/`getattr`** when direct access works.
9. **All public functions fully typed.** `Any` requires inline justification.
10. **Never set `_python_type`** on new characteristics — `BaseCharacteristic[T]` auto-resolves it.

## Workflow

1. **Research** — Cite official Bluetooth SIG specs (see "Fetching SIG Specs" below)
2. **Test** — Success + 2 failure cases minimum per function
3. **Implement** — Use templates from `gatt/characteristics/templates/`. Override `_decode_value()` for composites.
4. **Validate** — Run quality gates (no exceptions)
5. **Document** — Google-style docstrings. Update `docs/` if code changes break examples.

## Quality Gates

```bash
./scripts/format.sh --fix && ./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

## Fetching SIG Specs

- Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers/
- Specifications: https://www.bluetooth.com/specifications/specs/

To get a spec's HTML URL (**one spec at a time**):
1. `curl https://www.bluetooth.com/specifications/specs/` — find the service slug from href links
2. `curl https://www.bluetooth.com/specifications/specs/{slug}/` — extract public HTML link: `grep -o 'href="[^"]*out/en[^"]*"'`
3. Extract the full `?src=` value (including any `prefix_timestamp/` portion)
4. Build URL: `https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/{full_src_value}`
5. `fetch_webpage` that URL

**Never** `fetch_webpage` the listing page (strips hrefs). **Never** guess URL patterns. Use the first (no-lock-icon) HTML link, not the "HTML with cross-spec linking" (requires membership).

## Sub-Instructions

Detailed rules are in `.github/instructions/`:
- `bluetooth-gatt.instructions.md` — GATT layer, templates, pipeline, characteristic patterns
- `python-implementation.instructions.md` — Python coding standards, type safety, data modelling
- `testing.instructions.md` — Test structure, fixtures, edge cases, commands
- `documentation.instructions.md` — Doc style, code samples, diagrams

