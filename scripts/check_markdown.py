#!/usr/bin/env python3
"""Check markdown files for common issues."""

from __future__ import annotations

import json
import re
from pathlib import Path

# Get repository root
ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"


def check_broken_links(file_path: Path, content: str) -> list[tuple[int, str]]:
    """Check for broken internal links.

    Args:
        file_path: Path to the markdown file being checked.
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    # Pattern for markdown links: [text](url)
    link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"

    for i, line in enumerate(lines, 1):
        for match in re.finditer(link_pattern, line):
            link_text = match.group(1)
            url = match.group(2)

            # Skip external links
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue

            # Check for internal links
            if "/" in url or ".md" in url:
                # Resolve relative path
                target = file_path.parent / url.split("#")[0]
                if not target.exists() and not target.with_suffix("").exists():
                    issues.append((i, f"Broken link: [{link_text}]({url})"))

    return issues


def check_images(content: str) -> list[tuple[int, str]]:
    """Check for missing alt text in images.

    Args:
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    # Pattern for images: ![alt](url)
    image_pattern = r"!\[([^\]]*)\]\(([^\)]+)\)"

    for i, line in enumerate(lines, 1):
        for match in re.finditer(image_pattern, line):
            alt_text = match.group(1)
            url = match.group(2)

            if not alt_text or alt_text.strip() == "":
                issues.append((i, f"Image missing alt text: ![]({url})"))

    return issues


def check_heading_hierarchy(content: str) -> list[tuple[int, str]]:
    """Check for incorrect heading hierarchy.

    Args:
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    prev_level = 0
    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Track code blocks to ignore headings inside them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue

        # Only check lines that are markdown headings (# followed by space)
        # Not Python comments or other uses of #
        stripped = line.lstrip()
        if (
            not in_code_block
            and stripped.startswith("#")
            and len(stripped) > 1
            and stripped[stripped.count("#")] == " "
        ):
            # Count heading level
            level = len(line) - len(line.lstrip("#"))
            if level > 6:
                issues.append((i, f"Invalid heading level (H{level}): {line[:50]}"))
            elif prev_level > 0 and level > prev_level + 1:
                issues.append((i, f"Heading hierarchy skip (H{prev_level} -> H{level}): {line[:50]}"))

            if level > 0 and level <= 6:
                prev_level = level

    return issues


def check_code_blocks(content: str) -> list[tuple[int, str]]:
    """Check for malformed code blocks.

    Args:
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    in_code_block = False
    code_block_start = 0

    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_start = i
            else:
                in_code_block = False
        elif i == len(lines) and in_code_block:
            issues.append((code_block_start, f"Unclosed code block starting at line {code_block_start}"))

    return issues


def check_list_formatting(content: str) -> list[tuple[int, str]]:
    """Check for list formatting issues.

    Args:
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # Check for inconsistent list markers
        if re.match(r"^\s*[\*\-\+]\s+", line):
            # Check if there's a space after marker
            if not re.match(r"^\s*[\*\-\+]\s\s+", line) and re.match(r"^\s*[\*\-\+]\S", line):
                issues.append((i, f"list item missing space after marker: {line[:50]}"))

    return issues


def check_table_formatting(content: str) -> list[tuple[int, str]]:
    """Check for table formatting issues.

    Args:
        content: Content of the markdown file.

    Returns:
        List of tuples containing (line_number, issue_description).
    """
    issues: list[tuple[int, str]] = []
    lines = content.split("\n")

    in_table = False
    column_count = 0

    for i, line in enumerate(lines, 1):
        # Check if line is a table row
        if "|" in line and line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
                column_count = line.count("|") - 1
            else:
                # Check column consistency
                current_columns = line.count("|") - 1
                if current_columns != column_count and not re.match(r"^\s*\|[\s\-:]+\|\s*$", line):
                    issues.append((i, f"Table column mismatch: expected {column_count}, got {current_columns}"))
        elif in_table and line.strip() == "":
            in_table = False
            column_count = 0

    return issues


def check_markdown_file(file_path: Path) -> dict[str, str | list[tuple[int, str]]]:
    """Check a single markdown file for issues.

    Args:
        file_path: Path to the markdown file to check.

    Returns:
        Dictionary containing file path and list of issues found.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError as e:
        return {"file": str(file_path.relative_to(ROOT_DIR)), "error": f"Failed to read file: {e}", "issues": []}

    all_issues: list[tuple[int, str]] = []

    # Run all checks
    all_issues.extend(check_broken_links(file_path, content))
    all_issues.extend(check_images(content))
    all_issues.extend(check_heading_hierarchy(content))
    all_issues.extend(check_code_blocks(content))
    all_issues.extend(check_list_formatting(content))
    all_issues.extend(check_table_formatting(content))

    return {"file": str(file_path.relative_to(ROOT_DIR)), "issues": sorted(all_issues, key=lambda x: x[0])}


def main() -> None:
    """Main function to check all markdown files."""
    # Find all markdown files
    md_files = sorted(DOCS_DIR.rglob("*.md"))

    results = []
    total_issues = 0

    for md_file in md_files:
        result = check_markdown_file(md_file)
        if result.get("error") or result.get("issues"):
            results.append(result)
            total_issues += len(result.get("issues", []))

    # Print results
    print(
        json.dumps(
            {
                "total_files": len(md_files),
                "files_with_issues": len(results),
                "total_issues": total_issues,
                "results": results,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
