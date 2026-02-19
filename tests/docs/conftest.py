"""Pytest configuration for documentation verification tests.

These tests require built documentation (Sphinx HTML output) to verify
navigation, structure, accessibility, and Diataxis compliance.

Shared fixtures for both regular and Playwright-based documentation tests.

Selective Testing:
    Set DOCS_TEST_FILES environment variable to control which pages to test:
        export DOCS_TEST_FILES='["tutorials/index.html", "api/index.html"]'  # Test specific pages
        export DOCS_TEST_FILES='["ALL"]'                                      # Test all pages
        export DOCS_TEST_FILES='[]'                                             # Skip all tests (no docs changed)

    If DOCS_TEST_FILES is not set, all HTML files are tested (default behaviour).
"""

from __future__ import annotations

import http.server
import json
import multiprocessing
import os
import socket
import threading
import time
from collections.abc import Generator
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from tests.conftest import ROOT_DIR

# Skip playwright_tests folder during collection if playwright is not installed
# This prevents collection errors from breaking non-playwright tests
# Must use collect_ignore (not collect_ignore_glob) to ignore directories entirely
try:
    import playwright as _playwright  # pylint: disable=unused-import

    del _playwright  # Silence unused import - we only check importability
    collect_ignore: list[str] = []
except ImportError:
    # Use absolute path to the playwright_tests directory
    collect_ignore = [str(Path(__file__).parent / "playwright_tests")]

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

DOCS_BUILD_DIR = ROOT_DIR / "docs" / "build" / "html"

# Worker calculation thresholds
WORKER_THRESHOLD_FEW_FILES = 10  # Below this: minimal workers
WORKER_THRESHOLD_MEDIUM_FILES = 50  # Below this: medium workers
WORKER_FILES_PER_WORKER = 20  # Files per worker for large workloads
MAX_WORKERS = 8  # Maximum workers regardless of CPU count
MIN_WORKERS = 2  # Minimum workers for parallel testing

# Server configuration
DEFAULT_SERVER_PORT = 8000  # Base port for HTTP servers
SERVER_STARTUP_TIMEOUT_SECONDS = 3  # Time to wait for server startup
SERVER_HEALTH_CHECK_INTERVAL_SECONDS = 0.1  # Interval between health checks

# File count estimation
ESTIMATED_HTML_FILE_COUNT = 150  # Default estimate when docs not built


def pytest_xdist_auto_num_workers(config: pytest.Config) -> int:
    """Dynamically calculate optimal number of pytest-xdist workers.

    Scales workers based on the number of documentation files being tested:
    - Few files (< 10): 1-2 workers (avoid overhead)
    - Medium (10-50): 2-4 workers
    - Many (50+): 4-8 workers (up to CPU count)

    Each worker gets its own HTTP server on a unique port.

    Args:
        config: Pytest configuration object

    Returns:
        Optimal number of workers for current test scope
    """
    # Get test file count from environment variable (set by detect_changed_docs.py)
    test_files_env = os.environ.get("DOCS_TEST_FILES", "")

    if test_files_env:
        try:
            test_files_config = json.loads(test_files_env)
            if not test_files_config or test_files_config == []:
                # No files to test
                return 1
            if test_files_config == ["ALL"]:
                # Test all files - use all available cores
                if DOCS_BUILD_DIR.exists():
                    file_count = len(list(DOCS_BUILD_DIR.rglob("*.html")))
                else:
                    file_count = ESTIMATED_HTML_FILE_COUNT
            else:
                # Specific files
                file_count = len(test_files_config)
        except (json.JSONDecodeError, ValueError):
            file_count = ESTIMATED_HTML_FILE_COUNT
    # Default: test all files
    elif DOCS_BUILD_DIR.exists():
        file_count = len(list(DOCS_BUILD_DIR.rglob("*.html")))
    else:
        file_count = ESTIMATED_HTML_FILE_COUNT

    # Calculate optimal workers based on file count and available CPUs
    cpu_count = multiprocessing.cpu_count()

    if file_count < WORKER_THRESHOLD_FEW_FILES:
        # Few files - avoid xdist overhead
        workers = min(MIN_WORKERS, cpu_count)
    elif file_count < WORKER_THRESHOLD_MEDIUM_FILES:
        # Medium workload
        workers = min(4, cpu_count)
    else:
        # Large workload - scale up to CPU count
        workers = min(MAX_WORKERS, cpu_count, max(MIN_WORKERS, file_count // WORKER_FILES_PER_WORKER))

    # Log worker calculation for debugging
    print(
        f"\nDynamic worker calculation: {file_count} files, {cpu_count} CPUs → {workers} workers\n",
        flush=True,
    )

    return workers


def is_port_available(port: int) -> bool:
    """Check if a port is available for binding.

    Args:
        port: Port number to check

    Returns:
        True if port is available, False otherwise
    """
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
def docs_server_port(worker_id: str) -> int:
    """Fixture providing a unique port for each worker's docs server.

    Each pytest-xdist worker gets its own HTTP server on a unique port:
    - master or gw0: 8000
    - gw1: 8001
    - gw2: 8002
    - etc.

    This enables true parallel testing with multiple server instances.

    Args:
        worker_id: pytest-xdist worker identifier ('master' or 'gw0', 'gw1', etc.)

    Yields:
        Unique port number for this worker
    """
    if worker_id == "master":
        # Not using xdist
        port = DEFAULT_SERVER_PORT
    elif worker_id.startswith("gw"):
        # Extract worker number (gw0 -> 0, gw1 -> 1, etc.)
        worker_num = int(worker_id[2:])
        port = DEFAULT_SERVER_PORT + worker_num
    else:
        # Fallback for unexpected worker_id format
        port = find_available_port()

    print(f"Worker {worker_id} assigned port {port}", flush=True)
    return port


@pytest.fixture(scope="session")
def docs_server(docs_server_port: int, worker_id: str) -> Generator[str, None, None]:
    """Start a threaded HTTP server serving built Sphinx documentation.

    Each pytest-xdist worker gets its own ThreadingHTTPServer instance
    on a unique port, enabling true parallel testing without blocking.

    ThreadingHTTPServer handles concurrent requests efficiently, preventing
    "Connection reset" errors when multiple tests access the server simultaneously.

    Args:
        docs_server_port: Unique port for this worker's server
        worker_id: pytest-xdist worker identifier

    Yields:
        Base URL of the documentation server (e.g., "http://localhost:8001")

    Raises:
        RuntimeError: If documentation is not built or server fails to start
    """
    if not DOCS_BUILD_DIR.exists():
        raise RuntimeError(
            f"Documentation not built. Build directory not found: {DOCS_BUILD_DIR}\n"
            "Run 'sphinx-build -b html docs/source docs/build/html' to build documentation."
        )

    base_url = f"http://localhost:{docs_server_port}"

    # Each worker starts its own server (no coordination needed)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(DOCS_BUILD_DIR), **kwargs)

        def log_message(self, format: str, *args: Any) -> None:  # pylint: disable=redefined-builtin # noqa: A002
            """Suppress server log messages."""

    # Use ThreadingHTTPServer for concurrent request handling
    # This prevents "Connection reset" errors during parallel testing
    class ThreadedDocsServer(ThreadingHTTPServer):
        allow_reuse_address = True
        daemon_threads = True  # Allow clean shutdown

    print(f"Worker {worker_id} starting server on port {docs_server_port}", flush=True)

    # Start server in a thread
    with ThreadedDocsServer(("127.0.0.1", docs_server_port), Handler) as server:
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        # Wait for server to be ready (shorter timeout since no coordination needed)
        max_wait = SERVER_STARTUP_TIMEOUT_SECONDS
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                import urllib.request

                with urllib.request.urlopen(f"{base_url}/index.html", timeout=1):
                    print(f"Worker {worker_id} server ready on port {docs_server_port}", flush=True)
                    break
            except Exception:
                time.sleep(SERVER_HEALTH_CHECK_INTERVAL_SECONDS)
        else:
            server.shutdown()
            raise RuntimeError(f"Documentation server for worker {worker_id} failed to start within {max_wait} seconds")

        try:
            yield base_url
        finally:
            # Ensure server shuts down even on KeyboardInterrupt (Ctrl+C)
            print(f"Worker {worker_id} shutting down server on port {docs_server_port}", flush=True)
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
                print("[INFO] No documentation changes detected, skipping all tests")
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
                    print(f"Skipping {len(missing_files)} non-existent files:")
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
