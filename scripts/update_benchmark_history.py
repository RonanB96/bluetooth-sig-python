#!/usr/bin/env python3
"""Update benchmark history with latest results, keeping only summary data."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Maximum number of historical data points to retain
MAX_HISTORY_ENTRIES = 100


def extract_summary(benchmark_data: dict[str, Any]) -> dict[str, Any]:
    """Extract minimal summary data from full benchmark results."""
    benchmarks = benchmark_data.get("benchmarks", [])

    # Ensure datetime is always serialized as ISO format string
    timestamp = benchmark_data.get("datetime")
    if isinstance(timestamp, datetime):
        timestamp = timestamp.isoformat()
    elif not isinstance(timestamp, str):
        timestamp = datetime.now().astimezone().isoformat()

    summary = {
        "timestamp": timestamp,
        "commit": benchmark_data.get("commit_info", {}).get("id", "unknown")[:8],
        "results": {}
    }

    for bench in benchmarks:
        name = bench.get("name", "unknown")
        stats = bench.get("stats", {})

        # Store only essential statistics (mean, max, stddev) in microseconds
        summary["results"][name] = {
            "mean": round(stats.get("mean", 0) * 1_000_000, 2),  # Convert to µs
            "max": round(stats.get("max", 0) * 1_000_000, 2),  # Convert to µs
            "stddev": round(stats.get("stddev", 0) * 1_000_000, 2),  # Convert to µs
        }

    return summary


def update_history(current_json_path: Path, history_json_path: Path) -> None:
    """Update benchmark history with current results."""
    # Read current benchmark results
    if not current_json_path.exists():
        print(f"❌ Current benchmark file not found: {current_json_path}")
        sys.exit(1)

    with open(current_json_path, encoding="utf-8") as f:
        current_data = json.load(f)

    # Extract summary from current results
    summary = extract_summary(current_data)

    # Read existing history or create new
    history = []
    if history_json_path.exists():
        with open(history_json_path, encoding="utf-8") as f:
            history = json.load(f)

    # Append new summary
    history.append(summary)

    # Rotate: keep only last MAX_HISTORY_ENTRIES
    if len(history) > MAX_HISTORY_ENTRIES:
        history = history[-MAX_HISTORY_ENTRIES:]

    # Write updated history
    history_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_json_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"✅ Updated benchmark history: {len(history)} entries")
    print(f"   Latest: {summary['timestamp'][:19]} (commit {summary['commit']})")
    print(f"   Oldest: {history[0]['timestamp'][:19]} (commit {history[0]['commit']})")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: update_benchmark_history.py <current_benchmark.json> <history.json>")
        sys.exit(1)

    current_json_path = Path(sys.argv[1])
    history_json_path = Path(sys.argv[2])

    update_history(current_json_path, history_json_path)


if __name__ == "__main__":
    main()
