#!/usr/bin/env python3
"""Lint Python code blocks in markdown documentation files and check markdown/mkdocs formatting.

This script uses md-snakeoil (built on Ruff) to format and lint Python code blocks
in markdown files. Configuration for ignored rules is managed in pyproject.toml under
[tool.ruff.lint.per-file-ignores] for "docs/**/*.md" files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def lint_python_blocks(docs_path: Path) -> int:
    """Lint Python code blocks in markdown files using md-snakeoil.

    md-snakeoil automatically uses the project's Ruff configuration from pyproject.toml,
    including per-file-ignores for documentation files.

    Returns:
        Number of files with issues (0 if all passed).
    """
    print("=" * 60)
    print("Linting Python code blocks with md-snakeoil...")
    print("=" * 60)

    # md-snakeoil uses the project's ruff configuration automatically
    # The per-file-ignores in pyproject.toml handle docs-specific exemptions
    cmd = ["snakeoil", str(docs_path)]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Print output
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # md-snakeoil returns non-zero exit code if there are formatting issues
    if result.returncode != 0:
        return 1

    return 0


def lint_markdown(docs_path: Path) -> tuple[int, int]:
    """Lint markdown files using markdownlint and check mkdocs build.

    Returns (markdown_issues, mkdocs_issues) tuple.
    """
    markdown_issues = 0
    mkdocs_issues = 0

    # Check if markdownlint-cli is available
    result = subprocess.run(["which", "markdownlint"], capture_output=True, check=False)
    has_markdownlint = result.returncode == 0

    if has_markdownlint:
        print("\n" + "=" * 60)
        print("Checking markdown formatting with markdownlint...")
        print("=" * 60)

        result = subprocess.run(["markdownlint", str(docs_path)], capture_output=True, text=True, check=False)

        if result.stdout or result.stderr:
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            markdown_issues = 1
        else:
            print("✅ All markdown files are properly formatted")
    else:
        print("\n⚠️  markdownlint not found - skipping markdown linting")
        print("   Install with: npm install -g markdownlint-cli")

    # Check mkdocs build
    print("\n" + "=" * 60)
    print("Checking mkdocs build...")
    print("=" * 60)

    result = subprocess.run(["mkdocs", "build", "--strict"], capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print("❌ mkdocs build failed:")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        mkdocs_issues = 1
    else:
        print("✅ mkdocs build successful")

    return markdown_issues, mkdocs_issues


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1:
        docs_path = Path(sys.argv[1])
    else:
        docs_path = Path("docs")

    if not docs_path.exists():
        print(f"Error: {docs_path} does not exist")
        sys.exit(1)

    # Lint Python code blocks with md-snakeoil
    python_issues = lint_python_blocks(docs_path)

    # Run markdown and mkdocs linting
    markdown_issues, mkdocs_issues = lint_markdown(docs_path.parent)

    # Final summary
    print(f"\n{'=' * 60}")
    print("Final Summary:")
    print(f"  Python code blocks: {python_issues} issues")
    print(f"  Markdown formatting: {markdown_issues} issues")
    print(f"  MkDocs build: {mkdocs_issues} issues")
    print("=" * 60)

    total_all_issues = python_issues + markdown_issues + mkdocs_issues
    if total_all_issues == 0:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print(f"❌ Total issues: {total_all_issues}")
        sys.exit(1)


if __name__ == "__main__":
    main()
