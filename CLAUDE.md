# Bluetooth SIG Standards Library

Pure Python library for Bluetooth SIG standards interpretation. Core lives in `src/bluetooth_sig/` (framework-agnostic).

**Working directory:** repository root. **Python version:** 3.10+.

## Build & Test

```bash
./scripts/format.sh --fix && ./scripts/format.sh --check
./scripts/lint.sh --all
python -m pytest tests/ -v
```

For complete rules and patterns, see `.github/copilot-instructions.md` and `.github/instructions/` sub-files (loaded based on file type).

Architecture guides: `docs/AGENT_GUIDE.md`, `docs/BLUETOOTH_SIG_ARCHITECTURE.md`
