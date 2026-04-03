# Bluetooth SIG Standards Library

Pure Python library for Bluetooth SIG standards interpretation (GATT characteristics, services, advertisements).

**Working directory:** repository root.

## Quick Start

```bash
./scripts/format.sh --fix # Format
./scripts/lint.sh --all                                     # Lint
python -m pytest tests/ -v                                  # Test
python -m pytest -k "battery" -v                            # Single test
```

## Canonical Guidance

Use `.github/copilot-instructions.md` as the single source of truth for project-wide rules.

Use focused files in `.github/instructions/` for file-type and domain-specific rules:
- `bluetooth-gatt.instructions.md`
- `python-implementation.instructions.md`
- `testing.instructions.md`
- `documentation.instructions.md`
