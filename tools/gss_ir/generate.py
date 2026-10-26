"""Write canonical IR for every characteristic that is not blacklisted.

A characteristic that cannot be normalised is recorded and generation continues.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tools.gss_ir.normalise import Unsupported, iter_characteristic_paths, normalise_path
from tools.gss_ir.v1 import IR_VERSION, IrDocument, encode_ir


class GenerateError(RuntimeError):
    """The blacklist or the SIG submodule could not be read."""

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


def _load_blacklist(path: Path) -> tuple[str, ...]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise GenerateError(f"blacklist is not JSON: {error}") from error
    except OSError as error:
        raise GenerateError(str(error)) from error
    if not isinstance(loaded, list) or not all(isinstance(item, str) for item in loaded):
        raise GenerateError("blacklist must be a JSON array of identifiers")
    if len(loaded) != len(set(loaded)):
        raise GenerateError("blacklist contains a duplicate identifier")
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


def _error_record(path: Path, root: Path, result: Unsupported) -> dict[str, str]:
    return {
        "identifier": path.stem,
        "source_path": path.resolve().relative_to(root.resolve()).as_posix(),
        "rule": result.rule,
        "detail": result.detail,
    }


def _write_errors(destination: Path, errors: list[dict[str, str]]) -> bytes:
    payload = _canonical_json(sorted(errors, key=lambda item: item["identifier"]))
    output = destination / "generated/errors.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return payload


def generate_characteristics(
    characteristics_path: Path,
    *,
    root: Path | None = None,
    output_root: Path | None = None,
) -> dict[str, bytes]:
    """Write IR for every characteristic outside the blacklist.

    Args:
        characteristics_path: JSON array of characteristic identifiers to skip.
            An empty array tries every characteristic.
        root: Repository root used to read SIG YAML and the submodule commit.
        output_root: Directory that receives ``generated/``. Defaults to ``root``.

    Returns:
        Repository-relative output path to the bytes written there.

    Raises:
        GenerateError: If the blacklist or the SIG submodule commit cannot be read.
    """
    repo = repository_root() if root is None else root
    destination = repo if output_root is None else output_root
    blocked = _load_blacklist(characteristics_path)
    paths = iter_characteristic_paths(repo)
    known = {path.stem for path in paths}
    unknown = next((identifier for identifier in blocked if identifier not in known), None)
    if unknown is not None:
        raise GenerateError(f"blacklist identifier is not a characteristic: {unknown}")
    blocked_ids = set(blocked)
    documents: list[IrDocument] = []
    errors: list[dict[str, str]] = []
    seen_identifiers: dict[str, str] = {}
    seen_uuids: dict[int, str] = {}
    _write_errors(destination, errors)
    for path in paths:
        if path.stem in blocked_ids:
            continue
        result = normalise_path(path, root=repo)
        if isinstance(result, Unsupported):
            errors.append(_error_record(path, repo, result))
            _write_errors(destination, errors)
            continue
        if result.identifier in blocked_ids:
            continue
        previous = seen_identifiers.get(result.identifier)
        if previous is not None:
            errors.append(
                {
                    "identifier": path.stem,
                    "source_path": path.resolve().relative_to(repo.resolve()).as_posix(),
                    "rule": "identifier",
                    "detail": f"duplicate identifier {result.identifier} also read from {previous}",
                }
            )
            _write_errors(destination, errors)
            continue
        previous_uuid = seen_uuids.get(result.uuid)
        if previous_uuid is not None:
            errors.append(
                {
                    "identifier": path.stem,
                    "source_path": path.resolve().relative_to(repo.resolve()).as_posix(),
                    "rule": "characteristic_uuid",
                    "detail": f"duplicate UUID 0x{result.uuid:04X} also used by {previous_uuid}",
                }
            )
            _write_errors(destination, errors)
            continue
        seen_identifiers[result.identifier] = path.stem
        seen_uuids[result.uuid] = result.identifier
        documents.append(result)
    error_payload = _write_errors(destination, errors)
    files: dict[str, bytes] = {"generated/errors.json": error_payload}
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
    files["generated/classification.json"] = _canonical_json(
        {
            "supported": sorted(document.identifier for document in documents),
            "unsupported": sorted(errors, key=lambda item: item["identifier"]),
        }
    )
    for relative, payload in files.items():
        output = destination / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    return files


def main(argv: list[str] | None = None) -> int:
    """Write IR for every characteristic outside the blacklist.

    Args:
        argv: Command arguments, excluding the program name.

    Returns:
        Process status, ``0`` on success and ``1`` on a generate error.
    """
    parser = argparse.ArgumentParser(
        description="Write canonical IR for every GSS characteristic outside the blacklist."
    )
    parser.add_argument("characteristics", type=Path, help="JSON array of identifiers to skip")
    args = parser.parse_args(argv)
    try:
        generate_characteristics(args.characteristics)
    except GenerateError as error:
        print(error.detail)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
