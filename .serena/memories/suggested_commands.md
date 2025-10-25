______________________________________________________________________

## applyTo: '\*\*'

# Suggested Commands

- `git submodule init && git submodule update` # required to pull official Bluetooth SIG YAML registry
- `python -c "import bluetooth_sig; print('✅ Framework ready')"` # quick import smoke test after setup
- `./scripts/format.sh --fix` # apply formatting (ruff/black wrappers)
- `./scripts/format.sh --check` # verify formatting passes
- `./scripts/lint.sh --all` # run full lint suite (ruff+pylint)
- `python -m pytest tests/ -v` # execute complete test suite
- `python -m pytest tests/test_uuid_registry.py -v` # focused registry loader test
