______________________________________________________________________

## applyTo: '\*\*'

# Task Completion Checklist

- Ensure Bluetooth SIG git submodule remains initialized/updated.
- Run `./scripts/format.sh --fix` then `./scripts/format.sh --check` to keep formatting compliant.
- Execute `./scripts/lint.sh --all` for full lint (pylint, ruff) coverage.
- Run `python -m pytest tests/ -v` and address failures before finishing.
- Cite consulted Bluetooth SIG/Python documentation in final notes.
- Confirm no forbidden imports or hardcoded UUIDs were introduced.
