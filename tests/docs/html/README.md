# HTML Parsing Tests

Static HTML validation using BeautifulSoup – no browser required.

## Purpose

Validates **build-time generated** content that doesn't exist in markdown sources:

- Theme-generated navigation (sidebar, footer, breadcrumbs)
- Sphinx-added accessibility attributes (lang, ARIA labels)
- Generated anchor IDs and internal links
- API documentation structure
- Security attributes on external links

**Not tested here:** Content quality (tested in markdown), interactive features (tested in Playwright).

## Quick Start

```bash
# Run all tests (parallel)
pytest tests/docs/html/ -v -n auto -m built_docs -p no:playwright

# Selective testing (respects DOCS_TEST_FILES env var)
export DOCS_TEST_FILES='["index.html"]'
pytest tests/docs/html/ -v -n auto -m built_docs -p no:playwright
```

## Why Not Playwright?

- **10-50× faster** than browser tests
- **No Chromium installation**
- **Static validation only** – uses BeautifulSoup instead of headless browser
