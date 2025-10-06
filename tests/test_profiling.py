"""Tests for profiling utilities."""

from __future__ import annotations

import time

from bluetooth_sig.utils.profiling import (
    ProfilingSession,
    TimingResult,
    benchmark_function,
    compare_implementations,
    format_comparison,
    timer,
)


class TestTimer:
    """Test the timer context manager."""

    def test_timer_basic(self):
        """Test basic timer functionality."""
        with timer("test_operation") as t:
            time.sleep(0.01)  # Sleep for 0.01 seconds

        assert "elapsed" in t
        assert t["elapsed"] >= 0.01
        assert t["elapsed"] < 0.05  # Should complete quickly

    def test_timer_no_exception(self):
        """Test timer handles operations without exceptions."""
        with timer() as t:
            x = 1 + 1  # noqa: F841

        assert "elapsed" in t
        assert t["elapsed"] >= 0


class TestTimingResult:
    """Test TimingResult dataclass."""

    def test_timing_result_creation(self):
        """Test creating a TimingResult."""
        result = TimingResult(
            operation="test_op",
            iterations=1000,
            total_time=1.0,
            avg_time=0.001,
            min_time=0.0009,
            max_time=0.0015,
            per_second=1000.0,
        )

        assert result.operation == "test_op"
        assert result.iterations == 1000
        assert result.total_time == 1.0
        assert result.avg_time == 0.001

    def test_timing_result_str(self):
        """Test string representation of TimingResult."""
        result = TimingResult(
            operation="test_op",
            iterations=1000,
            total_time=1.0,
            avg_time=0.001,
            min_time=0.0009,
            max_time=0.0015,
            per_second=1000.0,
        )

        result_str = str(result)
        assert "test_op" in result_str
        assert "1000" in result_str
        assert "1.0000s" in result_str


class TestBenchmarkFunction:
    """Test benchmark_function utility."""

    def test_benchmark_simple_function(self):
        """Test benchmarking a simple function."""
        result = benchmark_function(
            lambda: time.sleep(0.001),
            iterations=10,
            operation="sleep_test",
        )

        assert result.operation == "sleep_test"
        assert result.iterations == 10
        assert result.avg_time >= 0.001
        assert result.min_time > 0
        assert result.max_time > 0
        assert result.per_second > 0

    def test_benchmark_fast_function(self):
        """Test benchmarking a very fast function."""
        result = benchmark_function(
            lambda: 1 + 1,
            iterations=1000,
            operation="addition",
        )

        assert result.operation == "addition"
        assert result.iterations == 1000
        assert result.avg_time < 0.001  # Should be very fast
        assert result.per_second > 1000  # Should handle many ops/sec

    def test_benchmark_with_state(self):
        """Test benchmarking a function that modifies state."""
        counter = [0]

        def increment():
            counter[0] += 1

        result = benchmark_function(
            increment,
            iterations=100,
            operation="counter",
        )

        # Should have run iterations + 1 (warmup)
        assert counter[0] == 101
        assert result.iterations == 100


class TestCompareImplementations:
    """Test compare_implementations utility."""

    def test_compare_two_implementations(self):
        """Test comparing two implementations."""
        results = compare_implementations(
            {
                "fast": lambda: 1 + 1,
                "slow": lambda: time.sleep(0.001),
            },
            iterations=10,
        )

        assert "fast" in results
        assert "slow" in results
        assert results["fast"].avg_time < results["slow"].avg_time

    def test_compare_empty_dict(self):
        """Test comparing with empty implementations dict."""
        results = compare_implementations({}, iterations=10)
        assert results == {}


class TestFormatComparison:
    """Test format_comparison utility."""

    def test_format_comparison_with_baseline(self):
        """Test formatting comparison results with baseline."""
        results = {
            "baseline": TimingResult(
                operation="baseline",
                iterations=1000,
                total_time=1.0,
                avg_time=0.001,
                min_time=0.0009,
                max_time=0.0015,
                per_second=1000.0,
            ),
            "optimized": TimingResult(
                operation="optimized",
                iterations=1000,
                total_time=0.5,
                avg_time=0.0005,
                min_time=0.0004,
                max_time=0.0008,
                per_second=2000.0,
            ),
        }

        formatted = format_comparison(results, baseline="baseline")

        assert "Performance Comparison" in formatted
        assert "baseline" in formatted
        assert "optimized" in formatted
        assert "(baseline)" in formatted
        assert "faster" in formatted

    def test_format_comparison_without_baseline(self):
        """Test formatting comparison results without baseline."""
        results = {
            "impl1": TimingResult(
                operation="impl1",
                iterations=1000,
                total_time=1.0,
                avg_time=0.001,
                min_time=0.0009,
                max_time=0.0015,
                per_second=1000.0,
            ),
        }

        formatted = format_comparison(results)

        assert "Performance Comparison" in formatted
        assert "impl1" in formatted

    def test_format_comparison_empty(self):
        """Test formatting empty results."""
        formatted = format_comparison({})
        assert "No results to display" in formatted


class TestProfilingSession:
    """Test ProfilingSession class."""

    def test_session_creation(self):
        """Test creating a profiling session."""
        session = ProfilingSession(name="test_session")

        assert session.name == "test_session"
        assert session.results == []

    def test_session_add_result(self):
        """Test adding results to session."""
        session = ProfilingSession(name="test_session")

        result = TimingResult(
            operation="test_op",
            iterations=1000,
            total_time=1.0,
            avg_time=0.001,
            min_time=0.0009,
            max_time=0.0015,
            per_second=1000.0,
        )

        session.add_result(result)
        assert len(session.results) == 1
        assert session.results[0] == result

    def test_session_str(self):
        """Test string representation of session."""
        session = ProfilingSession(name="test_session")

        result = TimingResult(
            operation="test_op",
            iterations=1000,
            total_time=1.0,
            avg_time=0.001,
            min_time=0.0009,
            max_time=0.0015,
            per_second=1000.0,
        )

        session.add_result(result)

        session_str = str(session)
        assert "test_session" in session_str
        assert "test_op" in session_str
