# Documentation Build Guide

This guide explains how to build and serve the Bluetooth SIG Standards Library documentation locally. It covers system requirements, build commands, troubleshooting, and integration with CI/CD.

**Note**: This file is intentionally excluded from the generated documentation (for developers only).

## Table of Contents

- [Documentation Build Guide](#documentation-build-guide)
  - [Table of Contents](#table-of-contents)
  - [Quick Start](#quick-start)
  - [Requirements](#requirements)
    - [Python Dependencies](#python-dependencies)
    - [System Dependencies](#system-dependencies)
      - [Ubuntu/Debian](#ubuntudebian)
      - [Alpine Linux](#alpine-linux)
      - [macOS (with Homebrew)](#macos-with-homebrew)
      - [Windows](#windows)
  - [Build Commands](#build-commands)
    - [Development Server](#development-server)
    - [Production Build](#production-build)
    - [Other Useful Commands](#other-useful-commands)
  - [Generated Outputs](#generated-outputs)
    - [Site Structure](#site-structure)
    - [Automatic Generation](#automatic-generation)
    - [Diagram Generation](#diagram-generation)
  - [Configuration](#configuration)
    - [Sphinx Configuration](#sphinx-configuration)
    - [Pre-Build Hooks](#pre-build-hooks)
    - [Post-Build Hooks](#post-build-hooks)
  - [Troubleshooting](#troubleshooting)
    - [Sphinx Command Not Found](#sphinx-command-not-found)
    - [PlantUML: Java Runtime Not Found](#plantuml-java-runtime-not-found)
    - [Graphviz: Dot Command Not Found](#graphviz-dot-command-not-found)
    - [API Documentation Missing](#api-documentation-missing)
    - [Diagrams Not Generating](#diagrams-not-generating)
    - [Build Warnings or Errors](#build-warnings-or-errors)
  - [Development Tips](#development-tips)
  - [Performance Optimization](#performance-optimization)
  - [Integration with CI/CD](#integration-with-cicd)
  - [File Exclusions](#file-exclusions)

## Quick Start

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y graphviz plantuml \
    openjdk-11-jre-headless

# Build the documentation
sphinx-build -b html docs/source docs/build/html

# Serve locally for development
python -m http.server -d docs/build/html 8000
```

The generated site will be available at `http://127.0.0.1:8000/` when serving, or in the `docs/build/html` directory when built.

**Note**: Mermaid diagrams are rendered client-side via JavaScript and require no additional system dependencies.

## Requirements


### Python Dependencies

The documentation build requires the `docs` optional dependency group defined in `pyproject.toml`

### System Dependencies

The documentation generation also requires system packages for UML and dependency graph generation:

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y graphviz plantuml openjdk-11-jre-headless
```

#### Alpine Linux

```bash
apk add graphviz openjdk11-jre wget
wget https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar \
    -O /tmp/plantuml.jar
echo '#!/bin/sh' > /usr/local/bin/plantuml
echo 'exec java -jar /tmp/plantuml.jar "$@"' >> \
    /usr/local/bin/plantuml
chmod +x /usr/local/bin/plantuml
```

#### macOS (with Homebrew)

```bash
brew install graphviz plantuml
brew install --cask temurin11  # OpenJDK 11
```

#### Windows

- Install [Graphviz](https://graphviz.org/download/) and add to PATH
- Install [PlantUML](https://plantuml.com/download)
- Install OpenJDK 11 or later

## Build Commands

### Development Server

Start a local development server with auto-reload:

```bash
# Build documentation
sphinx-build -b html docs/source docs/build/html

# Serve with Python's built-in HTTP server
python -m http.server -d docs/build/html 8000
# Available at http://127.0.0.1:8000
```

For live-reload during development, use `sphinx-autobuild`:

```bash
# Install sphinx-autobuild if not already installed
pip install sphinx-autobuild

# Start auto-reloading server
sphinx-autobuild docs/source docs/build/html
# Available at http://127.0.0.1:8000 with live reload
```

Options:

- `sphinx-build -j auto` - Use all CPU cores for parallel builds
- `sphinx-build -a` - Rebuild all files (not just changed ones)
- `sphinx-build -E` - Don't use cached environment, rebuild from scratch
- `sphinx-autobuild --port 8080` - Serve on different port

### Production Build

Build static site for deployment:

```bash
sphinx-build -b html docs/source docs/build/html
```

Options:

- `sphinx-build -b html -j auto` - Parallel build using all CPU cores
- `sphinx-build -b html -W` - Turn warnings into errors (strict mode)
- `sphinx-build -b html -a -E` - Full clean rebuild
- `sphinx-build -b html -q` - Quiet output (errors only)
- `sphinx-build -b html -v` - Verbose output

### Other Useful Commands

```bash
# Validate configuration and content (strict mode)
sphinx-build -b html -W docs/source docs/build/html

# Clean generated files
rm -rf docs/build/

# Check for broken links
sphinx-build -b linkcheck docs/source docs/build/linkcheck

# Generate only specific pages (faster for testing)
sphinx-build -b html docs/source docs/build/html index.md
```

## Generated Outputs

### Site Structure

```text
docs/build/html/
├── index.html              # Home page
├── tutorials/              # Tutorial pages
├── how-to/                 # How-to guides
├── reference/              # Reference documentation
├── explanation/            # Explanation articles
├── api/                    # API reference (auto-generated by AutoAPI)
├── performance/            # Performance documentation
├── community/              # Community documentation
├── _static/                # Static assets (CSS, JS, images)
├── coverage/               # Test coverage reports (if available, CI only)
└── diagrams/               # Generated UML and dependency diagrams
```

### Automatic Generation

The build process automatically generates:

1. **API Documentation** - Extracted from Python docstrings using Sphinx AutoAPI
2. **Supported Characteristics List** - Auto-generated from codebase via `scripts/generate_char_service_list.py`
3. **UML Diagrams** - Class and package diagrams via pyreverse → PlantUML → SVG
4. **Dependency Graphs** - Module dependency visualizations using pydeps + Graphviz
5. **Mermaid Diagrams** - Architecture diagrams rendered client-side via JavaScript
6. **Coverage Reports** - Test coverage integration (when available, CI only)

### Diagram Generation

The project includes automatic diagram generation via `scripts/generate_diagrams.py`:

**Generated diagram locations:**

- `docs/source/diagrams/puml/` - PlantUML source files (from pyreverse)
- `docs/source/diagrams/svg/` - Rendered SVG outputs (packages, classes)
- `docs/source/diagrams/deps/` - Dependency graph SVGs (from pydeps)
- `docs/source/diagrams/.cache/` - Cache to avoid regenerating unchanged diagrams

**Mermaid diagrams** in markdown files are rendered client-side and require no generation step.

## Configuration

### Sphinx Configuration

Primary configuration is in `docs/source/conf.py`:

- Project metadata and URLs
- Theme configuration (Furo with Bluetooth branding)
- Extension settings (AutoAPI, MyST Parser, Mermaid, etc.)
- Build hooks (pre-build script execution)
- HTML output options

### Pre-Build Hooks

Custom processing is handled by the `run_pre_build_scripts()` function in `conf.py` via the `config-inited` event:

- **Characteristics List Generation** - Runs `scripts/generate_char_service_list.py` to create supported characteristics documentation
- **Diagram Generation** - Runs `scripts/generate_diagrams.py` with `STRICT_DIAGRAMS=1` to ensure diagrams are generated
- **Build Validation** - Exits with error code if generation scripts fail (strict mode)

### Post-Build Hooks

Post-processing is handled via the `build-finished` event:

- **Table Header Fixes** - Adds `<thead>` elements to tables for accessibility compliance
- **AutoAPI Anchor Fixes** - Removes incorrect `src.` prefix from API reference anchor links

## Troubleshooting

### Sphinx Command Not Found

```bash
pip install -e ".[docs]"
```

### PlantUML: Java Runtime Not Found

```bash
# Ubuntu/Debian
sudo apt-get install openjdk-11-jre-headless

# macOS
brew install --cask temurin11

# Verify installation
java -version
```

### Graphviz: Dot Command Not Found

```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Verify installation
dot -V
```

### API Documentation Missing

- Ensure source code has proper Google-style docstrings
- Check that `src/` directory structure matches AutoAPI configuration
- Verify `autoapi_dirs` configuration in `docs/source/conf.py`
- Check for errors in build output

### Diagrams Not Generating

- Check that PlantUML files use correct syntax
- Ensure system dependencies (Java, Graphviz) are installed
- Look for error messages in build output
- Verify `scripts/generate_diagrams.py` runs without errors

### Build Warnings or Errors

- Use `sphinx-build -W` to treat warnings as errors (strict mode)
- Check for missing references or broken links
- Verify all autodoc targets exist
- Review `docs/source/conf.py` for configuration issues

## Development Tips

1. **Use development server** - `sphinx-autobuild` provides live reload for faster iteration
2. **Check build warnings** - Use `-W` flag to catch issues early
3. **Validate links** - Regularly check for broken internal/external links using `sphinx-build -b linkcheck`
4. **Test locally** - Always build and test locally before pushing changes
5. **Clear cache** - Delete `docs/build/` directory if encountering stale content issues
6. **Incremental builds** - Sphinx caches build environment for faster rebuilds

## Performance Optimization

For faster builds during development:

- Use parallel builds: `sphinx-build -j auto`
- Keep AutoAPI files: `autoapi_keep_files = True` (already enabled)
- Disable viewcode: `sphinx.ext.viewcode` is already disabled for performance
- Use incremental builds: Only changed files are rebuilt by default
- Skip diagram generation: Comment out diagram generation in `conf.py` temporarily

## Integration with CI/CD

The documentation build is automated in GitHub Actions (`.github/workflows/test-coverage.yml`):

1. **System Dependencies** - Installs graphviz, plantuml, openjdk-11-jre-headless
2. **Python Dependencies** - Installs `.[docs]` optional dependencies
3. **Coverage Integration** - Downloads and symlinks coverage reports to `docs/source/coverage`
4. **Benchmark Integration** - Downloads benchmark artifacts to link into docs
5. **Build** - Runs `sphinx-build -b html docs/source docs/build/html` with automatic diagram generation
6. **Deploy** - Publishes to GitHub Pages (main branch only)

For local testing that matches CI:

```bash
# Simulate CI environment
pip install -e ".[docs]"
sudo apt-get install -y graphviz plantuml \
    openjdk-11-jre-headless
sphinx-build -b html -W docs/source docs/build/html
```

## File Exclusions

This documentation build guide (`DOCS_BUILD.md`) is intentionally excluded from the generated documentation. Files excluded from the docs include:

- `DOCS_BUILD.md` (this file)
- `docs/build/` directory (build output)
- `docs/source/coverage/` (symlinked coverage reports, CI only)
- `docs/source/diagrams/.cache/` (diagram generation cache)
- Generated diagram SVG files in `docs/source/diagrams/svg/` and `docs/source/diagrams/deps/`
- Generated PUML files in `docs/source/diagrams/puml/`
- `docs/source/benchmarks/` (linked benchmark data, CI only)

See `.gitignore` and `docs/source/conf.py` (`exclude_patterns`) for complete exclusion rules.
