# Bluetooth SIG Standards Library

A pure Python library for Bluetooth SIG standards interpretation (GATT characteristics, services, advertisements). Core lives in `src/bluetooth_sig/` must remain framework-agnostic.

## Architectural Prohibitions

Never use:
- `TYPE_CHECKING` blocks or lazy imports in core logic
- Hardcoded UUID strings in implementation code (use registry resolution)
- `from typing import Optional` (use `Type | None`)
- Bare `except:` or silent `pass`
- Raw `dict`/`tuple` returns (use `msgspec.Struct`)
- Untyped public functions
- Framework imports (`homeassistant`, `bleak`, `simplepyble`) in `src/bluetooth_sig/`
- `hasattr`/`getattr` when direct access works

These are non-negotiable. Violations require explicit justification.

## Mandatory Workflow

1. **Research** — Cite official: Bluetooth SIG Assigned Numbers, SIG Specs (HTML), or `docs/AGENT_GUIDE.md`
2. **Test** — Every function: success + 2 failure cases minimum
3. **Implement** — Use templates from `gatt/characteristics/templates/`. Override `_decode_value()` for composites.
4. **Type** — All public functions must be fully typed. Generic `BaseCharacteristic[T]` auto-resolves `_python_type`.
5. **Validate** — Run full quality gates before completion
6. **Documentation** — If code changes break code blocks in `./docs/`, update those blocks. Add docstrings to all new public functions (Google style).

## Quality Gates

```bash
./scripts/format.sh --fix && ./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

No exceptions. Pipe output to file; fix issues, don't suppress.

## Reference

**Official Specs:**
- Bluetooth SIG Assigned Numbers: https://www.bluetooth.com/specifications/assigned-numbers/
- Bluetooth SIG Specifications (search): https://www.bluetooth.com/specifications/specs/ — to get the actual HTML spec URL, do the following **one spec at a time**:
  1. Find the service slug from the base page: `curl https://www.bluetooth.com/specifications/specs/` | grep -o 'href="[^"]*specifications/specs/[^"]*"'`
  2. `curl https://www.bluetooth.com/specifications/specs/{slug}/` and extract the public HTML link: `grep -o 'href="[^"]*out/en[^"]*"'` — this returns something like `href="...?src=prefix_timestamp/SPEC_v1.0/out/en/index-en.html"`
  3. Extract the FULL `?src=` value (everything after `?src=`, including any `prefix_timestamp/` portion)
  4. Build full URL: `https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/{full_src_value}`
  5. `fetch_webpage` that full URL to get the spec content
  - **Never** use `fetch_webpage` directly on the listing page — it strips hrefs
  - **Never** guess URL patterns — always curl the slug page first
  - The public (no-login) HTML link is the first entry in the Documents table on the service page (no lock icon); `HTML with cross-spec linking` requires membership — do not use it

**Entry points:** `src/bluetooth_sig/core/translator.py` (public API), `src/bluetooth_sig/gatt/` (characteristics), `src/bluetooth_sig/registry/` (UUID lookup)

**Sub-instructions:** `python-implementation.instructions.md`, `bluetooth-gatt.instructions.md`, `testing.instructions.md`, `documentation.instructions.md`

Trust these instructions. Search codebase only if missing or wrong.

