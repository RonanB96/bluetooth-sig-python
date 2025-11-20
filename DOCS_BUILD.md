# Documentation Build Guide

This guide explains how to build and serve the Bluetooth SIG Standards Library documentation locally. It covers system requirements, build commands, troubleshooting, and integration with CI/CD.

**Note**: This file is intentionally excluded from the generated documentation (for developers only).

## Table of Contents

- [Quick Start](#quick-start)
- [Requirements](#requirements)
  - [Python Dependencies](#python-dependencies)
  - [System Dependencies](#system-dependencies)
- [Build Commands](#build-commands)
  - [Development Server](#development-server)
  - [Production Build](#production-build)
- [Generated Outputs](#generated-outputs)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
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
mkdocs build

# Serve locally for development
mkdocs serve
```

The generated site will be available at `http://127.0.0.1:8000/bluetooth-sig-python/` when serving, or in the `site/` directory when built.

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
mkdocs serve
# Available at http://127.0.0.1:8000
```

Options:

- `mkdocs serve --dev-addr 0.0.0.0:8080` - Serve on different host/port
- `mkdocs serve --livereload` - Enable live reloading (default)
- `mkdocs serve --no-livereload` - Disable live reloading

### Production Build

Build static site for deployment:

```bash
mkdocs build
```

Options:

- `mkdocs build --clean` - Clean output directory before build
- `mkdocs build --strict` - Fail on warnings
- `mkdocs build --verbose` - Verbose output

### Other Useful Commands

```bash
# Validate configuration and content
mkdocs build --strict

# Clean generated files
rm -rf site/

# Check for broken links (if mkdocs-linkcheck plugin installed)
mkdocs build --strict --verbose
```

## Generated Outputs

### Site Structure

```text
site/
├── index.html              # Home page
├── quickstart/             # Tutorial pages
├── guides/                 # How-to guides
├── api/                    # API reference (auto-generated)
├── architecture/           # Architecture documentation
├── assets/                 # Static assets (CSS, JS, images)
├── coverage/               # Test coverage reports (if available)
└── diagrams/               # Generated UML and dependency diagrams
```

### Automatic Generation

The build process automatically generates:

1. **API Documentation** - Extracted from Python docstrings using mkdocstrings
2. **Supported Characteristics List** - Auto-generated from codebase via `scripts/generate_char_service_list.py`
3. **UML Diagrams** - Class and package diagrams via pyreverse → PlantUML → SVG
4. **Dependency Graphs** - Module dependency visualizations using pydeps + Graphviz
5. **Mermaid Diagrams** - Architecture diagrams rendered client-side via JavaScript
6. **Coverage Reports** - Test coverage integration (when available, CI only)

### Diagram Generation

The project includes automatic diagram generation via `scripts/generate_diagrams.py`:

**Generated diagram locations:**

- `docs/diagrams/puml/` - PlantUML source files (from pyreverse)
- `docs/diagrams/svg/` - Rendered SVG outputs (packages, classes)
- `docs/diagrams/deps/` - Dependency graph SVGs (from pydeps)
- `docs/diagrams/.cache/` - Cache to avoid regenerating unchanged diagrams

**Mermaid diagrams** in markdown files are rendered client-side and require no generation step.

## Configuration

### MkDocs Configuration

Primary configuration is in `mkdocs.yml`:

- Site metadata and URLs
- Theme configuration (Material Design)
- Plugin settings (search, mkdocstrings, etc.)
- Navigation structure
- Markdown extensions

### Documentation Hooks

Custom processing is handled by `docs_hooks.py` via the `on_pre_build` hook:

- **Characteristics List Generation** - Runs `scripts/generate_char_service_list.py` to create supported-characteristics.md
- **Diagram Generation** - Runs `scripts/generate_diagrams.py` with `STRICT_DIAGRAMS=1` to ensure diagrams are generated
- **Build Validation** - Fails the build if generation scripts fail (strict mode)

## Troubleshooting

### MkDocs Command Not Found

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
- Check that `src/` directory structure matches mkdocstrings configuration
- Verify Python path configuration in `mkdocs.yml`

### Diagrams Not Generating

- Check that PlantUML files use correct syntax
- Ensure system dependencies (Java, Graphviz) are installed
- Look for error messages in build output

## Development Tips

1. **Use development server** - `mkdocs serve` provides live reload for faster iteration
2. **Check build warnings** - Use `--strict` flag to catch issues early
3. **Validate links** - Regularly check for broken internal/external links
4. **Test locally** - Always build and test locally before pushing changes
5. **Clear cache** - Delete `site/` directory if encountering stale content issues

## Performance Optimization

For faster builds during development:

- Comment out heavy plugins in `mkdocs.yml` temporarily
- Disable diagram generation if not needed
- Use `mkdocs serve` instead of full builds for content changes

## Integration with CI/CD

The documentation build is automated in GitHub Actions (`.github/workflows/test-coverage.yml`):

1. **System Dependencies** - Installs graphviz, plantuml, openjdk-11-jre-headless
2. **Python Dependencies** - Installs `.[docs]` optional dependencies
3. **Coverage Integration** - Downloads and symlinks coverage reports to `docs/coverage`
4. **Benchmark Integration** - Downloads benchmark artifacts to link into docs
5. **Build** - Runs `mkdocs build` with automatic diagram generation
6. **Deploy** - Publishes to GitHub Pages (main branch only)

For local testing that matches CI:

```bash
# Simulate CI environment
pip install -e ".[docs]"
sudo apt-get install -y graphviz plantuml \
    openjdk-11-jre-headless
mkdocs build --strict --verbose
```

## File Exclusions

This documentation build guide (`DOCS_BUILD.md`) is intentionally excluded from the generated documentation. Files excluded from the docs include:

- `DOCS_BUILD.md` (this file)
- `site/` directory (build output)
- `docs/coverage/` (symlinked coverage reports, CI only)
- `docs/diagrams/.cache/` (diagram generation cache)
- Generated diagram SVG files in `docs/diagrams/svg/` and `docs/diagrams/deps/`
- Generated PUML files in `docs/diagrams/puml/`
- `docs/benchmarks/` (linked benchmark data, CI only)

See `.gitignore` and `mkdocs.yml` (`not_in_nav`) for complete exclusion rules.
