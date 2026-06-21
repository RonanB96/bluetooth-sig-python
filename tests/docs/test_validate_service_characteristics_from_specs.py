"""Unit tests for scripts/validate_service_characteristics_from_specs.py."""

from __future__ import annotations

from pathlib import Path

from bluetooth_sig.gatt.characteristics.registry import get_characteristic_class_map
from scripts import validate_service_characteristics_from_specs as validator


def _write_spec(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")


def test_parse_spec_table_reads_valid_characteristics_table(tmp_path: Path) -> None:
    """Valid parser-format tables should produce normalized characteristic rows."""
    spec_file = tmp_path / "battery_service_spec.txt"
    _write_spec(
        spec_file,
        """
## Service Characteristics (Parser Format)
Service Name: Battery Service
| Characteristic | Req | Properties | Security |
|----------------|-----|------------|----------|
| Battery Level | M | Read | N/A |
| Battery Level Status | O | Read | N/A |
""",
    )

    parsed = validator._parse_spec_table(spec_file)

    assert parsed is not None
    assert parsed.service_name == "Battery Service"
    assert [row.name for row in parsed.characteristics] == ["Battery Level", "Battery Level Status"]


def test_main_returns_non_zero_for_unmatched_specs(tmp_path: Path) -> None:
    """Unmatched parsed specs should fail validation instead of silently passing."""
    spec_file = tmp_path / "unknown_service_spec.txt"
    _write_spec(
        spec_file,
        """
## Service Characteristics (Parser Format)
Service Name: Totally Unknown Service
| Characteristic | Req | Properties | Security |
|----------------|-----|------------|----------|
| Custom Metric | M | Read | N/A |
""",
    )

    exit_code = validator.main(spec_dir=tmp_path, pattern="*_spec.txt", verbose=False)

    assert exit_code == 1


def test_main_returns_zero_when_no_spec_files(tmp_path: Path) -> None:
    """An empty spec directory is a successful no-op run."""
    exit_code = validator.main(spec_dir=tmp_path, pattern="*_spec.txt", verbose=False)

    assert exit_code == 0


def test_compare_service_flags_requirement_mismatch() -> None:
    """Requirement mismatches between spec and implementation should be reported."""
    from bluetooth_sig.types.gatt_enums import ServiceName

    spec_table = validator.SpecTable(
        file_path=Path("battery_service_spec.txt"),
        service_name="Battery Service",
        characteristics=(validator.SpecCharacteristic(name="Battery Level", requirement="O"),),
    )
    service_chars = validator._build_service_characteristics_map()
    comparison = validator._compare_service(
        spec_table=spec_table,
        service_name=ServiceName.BATTERY,
        impl_chars=service_chars[ServiceName.BATTERY],
        char_class_map=get_characteristic_class_map(),
    )

    assert not comparison.is_ok
    assert comparison.requirement_mismatches
