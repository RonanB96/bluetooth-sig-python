#!/usr/bin/env python3
"""Detect changed documentation files for selective Playwright testing.

This script analyzes git diffs to determine which documentation pages need
testing, mapping source files to their built HTML equivalents.

Usage:
    python scripts/detect_changed_docs.py --base origin/main --head HEAD
    python scripts/detect_changed_docs.py --base main --head feature-branch --verbose

Output:
    JSON array of HTML file paths to test:
        ["tutorials/index.html", "api/bluetooth_sig/core/translator.html"]  # Specific files
        ["ALL"]                                                              # Test everything
        []                                                                   # No docs changed

When comprehensive testing is triggered:
    - Changes to docs/source/conf.py (Sphinx configuration)
    - Changes to docs/source/_templates/ (affects all pages)
    - Changes to docs/source/_static/*.{css,js} (global styling)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_git_command(cmd: list[str]) -> str:
    """Execute git command and return stdout.

    Args:
        cmd: Git command and arguments

    Returns:
        Command stdout as string

    Raises:
        SystemExit: If git command fails
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_changed_files(base: str, head: str) -> list[str]:
    """Get list of changed files between two git refs.

    Args:
        base: Base git ref (e.g., 'origin/main')
        head: Head git ref (e.g., 'HEAD')

    Returns:
        List of changed file paths relative to repository root
    """
    output = run_git_command(["git", "diff", "--name-only", f"{base}...{head}"])
    if not output:
        return []
    return output.split("\n")


def map_source_to_html(source_path: str) -> list[str]:
    """Map documentation source file to built HTML path(s).

    Args:
        source_path: Relative path to source file (e.g., 'docs/source/tutorials/index.md')

    Returns:
        List of HTML file paths to test (relative to docs/build/html/)
        Empty list if file doesn't map to testable HTML

    Examples:
        'docs/source/tutorials/index.md' -> ['tutorials/index.html']
        'docs/source/api/index.rst' -> ['api/index.html']
        'src/bluetooth_sig/core/translator.py' -> ['api/bluetooth_sig/core/translator.html']
    """
    path = Path(source_path)

    # Handle docs/source/ markdown and RST files
    if path.parts[:2] == ("docs", "source"):
        relative = Path(*path.parts[2:])  # Remove 'docs/source/' prefix

        # Skip non-documentation files
        if path.suffix not in {".md", ".rst", ".py"}:
            return []

        # Map to HTML: change extension and keep directory structure
        html_path = relative.with_suffix(".html")
        return [str(html_path)]

    # Handle Python source files that AutoAPI generates docs for
    if path.parts[0] == "src" and path.suffix == ".py":
        # AutoAPI generates: src/bluetooth_sig/core/translator.py
        #                 -> api/bluetooth_sig/core/translator.html
        # But __init__.py files map to index.html:
        #                    src/bluetooth_sig/__init__.py
        #                 -> api/bluetooth_sig/index.html
        relative = Path(*path.parts[1:])  # Remove 'src/' prefix

        if path.name == "__init__.py":
            # Package __init__.py maps to index.html in that directory
            html_path = Path("api") / relative.parent / "index.html"
        else:
            # Regular Python files map to .html with same name
            html_path = Path("api") / relative.with_suffix(".html")

        return [str(html_path)]

    return []


def should_test_all(changed_files: list[str]) -> bool:
    """Determine if all documentation pages should be tested.

    Args:
        changed_files: List of changed file paths

    Returns:
        True if comprehensive testing needed, False otherwise

    Comprehensive testing is triggered by:
        - Changes to conf.py (Sphinx configuration)
        - Changes to documentation templates
        - Changes to static assets that affect all pages
    """
    for file_path in changed_files:
        path = Path(file_path)

        # Sphinx configuration change affects all pages
        if path.name == "conf.py" and "docs" in path.parts:
            return True

        # Template changes affect all pages
        if "_templates" in path.parts:
            return True

        # Static asset changes that affect layout/styling
        if "_static" in path.parts and path.suffix in {".css", ".js"}:
            return True

    return False


def main() -> None:
    """Main entry point for change detection script."""
    parser = argparse.ArgumentParser(
        description="Detect changed documentation files for selective testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base",
        default="origin/main",
        help="Base git ref for comparison (default: origin/main)",
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="Head git ref for comparison (default: HEAD)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose debugging information",
    )

    args = parser.parse_args()

    # Get changed files
    changed_files = get_changed_files(args.base, args.head)

    if args.verbose:
        print(f"📋 Found {len(changed_files)} changed files:", file=sys.stderr)
        for file in changed_files[:10]:
            print(f"   - {file}", file=sys.stderr)
        if len(changed_files) > 10:
            print(f"   ... and {len(changed_files) - 10} more", file=sys.stderr)

    # Check if comprehensive testing needed
    if should_test_all(changed_files):
        if args.verbose:
            print("🔄 Comprehensive testing triggered (conf.py or template changed)", file=sys.stderr)
        print(json.dumps(["ALL"]))
        return

    # Map to HTML files
    html_files: set[str] = set()
    for changed_file in changed_files:
        mapped = map_source_to_html(changed_file)
        html_files.update(mapped)

    # Output results
    if not html_files:
        # No documentation-related changes detected - skip all tests
        if args.verbose:
            print("\n📊 No documentation changes detected", file=sys.stderr)
        print(json.dumps([]))
        return

    result = sorted(html_files)

    if args.verbose:
        print("\n📊 Testing strategy:", file=sys.stderr)
        print(f"   → {len(result)} specific pages:", file=sys.stderr)
        for file in result[:10]:
            print(f"      - {file}", file=sys.stderr)
        if len(result) > 10:
            print(f"      ... and {len(result) - 10} more", file=sys.stderr)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
