# Documentation Test Reorganization Summary

## Changes Made

### Directory Structure
```
tests/docs/
├── conftest.py                          # Shared fixtures (docs_build_dir, docs_server, etc.)
├── test_source_content.py               # NEW: Tests on markdown/RST source files
├── test_docs_hooks.py                   # UNCHANGED: Python unit tests
├── test_generate_diagrams.py            # UNCHANGED: Python unit tests
└── playwright/                          # NEW: Browser-based tests directory
    ├── __init__.py                      # NEW: Package marker
    ├── test_diataxis_structure.py       # NEW: Extracted from test_diataxis_compliance.py
    ├── test_accessibility.py            # MOVED: All accessibility tests
    ├── test_documentation_quality.py    # MOVED: Quality checks requiring rendering
    └── test_navigation.py               # MOVED: Navigation and theme tests
```

### Test File Categories

#### Source-Based Tests (No Build Required)
**File**: `test_source_content.py`
- ✅ `test_markdown_images_have_alt_text` - Parse markdown image syntax
- ✅ `test_code_blocks_have_language` - Check code fence language tags
- ✅ `test_tutorials_use_appropriate_language` - Diátaxis tutorials compliance
- ✅ `test_reference_docs_maintain_neutral_tone` - Diátaxis reference compliance
- ✅ `test_how_to_guides_are_task_focused` - Diátaxis how-to compliance
- ✅ `test_markdown_links_have_descriptive_text` - Link quality check
- ✅ `test_heading_hierarchy_no_skips` - Markdown heading structure

**Benefits**:
- Run in ~1 second (vs 20+ seconds for Playwright)
- No documentation build required
- No web server or browser needed
- Can run in CI before doc build
- Better error messages (points to source file + line)

#### Playwright Tests (Requires Built Docs)
**Directory**: `playwright/`

##### test_diataxis_structure.py
- `test_documentation_has_diataxis_structure` - Check rendered navigation
- `test_diataxis_section_exists` - Verify sections accessible

##### test_accessibility.py (16 tests)
- `test_page_has_proper_title`
- `test_heading_hierarchy`
- `test_heading_hierarchy_no_skips`
- `test_language_attribute`
- `test_images_have_alt_text`
- `test_links_have_descriptive_text`
- `test_page_has_main_landmark`
- `test_interactive_elements_keyboard_accessible`
- `test_skip_to_content_link`
- `test_page_load_performance`
- `test_code_blocks_render_properly`
- `test_code_copy_buttons_exist`
- `test_tables_have_proper_headers`
- `test_images_load_successfully`
- `test_form_inputs_have_labels`
- `test_external_links_open_securely`

##### test_documentation_quality.py (5 tests)
- `test_code_blocks_have_language_indicator`
- `test_version_information_present`
- `test_page_has_css_styling`
- `test_page_has_footer`
- `test_mobile_menu_toggle_exists`

##### test_navigation.py (8 tests)
- `test_page_loads_successfully`
- `test_navigation_structure_exists`
- `test_internal_anchor_links_valid`
- `test_page_has_footer`
- `test_sidebar_navigation_exists`
- `test_page_has_breadcrumbs`
- `test_mobile_menu_toggle_exists`
- `test_documentation_has_theme`

#### Python Unit Tests (Unchanged)
- `test_docs_hooks.py` - Tests docs build hooks
- `test_generate_diagrams.py` - Tests diagram generation

## Running Tests

### Run all tests
```bash
pytest tests/docs/
```

### Run only source tests (fast, no build needed)
```bash
pytest tests/docs/test_source_content.py
```

### Run only Playwright tests (requires built docs)
```bash
pytest tests/docs/playwright/ -m playwright
```

### Run specific test categories
```bash
# Accessibility only
pytest tests/docs/playwright/test_accessibility.py

# Navigation only
pytest tests/docs/playwright/test_navigation.py

# Diátaxis compliance
pytest tests/docs/test_source_content.py -k diataxis
pytest tests/docs/playwright/test_diataxis_structure.py
```

## CI/CD Integration

### Recommended Pipeline
```yaml
# Stage 1: Source validation (fast, no build)
- name: Validate documentation source
  run: pytest tests/docs/test_source_content.py

# Stage 2: Build documentation
- name: Build docs
  run: sphinx-build docs/source docs/build/html

# Stage 3: Playwright tests (requires build)
- name: Test rendered documentation
  run: pytest tests/docs/playwright/ -m built_docs
```

## Migration Benefits

### Performance Improvements
- **Before**: All tests required doc build + browser (~45 seconds total)
- **After**: Source tests run in ~1 second, catch issues early

### Developer Experience
- Faster feedback loop
- Clear separation of concerns
- Can fix source issues before committing
- Playwright tests only run when needed

### Maintenance
- Source tests less brittle (no HTML structure dependencies)
- Easier to debug (direct file references)
- No browser/Playwright version conflicts for source tests

## Test Coverage

### What Source Tests Cover
- Content quality (language, tone, structure)
- Diátaxis compliance (at source level)
- Markdown syntax issues
- Basic accessibility (alt text, headings)
- Code block formatting

### What Playwright Tests Cover
- Rendered output correctness
- Navigation functionality
- Theme integration
- Browser accessibility features
- Performance metrics
- Cross-references and links
- Search functionality

## Notes

- All Playwright test fixtures remain in parent `conftest.py`
- Fixtures are automatically available to subdirectories
- Tests can still share common utilities
- The `@pytest.mark.playwright` marker identifies browser-dependent tests
- The `@pytest.mark.built_docs` marker identifies tests requiring built documentation
