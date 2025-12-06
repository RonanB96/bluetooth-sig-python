"""Pytest configuration for documentation verification tests.

These tests require built documentation (Sphinx HTML output) and use Playwright
to verify navigation, structure, accessibility, and Diátaxis compliance.
"""

from __future__ import annotations

import http.server
import os
import socketserver
import threading
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page

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

# ============================================================================
# Playwright Configuration
# ============================================================================

# Configure Playwright to use browsers from default cache location
# This must be set before pytest-playwright plugin loads
# Remove any overrides that might cause issues
if "PLAYWRIGHT_BROWSERS_PATH" in os.environ:
    del os.environ["PLAYWRIGHT_BROWSERS_PATH"]
if "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD" in os.environ:
    del os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"]

# Get repository root and docs build directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DOCS_BUILD_DIR = ROOT_DIR / "docs" / "build" / "html"


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest for documentation tests.

    Override Playwright's browser launch to use system chromium.
    """
    # Set launch options for system chromium
    config.option.browser_channel = None


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict[str, Any]) -> dict[str, Any]:
    """Override Playwright browser launch arguments.

    Args:
        browser_type_launch_args: Default launch arguments from pytest-playwright

    Returns:
        Modified launch arguments with additional browser options
    """
    # Use Playwright's bundled chromium (no executable_path needed)
    # It will use the browser from ~/.cache/ms-playwright/
    return {
        **browser_type_launch_args,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    }


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
def docs_server_port() -> Generator[int, None, None]:
    """Fixture providing an available port for the docs server.

    Finds an available port and yields it for the session. The port is
    automatically released when the session ends.

    Yields:
        Available port number
    """
    port = find_available_port()
    yield port
    # Port is automatically released when fixture scope ends


@pytest.fixture(scope="session")
def docs_server(docs_server_port: int) -> Generator[str, None, None]:
    """Start a simple HTTP server serving built Sphinx documentation.

    This fixture starts a server at session scope, serves the built HTML docs,
    and automatically shuts down after all tests complete or on interruption (Ctrl+C).

    Args:
        docs_server_port: Port to use for the server

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

    # Change to docs build directory
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(DOCS_BUILD_DIR), **kwargs)

        def log_message(self, format: str, *args: Any) -> None:
            """Suppress server log messages."""
            pass

    # Start server in a thread
    server = socketserver.TCPServer(("127.0.0.1", docs_server_port), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Wait for server to be ready
    base_url = f"http://localhost:{docs_server_port}"
    max_wait = 5
    start_time = time.time()

    while time.time() - start_time < max_wait:
        try:
            import urllib.request

            urllib.request.urlopen(f"{base_url}/index.html", timeout=1)
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
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Configure browser context for consistent testing.

    Args:
        browser_context_args: Default context arguments from pytest-playwright

    Returns:
        Modified context arguments with consistent viewport and locale
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-US",
        "timezone_id": "UTC",
    }


@pytest.fixture(autouse=True)
def monitor_console_errors(page: Page) -> Generator[None, None, None]:
    """Monitor and collect JavaScript console errors during tests.

    This fixture automatically monitors all console messages and fails tests
    if JavaScript errors are detected. It's applied to all tests automatically.

    Args:
        page: Playwright page fixture

    Yields:
        None - fixture runs before and after test execution

    Raises:
        AssertionError: If console errors are detected during test
    """
    errors: list[str] = []

    def handle_console(msg: Any) -> None:
        """Collect console error messages."""
        if msg.type == "error":
            error_text = msg.text
            # Ignore common non-critical errors
            if "404" in error_text or "Failed to load resource" in error_text:
                return  # Skip 404s for missing favicons, etc.
            errors.append(error_text)

    page.on("console", handle_console)
    yield

    # Check for errors after test completes
    if errors:
        error_summary = "\n".join(f"  - {err}" for err in errors[:5])
        if len(errors) > 5:
            error_summary += f"\n  ... and {len(errors) - 5} more errors"
        pytest.fail(f"JavaScript console errors detected:\n{error_summary}")


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
    """Generate parametrized tests for all HTML files.

    This hook dynamically parametrizes tests that use the 'html_file' fixture
    with all HTML files found in the built documentation.
    """
    if "html_file" in metafunc.fixturenames:
        html_files = []
        if DOCS_BUILD_DIR.exists():
            html_files = list(DOCS_BUILD_DIR.rglob("*.html"))

        # Create (file_path, url) tuples for parametrization
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

    url_map = {}
    for html_file in DOCS_BUILD_DIR.rglob("*.html"):
        relative_path = html_file.relative_to(DOCS_BUILD_DIR)
        url = f"{docs_server}/{relative_path}"
        url_map[html_file] = url
    return url_map
