"""Test Python code blocks extracted from markdown documentation.

This module automatically extracts and executes Python code blocks from
documentation files to ensure examples remain accurate and runnable.

Organization:
- Scans markdown files in docs/ directory
- Extracts code blocks marked with ```python
- Executes each block as an independent test
- Handles async code, mocking requirements, and incomplete examples
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Get repository root
ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"


def discover_doc_files() -> list[Path]:
    """Discover all markdown files in the docs directory recursively.

    Returns:
        List of Path objects for all .md files in docs/
    """
    if not DOCS_DIR.exists():
        return []

    # Find all .md files recursively, excluding generated/cache directories
    md_files: list[Path] = []
    for pattern in ["**/*.md"]:
        md_files.extend(DOCS_DIR.glob(pattern))

    # Exclude generated/cache directories
    excluded_patterns = [
        "**/.cache/**",
        "**/deps/**",
        "**/puml/**",
        "**/svg/**",
    ]

    filtered_files: list[Path] = []
    for md_file in md_files:
        excluded = False
        for excluded_pattern in excluded_patterns:
            if md_file.match(excluded_pattern):
                excluded = True
                break
        if not excluded:
            filtered_files.append(md_file)

    return sorted(filtered_files)


# Documentation files to scan (dynamically discovered)
DOC_FILES = discover_doc_files()


def extract_python_code_blocks(markdown_content: str) -> list[str]:
    """Extract Python code blocks from markdown content.

    Args:
        markdown_content: Raw markdown file content

    Returns:
        List of Python code block contents
    """
    # Match ```python...``` blocks, capturing content between backticks
    pattern = r"```python\n(.*?)```"
    matches = re.findall(pattern, markdown_content, re.DOTALL)
    return matches


def should_skip_code_block(code: str) -> tuple[bool, str]:
    """Determine if a code block should be skipped.

    Args:
        code: Python code block content

    Returns:
        Tuple of (should_skip, reason)
    """
    # Check for explicit SKIP marker with optional reason
    skip_match = re.search(r"#\s*SKIP:?\s*(.*)", code, re.IGNORECASE)
    if skip_match:
        reason = skip_match.group(1).strip() or "Explicitly marked to skip"
        return True, reason

    # Skip blocks with ellipsis - incomplete examples
    if "..." in code:
        return True, "Incomplete example (contains ...)"

    # Skip blocks that are just command-line examples
    if code.strip().startswith("pip install") or code.strip().startswith("pytest"):
        return True, "Command-line example, not Python code"

    # Skip bash commands
    if code.strip().startswith("bash"):
        return True, "Bash command, not Python code"

    # Only skip if it's PURELY comments with no actual code
    lines = code.strip().split("\n")
    non_comment_lines = [line for line in lines if line.strip() and not line.strip().startswith("#")]
    if len(non_comment_lines) == 0:
        return True, "Comment-only block, no executable code"

    return False, ""


def is_async_code(code: str) -> bool:
    """Check if code block contains async/await but no asyncio.run().

    Args:
        code: Python code block content

    Returns:
        True if code needs asyncio.run() wrapper
    """
    has_async = "async def" in code or "await " in code
    has_runner = "asyncio.run(" in code
    return has_async and not has_runner


def wrap_async_code(code: str) -> str:
    """Wrap async code with asyncio.run() for execution.

    Args:
        code: Python code block with async/await

    Returns:
        Code wrapped to execute the main async function
    """
    # Check for SKIP marker (don't try to wrap if marked for skip)
    if re.search(r"#\s*SKIP:", code, re.IGNORECASE):
        return code

    # If there's an async main() function, wrap it
    if "async def main(" in code:
        return f"{code}\n\nasyncio.run(main())"

    # If there's another async function defined, find and wrap it
    async_func_match = re.search(r"async def (\w+)\(", code)
    if async_func_match:
        func_name = async_func_match.group(1)
        # Check if function takes parameters - skip if it does
        if f"async def {func_name}()" in code:
            return f"{code}\n\nasyncio.run({func_name}())"
        # Has parameters - can't auto-execute, skip wrapping
        return code

    # For inline await expressions, wrap everything
    if "await " in code and "async def" not in code:
        wrapper_lines = ["async def _test_wrapper():"]
        wrapper_lines.extend(f"    {line}" for line in code.split("\n"))
        wrapper_lines.append("")
        wrapper_lines.append("asyncio.run(_test_wrapper())")
        wrapped = "\n".join(wrapper_lines)
        return wrapped

    return code


def create_mock_ble_context() -> dict[str, Any]:
    """Create mocked BLE library context for code execution.

    Returns:
        Dictionary of mocked objects to inject into execution namespace
    """
    # Mock BleakClient
    mock_client = MagicMock()
    mock_client.read_gatt_char = AsyncMock(return_value=bytearray([85]))
    mock_client.get_services = AsyncMock(return_value=[])
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.start_notify = AsyncMock()

    # Mock BleakScanner
    mock_scanner = MagicMock()
    mock_device = MagicMock()
    mock_device.name = "Test Device"
    mock_device.address = "AA:BB:CC:DD:EE:FF"
    mock_scanner.discover = AsyncMock(return_value=[mock_device])

    # Create proxy for asyncio: preserve real asyncio.run, but mock sleep
    class AsyncioProxy:  # pragma: no cover - small helper for tests
        def __init__(self) -> None:
            self._real = asyncio
            # Only mock sleep; keep other attributes (run, etc.) real
            self.sleep = AsyncMock()

        def __getattr__(self, name: str) -> Any:
            return getattr(self._real, name)

    mock_asyncio = AsyncioProxy()

    # Provide stub values for common undefined variables in examples
    stub_values = {
        "address": "AA:BB:CC:DD:EE:FF",
        "device_address": "AA:BB:CC:DD:EE:FF",
        "devices": ["AA:BB:CC:DD:EE:FF"],
        "blood_pressure_measurement_bytes": bytearray([0x00, 0x64, 0x00, 0x50, 0x00, 0x00]),
        "intermediate_cuff_pressure_bytes": bytearray([0x00, 0x78, 0x00, 0x00, 0x00, 0x00]),
        "bpm_bytes": bytearray([0x00, 0x64, 0x00, 0x50, 0x00, 0x00]),
        "icp_bytes": bytearray([0x00, 0x78, 0x00, 0x00, 0x00, 0x00]),
        "services": [],
        "values_by_uuid": {},
    }
    # Provide common simple test data variables referenced in docs
    extra_stubs = {
        "battery_data": bytearray([85]),
        "temp_data": bytearray([0x64, 0x09]),
        "humidity_data": bytearray([0x32]),
        "data": bytearray([85]),
        "uuid": "2A19",
    }
    stub_values.update(extra_stubs)

    # Dummy device and connection manager to avoid real BLE operations
    class DummyDevice:
        def __init__(self, address: str, translator: Any | None = None) -> None:
            self.address = address

        async def connect(self) -> None:  # pragma: no cover - no IO
            return None

        async def read(self, uuid: str) -> bytearray:  # pragma: no cover - no IO
            return bytearray([85])

        async def disconnect(self) -> None:  # pragma: no cover - no IO
            return None

    class DummyConnectionManager:
        def __init__(self, addr: str) -> None:
            self.address = addr
            self.client = mock_client

        async def connect(self) -> None:  # pragma: no cover - no IO
            return None

        async def disconnect(self) -> None:  # pragma: no cover - no IO
            return None

        async def read(self, uuid: str) -> bytearray:  # pragma: no cover - no IO
            return bytearray([85])

    # Import BleakError if available, fallback to Exception
    try:
        from bleak.exc import BleakError  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        BleakError = Exception  # type: ignore

    # Create a singleton translator so doc code can use translator without explicit creation
    try:
        from bluetooth_sig import BluetoothSIGTranslator

        translator_instance = BluetoothSIGTranslator()
    except Exception:
        translator_instance = None

    return {
        "BleakClient": lambda addr: mock_client,
        "BleakScanner": mock_scanner,
        # Provide an asyncio proxy that exposes real asyncio.run but mocks sleep
        "asyncio": mock_asyncio,
        # Add translator so doc snippets that reference it without creating still work
        "translator": translator_instance,
        # Standard stub variables
        "client": mock_client,
        "device": DummyDevice("AA:BB:CC:DD:EE:FF"),
        "Device": DummyDevice,
        "BleakRetryConnectionManager": DummyConnectionManager,
        "BleakError": BleakError,
        **stub_values,
    }


def execute_code_block(code: str, file_path: Path, block_num: int) -> None:
    """Execute a Python code block with proper error handling.

    Args:
        code: Python code to execute
        file_path: Source documentation file path
        block_num: Code block number in file

    Raises:
        AssertionError: If code execution fails with details
    """
    # Create isolated namespace for execution
    namespace: dict[str, Any] = {
        "__name__": "__main__",
        "asyncio": asyncio,
    }

    # Always add mocked BLE context (includes stub values for common variables)
    namespace.update(create_mock_ble_context())

    # Handle async code
    if is_async_code(code):
        code = wrap_async_code(code)

    # Execute code
    try:
        # Exec is required to execute user-provided code blocks; the
        # security-related warning is acknowledged but acceptable in this
        # isolated test environment. Disable pylint since this is intentional.
        exec(code, namespace)  # noqa: S102  # pylint: disable=exec-used
    except Exception as e:
        # Provide detailed error message with context
        error_msg = (
            f"\n{'=' * 70}\n"
            f"Code block execution failed!\n"
            f"File: {file_path.relative_to(ROOT_DIR)}\n"
            f"Block: #{block_num}\n"
            f"Error: {type(e).__name__}: {e}\n"
            f"{'=' * 70}\n"
            f"Code:\n{code}\n"
            f"{'=' * 70}"
        )
        pytest.fail(error_msg)


def collect_code_blocks() -> list[tuple[Path, int, str]]:
    """Collect all Python code blocks from documentation files.

    Returns:
        List of tuples: (file_path, block_number, code)
    """
    code_blocks = []

    for doc_file in DOC_FILES:
        if not doc_file.exists():
            continue

        content = doc_file.read_text(encoding="utf-8")
        blocks = extract_python_code_blocks(content)

        for idx, block in enumerate(blocks, start=1):
            code_blocks.append((doc_file, idx, block))

    return code_blocks


# Collect all code blocks for parametrization
ALL_CODE_BLOCKS = collect_code_blocks()


@pytest.mark.docs
@pytest.mark.code_blocks
@pytest.mark.parametrize(
    "doc_file,block_num,code",
    [
        pytest.param(
            file_path,
            block_num,
            code,
            id=f"{file_path.relative_to(DOCS_DIR)}-block{block_num}",
        )
        for file_path, block_num, code in ALL_CODE_BLOCKS
    ],
)
def test_documentation_code_block(doc_file: Path, block_num: int, code: str) -> None:
    """Test that a documentation code block executes successfully.

    Args:
        doc_file: Path to documentation file
        block_num: Code block number within the file
        code: Python code block content
    """
    # Check if this block should be skipped
    should_skip, reason = should_skip_code_block(code)
    if should_skip:
        pytest.skip(reason)

    # Execute the code block
    execute_code_block(code, doc_file, block_num)


@pytest.mark.docs
def test_code_blocks_collected() -> None:
    """Verify that code blocks were successfully collected from docs."""
    assert len(ALL_CODE_BLOCKS) > 0, "No Python code blocks found in documentation files"

    # Report statistics
    files_with_blocks = len({file_path for file_path, _, _ in ALL_CODE_BLOCKS})
    total_blocks = len(ALL_CODE_BLOCKS)

    print(f"\n{'=' * 70}")
    print("Documentation Code Block Statistics:")
    print(f"  Files scanned: {len(DOC_FILES)}")
    print(f"  Files with code blocks: {files_with_blocks}")
    print(f"  Total code blocks found: {total_blocks}")
    print(f"{'=' * 70}")

    # Ensure all expected files exist
    missing_files = [f for f in DOC_FILES if not f.exists()]
    if missing_files:
        pytest.fail(f"Missing documentation files: {missing_files}")
