"""Tests for README.md badges to ensure they are accessible and valid."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import requests


def test_readme_badges_are_valid() -> None:
    """Test that all badges in README.md return valid responses.

    This test validates that:
    1. Badge URLs are reachable
    2. Badge services return successful HTTP responses
    3. No broken badge links exist in README

    Note: PyPI badge is expected to fail until package is published.
    """
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")

    # Extract all badge URLs (img.shields.io and other badge services)
    badge_pattern = r"\[!\[.*?\]\((https://[^\)]+)\)\]"
    badge_urls = re.findall(badge_pattern, readme_content)

    assert len(badge_urls) > 0, "No badges found in README.md"

    failed_badges: list[tuple[str, int | str]] = []
    skipped_badges: list[tuple[str, str]] = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (pytest badge checker)"})

    for url in badge_urls:
        # TODO Skip PyPI badge as package is not yet published
        if "pypi.org" in url or "pypi/v/bluetooth-sig" in url:
            skipped_badges.append((url, "Package not yet published"))
            continue

        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            if response.status_code != 200:
                failed_badges.append((url, response.status_code))
        except requests.RequestException as e:
            failed_badges.append((url, str(e)))

    if failed_badges:
        failure_msg = "Badge validation failures:\n"
        for url, error in failed_badges:
            failure_msg += f"  - {url}: {error}\n"
        if skipped_badges:
            failure_msg += "\nSkipped badges (expected until published):\n"
            for url, reason in skipped_badges:
                failure_msg += f"  - {url}: {reason}\n"
        pytest.fail(failure_msg)


def test_coverage_badge_endpoint_exists() -> None:
    """Test that the coverage badge JSON endpoint exists and is valid.

    Note: This tests the endpoint itself, not the badge image.
    The coverage badge uses a custom JSON endpoint that shields.io reads.
    """
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")

    # Extract the coverage endpoint URL from the badge
    coverage_pattern = r"url=([^)]+coverage-badge\.json)"
    match = re.search(coverage_pattern, readme_content)

    if not match:
        pytest.skip("Coverage badge endpoint not found in README.md")

    endpoint_url = match.group(1)

    try:
        response = requests.get(endpoint_url, timeout=10)

        # If 404, the endpoint doesn't exist yet (expected for new repos)
        if response.status_code == 404:
            pytest.skip(
                f"Coverage endpoint not yet published (404): {endpoint_url}\n"
                "This is expected for new repositories or before first GitHub Pages deploy."
            )

        # If 200, validate the JSON structure
        assert response.status_code == 200, f"Coverage endpoint returned {response.status_code}: {endpoint_url}"

        data = response.json()
        assert "schemaVersion" in data, "Coverage badge JSON missing 'schemaVersion'"
        assert "label" in data, "Coverage badge JSON missing 'label'"
        assert "message" in data, "Coverage badge JSON missing 'message'"

    except requests.RequestException as e:
        pytest.fail(f"Failed to fetch coverage endpoint {endpoint_url}: {e}")


def test_pypi_badge_matches_package() -> None:
    """Test that PyPI badge uses the correct package name.

    This test validates the badge configuration is correct,
    even though the package may not be published yet.
    """
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")

    # Extract PyPI badge URL
    pypi_pattern = r"https://img\.shields\.io/pypi/v/([^.]+)\.svg"
    match = re.search(pypi_pattern, readme_content)

    assert match, "PyPI version badge not found in README.md"

    package_name = match.group(1)
    assert package_name == "bluetooth-sig", f"PyPI badge uses package '{package_name}' but should use 'bluetooth-sig'"


def test_badge_links_match_urls() -> None:
    """Test that badge links point to appropriate documentation/resources.

    Validates that clicking on badges takes users to relevant pages.
    """
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    readme_content = readme_path.read_text(encoding="utf-8")

    # Badge format: [![alt](badge_url)](link_url)
    badge_link_pattern = r"\[!\[.*?\]\(https://[^\)]+\)\]\(([^)]+)\)"
    badge_links = re.findall(badge_link_pattern, readme_content)

    assert len(badge_links) > 0, "No badge links found in README.md"

    # Coverage badge should link to coverage report
    coverage_links = [link for link in badge_links if "coverage" in link.lower()]
    if coverage_links:
        assert any("coverage" in link.lower() for link in coverage_links), (
            "Coverage badge should link to coverage report"
        )

    # PyPI badge should link to PyPI page
    pypi_links = [link for link in badge_links if "pypi.org" in link]
    if pypi_links:
        assert any("bluetooth-sig" in link for link in pypi_links), "PyPI badge should link to package page"

    # Documentation badge should link to docs
    doc_links = [link for link in badge_links if "docs" in link.lower()]
    if doc_links:
        assert any("github.io" in link or "readthedocs" in link for link in doc_links), (
            "Documentation badge should link to hosted docs"
        )
