"""Sphinx configuration for Bluetooth SIG Standards Library.

Optimised for fast parallel builds using sphinx-autoapi
for automatic API generation and MyST Parser for Markdown support.

Based on:
- https://www.sphinx-doc.org/en/master/usage/configuration.html
- https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html
- https://myst-parser.readthedocs.io/en/latest/configuration.html
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from sphinx.application import Sphinx

# Add source directory to path for imports (not for AutoAPI scanning)
# AutoAPI scans from autoapi_dirs, this is just for import resolution
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Bluetooth SIG Standards Library"
copyright = "2025, RonanB96"
author = "RonanB96"

# Get version from git describe (single source of truth)
_version_result = subprocess.run(
    ["git", "describe", "--tags"],
    capture_output=True,
    text=True,
    check=True,
    cwd=Path(__file__).parent.parent.parent,
)
release = _version_result.stdout.strip().lstrip("v")
version = release
build_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Core documentation generation
    "sphinx.ext.autodoc",  # Required by autoapi
    # "sphinx.ext.viewcode",  # DISABLED: Generates _modules/ source pages (slow)
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
# https://myst-parser.readthedocs.io/en/latest/configuration.html
# Only enable extensions that are actually used in documentation
myst_enable_extensions = [
    "colon_fence",  # ::: fenced directives (CRITICAL: used extensively)
    "html_admonition",  # HTML admonitions (tip/note blocks)
    "linkify",  # Auto-link URLs (useful for maintenance)
]

# Enable mermaid code blocks to be rendered as mermaid directives
myst_fence_as_directive = ["mermaid"]

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
# https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html
# Automatic API documentation generation (replaces mkdocstrings + gen_ref_pages.py)

autoapi_type = "python"
autoapi_dirs = ["../../src"]  # Scans from src to get correct module names
autoapi_root = "api"  # Puts generated docs in docs/source/api/

# Ignore patterns for AutoAPI scanning
autoapi_ignore = [
    "**/test_*",
    "**/tests/*",
    "**/__pycache__/*",
    "**/conftest.py",
]

# AutoAPI rendering options
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]

# Keep generated files for incremental builds (critical for performance)
autoapi_keep_files = True
autoapi_generate_api_docs = True
autoapi_add_toctree_entry = False  # Manual toctree control

# Python-specific AutoAPI settings
autoapi_python_class_content = "both"  # Include both class and __init__ docstrings
autoapi_member_order = "groupwise"  # Group by type (classes, functions, etc.)


# Override AutoAPI's module name extraction to remove 'src' prefix
def autoapi_skip_member(
    app: Sphinx,
    what: str,
    name: str,
    obj: object,
    skip: bool,
    options: dict[str, object],
) -> bool:
    """Skip certain members during API documentation generation.

    Args:
        app: Sphinx application object
        what: Type of the object (e.g., 'function', 'class')
        name: Fully qualified name of the object
        obj: The object itself
        skip: Whether AutoAPI will skip this member
        options: Options given to the directive

    Returns:
        True to skip the member, False to include it
    """
    # Skip test files and private members
    if "test_" in name or name.startswith("_"):
        return True
    return skip


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
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- HTML output configuration -----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

# GitHub integration context
html_context = {
    "display_github": True,
    "github_user": "RonanB96",
    "github_repo": "bluetooth-sig-python",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
}

# Furo theme options for branding and navigation
# https://pradyunsg.me/furo/customisation/
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
    "source_directory": "docs/source/",
}
# Configure sidebars for consistent navigation
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_sidebars
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ],
    # Minimal sidebars for special pages
    "genindex": ["sidebar/brand.html", "sidebar/search.html", "sidebar/navigation.html"],
    "py-modindex": ["sidebar/brand.html", "sidebar/search.html", "sidebar/navigation.html"],
    "search": ["sidebar/brand.html", "sidebar/navigation.html"],
}
# Static files directory
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_static_path
html_static_path = ["_static"]

# Custom CSS files to include
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_css_files
html_css_files = [
    "custom.css",
]

# -- Mermaid configuration ---------------------------------------------------
# https://sphinxcontrib-mermaid-demo.readthedocs.io/en/latest/

mermaid_version = "10.9.0"
mermaid_init_js = "mermaid.initialize({startOnLoad:true, theme: 'neutral'});"

# -- Build performance optimisation ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-parallel_read_safe

# Parallel build configuration (use with sphinx-build -j auto)
parallel_read_safe = True
parallel_write_safe = True

# Nitpicky mode disabled for faster builds (enable for release checks)
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-nitpicky
nitpicky = False


def fix_table_headers(
    app: Sphinx,
    exception: Exception | None,
) -> None:
    """Post-process HTML files to add proper table headers for accessibility.

    Fixes AutoAPI-generated tables that lack <thead> elements.

    Args:
        app: Sphinx application object
        exception: Build exception if any occurred
    """
    if exception is not None or app.builder.format != "html":
        return

    build_dir = Path(app.outdir)

    # Pattern 1: autosummary tables without thead (API docs)
    autosummary_pattern = re.compile(
        r'(<table[^>]*class="[^"]*autosummary[^"]*"[^>]*>)\s*(<tbody>)', re.IGNORECASE | re.DOTALL
    )

    # Pattern 2: domainindex-table without proper headers (py-modindex.html)
    domainindex_pattern = re.compile(r'(<table[^>]*class="domainindex-table"[^>]*>)\s*(<tr)', re.IGNORECASE | re.DOTALL)

    # Pattern 3: genindextable without proper headers (genindex.html)
    genindex_pattern = re.compile(
        r'(<table[^>]*class="[^"]*genindextable[^"]*"[^>]*>)\s*(<tr)', re.IGNORECASE | re.DOTALL
    )

    def add_autosummary_thead(match: re.Match[str]) -> str:
        """Add thead for autosummary tables.

        Args:
            match: Regular expression match object

        Returns:
            Replacement string with thead element
        """
        table_tag = match.group(1)
        tbody_tag = match.group(2)
        thead = (
            '\n<thead>\n<tr><th class="head"><p>Name</p></th><th class="head"><p>Description</p></th></tr>\n</thead>\n'
        )
        return f"{table_tag}{thead}{tbody_tag}"

    def add_domainindex_thead(match: re.Match[str]) -> str:
        """Add thead for domainindex tables.

        Args:
            match: Regular expression match object

        Returns:
            Replacement string with thead element
        """
        table_tag = match.group(1)
        tr_tag = match.group(2)
        thead = (
            "\n<thead>\n"
            '<tr><th class="head"><p>Navigation</p></th>'
            '<th class="head"><p>Module</p></th>'
            '<th class="head"><p>Description</p></th></tr>\n'
            "</thead>\n<tbody>\n"
        )
        return f"{table_tag}{thead}{tr_tag}"

    def add_genindex_thead(match: re.Match[str]) -> str:
        """Add thead for genindex tables.

        Args:
            match: Regular expression match object

        Returns:
            Replacement string with thead element
        """
        table_tag = match.group(1)
        tr_tag = match.group(2)
        # These are multi-column index tables, use a simple generic header
        thead = '\n<thead>\n<tr><th class="head"><p>Index Entries</p></th></tr>\n</thead>\n<tbody>\n'
        return f"{table_tag}{thead}{tr_tag}"

    # Process all HTML files
    html_files = list(build_dir.rglob("*.html"))
    fixed_counts = {"autosummary": 0, "domainindex": 0, "genindex": 0}

    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8")
            modified = False

            # Fix autosummary tables
            new_content, count = autosummary_pattern.subn(add_autosummary_thead, content)
            if count > 0:
                content = new_content
                fixed_counts["autosummary"] += count
                modified = True

            # Fix domainindex tables (py-modindex.html)
            if "py-modindex" in html_file.name or "domainindex" in html_file.name:
                new_content, count = domainindex_pattern.subn(add_domainindex_thead, content)
                if count > 0:
                    content = new_content
                    fixed_counts["domainindex"] += count
                    modified = True
                    # Add closing tbody tag before </table>
                    content = content.replace("</table>", "</tbody>\n</table>")

            # Fix genindex tables (genindex.html)
            if "genindex" in html_file.name:
                new_content, count = genindex_pattern.subn(add_genindex_thead, content)
                if count > 0:
                    content = new_content
                    fixed_counts["genindex"] += count
                    modified = True
                    # Add closing tbody tag before </table>
                    content = content.replace("</table>", "</tbody>\n</table>")

            if modified:
                html_file.write_text(content, encoding="utf-8")

        except Exception as e:
            print(f"Warning: Could not process {html_file}: {e}")

    total = sum(fixed_counts.values())
    if total > 0:
        print(f"✓ Fixed {total} tables with proper headers:")
        for table_type, count in fixed_counts.items():
            if count > 0:
                print(f"  - {table_type}: {count}")


def fix_autoapi_anchors(
    app: Sphinx,
    exception: Exception | None,
) -> None:
    """Fix anchor links after build to remove 'src.' prefix.

    Post-build hook that fixes AutoAPI-generated anchor IDs that incorrectly
    include the 'src.' prefix from the source directory structure.

    Changes:
    - #module-src.bluetooth_sig.X -> #module-bluetooth_sig.X
    - #src.bluetooth_sig.X.Y -> #bluetooth_sig.X.Y
    - href="...src.bluetooth_sig..." -> href="...bluetooth_sig..."

    Args:
        app: Sphinx application object
        exception: Build exception if any occurred
    """
    if exception is not None or app.builder.format != "html":
        return

    build_dir = Path(app.outdir)
    if not build_dir.exists():
        return

    # Patterns to fix
    patterns = [
        # Fix module anchor IDs
        (r'id="module-src\.bluetooth_sig\.', 'id="module-bluetooth_sig.'),
        (r"#module-src\.bluetooth_sig\.", "#module-bluetooth_sig."),
        # Fix class/function anchor IDs
        (r'id="src\.bluetooth_sig\.', 'id="bluetooth_sig.'),
        (r"#src\.bluetooth_sig\.", "#bluetooth_sig."),
        # Fix href links
        (r'href="([^"]*)/src\.bluetooth_sig\.', r'href="\1/bluetooth_sig.'),
        # Fix py:module directives in source
        (r"py:module:: src\.bluetooth_sig\.", "py:module:: bluetooth_sig."),
    ]

    # Process all HTML files
    html_files = list(build_dir.rglob("*.html"))
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding="utf-8")
            modified = content

            # Apply all patterns
            for pattern, replacement in patterns:
                modified = re.sub(pattern, replacement, modified)

            # Only write if changes were made
            if modified != content:
                html_file.write_text(modified, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to fix anchors in {html_file}: {e}")


def run_pre_build_scripts(app: Sphinx, config: object) -> None:
    """Run generation scripts before building documentation.

    This replicates the behaviour from docs_hooks.py (which was MkDocs-specific)
    for Sphinx builds. Executes two pre-build steps:
    1. Generates comprehensive list of supported characteristics and services
       from the registry system → docs/source/reference/characteristics.md
    2. Generates class diagrams and dependency graphs using pyreverse and pydeps
       → docs/diagrams/*.svg (C4 model, package structure, etc.)

    Args:
        app: Sphinx application object
        config: Sphinx config object (unused but required by event signature)

    Raises:
        subprocess.CalledProcessError: If any generation script fails.
    """
    repo_root = Path(__file__).parent.parent.parent

    # =========================================================================
    # Step 1: Generate characteristics and services documentation
    # =========================================================================
    script_path = repo_root / "scripts" / "generate_char_service_list.py"

    if not script_path.exists():
        print(f"Warning: Generate script not found at {script_path}")
    else:
        try:
            print("Running characteristics generation script...")
            print("  → Outputs to: docs/source/reference/characteristics.md")
            subprocess.run(
                [sys.executable, str(script_path)],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )
            print("✓ Characteristics documentation generated successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to generate characteristics: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise

    # =========================================================================
    # Step 2: Generate architecture diagrams
    # =========================================================================
    diag_script = repo_root / "scripts" / "generate_diagrams.py"
    if not diag_script.exists():
        print(f"Warning: Diagrams generation script not found at {diag_script}")
    else:
        try:
            print("Running diagrams generation script...")
            print("  → Outputs to: docs/source/diagrams/*.svg")
            # Force strict behaviour for published docs
            env = dict(os.environ)
            env["STRICT_DIAGRAMS"] = "1"
            subprocess.run(
                [sys.executable, str(diag_script)],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            print("✓ Diagrams generated successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to generate diagrams: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise


def setup(app: Sphinx) -> None:
    """Sphinx setup hook.

    Connects custom event handlers to Sphinx events.

    Args:
        app: Sphinx application object
    """
    # Run generation scripts before build starts
    app.connect("config-inited", run_pre_build_scripts)

    # Skip members during API generation
    app.connect("autoapi-skip-member", autoapi_skip_member)

    # Post-build fixes
    app.connect("build-finished", fix_table_headers)
    app.connect("build-finished", fix_autoapi_anchors)
