---
description: Core project layout, non-negotiable rules, workflow, and quality gates
alwaysApply: true
---

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
5. **Top-of-module imports** — see `python-implementation.instructions.md` (Imports).
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

Adopted specification text is already in `.tmp/sig-specs/` (245 kept documents). Search that. Do not download the catalogue again.

- Index: `.tmp/sig-specs/manifest.json`. Use `disposition: kept`.
- Text: `.tmp/sig-specs/txt/<slug>_spec.txt`.
- For one title, open the kept entry with the highest numeric version (`1.10` is newer than `1.9`). Skip `not_needed`.
- Current Core text: `core-specification-6-3`. Supplement data types: `core-specification-supplement-15`. Do not search `core-specification-amended-*` unless that version was requested.
- Search the chosen file with `rg`. Read a short window around the hit. Do not load a Core or Mesh file whole.
- HTML text splits headings (`3.1`, then `.`, then the title) and uses pipe tables. PDF text keeps a heading on one line and uses spaced columns. Lines with long dot leaders are the contents list.

Assigned Numbers remain https://www.bluetooth.com/specifications/assigned-numbers/. Fetch a specification from https://www.bluetooth.com/specifications/specs/ only when that slug has no kept text file. Use the first public HTML link (`out/en`), not the locked cross-spec link, and do not guess the URL. Never `fetch_webpage` the listing page.

## Sub-Instructions

Detailed rules are in `.github/instructions/` (symlinked from `.cursor/rules/`):
- `bluetooth-gatt.instructions.md` — GATT layer, templates, pipeline, characteristic patterns
- `python-implementation.instructions.md` — Python coding standards, type safety, data modelling
- `testing.instructions.md` — Test structure, fixtures, edge cases, commands
- `documentation.instructions.md` — Doc style, code samples, diagrams
