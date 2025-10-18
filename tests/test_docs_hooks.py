"""Unit tests for docs_hooks.on_pre_build.

These tests exercise the pre-build hook's behaviour for diagram generation
and ensure failures surface as errors that will break the docs build.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterable, Mapping, Sequence

import pytest

import docs_hooks


def _completedproc_ok(cmd: Sequence[str], **_kwargs: Mapping[str, object]) -> subprocess.CompletedProcess[str]:
    """Return a CompletedProcess-like object representing success.

    We avoid importing private types from subprocess to keep tests simple.
    """
    return subprocess.CompletedProcess(cmd, 0, stdout="ok", stderr="")


def test_on_pre_build_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """If subprocess.run succeeds for both generation steps, the hook should complete without raising."""

    def _run_success_handler(*a: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raw: object = a[0] if a else []
        if isinstance(raw, (list, tuple)):
            seq = list(raw)  # type: ignore[arg-type]
        else:
            seq = [str(raw)]
        return _completedproc_ok(seq)

    monkeypatch.setattr(subprocess, "run", _run_success_handler)
    # Should not raise
    docs_hooks.on_pre_build(config={})  # type: ignore[attr-defined]


def test_on_pre_build_diagrams_failure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """If the diagrams generation subprocess fails, the hook should fail the build (raise CalledProcessError)."""

    def fake_run(cmd: Iterable[str], **_kwargs: Mapping[str, object]) -> subprocess.CompletedProcess[str]:
        # The second script invocation is generate_diagrams.py; detect by
        # filename and raise a CalledProcessError to simulate failure.
        if isinstance(cmd, (list, tuple)) and cmd and "generate_diagrams.py" in str(cmd[-1]):
            raise subprocess.CalledProcessError(returncode=2, cmd=list(cmd), output="out", stderr="err")
        if isinstance(cmd, (list, tuple)):
            seq = list(cmd)
        else:
            seq = [str(cmd)]
        return _completedproc_ok(seq)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        docs_hooks.on_pre_build(config={})  # type: ignore[attr-defined]
