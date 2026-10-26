"""Handwritten override codecs warn when a GSS document exists for the same id."""

from __future__ import annotations

import warnings
from pathlib import Path

from tools.gss_ir.sources.overrides import (
    gss_characteristic_ids,
    handwritten_gss_overlaps,
    handwritten_override_ids,
    warn_handwritten_gss_overlaps,
)

ROOT = Path(__file__).resolve().parents[3]


def test_checked_in_overrides_have_no_gss_document() -> None:
    override_ids = handwritten_override_ids(ROOT / "btsig/override")
    overlaps = handwritten_gss_overlaps(override_ids, gss_characteristic_ids(ROOT / "bluetooth_sig/gss"))

    assert override_ids == (
        "org.bluetooth.characteristic.gap.device_name",
        "org.bluetooth.characteristic.protocol_mode",
        "org.bluetooth.characteristic.gatt.service_changed",
        "org.bluetooth.characteristic.volume_state",
    )
    assert overlaps == ()
    assert warn_handwritten_gss_overlaps(ROOT) == ()


def test_handwritten_gss_overlap_warns(tmp_path: Path) -> None:
    source = tmp_path / "btsig" / "override" / "battery_level" / "src"
    source.mkdir(parents=True)
    (source / "battery_level.c").write_text(
        '"org.bluetooth.characteristic.battery_level"\n',
        encoding="utf-8",
    )
    gss = tmp_path / "bluetooth_sig" / "gss"
    gss.mkdir(parents=True)
    (gss / "org.bluetooth.characteristic.battery_level.yaml").write_text(
        """
characteristic:
  identifier: org.bluetooth.characteristic.battery_level
  name: Battery Level
  description: Level.
  structure:
    - field: Level
      type: uint8
      size: "1"
      description: Percent.
""",
        encoding="utf-8",
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        overlaps = warn_handwritten_gss_overlaps(tmp_path)

    assert overlaps == ("org.bluetooth.characteristic.battery_level",)
    assert len(caught) == 1
    assert "org.bluetooth.characteristic.battery_level" in str(caught[0].message)
    assert "GSS" in str(caught[0].message)
