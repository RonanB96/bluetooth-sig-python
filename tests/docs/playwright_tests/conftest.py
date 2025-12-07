"""Playwright-specific fixtures for documentation browser tests.

These fixtures configure Playwright browser automation for testing
documentation navigation, accessibility, and interactive features.
"""

from __future__ import annotations

import os
from collections.abc import Generator
from typing import Any

import pytest
from playwright.sync_api import ConsoleMessage, Page

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

    def handle_console(msg: ConsoleMessage) -> None:  # type: ignore[type-arg]
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
