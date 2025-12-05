# Migrate Documentation from MkDocs to Sphinx with Parallel Builds

## Objective

Migrate the project's documentation system from MkDocs to Sphinx to achieve **build times under 1 minute** for 331 Python modules through parallel processing. The current MkDocs setup is single-threaded and cannot meet performance requirements.

## Context

- **Current Setup**: MkDocs 1.6.0 + Material theme + mkdocstrings
- **Python Modules**: 331 files in `src/bluetooth_sig/`
- **Markdown Files**: 29 documentation pages organized using Diátaxis framework
- **Performance Goal**: <1 minute build time (estimated 4-8x improvement with parallel builds)
- **Detailed Plan**: See `SPHINX_MIGRATION_PLAN.md` in repository root

## Research Requirements

### 1. Sphinx Ecosystem Research (MANDATORY)

Before implementation, you MUST research and verify:

- [ ] **Latest Sphinx versions and compatibility**: Check sphinx.org for current stable releases
- [ ] **sphinx-autoapi best practices**: Review <https://sphinx-autoapi.readthedocs.io/> for optimal configuration with 300+ modules
- [ ] **MyST Parser syntax**: Study <https://myst-parser.readthedocs.io/> for Markdown compatibility
- [ ] **Sphinx Design patterns**: Review <https://sphinx-design.readthedocs.io/> for Material-like grid cards
- [ ] **Furo theme customization**: Check <https://pradyunsg.me/furo/> for dark/light mode configuration
- [ ] **PyData Sphinx theme**: Review <https://pydata-sphinx-theme.readthedocs.io/> as alternative modern theme
- [ ] **Parallel build optimization**: Research `-j` flag best practices and pitfalls
- [ ] **sphinxcontrib-mermaid**: Verify Mermaid diagram compatibility

Search DuckDuckGo for:

- "sphinx autoapi parallel builds optimization 2024"
- "sphinx vs mkdocs migration checklist"
- "myst parser advanced features"
- "sphinx build performance tuning"

### 2. Compare Against Reference Implementations

Study these Sphinx-based projects for patterns:

- NumPy docs: <https://numpy.org/doc/>
- Pandas docs: <https://pandas.pydata.org/docs/>
- Django docs: <https://docs.djangoproject.com/>

## Implementation Requirements

### Phase 1: Setup Sphinx Scaffold

1. Install all required dependencies (verify latest compatible versions)
2. Create `docs_sphinx/` directory structure
3. Configure `conf.py` with:
   - AutoAPI for automatic API documentation
   - MyST Parser for Markdown support
   - Sphinx Design for grid cards
   - Modern theme with dark/light mode support (Furo or PyData theme)
   - Parallel build optimization settings

### Phase 2: Content Migration

1. Copy all Markdown files from `docs/` to `docs_sphinx/source/`
2. Convert Material theme grid cards to Sphinx Design syntax
3. Update internal links (remove `.md` extensions for Sphinx)
4. Create main `index.md` with proper toctree structures
5. Preserve Diátaxis framework organization (tutorials/how-to/reference/explanation)

### Phase 3: API Documentation

1. Configure AutoAPI to discover all 331 modules in `src/bluetooth_sig/`
2. Set up proper ignore patterns for `__pycache__` and test files
3. Verify Google-style docstrings render correctly
4. Test cross-references between API docs and guides
5. Archive old `scripts/gen_ref_pages.py` (no longer needed)

### Phase 4: Build & Benchmark

1. Run parallel build: `sphinx-build -j auto source build`
2. Measure and document build time (MUST be <60 seconds)
3. Test incremental builds
4. Verify local server rendering: `python -m http.server --directory build 8000`
5. Check all navigation, search, and cross-references

### Phase 5: CI/CD Integration

1. Update `.github/workflows/docs.yml` for Sphinx
2. Add `docs` extra to `pyproject.toml` with all Sphinx dependencies
3. Test CI build passes with parallel processing
4. Verify GitHub Pages deployment works

## Quality Standards (Zero Tolerance)

### Build Requirements

- ✅ Build completes in <60 seconds (full clean build)
- ✅ Zero warnings with `sphinx-build -W` flag
- ✅ Zero errors in any phase
- ✅ All 331 modules documented
- ✅ All 29 markdown pages migrated

### Code Quality

- ✅ Follow Python best practices for `conf.py`
- ✅ Use type hints where applicable
- ✅ Add explanatory comments for complex configurations
- ✅ Clean, maintainable code structure

### Feature Parity

- ✅ All Markdown content preserved
- ✅ Mermaid diagrams render correctly
- ✅ Code syntax highlighting works
- ✅ Search functionality operational
- ✅ Cross-references intact
- ✅ Grid cards converted to Sphinx Design
- ✅ Dark theme available
- ✅ Breadcrumb navigation present

### Testing

- ✅ Local build succeeds
- ✅ Local server renders correctly
- ✅ All internal links work
- ✅ Search returns relevant results
- ✅ Mobile responsive design
- ✅ CI/CD pipeline passes

## Deliverables

1. **Working Sphinx Documentation System**
   - `docs_sphinx/` directory with complete configuration
   - `docs_sphinx/source/conf.py` with all optimizations
   - All migrated Markdown content

2. **Updated CI/CD**
   - `.github/workflows/docs.yml` for Sphinx builds
   - `pyproject.toml` with `docs` dependency group

3. **Documentation**
   - Update `README.md` with new build commands
   - Update `CONTRIBUTING.md` with Sphinx workflow
   - Keep `SPHINX_MIGRATION_PLAN.md` as reference

4. **Performance Metrics**
   - Benchmark results showing <60s build time
   - Comparison with previous MkDocs build time

## Constraints

### DO NOT

- ❌ Delete existing MkDocs setup until Sphinx is proven working
- ❌ Suppress warnings/errors without fixing root cause
- ❌ Use outdated package versions
- ❌ Skip testing any phase
- ❌ Hardcode absolute paths
- ❌ Commit build artifacts to repository

### DO

- ✅ Research extensively before implementing
- ✅ Follow official documentation for all tools
- ✅ Test incrementally after each phase
- ✅ Document any deviations from plan with justification
- ✅ Use parallel builds (`-j auto`)
- ✅ Verify on clean environment

## Success Criteria

The migration is complete when ALL of these are true:

- [ ] Full Sphinx build completes in <60 seconds
- [ ] `sphinx-build -W --keep-going source build` passes with zero warnings/errors
- [ ] All 331 Python modules have API documentation
- [ ] All 29 markdown pages render correctly
- [ ] Local server displays documentation properly
- [ ] All navigation links work
- [ ] Search functionality works
- [ ] Mermaid diagrams render
- [ ] Code blocks have copy buttons
- [ ] Dark theme toggles correctly
- [ ] CI/CD pipeline passes
- [ ] GitHub Pages deployment succeeds
- [ ] Documentation matches Material theme aesthetic

## Additional Context

### Current MkDocs Configuration

See `mkdocs.yml` for current setup details.

### Generated API Docs

Currently generated by `scripts/gen_ref_pages.py` (170 lines) - this will be replaced by AutoAPI.

### Content Organization

Follows Diátaxis framework:

- `tutorials/` - Learning-oriented
- `how-to/` - Task-oriented
- `reference/` - Information-oriented
- `explanation/` - Understanding-oriented

### Key Files to Reference

- `SPHINX_MIGRATION_PLAN.md` - Comprehensive migration plan
- `mkdocs.yml` - Current MkDocs configuration
- `scripts/gen_ref_pages.py` - Current API doc generation
- `docs/` - All current documentation content

## Timeline

Expected completion: 4-6 hours of focused work

## Questions?

Review `SPHINX_MIGRATION_PLAN.md` for detailed technical specifications, dependency versions, and step-by-step instructions.
