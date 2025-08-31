# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing and code quality checks.

## Workflows

### Test and Coverage (`test-coverage.yml`)
- **Triggers**: Push to `main`, Pull Requests to `main`
- **Matrix**: Python 3.11, 3.12 (Home Assistant compatible versions)
- **Purpose**: Run comprehensive test suite with coverage reporting
- **Features**:
  - Automatic git submodule initialization for `bluetooth_sig` dependency
  - Test execution with pytest and coverage reporting (76% coverage)
  - Coverage upload to Codecov for Python 3.12 runs
  - Uses project configuration from `pyproject.toml`

### Lint and Code Quality (`lint-check.yml`)
- **Triggers**: Push to `main`, Pull Requests to `main` 
- **Python**: 3.12 (latest supported)
- **Purpose**: Ensure code quality and consistent formatting
- **Tools**:
  - **flake8**: Style guide enforcement with project's `.flake8` config
  - **black**: Code formatting verification with diff output
  - **isort**: Import sorting verification with diff output
  - **pylint**: Static code analysis (current score: 9.73/10)

## Local Development

To run the same checks locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
python -m pytest tests/ --cov=src/ble_gatt_device --cov-report=term-missing

# Run linting tools
flake8 src/ tests/ --count --statistics
black --check --diff src/ tests/
isort --check-only --diff src/ tests/
pylint src/ble_gatt_device/ --exit-zero --score y
```

## Notes

- All tool configurations are defined in `pyproject.toml`
- Workflows use `--exit-zero` for pylint to prevent CI failures on minor issues
- Coverage reporting is optional and won't fail the build
- Git submodules are automatically initialized for the Bluetooth SIG UUID registry dependency