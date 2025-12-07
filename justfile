# Justfile for bluetooth-sig-python

# Show available commands
list:
    @just --list

# Initialize the bluetooth_sig submodule (REQUIRED before first use)
init:
    git submodule init
    git submodule update
    @echo "✅ Submodule initialized. Run 'just install' to set up Python environment."

# Install dependencies for development
install:
    pip install -e .[dev,test,examples]

# Run all the formatting, linting, and testing commands
qa:
    ./scripts/format.sh --fix
    ./scripts/lint.sh --all
    python -m pytest tests/ -n auto --ignore=tests/benchmarks/ -v

# Run all the tests, but allow for arguments to be passed
test *ARGS:
    python -m pytest tests/ -n auto --ignore=tests/benchmarks/ {{ARGS}}

# Run all the tests, but on failure, drop into the debugger (serial execution required)
pdb *ARGS:
    python -m pytest tests/ --pdb --maxfail=10 --pdbcls=IPython.terminal.debugger:TerminalPdb {{ARGS}}

# Run performance benchmarks
benchmark:
    python -m pytest tests/benchmarks/ --benchmark-only --benchmark-columns=min,max,mean,stddev --benchmark-sort=name

# Run coverage and build HTML report (matches CI requirements)
coverage:
    python -m pytest tests/ -n auto --ignore=tests/benchmarks/ --cov=src/bluetooth_sig --cov-report=html --cov-report=xml --cov-report=term-missing --cov-fail-under=70

# Build documentation site with Sphinx (parallel build)
docs:
    sphinx-build -j auto -b html docs/source docs/build/html

# Serve documentation locally (opens built docs in browser)
docs-serve:
    @echo "Opening documentation in browser..."
    python -m http.server --directory docs/build/html 8000

# Build the project distribution
build:
    rm -rf build dist
    python -m build

# Remove all build, test, coverage and Python artifacts
clean:
    rm -fr build/
    rm -fr dist/
    rm -fr site/
    rm -fr .eggs/
    rm -fr .pytest_cache/
    rm -fr .mypy_cache/
    rm -fr .ruff_cache/
    rm -fr htmlcov/
    rm -f .coverage
    rm -f benchmark.json
    find . -type d -name '*.egg-info' -exec rm -fr {} +
    find . -type f -name '*.egg' -delete
    find . -type f -name '*.pyc' -delete
    find . -type f -name '*.pyo' -delete
    find . -type f -name '*~' -delete
    find . -type d -name '__pycache__' -exec rm -fr {} +

VERSION := `grep -m1 '^version' pyproject.toml | sed -E 's/version = "(.*)"/\1/'`

# Print the current version of the project
version:
    @echo "Current version is {{VERSION}}"
