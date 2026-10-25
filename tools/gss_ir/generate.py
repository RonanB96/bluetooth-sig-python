"""Write canonical IR and the provenance manifest for selected characteristics."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tools.gss_ir.normalise import Unsupported, iter_characteristic_paths, normalise_identifier, normalise_path
from tools.gss_ir.v1 import IR_VERSION, IrDocument, encode_ir


class GenerateError(RuntimeError):
    """A selected characteristic could not be written."""

    def __init__(self, detail: str) -> None:
        """Initialise the error with a diagnostic detail."""
        super().__init__(detail)
        self.detail = detail


def repository_root() -> Path:
    """Return the repository root that contains this file.

    Returns:
        Absolute repository path.
    """
    return Path(__file__).resolve().parents[2]


def _canonical_json(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _load_characteristics(path: Path) -> tuple[str, ...]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise GenerateError(f"characteristic list is not JSON: {error}") from error
    except OSError as error:
        raise GenerateError(str(error)) from error
    if not isinstance(loaded, list) or not loaded or not all(isinstance(item, str) for item in loaded):
        raise GenerateError("characteristic list must be a non-empty JSON array of identifiers")
    if len(loaded) != len(set(loaded)):
        raise GenerateError("characteristic list contains a duplicate identifier")
    return tuple(loaded)


def _sig_commit(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root / "bluetooth_sig"), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise GenerateError(f"SIG submodule commit is unavailable: {error}") from error
    commit = completed.stdout.strip()
    if not commit:
        raise GenerateError("SIG submodule commit is empty")
    return commit


def _classification(root: Path) -> bytes:
    supported: list[str] = []
    unsupported: list[dict[str, str]] = []
    for path in iter_characteristic_paths(root):
        result = normalise_path(path, root=root)
        source_path = path.resolve().relative_to(root.resolve()).as_posix()
        if isinstance(result, Unsupported):
            unsupported.append(
                {
                    "identifier": path.stem,
                    "source_path": source_path,
                    "rule": result.rule,
                    "detail": result.detail,
                }
            )
        else:
            supported.append(result.identifier)
    payload = {
        "supported": sorted(supported),
        "unsupported": sorted(unsupported, key=lambda item: item["identifier"]),
    }
    return _canonical_json(payload)


def _documents(identifiers: tuple[str, ...], root: Path) -> tuple[IrDocument, ...]:
    documents: list[IrDocument] = []
    for identifier in identifiers:
        result = normalise_identifier(identifier, root=root)
        if isinstance(result, Unsupported):
            raise GenerateError(f"{identifier} is unsupported by {result.rule}: {result.detail}")
        documents.append(result)
    return tuple(documents)


def generate_characteristics(
    characteristics_path: Path,
    *,
    root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, bytes]:
    """Write IR, the manifest, and the corpus classification for selected characteristics.

    Args:
        characteristics_path: JSON array of characteristic identifiers.
        root: Repository root used to read SIG YAML and the submodule commit.
        output_root: Directory that receives ``generated/``. Defaults to ``root``.

    Returns:
        Repository-relative output path to the bytes written there.

    Raises:
        GenerateError: If a selected characteristic cannot be written.
    """
    repo = repository_root() if root is None else root
    destination = repo if output_root is None else output_root
    identifiers = _load_characteristics(characteristics_path)
    documents = _documents(identifiers, repo)
    files: dict[str, bytes] = {}
    manifest_files: list[dict[str, str]] = []
    for document in documents:
        relative = f"generated/ir/{IR_VERSION}/{document.identifier}.json"
        payload = encode_ir(document)
        files[relative] = payload
        manifest_files.append(
            {
                "path": relative,
                "source_path": document.provenance.source_path,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    manifest = _canonical_json(
        {
            "sig_commit": _sig_commit(repo),
            "schema_version": IR_VERSION,
            "files": sorted(manifest_files, key=lambda item: item["path"]),
        }
    )
    files["generated/MANIFEST.json"] = manifest
    files["generated/classification.json"] = _classification(repo)
    for relative, payload in files.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    return files


def main(argv: list[str] | None = None) -> int:
    """Write IR for the listed characteristics.

    Args:
        argv: Command arguments, excluding the program name.

    Returns:
        Process status, ``0`` on success and ``1`` on a generate error.
    """
    parser = argparse.ArgumentParser(description="Write canonical IR for selected GSS characteristics.")
    parser.add_argument("characteristics", type=Path)
    args = parser.parse_args(argv)
    try:
        generate_characteristics(args.characteristics)
    except GenerateError as error:
        print(error.detail)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
