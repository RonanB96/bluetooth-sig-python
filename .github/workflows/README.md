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
  - **flake8**: Style guide enforcement using `pyproject.toml` config (via flake8-pyproject)
  - **black**: Code formatting verification with diff output
  - **isort**: Import sorting verification with diff output
  - **pylint**: Static code analysis (current score: 9.73/10)
- **Environment Setup**: All tools run via `python -m` to ensure proper configuration loading

## Local Development

To run the same checks locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Initialize git submodules (required for UUID registry)
git submodule update --init --recursive

# Run tests with coverage
python -m pytest tests/ --cov=src/ble_gatt_device --cov-report=term-missing

# Run linting tools (use python -m for proper configuration loading)
python -m flake8 src/ tests/ --count --statistics
python -m black --check --diff src/ tests/
python -m isort --check-only --diff src/ tests/
python -m pylint src/ble_gatt_device/ --exit-zero --score y
```

## Environment Setup Requirements

### For Copilot Coding Agent
When testing locally or in agent environments, ensure:

1. **Python 3.11+** is available
2. **Git submodules** are initialized: `git submodule update --init --recursive`
3. **Package installation** in development mode: `pip install -e ".[dev]"`
4. **Tool execution** via Python modules: Use `python -m tool_name` instead of direct commands
5. **Configuration loading**: flake8-pyproject allows flake8 to read from `pyproject.toml`

### Key Environment Dependencies
- Git submodule `bluetooth_sig` must be present for UUID registry functionality
- All linting tools should be run via `python -m` to ensure proper configuration loading
- Black handles most formatting that would trigger flake8 style errors

## Notes

- All tool configurations are defined in `pyproject.toml` (no separate `.flake8` file)
- Workflows use `--exit-zero` for pylint to prevent CI failures on minor issues
- Coverage reporting is optional and won't fail the build
- Git submodules are automatically initialized for the Bluetooth SIG UUID registry dependency
- Use `python -m` prefix for all tools to ensure proper package and configuration loading