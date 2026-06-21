"""Benchmark cold import startup in isolated subprocesses."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _subprocess_import_ms(import_stmt: str) -> float:
    script = f"""
import sys, time
t0 = time.perf_counter()
{import_stmt}
elapsed_ms = (time.perf_counter() - t0) * 1000
print(f"{{elapsed_ms:.3f}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    return float(result.stdout.strip())


def _subprocess_char_module_count(import_stmt: str) -> int:
    script = f"""
import sys
{import_stmt}
mods = [m for m in sys.modules if m.startswith("bluetooth_sig.gatt.characteristics.")]
print(len(mods))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    return int(result.stdout.strip())


def _subprocess_lazy_characteristic_import_ms() -> float:
    script = """
import bluetooth_sig  # noqa: F401
import time
t0 = time.perf_counter()
from bluetooth_sig.gatt.characteristics import BatteryLevelCharacteristic  # noqa: F401
elapsed_ms = (time.perf_counter() - t0) * 1000
print(f"{elapsed_ms:.3f}")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    return float(result.stdout.strip())


@pytest.mark.benchmark
class TestImportStartupPerformance:
    """Cold import benchmarks (fresh interpreter per iteration)."""

    def test_root_import_time(self, benchmark: Any) -> None:
        """Benchmark import bluetooth_sig in a subprocess."""
        elapsed_ms = benchmark(_subprocess_import_ms, "import bluetooth_sig")
        assert elapsed_ms < 2000.0

    def test_translator_only_import_time(self, benchmark: Any) -> None:
        """Benchmark lightweight translator import path."""
        elapsed_ms = benchmark(
            _subprocess_import_ms,
            "from bluetooth_sig.core.translator import BluetoothSIGTranslator",
        )
        assert elapsed_ms < 2000.0

    def test_root_import_characteristic_module_count(self, benchmark: Any) -> None:
        """Benchmark characteristic module count after root import."""
        count = benchmark(_subprocess_char_module_count, "import bluetooth_sig")
        assert count <= 45


@pytest.mark.benchmark
class TestPrewarmStartupPerformance:
    """Benchmark registry prewarm after lazy import startup."""

    def test_prewarm_registries_wall_time(self, benchmark: Any) -> None:
        """Benchmark full prewarm_registries() wall time."""
        from bluetooth_sig.utils.prewarm import prewarm_registries

        benchmark(prewarm_registries)

    def test_lazy_characteristic_import_after_root(self, benchmark: Any) -> None:
        """Benchmark first lazy characteristic class resolution after root import."""
        elapsed_ms = benchmark(_subprocess_lazy_characteristic_import_ms)
        assert elapsed_ms < 2000.0
