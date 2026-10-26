# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing, code quality checks, and releases.

## Workflows

### Test and Coverage (`test-coverage.yml`)

- **Triggers**: Push to `main`, Pull Requests to `main`
- **Purpose**: Benchmarks, documentation build, and GitHub Pages deploy
- The Python library pytest job is disabled. `btsig.yml` checks the C library.

### btsig (`btsig.yml`)

- **Triggers**: Push and pull requests to `main` and `v2_dev`
- **Purpose**: Format, build, and clang-tidy the `btsig` library
- **Checks**:
  - `clang-format-18` with `btsig/.clang-format` on every C file under `btsig` and `examples/characteristic_api`, skipping build directories
  - CMake build of the library from `btsig/modules`, then the sample programs from `examples/characteristic_api`, with `-Werror`
  - `clang-tidy-18` using `btsig/.clang-tidy` on every translation unit in the library and sample compile databases

### Lint and Code Quality (`lint-check.yml`)

- **Triggers**: Push and pull requests to `main` and `v2_dev`
- **Python**: 3.12 (latest supported)
- **Purpose**: Ensure code quality and consistent formatting
- **Tools**:
  - **ruff**: Formatting and linting of `src/`, `tests/`, `examples/`, and `tools/`
  - **mypy**: strict for production code and `tools/`, lenient for tests/examples
- **Environment Setup**: All tools run via `python -m` to ensure proper configuration loading

### Release (`release.yml`)

- **Trigger**: Push of a `v*.*.*` tag (e.g. `v0.1.0`)
- **Purpose**: Build, publish to PyPI, and create a GitHub Release
- **Jobs**:
  1. **build** — builds sdist + wheel using `hatchling`, verifies with `twine check`
  2. **publish-pypi** — publishes to PyPI via trusted publisher (OIDC). Requires the `pypi` GitHub environment.
  3. **github-release** — generates release notes with `git-cliff` and creates a GitHub Release with the distribution artefacts.
- **Prerequisites**: The repository must have a `pypi` environment configured with PyPI trusted publisher credentials.

## Local Development

To run the same checks locally:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Initialise git submodules (required for UUID registry)
git submodule update --init --recursive

# Run tests with coverage
python -m pytest tests/ --cov=src/bluetooth_sig --cov-report=term-missing

# Run linting
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/

# Run type checking
python -m mypy src/bluetooth_sig/
```

## Environment Setup Requirements

### For Copilot Coding Agent

When testing locally or in agent environments, ensure:

1. **Python 3.11+** is available
1. **Git submodules** are initialised: `git submodule update --init --recursive`
1. **Package installation** in development mode: `pip install -e ".[dev]"`
1. **Tool execution** via Python modules: Use `python -m tool_name` instead of direct commands

### Key Environment Dependencies

- Git submodule `bluetooth_sig` must be present for UUID registry functionality
- All linting/formatting is handled by `ruff` — configured in `pyproject.toml`

## Notes

- All tool configurations are defined in `pyproject.toml`
- The Python library coverage job is disabled. `btsig/.clang-tidy` is the C lint config.
- Git submodules are automatically initialised for the Bluetooth SIG UUID registry dependency
- Use `python -m` prefix for all tools to ensure proper package and configuration loading
