# Documentation Playwright Tests

Automated browser testing for the Bluetooth SIG Standards Library documentation using [Playwright](https://playwright.dev/).

## Overview

These tests verify:

- **Accessibility**: WCAG 2.1 compliance, ARIA attributes, semantic HTML
- **Navigation**: Links, anchors, breadcrumbs, sidebar structure
- **Quality**: Code blocks, styling, version information
- **Structure**: Diátaxis framework compliance

## Test Strategy

### Selective Testing (Default in CI)

The test suite automatically detects which documentation pages changed in your PR and only tests those pages, dramatically reducing CI runtime from ~35 minutes to ~2-5 minutes for typical changes.

**Triggers for comprehensive testing:**

- Changes to `docs/source/conf.py` (Sphinx configuration)
- Changes to `docs/source/_templates/` (affects all pages)
- Changes to `docs/source/_static/*.{css,js}` (global styling/scripts)

**Selective testing examples:**

- Edit `docs/source/tutorials/index.md` → Tests only `tutorials/index.html`
- Edit `src/bluetooth_sig/core/translator.py` → Tests only `api/bluetooth_sig/core/translator.html` (AutoAPI)
- Edit `docs/source/conf.py` → Tests all HTML pages

### How It Works

1. **Change Detection**: [`scripts/detect_changed_docs.py`](../../../scripts/detect_changed_docs.py) compares git refs to find changed source files
2. **Path Mapping**: Maps source files to their built HTML equivalents
3. **Parametrization**: [`tests/docs/conftest.py`](../conftest.py) filters test parametrization based on `DOCS_TEST_FILES` environment variable
4. **Parallel Execution**: `pytest-xdist` runs tests with `-n auto` for optimal parallelization

## Requirements

### System Dependencies

```bash
# Install Playwright browsers (one-time setup)
playwright install chromium --with-deps
```

### Python Dependencies

Installed automatically with test extras:

```bash
pip install -e ".[test]"
```

### Built Documentation

Tests require built Sphinx documentation. Build using the [justfile](../../../justfile) recipe:

```bash
just docs
```

Or directly with Sphinx:

```bash
sphinx-build -j auto -b html docs/source docs/build/html
```

## Running Tests Locally

### Using justfile recipes (recommended)

See [justfile](../../../justfile) for all available recipes:

```bash
# Test all documentation pages
just docs-test-all

# Test only changed pages (compares with origin/main)
just docs-test-changed

# Test specific pages
just docs-test-files tutorials/index.html api/index.html
```

### Using pytest directly

```bash
# Test all pages
DOCS_TEST_FILES='["ALL"]' pytest tests/docs/playwright_tests/ \
    -m "built_docs and playwright" \
    -n auto \
    -v

# Test specific pages
DOCS_TEST_FILES='["tutorials/index.html", "api/index.html"]' \
    pytest tests/docs/playwright_tests/ \
    -m "built_docs and playwright" \
    -n auto \
    -v

# Test changed pages (uses scripts/detect_changed_docs.py)
CHANGED=$(python scripts/detect_changed_docs.py --base origin/main --head HEAD)
DOCS_TEST_FILES="$CHANGED" pytest tests/docs/playwright_tests/ \
    -m "built_docs and playwright" \
    -n auto \
    -v
```

### Running without selective testing

If `DOCS_TEST_FILES` is not set, all HTML files are tested (default):

```bash
pytest tests/docs/playwright_tests/ -m "built_docs and playwright" -n auto -v
```

## Test Structure

### Test Files

- `test_accessibility.py` - WCAG compliance, ARIA, performance metrics
- `test_navigation.py` - Links, anchors, navigation structure, breadcrumbs
- `test_documentation_quality.py` - Code blocks, styling, version info, footer
- `test_sidebar_content.py` - Sidebar sections, ordering, Furo theme compliance
- `test_diataxis_structure.py` - Diátaxis framework verification

### Fixtures

**Session-scoped:**

- `docs_server` - HTTP server on port 8000 serving built documentation
- `docs_server_port` - Available port for server
- `docs_build_dir` - Path to `docs/build/html/`
- `all_html_files` - List of all HTML files

**Function-scoped:**

- `html_file` - Parametrized fixture providing URL for each HTML file to test
- `page` (Playwright) - Browser page with console error monitoring

**Configuration:**

- `browser_type_launch_args` - Chromium launch options (headless, no-sandbox)
- `monitor_console_errors` - Automatic JavaScript error detection

## CI/CD Integration

### GitHub Actions Workflow

The `test-documentation` job runs after `build-docs` in [`.github/workflows/test-coverage.yml`](../../../.github/workflows/test-coverage.yml):

```yaml
test-documentation:
  name: Test Documentation with Playwright
  needs: build-docs
  steps:
    - Checkout with full git history
    - Download built documentation artifact
    - Install Playwright and dependencies
    - Cache Playwright browsers (~150MB)
    - Detect changed files with scripts/detect_changed_docs.py
    - Run selective tests with pytest -n auto
    - Upload test results on failure
```

### Performance Optimizations

1. **Browser Caching**: Playwright browsers cached across CI runs (~150MB, saves 30s)
2. **Parallel Execution**: `-n auto` uses all available CPU cores
3. **Selective Testing**: Only tests changed pages (typical PR: 2-5 min vs 35 min)
4. **Artifact Reuse**: Downloads pre-built docs from `build-docs` job

## Environment Variables

### `DOCS_TEST_FILES`

JSON array controlling which HTML files to test:

```bash
# Test all files
DOCS_TEST_FILES='["ALL"]'

# Test specific files (paths relative to docs/build/html/)
DOCS_TEST_FILES='["tutorials/index.html", "api/index.html"]'

# Not set (default): Test all files
unset DOCS_TEST_FILES
```

## Troubleshooting

### Tests are skipped with "built_docs marker required"

Build the documentation first:

```bash
just docs
# or
sphinx-build -j auto -b html docs/source docs/build/html
```

### Playwright browser not found

Install Chromium:

```bash
playwright install chromium --with-deps
```

### "Server failed to start" error

Check if port 8000 is available or another test session is running. The fixture automatically finds an available port.

### JavaScript console errors failing tests

The `monitor_console_errors` fixture automatically detects JavaScript errors. Check browser console output in test failure messages.

### Selective testing not working

Verify `DOCS_TEST_FILES` environment variable:

```bash
echo $DOCS_TEST_FILES
# Should output: ["file1.html", "file2.html"] or ["ALL"]
```

Check change detection script with verbose output:

```bash
python scripts/detect_changed_docs.py --base origin/main --head HEAD --verbose
```

See [`scripts/detect_changed_docs.py`](../../../scripts/detect_changed_docs.py) for implementation details.

### CI tests running too long

Verify selective testing is working:

1. Check `detect_changed_docs.py` output in CI logs
2. Verify `DOCS_TEST_FILES` is set correctly
3. Check if `conf.py` was changed (triggers full test suite)

## Test Markers

These tests use markers to control execution:

```python
@pytest.mark.built_docs       # Requires built documentation (skipped in default pytest runs)
@pytest.mark.playwright       # Requires Playwright/browser
@pytest.mark.accessibility    # Accessibility-specific tests
```

**Important**: Documentation tests are **skipped by default** when running `pytest` without markers. This prevents failures when documentation hasn't been built.

Enable with:

```bash
pytest -m "built_docs and playwright"  # Run documentation tests
pytest -m accessibility                 # Run only accessibility tests
```

## Performance Expectations

### Local Testing (4-core CPU)

- **All pages** (~150 files): 8-10 minutes with `-n auto`
- **Single page**: ~2-3 seconds per page
- **Changed pages** (typical PR, 5 files): 15-30 seconds

### CI Testing (GitHub Actions)

- **Selective** (typical PR, 5 files): 2-5 minutes total
- **Comprehensive** (conf.py change): 10-15 minutes with `-n auto`
- **Browser cache hit**: Saves ~30 seconds on setup

## Best Practices

1. **Always build docs before testing locally**: `just docs`
2. **Use selective testing for faster iteration**: `just docs-test-changed`
3. **Run comprehensive tests before merging**: Verify in CI or `just docs-test-all`
4. **Check change detection output**: Use `--verbose` flag to verify file mapping
5. **Parallelize with `-n auto`**: Automatically uses all available CPU cores

## Architecture

### Change Detection Flow

```text
Git Diff (base...head)
    ↓
scripts/detect_changed_docs.py (maps sources → HTML)
    ↓
JSON Array ["file1.html", "file2.html"] or ["ALL"]
    ↓
DOCS_TEST_FILES environment variable
    ↓
tests/docs/conftest.py (pytest_generate_tests hook)
    ↓
Filtered test parametrization (per HTML file)
    ↓
pytest -n auto (parallel execution)
```

### File Mapping Examples

| Source File | Built HTML File |
|-------------|-----------------|
| `docs/source/tutorials/index.md` | `tutorials/index.html` |
| `docs/source/api/index.rst` | `api/index.html` |
| `src/bluetooth_sig/core/translator.py` | `api/bluetooth_sig/core/translator.html` |
| `docs/source/conf.py` | **ALL** files (triggers comprehensive testing) |

## Related Documentation

- [Playwright Python Documentation](https://playwright.dev/python/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [pytest-xdist Parallel Testing](https://pytest-xdist.readthedocs.io/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Diátaxis Framework](https://diataxis.fr/)

## Contributing

When adding new documentation pages:

1. Add content to `docs/source/`
2. Build documentation: `just docs`
3. Run tests: `just docs-test-changed`
4. Verify your page passes all checks

When modifying test suite:

1. Follow existing test patterns
2. Use parametrized `html_file` fixture for per-page tests
3. Add appropriate markers (`@pytest.mark.built_docs`, etc.)
4. Document expected behaviour in test docstrings
5. Test with both selective and comprehensive modes
