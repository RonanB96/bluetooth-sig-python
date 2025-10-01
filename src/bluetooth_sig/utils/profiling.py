"""Profiling and performance measurement utilities for Bluetooth SIG library."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

T = TypeVar("T")


@dataclass
class TimingResult:
    """Result of a timing measurement."""

    operation: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    per_second: float

    def __str__(self) -> str:
        """Format timing result as human-readable string."""
        return (
            f"{self.operation}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total time: {self.total_time:.4f}s\n"
            f"  Average:    {self.avg_time*1000:.4f}ms per operation\n"
            f"  Min:        {self.min_time*1000:.4f}ms\n"
            f"  Max:        {self.max_time*1000:.4f}ms\n"
            f"  Throughput: {self.per_second:.0f} ops/sec"
        )


@dataclass
class ProfilingSession:
    """Track multiple profiling results in a session."""

    name: str
    results: list[TimingResult] = field(default_factory=list)

    def add_result(self, result: TimingResult) -> None:
        """Add a timing result to the session."""
        self.results.append(result)

    def __str__(self) -> str:
        """Format session results as human-readable string."""
        lines = [f"=== {self.name} ===", ""]
        for result in self.results:
            lines.append(str(result))
            lines.append("")
        return "\n".join(lines)


@contextmanager
def timer(operation: str = "operation"):
    """Context manager for timing a single operation.

    Args:
        operation: Name of the operation being timed

    Yields:
        Dictionary that will contain 'elapsed' key with timing result

    Example:
        >>> with timer("parse") as t:
        ...     parse_characteristic(data)
        >>> print(f"Elapsed: {t['elapsed']:.4f}s")
    """
    timing: dict[str, float] = {}
    start = time.perf_counter()
    try:
        yield timing
    finally:
        timing["elapsed"] = time.perf_counter() - start


def benchmark_function(
    func: Callable[[], T],
    iterations: int = 1000,
    operation: str = "function",
) -> TimingResult:
    """Benchmark a function by running it multiple times.

    Args:
        func: Function to benchmark (should take no arguments)
        iterations: Number of times to run the function
        operation: Name of the operation for reporting

    Returns:
        TimingResult with detailed performance metrics

    Example:
        >>> result = benchmark_function(
        ...     lambda: translator.parse_characteristic("2A19", b"\\x64"),
        ...     iterations=10000,
        ...     operation="Battery Level parsing"
        ... )
        >>> print(result)
    """
    times: list[float] = []

    # Warmup run
    func()

    # Timed runs
    start_total = time.perf_counter()
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    total_time = time.perf_counter() - start_total

    avg_time = total_time / iterations
    min_time = min(times)
    max_time = max(times)
    per_second = iterations / total_time if total_time > 0 else 0

    return TimingResult(
        operation=operation,
        iterations=iterations,
        total_time=total_time,
        avg_time=avg_time,
        min_time=min_time,
        max_time=max_time,
        per_second=per_second,
    )


def compare_implementations(
    implementations: dict[str, Callable[[], Any]],
    iterations: int = 1000,
) -> dict[str, TimingResult]:
    """Compare performance of multiple implementations.

    Args:
        implementations: Dict mapping implementation name to callable
        iterations: Number of times to run each implementation

    Returns:
        Dictionary mapping implementation names to their TimingResults

    Example:
        >>> results = compare_implementations({
        ...     "manual": lambda: manual_parse(data),
        ...     "sig_lib": lambda: translator.parse_characteristic("2A19", data)
        ... }, iterations=10000)
        >>> for name, result in results.items():
        ...     print(f"{name}: {result.avg_time*1000:.4f}ms")
    """
    results: dict[str, TimingResult] = {}
    for name, func in implementations.items():
        results[name] = benchmark_function(func, iterations, name)
    return results


def format_comparison(
    results: dict[str, TimingResult], baseline: str | None = None
) -> str:
    """Format comparison results as a human-readable table.

    Args:
        results: Dictionary of timing results
        baseline: Optional name of baseline implementation for comparison

    Returns:
        Formatted string with comparison table
    """
    if not results:
        return "No results to display"

    lines = ["Performance Comparison:", "=" * 80]

    # Header
    lines.append(
        f"{'Implementation':<30} {'Avg Time':<15} "
        f"{'Throughput':<20} {'vs Baseline'}"
    )
    lines.append("-" * 80)

    baseline_time = None
    if baseline and baseline in results:
        baseline_time = results[baseline].avg_time

    for name, result in results.items():
        avg_str = f"{result.avg_time*1000:.4f}ms"
        throughput_str = f"{result.per_second:.0f} ops/sec"

        if baseline_time and name != baseline:
            ratio = result.avg_time / baseline_time
            if ratio < 1:
                comparison = f"{1/ratio:.2f}x faster"
            else:
                comparison = f"{ratio:.2f}x slower"
        elif name == baseline:
            comparison = "(baseline)"
        else:
            comparison = "-"

        lines.append(f"{name:<30} {avg_str:<15} {throughput_str:<20} {comparison}")

    return "\n".join(lines)
