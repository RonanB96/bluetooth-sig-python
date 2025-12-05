"""Generate the code reference pages and navigation.

This script automatically generates API reference documentation for all Python modules
in the src/bluetooth_sig/ directory. It creates a page for each module with the
appropriate ::: directive for mkdocstrings to process.

The generated pages are placed in the reference/bluetooth_sig/ directory and organized
to match the source code structure. Material theme's automatic navigation handles
the sidebar tree structure.

PERFORMANCE: Implements timestamp-based incremental generation. Only regenerates .md
files when the source .py file is newer than the cached .md file in .cache/gen_ref/.
This significantly speeds up dirty builds (mkdocs build --dirty) by skipping unchanged files.
"""

from __future__ import annotations

from pathlib import Path

import mkdocs_gen_files

root = Path(__file__).parent.parent
src = root / "src"
cache_dir = root / ".cache" / "gen_ref"

# Create cache directory if it doesn't exist
cache_dir.mkdir(parents=True, exist_ok=True)

# Build a tree structure to track what modules/packages exist
module_tree: dict[tuple, list[tuple]] = {}  # parent -> list of children
packages_set: set[tuple] = set()  # Track all packages (even if they have no children)

generated_count = 0
skipped_count = 0

# First pass: collect all modules and build tree structure
all_modules = []
for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    parts = tuple(module_path.parts)

    # Skip internal/private modules
    if any(part.startswith("_") and part not in ("__init__", "__main__") for part in parts):
        continue

    if parts[-1] == "__init__":
        parts = parts[:-1]
        packages_set.add(parts)  # Mark this as a package
    elif parts[-1] == "__main__":
        continue

    if not parts:
        continue

    all_modules.append((parts, path))

    # Track parent-child relationships for index pages
    if len(parts) > 1:
        parent = parts[:-1]
        if parent not in module_tree:
            module_tree[parent] = []
        module_tree[parent].append(parts)

# Second pass: generate documentation
for parts, path in all_modules:
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src).with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    if module_path.name == "__init__":
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    # Check if regeneration is needed
    cache_path = cache_dir / full_doc_path
    needs_regeneration = True

    if cache_path.exists():
        source_mtime = path.stat().st_mtime
        cache_mtime = cache_path.stat().st_mtime
        if source_mtime <= cache_mtime:
            needs_regeneration = False
            skipped_count += 1

    # Generate content
    ident = ".".join(parts)
    is_index = doc_path.name == "index.md"

    if is_index:
        # Index pages: show package docstring + list children
        # Add breadcrumb navigation for non-root packages
        if parts:
            depth = len(parts)
            if depth > 1:
                parent_name = parts[-2]
                # Calculate relative path based on depth
                back_to_parent = "../index.md"
                back_to_root = "../" * depth + "index.md"
                content = (
                    f"**[⬆️ Back to {parent_name}]({back_to_parent})** | "
                    f"**[🏠 API Reference]({back_to_root})**\n\n---\n\n"
                )
            else:
                # Top-level package (bluetooth_sig)
                content = "**[🏠 API Reference](../index.md)**\n\n---\n\n"
        else:
            content = ""

        content += f"::: {ident}\n"
        content += "    options:\n"
        content += "      members: false\n"
        content += "      show_bases: false\n"
        content += "      show_source: false\n\n"

        # Get children of this package
        children = module_tree.get(parts, [])
        if children:
            # Separate into subpackages and modules
            subpackages = []
            modules = []
            for child in sorted(children):
                if child in packages_set:
                    subpackages.append(child[-1])
                else:
                    modules.append(child[-1])

            if subpackages or modules:
                content += "## Contents\n\n"

            if subpackages:
                content += "### 📦 Subpackages\n\n"
                for pkg in subpackages:
                    content += f"- **[{pkg}]({pkg}/index.md)**\n"
                content += "\n"

            if modules:
                content += "### 📄 Modules\n\n"
                for mod in modules:
                    content += f"- **[{mod}]({mod}.md)**\n"
                content += "\n"
    else:
        # Regular module pages: add navigation back to parent + full API documentation
        # Add back navigation to parent package index
        depth = len(parts)
        if depth > 1:
            parent_name = parts[-2]
            back_to_root = "../" * depth + "index.md"
            content = (
                f"**[⬆️ Back to {parent_name}](index.md)** | "
                f"**[📁 Browse {parent_name}](index.md#contents)** | "
                f"**[🏠 API Reference]({back_to_root})**\n\n---\n\n"
            )
        else:
            # Top-level module
            content = "**[🏠 API Reference](../index.md)**\n\n---\n\n"

        content += f"::: {ident}\n"

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(content)

    mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))

    if needs_regeneration:
        generated_count += 1
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(content)

# Print generation statistics for visibility
print(f"gen_ref_pages: Generated {generated_count} files, skipped {skipped_count} unchanged files")
