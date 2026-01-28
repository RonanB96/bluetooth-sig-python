"""Generate class and dependency diagrams used by the docs.

This script is intended to be run as a mkdocs pre-build hook (see
`docs_hooks.py`). It will attempt to:

-- generate PlantUML (.puml) for selected packages using pyreverse (pylint.pyreverse),
- render those .puml files to SVG using PlantUML (if available), and
- generate import/dependency graphs using pydeps (rendered as SVG).

The script is conservative by default: missing optional tools will trigger
warnings and the script will continue. Set STRICT_DIAGRAMS=1 to make the
script return non-zero on missing tools or rendering failures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, cast

DEFAULT_SRC = Path(__file__).parent.parent / "src"
DEFAULT_DOCS_DIAGRAMS = Path(__file__).parent.parent / "docs" / "source" / "diagrams"
DEFAULT_CACHE_DIR = DEFAULT_DOCS_DIAGRAMS / ".cache"
DEFAULT_CACHE_FILE = DEFAULT_CACHE_DIR / "diagrams_cache.json"


def _try_pyreverse(src_path: Path, package: str) -> dict[str, str] | None:
    """Attempt to generate PlantUML using pyreverse (pylint).

    This function prefers a module invocation (``python -m pylint.pyreverse``)
    and falls back to a system ``pyreverse`` command when available. The
    command writes PUML files into the current working directory so we run it
    in a temporary directory and then return the generated content on success.

    Returns a dict with 'classes' and 'packages' PUML content on success,
    or ``None`` when pyreverse is not available or when execution fails.
    """
    # pyreverse writes files like classes_<package>.puml and packages_<package>.puml into the cwd. Run it
    # in a temporary directory and read back the produced files.
    tmp = tempfile.TemporaryDirectory()
    try:
        # Prefer module invocation; this works when pylint is installed in the
        # active Python environment.
        cmd_module = [sys.executable, "-m", "pylint.pyreverse", "-o", "puml", "-p", package, str(src_path)]
        try:
            subprocess.run(cmd_module, check=True, capture_output=True, text=True, cwd=tmp.name)
        except subprocess.CalledProcessError:
            # Module invocation failed: try a CLI on PATH if present.
            if shutil.which("pyreverse"):
                cmd_cli = ["pyreverse", "-o", "puml", "-p", package, str(src_path)]
                try:
                    subprocess.run(cmd_cli, check=True, capture_output=True, text=True, cwd=tmp.name)
                except subprocess.CalledProcessError as ex:
                    print(f"Warning: pyreverse CLI failed for {package}: {ex}")
                    return None
            else:
                return None

        # Read the generated PUML files
        tmp_path = Path(tmp.name)
        classes_file = tmp_path / f"classes_{package}.puml"
        packages_file = tmp_path / f"packages_{package}.puml"

        result: dict[str, str] = {}
        if classes_file.exists():
            result["classes"] = classes_file.read_text(encoding="utf8")
        if packages_file.exists():
            result["packages"] = packages_file.read_text(encoding="utf8")

        return result if result else None
    finally:
        tmp.cleanup()


def write_puml(content: str, out_path: Path) -> None:
    """Write PlantUML content to `out_path`, creating parent directories.

    Parameters
    ----------
    content:
        PlantUML text to write.
    out_path:
        Path to the target .puml file.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf8")


def _compute_package_fingerprint(pkg_src: Path) -> str:
    """Compute a fast fingerprint for a package based on file mtimes and sizes.

    The fingerprint is cheap to compute and avoids reading file contents while
    still changing whenever a source file is modified or its size changes.
    """
    h = hashlib.sha256()
    if not pkg_src.exists():
        h.update(b"<missing>")
        return h.hexdigest()

    # Sort files for deterministic fingerprints
    for f in sorted(pkg_src.rglob("*.py")):
        try:
            st = f.stat()
        except OSError:
            continue
        # relative path + mtime_ns + size
        h.update(str(f.relative_to(pkg_src)).encode("utf8"))
        h.update(str(st.st_mtime_ns).encode("utf8"))
        h.update(str(st.st_size).encode("utf8"))

    return h.hexdigest()


def _load_cache(cache_file: Path) -> dict[str, dict[str, Any]]:
    """Load the diagrams cache from disk.

    The cache maps package -> metadata (fingerprint, timestamps, etc.).
    If the cache file cannot be read it is treated as empty.
    """
    if not cache_file.exists():
        return {}
    try:
        data = json.loads(cache_file.read_text(encoding="utf8"))
        if isinstance(data, dict):
            # JSON deserialization returns 'Any' — cast to the expected cache
            # shape so static type checkers understand the return value.
            return cast("dict[str, dict[str, Any]]", data)
        return {}
    except (json.JSONDecodeError, OSError, ValueError):
        return {}


def _save_cache(cache_file: Path, cache: dict[str, dict[str, Any]]) -> None:
    """Persist the diagrams cache to disk."""
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(cache, indent=2), encoding="utf8")


def generate_class_puml(src_path: Path, package: str, out_puml_dir: Path) -> bool:
    """Generate PlantUML (.puml) files for package (both classes and packages diagrams).

    Returns True if PUML files were created, False otherwise.
    """
    # Try pyreverse (pylint) first as it does not require modifying
    # production source. pyreverse is a robust, non-invasive analyzer.
    puml_contents = _try_pyreverse(src_path, package)
    if puml_contents is not None:
        out_puml_dir.mkdir(parents=True, exist_ok=True)
        success = False
        if "classes" in puml_contents:
            write_puml(puml_contents["classes"], out_puml_dir / f"classes_{package}.puml")
            success = True
        if "packages" in puml_contents:
            write_puml(puml_contents["packages"], out_puml_dir / f"packages_{package}.puml")
            success = True
        return success

    print(f"Warning: pyreverse not available, could not generate PUML for {package}")
    return False


def render_puml_to_svg(puml_dir: Path, svg_out_dir: Path) -> bool:
    """Attempt to render all .puml files in puml_dir to SVG.

    Returns True when all renderings completed; False if PlantUML is not
    available or any rendering failed.
    """
    svg_out_dir.mkdir(parents=True, exist_ok=True)

    plantuml_cmd = shutil.which("plantuml")
    if not plantuml_cmd:
        print("Warning: PlantUML not found (no 'plantuml' in PATH and PLANTUML_JAR unset)")
        return False

    success = True
    for puml_file in puml_dir.glob("*.puml"):
        cmd = [plantuml_cmd, "-tsvg", "-o", str(svg_out_dir), str(puml_file)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as ex:
            print(f"Warning: plantuml CLI failed to render {puml_file}: {ex}")
            success = False

    return success


def generate_pydeps_svg(package: str, out_svg: Path, max_bacon: int = 2) -> bool:
    """Run pydeps to create an import/dependency SVG for a package.

    Returns True on success, False on failure.
    """
    out_svg.parent.mkdir(parents=True, exist_ok=True)

    # pydeps uses Graphviz to render SVGs (calls `dot`). Detect missing
    # Graphviz early and provide an actionable error message rather than a
    # cryptic subprocess failure.
    if shutil.which("dot") is None:
        print(
            "Error: Graphviz 'dot' executable not found. "
            "pydeps requires Graphviz to render SVGs. "
            "Install Graphviz (e.g. 'apt-get install graphviz' or 'brew install graphviz')"
        )
        return False

    # Set PYTHONPATH to include the src directory so pydeps can find the package
    src_dir = Path(__file__).parent.parent / "src"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_dir)

    # Try python -m pydeps
    cmd_module = [
        sys.executable,
        "-m",
        "pydeps",
        package,
        "-T",
        "svg",
        "-o",
        str(out_svg),
        "--max-bacon",
        str(max_bacon),
        "--noshow",
    ]
    try:
        subprocess.run(cmd_module, check=True, capture_output=True, text=True, env=env, cwd=str(src_dir))
        return True
    except subprocess.CalledProcessError:
        # python -m pydeps failed (module missing or errored); try CLI
        pass

    if shutil.which("pydeps"):
        cmd = ["pydeps", package, "-T", "svg", "-o", str(out_svg), "--max-bacon", str(max_bacon), "--noshow"]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, env=env, cwd=str(src_dir))
            return True
        except subprocess.CalledProcessError as ex:
            print(f"Warning: pydeps CLI failed for {package}: {ex}")
            return False

    print("Warning: pydeps not found on PATH and module import failed")
    return False


def _find_packages_in_src(src_root: Path) -> list[str]:
    """Find top-level packages in a `src/` layout.

    Returns package names (module import names) discovered under `src/`.
    """
    pkgs: list[str] = []
    if not src_root.exists():
        return pkgs
    for item in sorted(src_root.iterdir()):
        if item.is_dir() and (item / "__init__.py").exists():
            pkgs.append(item.name)
    return pkgs


def generate_all_diagrams(
    *,
    src_root: Path = DEFAULT_SRC,
    docs_diagrams: Path = DEFAULT_DOCS_DIAGRAMS,
    packages: list[str] | None = None,
    render: bool = True,
    cache_file: Path | None = None,
    force: bool = False,
    pydeps_max_bacon: int = 2,
) -> tuple[int, dict[str, dict[str, bool]]]:
    """Generate diagrams for the given packages.

    Returns a tuple (exit_code, results) where results maps package -> {
    "puml": bool, "puml_rendered": bool, "pydeps": bool }.
    exit_code is 0 when at least one artifact was produced; non-zero when
    nothing was produced or strict mode is enabled and failures occurred.
    """
    if packages is None:
        packages = _find_packages_in_src(src_root)
    if not packages:
        print(f"No top-level packages found under {src_root}; nothing to diagram")
        strict = os.environ.get("STRICT_DIAGRAMS", "0") == "1"
        return (1 if strict else 0), {}

    # Load / prepare cache
    if cache_file is None:
        cache_file = DEFAULT_CACHE_FILE
    cache = _load_cache(cache_file)

    results: dict[str, dict[str, bool]] = {}
    any_artifact = False
    failures: dict[str, list[str]] = {}

    for package in packages:
        print(f"Processing package: {package}")
        pkg_src = src_root / package
        out_puml_dir = docs_diagrams / "puml"
        out_svg_dir = docs_diagrams / "svg"
        out_pydeps_svg = docs_diagrams / "deps" / f"{package}.svg"

        # Fast fingerprint to detect whether anything in the package has
        # changed since the last generation. This keeps incremental builds
        # fast by avoiding expensive external tools when nothing changed.
        fingerprint = _compute_package_fingerprint(pkg_src)
        cache_entry = cache.get(package, {})

        # Expected artifact paths
        puml_paths = [out_puml_dir / f"classes_{package}.puml", out_puml_dir / f"packages_{package}.puml"]
        svg_paths = [out_svg_dir / f"classes_{package}.svg", out_svg_dir / f"packages_{package}.svg"]

        existing_puml = [p for p in puml_paths if p.exists()]
        existing_svg = [s for s in svg_paths if s.exists()]
        existing_pydeps = out_pydeps_svg.exists()

        # If nothing changed and all artifacts exist, skip everything for this
        # package to save time. Cache contains previous fingerprint.
        if (
            not force
            and cache_entry.get("fingerprint") == fingerprint
            and existing_puml
            and existing_svg
            and existing_pydeps
        ):
            print(f"Skipping {package}: no changes detected (fingerprint match)")
            results[package] = {"puml": True, "puml_rendered": True, "pydeps": True}
            any_artifact = True
            continue

        # Decide whether to run pyreverse (PUML generation)
        should_generate_puml = force or not bool(existing_puml) or cache_entry.get("fingerprint") != fingerprint
        if should_generate_puml:
            print(f"Generating PUML for {package} (pyreverse)")
            made_puml = generate_class_puml(pkg_src, package, out_puml_dir)
        else:
            made_puml = bool(existing_puml)

        # Decide whether to render PUML -> SVG. Re-render when PUML files are
        # newer than existing SVGs, when any SVG is missing, or when forced.
        made_puml_rendered = False
        if render:
            if made_puml:
                # Use mtimes to determine staleness
                puml_mtime = max((p.stat().st_mtime_ns for p in existing_puml), default=0)
                svg_mtime = min((s.stat().st_mtime_ns for s in existing_svg), default=0)
                render_needed = force or (not existing_svg) or (puml_mtime > svg_mtime)
            # No newly generated puml; render only if some puml exists and
            # is newer than SVGs or missing SVGs
            elif existing_puml:
                puml_mtime = max(p.stat().st_mtime_ns for p in existing_puml)
                svg_mtime = min((s.stat().st_mtime_ns for s in existing_svg), default=0)
                render_needed = force or (not existing_svg) or (puml_mtime > svg_mtime)
            else:
                render_needed = False

            if render_needed:
                print(f"Rendering PUML -> SVG for {package} (PlantUML)")
                made_puml_rendered = render_puml_to_svg(out_puml_dir, out_svg_dir)
            else:
                made_puml_rendered = bool(existing_svg)

        # Decide whether to run pydeps (dependency graph)
        should_generate_pydeps = force or (cache_entry.get("fingerprint") != fingerprint) or not existing_pydeps
        if should_generate_pydeps:
            print(f"Generating pydeps SVG for {package}")
            # Pass the pydeps 'max_bacon' argument positionally to stay
            # compatible with test doubles that accept a third positional
            # parameter rather than a keyword argument.
            made_pydeps = generate_pydeps_svg(package, out_pydeps_svg, pydeps_max_bacon)
        else:
            made_pydeps = existing_pydeps

        results[package] = {
            "puml": made_puml,
            "puml_rendered": made_puml_rendered,
            "pydeps": made_pydeps,
        }
        if made_puml or made_puml_rendered or made_pydeps:
            any_artifact = True

        # Update cache for this package so future runs can skip unchanged
        cache[package] = {
            "fingerprint": fingerprint,
            "artifacts": {
                "puml": bool(made_puml),
                "puml_rendered": bool(made_puml_rendered),
                "pydeps": bool(made_pydeps),
            },
            "timestamp": int(time.time()),
        }

        # Track per-package failures so strict mode can fail when any
        # required artifact is missing. In strict mode we require:
        #   - puml must be generated
        #   - pydeps must succeed
        #   - if render is requested: puml_rendered must succeed
        pkg_failures: list[str] = []
        if not made_puml:
            pkg_failures.append("puml")
        if not made_pydeps:
            pkg_failures.append("pydeps")
        if render and not made_puml_rendered:
            pkg_failures.append("puml_rendered")
        if pkg_failures:
            failures[package] = pkg_failures

    strict = os.environ.get("STRICT_DIAGRAMS", "0") == "1"

    if strict and failures:
        # In strict mode any per-package failure should cause the overall
        # diagrams generation to fail. Provide a concise summary to help
        # maintainers triage the problem quickly.
        print("Error: Diagram generation failed for packages:")
        for pkg, missing in failures.items():
            print(f"  - {pkg}: missing/failed: {', '.join(missing)}")
        return 1, results

    if any_artifact:
        # Persist cache so subsequent incremental builds are faster
        _save_cache(cache_file, cache)
        return 0, results

    # nothing produced: if strict -> error, else return non-zero but still
    # allow mkdocs pre-build to continue if not strict (docs_hooks controls
    # whether the exception propagates).
    _save_cache(cache_file, cache)
    return (1 if strict else 0), results


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint — generate diagrams and return an exit code.

    The function is kept intentionally simple: it parses a small set of
    command-line arguments and delegates to :func:`generate_all_diagrams`.
    """
    parser = argparse.ArgumentParser(description="Generate docs diagrams (pyreverse + pydeps)")
    parser.add_argument("--src", type=Path, default=DEFAULT_SRC, help="Path to source root (default: src)")
    parser.add_argument(
        "--out", type=Path, default=DEFAULT_DOCS_DIAGRAMS, help="Output folder for diagrams under docs/"
    )
    parser.add_argument(
        "--package",
        "-p",
        action="append",
        help="Package(s) to document (may be provided multiple times); default: discover under src/",
    )
    parser.add_argument("--no-render", action="store_true", help="Do not attempt to render PUML to SVG")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration of all diagrams ignoring any cached results",
    )
    parser.add_argument(
        "--pydeps-max-bacon",
        type=int,
        default=2,
        help="pydeps --max-bacon (default: 2). Lower values are faster",
    )
    parser.add_argument(
        "--cache-file",
        type=Path,
        default=DEFAULT_CACHE_FILE,
        help="Path to the diagrams cache file (default: docs/diagrams/.cache/diagrams_cache.json)",
    )

    args = parser.parse_args(argv)

    exit_code, results = generate_all_diagrams(
        src_root=args.src,
        docs_diagrams=args.out,
        packages=args.package,
        render=not args.no_render,
        cache_file=args.cache_file,
        force=args.force,
        pydeps_max_bacon=args.pydeps_max_bacon,
    )

    # Summary
    print("Diagram generation summary:")
    for pkg, info in results.items():
        print(f"  {pkg}: puml={info['puml']} puml_rendered={info['puml_rendered']} pydeps={info['pydeps']}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
