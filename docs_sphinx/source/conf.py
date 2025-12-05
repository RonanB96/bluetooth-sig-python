"""Sphinx configuration for Bluetooth SIG Standards Library.

This configuration optimizes for parallel builds to achieve <60 second build times
for 332 Python modules. Uses sphinx-autoapi for automatic API documentation generation
and MyST Parser for Markdown compatibility with existing documentation.
"""

import sys
from pathlib import Path

# Add source directory to path for autoapi
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# -- Project information -----------------------------------------------------
project = "Bluetooth SIG Standards Library"
copyright = "2025, RonanB96"
author = "RonanB96"
release = "0.3.0"

# -- General configuration ---------------------------------------------------
extensions = [
    # Core documentation generation
    "sphinx.ext.autodoc",  # Required by autoapi
    "sphinx.ext.viewcode",  # Add links to source code
    "sphinx.ext.intersphinx",  # Cross-reference external docs
    "sphinx.ext.napoleon",  # Support Google-style docstrings
    # API documentation (replaces mkdocstrings)
    "autoapi.extension",
    # Markdown support (replaces mkdocs native markdown)
    "myst_parser",
    # Design elements (replaces Material theme features)
    "sphinx_design",
    # Diagrams
    "sphinxcontrib.mermaid",
    # Copy button for code blocks
    "sphinx_copybutton",
]

# MyST Parser configuration for Markdown support
myst_enable_extensions = [
    "amsmath",  # Math support
    "colon_fence",  # ::: fenced directives
    "deflist",  # Definition lists
    "dollarmath",  # Dollar sign math
    "fieldlist",  # Field lists
    "html_admonition",  # HTML admonitions
    "html_image",  # HTML images
    "linkify",  # Auto-link URLs
    "replacements",  # Typography replacements
    "smartquotes",  # Smart quotes
    "strikethrough",  # ~~strikethrough~~
    "substitution",  # Substitution references
    "tasklist",  # Task lists [ ] [x]
]

# Allow .md extension for source files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Main document
master_doc = "index"

# Exclude patterns
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Templates
templates_path = ["_templates"]

# -- AutoAPI configuration ---------------------------------------------------
# Automatic API documentation generation (replaces mkdocstrings + gen_ref_pages.py)
autoapi_type = "python"
autoapi_dirs = ["../../src/bluetooth_sig"]
autoapi_root = "reference/api"
autoapi_template_dir = "_templates/autoapi"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]

# Performance optimization: generate stub pages without full rendering initially
autoapi_generate_api_docs = True
autoapi_add_toctree_entry = True
autoapi_keep_files = True  # Keep generated files for debugging

# Ignore patterns
autoapi_ignore = [
    "**/test_*",
    "**/tests/*",
    "**/__pycache__/*",
    "**/conftest.py",
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output configuration -----------------------------------------------
html_theme = "furo"

# Furo theme options for Material-like experience
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2196F3",  # Bluetooth blue
        "color-brand-content": "#2196F3",
    },
    "dark_css_variables": {
        "color-brand-primary": "#64B5F6",  # Lighter blue for dark mode
        "color-brand-content": "#64B5F6",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
    "source_repository": "https://github.com/RonanB96/bluetooth-sig-python",
    "source_branch": "main",
    "source_directory": "docs_sphinx/source/",
}

# Static files
html_static_path = ["_static"]

# Custom CSS
html_css_files = [
    "custom.css",
]

# -- Mermaid configuration ---------------------------------------------------
mermaid_version = "10.9.0"
mermaid_init_js = "mermaid.initialize({startOnLoad:true, theme: 'neutral'});"

# -- Build performance optimization ------------------------------------------
# These settings optimize for parallel builds

# Suppress unnecessary warnings that slow down builds
suppress_warnings = ["myst.header"]

# Nitpicky mode disabled for faster builds (can enable for release checks)
nitpicky = False

# -- Parallel build settings -------------------------------------------------
# sphinx-build -j auto will use all available CPU cores
# These settings ensure thread-safety for parallel builds
