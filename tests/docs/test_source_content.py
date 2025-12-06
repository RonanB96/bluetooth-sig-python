"""Test documentation source files (markdown/RST) for quality and Diátaxis compliance.

These tests run directly on source files and don't require built documentation.
They can catch issues early in CI before the expensive doc build process.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Source directory for documentation
DOCS_SOURCE_DIR = Path(__file__).parent.parent.parent / "docs" / "source"

# Diátaxis compliance rules
DIATAXIS_RULES = {
    "tutorials": {
        "forbidden_phrases": [
            "you will learn",  # Presumptuous
            "let me explain",  # Too much explanation
            "there are many options",  # Too many alternatives
            "you should understand",  # Not hands-on
        ],
        "encouraged_phrases": [
            "we will",  # First-person plural
            "notice that",  # Points out observations
            "should look like",  # Sets expectations
            "let's",  # Inclusive language
        ],
        "purpose": "teach through practical guided experience",
    },
    "how-to": {
        "forbidden_phrases": [
            "first, let me teach you",  # Not a tutorial
            "you will learn",  # Not learning-oriented
            "this is how it works internally",  # Not task-focused
        ],
        "encouraged_patterns": [
            r"how to \w+",  # Title pattern
            r"this guide shows",  # Clear purpose
            r"to achieve",  # Goal-oriented
        ],
        "purpose": "guide through real-world problems",
    },
    "reference": {
        "forbidden_phrases": [
            "i think",  # No opinion
            "you should",  # No instruction
            "let me show you",  # No tutorial content
            "in my opinion",  # Not objective
        ],
        "required_elements": [
            "parameters",
            "returns",
            "attributes",
        ],
        "purpose": "provide accurate technical descriptions",
    },
    "explanation": {
        "encouraged_phrases": [
            "the reason is",
            "this is because",
            "historically",
            "an alternative approach",
            "why",
        ],
        "allowed_opinion": True,
        "purpose": "deepen understanding through context",
    },
}


@pytest.fixture
def docs_source_dir() -> Path:
    """Get documentation source directory."""
    return DOCS_SOURCE_DIR


@pytest.fixture
def all_markdown_files(docs_source_dir: Path) -> list[Path]:
    """Get all markdown source files."""
    if not docs_source_dir.exists():
        pytest.skip(f"Documentation source directory not found: {docs_source_dir}")
    return list(docs_source_dir.rglob("*.md"))


def test_markdown_images_have_alt_text(all_markdown_files: list[Path]) -> None:
    """Test that markdown images have alt text."""
    issues = []
    image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

    for file in all_markdown_files:
        content = file.read_text(encoding="utf-8")
        for match in image_pattern.finditer(content):
            alt_text = match.group(1)
            if not alt_text or alt_text.strip() == "":
                issues.append(f"{file.relative_to(DOCS_SOURCE_DIR)}: Empty alt text for image {match.group(2)}")

    if issues:
        pytest.fail("Images without alt text:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


def test_code_blocks_have_language(all_markdown_files: list[Path]) -> None:
    """Test that code blocks specify a language."""
    issues = []
    # Match ```\n or ``` \n (no language specified)
    bad_fence = re.compile(r"^```\s*$", re.MULTILINE)

    for file in all_markdown_files:
        content = file.read_text(encoding="utf-8")
        matches = bad_fence.findall(content)
        if matches:
            issues.append(f"{file.relative_to(DOCS_SOURCE_DIR)}: {len(matches)} code block(s) without language")

    if issues:
        pytest.fail("Code blocks without language:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


def test_tutorials_use_appropriate_language(docs_source_dir: Path) -> None:
    """Test that tutorial content uses learning-oriented language."""
    tutorials_dir = docs_source_dir / "tutorials"

    if not tutorials_dir.exists():
        pytest.skip("Tutorials directory not found")

    # Find all markdown files in tutorials
    tutorial_files = list(tutorials_dir.rglob("*.md"))
    if not tutorial_files:
        pytest.skip("No tutorial markdown files found")

    issues = []
    rules = DIATAXIS_RULES["tutorials"]

    for tutorial_file in tutorial_files:
        content = tutorial_file.read_text(encoding="utf-8").lower()

        # Check for forbidden phrases
        for phrase in rules["forbidden_phrases"]:
            if phrase.lower() in content:
                issues.append(f"{tutorial_file.name}: Contains forbidden phrase '{phrase}'")

    if issues:
        pytest.fail("Tutorial language issues found:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


def test_reference_docs_maintain_neutral_tone(docs_source_dir: Path) -> None:
    """Test that hand-written reference documentation maintains neutral, objective tone."""
    reference_dir = docs_source_dir / "reference"

    if not reference_dir.exists():
        pytest.skip("Reference directory not found")

    # Find reference files (hand-written markdown only)
    reference_files = list(reference_dir.rglob("*.md"))
    if not reference_files:
        pytest.skip("No reference markdown files found")

    issues = []
    rules = DIATAXIS_RULES["reference"]

    for ref_file in reference_files:
        content = ref_file.read_text(encoding="utf-8").lower()

        # Exclude code blocks from analysis
        content_without_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

        # Check for forbidden subjective phrases
        for phrase in rules["forbidden_phrases"]:
            if phrase.lower() in content_without_code:
                issues.append(f"{ref_file.name}: Contains subjective phrase '{phrase}'")

    if issues:
        pytest.fail(
            "Reference documentation should be objective:\n" + "\n".join(f"  - {issue}" for issue in issues[:10])
        )


def test_how_to_guides_are_task_focused(docs_source_dir: Path) -> None:
    """Test that how-to guides focus on solving specific tasks."""
    howto_dir = docs_source_dir / "how-to"

    if not howto_dir.exists():
        pytest.skip("How-to directory not found")

    howto_files = list(howto_dir.rglob("*.md"))
    if not howto_files:
        pytest.skip("No how-to markdown files found")

    issues = []

    for howto_file in howto_files:
        content = howto_file.read_text(encoding="utf-8")

        # Extract first heading (title)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)

        if title_match:
            title = title_match.group(1).strip().lower()

            # How-to guides should typically start with "How to" or describe a task
            has_task_focus = any(
                pattern in title for pattern in ["how to", "guide", "using", "integrating", "adding", "testing"]
            )

            if not has_task_focus:
                issues.append(f"{howto_file.name}: Title may not be task-focused: '{title}'")

    # This is informational, not a hard failure
    if issues:
        print("\nHow-to guide title observations:\n" + "\n".join(f"  - {issue}" for issue in issues[:5]))


def test_markdown_links_have_descriptive_text(all_markdown_files: list[Path]) -> None:
    """Test that markdown links have descriptive text, not bare URLs."""
    issues = []
    # Match [text](url)
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for file in all_markdown_files:
        content = file.read_text(encoding="utf-8")

        for match in link_pattern.finditer(content):
            text = match.group(1).strip()
            url = match.group(2).strip()

            # Check if link text is just the URL or "click here" type
            if text.lower() in ["click here", "here", "link", "read more"] or text == url:
                issues.append(f"{file.relative_to(DOCS_SOURCE_DIR)}: Non-descriptive link text '{text}'")

    if issues:
        pytest.fail("Links need descriptive text:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))


def test_heading_hierarchy_no_skips(all_markdown_files: list[Path]) -> None:
    """Test markdown headings don't skip levels (e.g., h2 to h4)."""
    issues = []

    for file in all_markdown_files:
        content = file.read_text(encoding="utf-8")
        headings = re.findall(r"^(#{1,6})\s+", content, re.MULTILINE)

        for i in range(len(headings) - 1):
            current_level = len(headings[i])
            next_level = len(headings[i + 1])

            # Check if we skip levels (e.g., ## -> ####)
            if next_level > current_level + 1:
                issues.append(
                    f"{file.relative_to(DOCS_SOURCE_DIR)}: Heading skip from h{current_level} to h{next_level}"
                )
                break  # One issue per file is enough

    if issues:
        pytest.fail("Heading hierarchy issues:\n" + "\n".join(f"  - {issue}" for issue in issues[:10]))
