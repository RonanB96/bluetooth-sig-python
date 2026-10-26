"""Import boundaries from ADR-0002."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

_CONTRACT = ("tools.gss_ir", "tools.gss_ir.v1")
_SOURCES = ("tools.gss_ir.sources",)
_NORMALISER = ("tools.gss_ir.v1", "tools.gss_ir.sources", "tools.gss_ir.normalise")
_GENERATOR = ("tools.gss_ir", "tools.gss_ir.v1", "tools.gss_ir.normalise", "tools.gss_ir.sources")
_EMITTER = ("tools.gss_ir", "tools.gss_ir.v1")


def _module_name(path: Path) -> tuple[str, bool]:
    relative = path.relative_to(ROOT).with_suffix("")
    parts = relative.parts
    is_package = parts[-1] == "__init__"
    if is_package:
        parts = parts[:-1]
    return ".".join(parts), is_package


def _role(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative.startswith("src/bluetooth_sig/"):
        return "runtime"
    if relative in {"tools/gss_ir/v1.py", "tools/gss_ir/__init__.py"}:
        return "contract"
    if "/sources/" in relative:
        return "sources"
    if "/normalise/" in relative:
        return "normaliser"
    if relative.endswith("/generate.py"):
        return "generator"
    if relative.endswith("/emit_cpp.py"):
        return "emitter"
    if relative == "tools/__init__.py":
        return "tools"
    return "unknown"


def _imported(module: str, is_package: bool, node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if not isinstance(node, ast.ImportFrom):
        return []
    if node.level == 0:
        return [node.module or ""]
    base_parts = module.split(".") if is_package else module.split(".")[:-1]
    if node.level > 1:
        base_parts = base_parts[: 1 - node.level]
    if node.module:
        base_parts.extend(node.module.split("."))
    return [".".join(base_parts)]


def _allowed(role: str, imported: str) -> bool:
    top = imported.split(".", 1)[0]
    if role == "runtime":
        return not (imported == "tools" or imported.startswith("tools."))
    if imported == "bluetooth_sig" or imported.startswith("bluetooth_sig."):
        return False
    if top in sys.stdlib_module_names:
        return True
    if role == "contract":
        return imported == "msgspec" or imported.startswith("msgspec.") or imported in _CONTRACT
    if role == "sources":
        return imported == "yaml" or imported.startswith("yaml.") or _under(imported, _SOURCES)
    if role == "normaliser":
        return _under(imported, _NORMALISER)
    if role == "generator":
        return _under(imported, _GENERATOR)
    if role == "emitter":
        return _under(imported, _EMITTER)
    return False


def _under(imported: str, prefixes: tuple[str, ...]) -> bool:
    return any(imported == prefix or imported.startswith(f"{prefix}.") for prefix in prefixes)


def test_python_roles_follow_the_import_table() -> None:
    roots = [ROOT / "tools", ROOT / "src" / "bluetooth_sig"]
    violations: list[str] = []
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            role = _role(path)
            module, is_package = _module_name(path)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                for imported in _imported(module, is_package, node):
                    if imported and not _allowed(role, imported):
                        violations.append(f"{path.relative_to(ROOT)} ({role}) imports {imported}")
    assert violations == []
