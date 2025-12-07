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

# Test all documentation pages with Playwright
docs-test-all:
    @echo "🧪 Testing all documentation pages..."
    DOCS_TEST_FILES='["ALL"]' pytest tests/docs/playwright_tests/ -m "built_docs and playwright" -n auto -v

# Test only changed documentation pages (compares with main branch)
docs-test-changed:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "🔍 Detecting changed documentation files..."
    CHANGED=$$(python scripts/detect_changed_docs.py --base origin/main --head HEAD --verbose)
    echo "📋 Files to test: $$CHANGED"
    export DOCS_TEST_FILES="$$CHANGED"
    pytest tests/docs/playwright_tests/ -m "built_docs and playwright" -n auto -v

# Test specific documentation pages (provide space-separated paths)
docs-test-files FILES:
    #!/usr/bin/env bash
    set -euo pipefail
    FILES_JSON=$$(python -c "import sys, json; print(json.dumps(sys.argv[1:]))" {{FILES}})
    echo "📋 Testing files: $$FILES_JSON"
    export DOCS_TEST_FILES="$$FILES_JSON"
    pytest tests/docs/playwright_tests/ -m "built_docs and playwright" -n auto -v

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

# Print the current version of the project (from git describe)
version:
    @git describe --tags
