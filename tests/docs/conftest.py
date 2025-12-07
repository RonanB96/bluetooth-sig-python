"""Pytest configuration for documentation verification tests.

These tests require built documentation (Sphinx HTML output) to verify
navigation, structure, accessibility, and Diataxis compliance.

Shared fixtures for both regular and Playwright-based documentation tests.

Selective Testing:
    Set DOCS_TEST_FILES environment variable to control which pages to test:
        export DOCS_TEST_FILES='["tutorials/index.html", "api/index.html"]'  # Test specific pages
        export DOCS_TEST_FILES='["ALL"]'                                      # Test all pages
        export DOCS_TEST_FILES='[]'                                             # Skip all tests (no docs changed)

    If DOCS_TEST_FILES is not set, all HTML files are tested (default behavior).
"""

from __future__ import annotations

import http.server
import json
import os
import socketserver
import threading
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

# ============================================================================
# Shared Test Constants
# ============================================================================

# CSS class names used in Furo theme
CSS_CLASS_SIDEBAR_TREE = "sidebar-tree"
CSS_CLASS_TOCTREE_L1 = "toctree-l1"
CSS_CLASS_SIDEBAR_BRAND = "sidebar-brand"
CSS_CLASS_SIDEBAR_SEARCH = "sidebar-search"
CSS_CLASS_SIDEBAR_DRAWER = "sidebar-drawer"
CSS_CLASS_TOCTREE_CHECKBOX = "toctree-checkbox"

# CSS selectors for Furo theme (for Playwright tests)
SELECTOR_SIDEBAR_TREE = ".sidebar-tree"
SELECTOR_SIDEBAR_DRAWER = ".sidebar-drawer"
SELECTOR_SIDEBAR_BRAND = ".sidebar-brand"
SELECTOR_SIDEBAR_SEARCH = ".sidebar-search"
SELECTOR_TOCTREE_L1 = ".toctree-l1"
SELECTOR_TOCTREE_CHECKBOX = "input.toctree-checkbox"
SELECTOR_SIDEBAR_TREE_LINK = f"{SELECTOR_SIDEBAR_TREE} a.reference"
SELECTOR_TOP_LEVEL_ITEMS = f"{SELECTOR_SIDEBAR_TREE} > ul > li{SELECTOR_TOCTREE_L1}"

# Required sections following Diátaxis framework
REQUIRED_SECTIONS = {
    "Tutorials": "tutorials/index.html",
    "How-to Guides": "how-to/index.html",
    "API Reference": "api/index.html",
    "Understanding the Library": "explanation/index.html",
    "Community": "community/index.html",
    "Performance & Benchmarks": "performance/index.html",
}

# Expected section order
EXPECTED_SECTION_ORDER = [
    "Tutorials",
    "How-to Guides",
    "API Reference",
    "Understanding the Library",
    "Community",
    "Performance & Benchmarks",
]

# Get repository root and docs build directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_BUILD_DIR = ROOT_DIR / "docs" / "build" / "html"


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False otherwise
    """
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from the given port.

    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        Available port number

    Raises:
        RuntimeError: If no available port found
    """
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")


@pytest.fixture(scope="session")
def docs_server_port(worker_id: str) -> Generator[int, None, None]:
    """Fixture providing an available port for the docs server.

    When running with pytest-xdist, ensures all workers use the same port
    by having only the master/gw0 worker find and reserve the port.

    Args:
        worker_id: pytest-xdist worker identifier ('master' or 'gw0', 'gw1', etc.)

    Yields:
        Available port number
    """
    if worker_id == "master":
        # Not using xdist, find an available port
        port = find_available_port()
        yield port
    else:
        # xdist worker - use fixed port that master/gw0 will bind
        # All workers will attempt to connect to the same server
        yield 8000


@pytest.fixture(scope="session")
def docs_server(docs_server_port: int, worker_id: str) -> Generator[str, None, None]:
    """Start a simple HTTP server serving built Sphinx documentation.

    This fixture starts a server at session scope, serves the built HTML docs,
    and automatically shuts down after all tests complete or on interruption (Ctrl+C).

    When using pytest-xdist, only the master/gw0 worker starts the server,
    and all other workers connect to it.

    Args:
        docs_server_port: Port to use for the server
        worker_id: pytest-xdist worker identifier

    Yields:
        Base URL of the documentation server (e.g., "http://localhost:8000")

    Raises:
        RuntimeError: If documentation is not built or server fails to start
    """
    if not DOCS_BUILD_DIR.exists():
        raise RuntimeError(
            f"Documentation not built. Build directory not found: {DOCS_BUILD_DIR}\n"
            "Run 'sphinx-build -b html docs/source docs/build/html' to build documentation."
        )

    base_url = f"http://localhost:{docs_server_port}"

    # Only gw0 (first worker) or master (non-xdist) should start the server
    # All other workers (gw1, gw2, etc.) should wait for it
    is_server_worker = worker_id in ("master", "gw0")

    if not is_server_worker:
        # xdist worker (gw1, gw2, etc.) - wait for server to be ready (started by gw0)
        max_wait = 30
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                import urllib.request

                with urllib.request.urlopen(f"{base_url}/index.html", timeout=1):
                    break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError(f"Documentation server not ready within {max_wait} seconds")

        yield base_url
        return

    # gw0 or master: start the server
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(DOCS_BUILD_DIR), **kwargs)

        def log_message(self, fmt: str, *args: Any) -> None:
            """Suppress server log messages."""
            pass  # pylint: disable=unnecessary-pass

    # Enable address reuse to prevent "Address already in use" errors
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    # Start server in a thread
    with ReuseAddrTCPServer(("127.0.0.1", docs_server_port), Handler) as server:
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        base_url = f"http://localhost:{docs_server_port}"
        max_wait = 5
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                import urllib.request

                with urllib.request.urlopen(f"{base_url}/index.html", timeout=1):
                    break
            except Exception:
                time.sleep(0.1)
        else:
            server.shutdown()
            raise RuntimeError(f"Documentation server failed to start within {max_wait} seconds")

        try:
            yield base_url
        finally:
            # Ensure server shuts down even on KeyboardInterrupt (Ctrl+C)
            server.shutdown()
            server.server_close()


@pytest.fixture(scope="session")
def docs_build_dir() -> Path:
    """Fixture providing the path to built documentation.

    Returns:
        Path to the docs/build/html directory
    """
    return DOCS_BUILD_DIR


@pytest.fixture(scope="session")
def all_html_files(docs_build_dir: Path) -> list[Path]:
    """Fixture providing all HTML files in the built documentation.

    Returns:
        List of paths to all HTML files in docs/build/html
    """
    if not docs_build_dir.exists():
        return []
    return sorted(docs_build_dir.rglob("*.html"))


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Generate parametrized tests for HTML files (all or selective).

    This hook dynamically parametrizes tests that use the 'html_file' fixture
    with HTML files based on the DOCS_TEST_FILES environment variable.

    Environment Variables:
        DOCS_TEST_FILES: JSON array of HTML file paths to test
            - ["ALL"]: Test all HTML files (default if not set)
            - ["tutorials/index.html", "api/index.html"]: Test specific files
            - []: Skip all tests (no documentation changes detected)

    The paths in DOCS_TEST_FILES should be relative to docs/build/html/.
    """
    if "html_file" in metafunc.fixturenames:
        # Check for selective testing via environment variable
        test_files_env = os.environ.get("DOCS_TEST_FILES", "")

        if test_files_env:
            try:
                test_files_config = json.loads(test_files_env)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid DOCS_TEST_FILES JSON: {test_files_env}\n"
                    f'Expected format: ["file1.html", "file2.html"], ["ALL"], or []\n'
                    f"Error: {e}"
                ) from e

            # Handle empty list - skip all tests (no docs changes)
            if test_files_config == []:
                print("ℹ️  No documentation changes detected, skipping all tests")
                metafunc.parametrize("html_file", [], ids=[])
                return

            # Check if comprehensive testing requested
            if test_files_config == ["ALL"]:
                # Test all files
                html_files = []
                if DOCS_BUILD_DIR.exists():
                    html_files = sorted(DOCS_BUILD_DIR.rglob("*.html"))
            else:
                # Test specific files
                html_files = []
                missing_files = []
                if DOCS_BUILD_DIR.exists():
                    for relative_path in test_files_config:
                        file_path = DOCS_BUILD_DIR / relative_path
                        if file_path.exists():
                            html_files.append(file_path)
                        else:
                            missing_files.append(relative_path)

                # Report missing files but continue with found files
                if missing_files:
                    print(f"⚠️  Skipping {len(missing_files)} non-existent files:")
                    for missing in missing_files[:5]:
                        print(f"     - {missing}")
                    if len(missing_files) > 5:
                        print(f"     ... and {len(missing_files) - 5} more")

                # Sort for consistent test ordering
                html_files = sorted(html_files)
        else:
            # Default: test all files
            html_files = []
            if DOCS_BUILD_DIR.exists():
                html_files = sorted(DOCS_BUILD_DIR.rglob("*.html"))

        # Create parametrization
        ids = [str(f.relative_to(DOCS_BUILD_DIR)) for f in html_files]
        metafunc.parametrize("html_file", html_files, ids=ids, indirect=True)


@pytest.fixture
def html_file(request: pytest.FixtureRequest, docs_server: str) -> str:
    """Convert HTML file path to URL.

    Args:
        request: Pytest request with param containing HTML file path
        docs_server: Base URL of docs server

    Returns:
        Full URL to the HTML file
    """
    file_path: Path = request.param
    relative_path = file_path.relative_to(DOCS_BUILD_DIR)
    return f"{docs_server}/{relative_path}"


@pytest.fixture(scope="session")
def html_file_url(docs_server: str) -> dict[Path, str]:
    """Fixture providing URL mapping for HTML files.

    Returns:
        Dict mapping file paths to their URLs
    """
    if not DOCS_BUILD_DIR.exists():
        return {}

    url_map: dict[Path, str] = {}
    for html_file in DOCS_BUILD_DIR.rglob("*.html"):
        relative_path = html_file.relative_to(DOCS_BUILD_DIR)
        url = f"{docs_server}/{relative_path}"
        url_map[html_file] = url
    return url_map
