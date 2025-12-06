# Playwright to Source File Testing Migration Analysis

## Executive Summary

After reviewing all Playwright tests in `tests/docs/`, many tests can be migrated from testing built HTML to testing source Markdown/RST files directly. This would:
1. **Speed up tests** - No need to build docs or start web server
2. **Run earlier** - Can validate in CI before doc build
3. **Provide better error messages** - Point to actual source files
4. **Reduce complexity** - No Playwright/browser overhead

## Current Test Files

### 1. test_diataxis_compliance.py (PARTIAL MIGRATION)
**Current**: 4 Playwright tests + 2 file-reading tests
**Can migrate to source**:
- ✅ `test_tutorials_use_appropriate_language` - Reads HTML files, can read `.md` instead
- ⚠️ `test_reference_docs_are_neutral` - Currently tests `api/` (auto-generated), should also test `reference/` (hand-written .md)
- ✅ `test_how_to_guides_are_task_focused` - Extracts titles from HTML, can parse markdown headers

**Must stay Playwright**:
- `test_documentation_has_diataxis_structure` - Checks rendered navigation
- `test_diataxis_section_exists` - Checks page accessibility and rendering

**Note**: Project has both `api/` (sphinx-autoapi generated) and `reference/` (hand-written markdown). Only hand-written reference docs can be tested at source level.

### 2. test_accessibility.py (MOSTLY STAY PLAYWRIGHT)
**Current**: 16 Playwright tests
**Can migrate to source**:
- ✅ `test_images_have_alt_text` - Parse markdown image syntax `![alt](src)`
- ⚠️ `test_links_have_descriptive_text` - Parse markdown links, but limited (no "click here" detection in rendered HTML)
- ⚠️ `test_heading_hierarchy` - Can parse markdown headers

**Must stay Playwright** (these test rendered HTML/accessibility):
- `test_page_has_proper_title` - HTML `<title>` tag
- `test_heading_hierarchy_no_skips` - Needs full document structure
- `test_language_attribute` - HTML `<html lang="">`
- `test_page_has_main_landmark` - Rendered HTML structure
- `test_interactive_elements_keyboard_accessible` - Browser interaction
- `test_skip_to_content_link` - Rendered navigation
- `test_page_load_performance` - Browser performance
- `test_code_blocks_render_properly` - Rendering check
- `test_code_copy_buttons_exist` - Theme feature
- `test_tables_have_proper_headers` - Rendered table HTML
- `test_images_load_successfully` - HTTP requests
- `test_form_inputs_have_labels` - Rendered forms
- `test_external_links_open_securely` - Rendered HTML attributes

### 3. test_documentation_quality.py (MIXED)
**Current**: 5 Playwright tests
**Can migrate to source**:
- ✅ `test_code_blocks_have_language_indicator` - Parse markdown code fences
- ⚠️ `test_version_information_present` - Could check source, but version in conf.py

**Must stay Playwright**:
- `test_page_has_css_styling` - Rendering/theme
- `test_page_has_footer` - Rendering/theme
- `test_mobile_menu_toggle_exists` - Rendering/theme

### 4. test_navigation.py (ALL STAY PLAYWRIGHT)
**Current**: 8 Playwright tests
**Must stay Playwright** (all test rendered HTML/navigation):
- `test_page_loads_successfully` - HTTP status
- `test_navigation_structure_exists` - Rendered nav
- `test_internal_anchor_links_valid` - Link resolution
- `test_page_has_footer` - Rendered HTML
- `test_sidebar_navigation_exists` - Rendered nav
- `test_page_has_breadcrumbs` - Rendered nav
- `test_mobile_menu_toggle_exists` - Rendered nav
- `test_documentation_has_theme` - Rendering

### 5. test_docs_hooks.py (KEEP AS-IS)
**Current**: 2 unit tests (no Playwright)
**Status**: Already tests Python code, no migration needed

### 6. test_generate_diagrams.py (KEEP AS-IS)
**Current**: Tests diagram generation
**Status**: Tests Python code, no migration needed

## Recommended New Test File Structure

### Create: test_source_content.py
Tests that run on source markdown/RST files BEFORE building:

```python
"""Test documentation source files (markdown/RST) for quality and compliance.

These tests run directly on source files and don't require built documentation.
They can catch issues early in CI before the expensive doc build process.
"""
from pathlib import Path
import re
import pytest

DOCS_SOURCE_DIR = Path(__file__).parent.parent.parent / "docs" / "source"

@pytest.fixture
def source_files() -> list[Path]:
    """Get all markdown source files."""
    return list(DOCS_SOURCE_DIR.rglob("*.md"))

def test_markdown_images_have_alt_text(source_files: list[Path]) -> None:
    """Test that markdown images have alt text."""
    issues = []
    image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')

    for file in source_files:
        content = file.read_text(encoding="utf-8")
        for match in image_pattern.finditer(content):
            alt_text = match.group(1)
            if not alt_text or alt_text.strip() == "":
                issues.append(f"{file.name}: Empty alt text for image {match.group(2)}")

    assert not issues, f"Images without alt text:\n" + "\n".join(issues[:10])

def test_code_blocks_have_language(source_files: list[Path]) -> None:
    """Test that code blocks specify a language."""
    issues = []
    # Match ```\n or ``` \n (no language specified)
    bad_fence = re.compile(r'^```\s*$', re.MULTILINE)

    for file in source_files:
        content = file.read_text(encoding="utf-8")
        matches = bad_fence.findall(content)
        if matches:
            issues.append(f"{file.name}: {len(matches)} code blocks without language")

    assert not issues, f"Code blocks without language:\n" + "\n".join(issues[:10])

def test_tutorials_avoid_presumptuous_language() -> None:
    """Test that tutorial content avoids presumptuous phrases."""
    tutorials_dir = DOCS_SOURCE_DIR / "tutorials"
    if not tutorials_dir.exists():
        pytest.skip("Tutorials directory not found")

    forbidden = ["you will learn", "let me explain", "you should understand"]
    issues = []

    for file in tutorials_dir.rglob("*.md"):
        content = file.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase in content:
                issues.append(f"{file.name}: Contains '{phrase}'")

    assert not issues, f"Tutorial language issues:\n" + "\n".join(issues[:10])

def test_reference_docs_avoid_subjective_language() -> None:
    """Test that reference docs maintain neutral tone."""
    reference_dir = DOCS_SOURCE_DIR / "reference"
    if not reference_dir.exists():
        pytest.skip("Reference directory not found")

    subjective = ["i think", "you should", "in my opinion"]
    issues = []

    for file in reference_dir.rglob("*.md"):
        content = file.read_text(encoding="utf-8").lower()
        # Exclude code blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        for phrase in subjective:
            if phrase in content:
                issues.append(f"{file.name}: Contains '{phrase}'")

    assert not issues, f"Reference docs should be objective:\n" + "\n".join(issues[:10])

def test_markdown_links_not_just_urls() -> None:
    """Test that markdown links have descriptive text, not bare URLs."""
    issues = []
    # Match [http://example.com](http://example.com) or [url](url)

    for file in source_files:
        content = file.read_text(encoding="utf-8")
        # Find links where text is URL or variations
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for match in link_pattern.finditer(content):
            text = match.group(1).strip()
            url = match.group(2).strip()

            # Check if link text is just the URL or "click here" type
            if text.lower() in ["click here", "here", "link"] or text == url:
                issues.append(f"{file.name}: Non-descriptive link text '{text}'")

    assert not issues, f"Links need descriptive text:\n" + "\n".join(issues[:10])

def test_heading_hierarchy_in_source() -> None:
    """Test markdown headings don't skip levels."""
    issues = []

    for file in source_files:
        content = file.read_text(encoding="utf-8")
        headings = re.findall(r'^(#{1,6})\s+', content, re.MULTILINE)

        for i in range(len(headings) - 1):
            current_level = len(headings[i])
            next_level = len(headings[i + 1])

            # Check if we skip levels (e.g., ## -> ####)
            if next_level > current_level + 1:
                issues.append(
                    f"{file.name}: Heading skip from h{current_level} to h{next_level}"
                )
                break  # One issue per file is enough

    assert not issues, f"Heading hierarchy issues:\n" + "\n".join(issues[:10])
```

## Migration Priority

### High Priority (Easy wins, high value)
1. ✅ **Code fence language detection** - Simple regex on source
2. ✅ **Image alt text** - Simple regex on source
3. ✅ **Diataxis language compliance** - Already reading files, just change path
4. ✅ **Heading hierarchy** - Can parse from markdown

### Medium Priority (Moderate effort)
1. ⚠️ **Link descriptiveness** - Partial coverage (can't catch all cases)
2. ⚠️ **Subjective language in reference** - Good for catching obvious issues

### Low Priority / Keep Playwright
- All navigation/rendering tests
- Accessibility tests requiring browser
- Performance tests
- Theme/styling tests

## Implementation Steps

1. **Create fixture for source files**
   ```python
   @pytest.fixture
   def docs_source_dir() -> Path:
       return Path(__file__).parent.parent.parent / "docs" / "source"
   ```

2. **Create test_source_content.py** with migrations

3. **Update test_diataxis_compliance.py**
   - Fix `api/` → `reference/` bug
   - Consider keeping HTML tests for structure validation
   - Add complementary source file tests

4. **Update CI/CD**
   - Run source tests before doc build
   - Keep Playwright tests in "built_docs" stage

## Benefits of Migration

### Performance
- Source tests: ~0.1s per test
- Playwright tests: ~1-3s per test
- No doc build required for source tests

### Developer Experience
- Faster feedback on PRs
- Better error messages (points to source file + line)
- Can fix issues before committing

### Maintenance
- Less brittle (no HTML structure dependencies)
- No browser/Playwright version issues
- Simpler test code

## Risks & Limitations

### What Source Tests Can't Check
1. **Rendering issues** - How content actually displays
2. **Theme integration** - Navigation, search, etc.
3. **Link resolution** - Cross-references, API links
4. **Sphinx directives** - Special RST/MyST features
5. **Browser behavior** - Accessibility, performance

### Recommendation
- Keep both types of tests
- Use source tests for content quality
- Use Playwright for integration/rendering

## Conclusion

**Migrate ~30% of current Playwright tests to source file tests**, specifically:
- Diataxis language compliance
- Code block language indicators
- Image alt text
- Basic link quality
- Heading hierarchy

This provides early feedback while keeping comprehensive end-to-end testing with Playwright.
