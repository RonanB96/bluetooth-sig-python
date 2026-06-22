"""Batch parse tests for #192 dependency declaration expansion.

Characteristics updated in this PR (optional dependencies):
- LocationAndSpeedCharacteristic → LNFeatureCharacteristic
- WeightMeasurementCharacteristic → WeightScaleFeatureCharacteristic
"""

from __future__ import annotations

from bluetooth_sig import BluetoothSIGTranslator
from bluetooth_sig.gatt.characteristics.location_and_speed import (
    LNFeatureCharacteristic,
    LocationAndSpeedCharacteristic,
)
from bluetooth_sig.gatt.characteristics.weight_measurement import (
    WeightMeasurementCharacteristic,
    WeightMeasurementData,
)
from bluetooth_sig.gatt.characteristics.weight_scale_feature import WeightScaleFeatureCharacteristic


class TestDependencyDeclarationBatchParse:
    """Batch parse ordering and optional dependency behaviour."""

    def test_location_and_speed_batch_with_ln_feature_out_of_order(self) -> None:
        """Optional LN Feature is resolved when present; measurement listed first."""
        translator = BluetoothSIGTranslator()
        las_uuid = str(LocationAndSpeedCharacteristic.get_class_uuid())
        ln_uuid = str(LNFeatureCharacteristic.get_class_uuid())
        measurement_data = bytearray([0x00, 0x00])
        ln_feature_data = bytearray([0x01, 0x00, 0x00, 0x00])

        results = translator.parse_characteristics(
            {
                las_uuid: measurement_data,
                ln_uuid: ln_feature_data,
            }
        )

        assert las_uuid in results
        assert ln_uuid in results

    def test_location_and_speed_batch_without_ln_feature(self) -> None:
        """Optional LN Feature absence does not block Location and Speed parse."""
        translator = BluetoothSIGTranslator()
        las_uuid = str(LocationAndSpeedCharacteristic.get_class_uuid())
        measurement_data = bytearray([0x00, 0x00])

        results = translator.parse_characteristics({las_uuid: measurement_data})

        assert las_uuid in results

    def test_weight_measurement_batch_with_scale_feature_out_of_order(self) -> None:
        """Optional Weight Scale Feature is resolved when present."""
        translator = BluetoothSIGTranslator()
        wm_uuid = str(WeightMeasurementCharacteristic.get_class_uuid())
        feature_uuid = str(WeightScaleFeatureCharacteristic.get_class_uuid())
        measurement_data = bytearray([0x00, 0x88, 0x13])
        feature_data = bytearray([0x00, 0x00, 0x00, 0x00])

        results = translator.parse_characteristics(
            {
                wm_uuid: measurement_data,
                feature_uuid: feature_data,
            }
        )

        assert wm_uuid in results
        assert feature_uuid in results
        assert isinstance(results[wm_uuid], WeightMeasurementData)

    def test_weight_measurement_batch_without_scale_feature(self) -> None:
        """Optional Weight Scale Feature absence does not block measurement parse."""
        translator = BluetoothSIGTranslator()
        wm_uuid = str(WeightMeasurementCharacteristic.get_class_uuid())
        measurement_data = bytearray([0x00, 0x88, 0x13])

        results = translator.parse_characteristics({wm_uuid: measurement_data})

        assert wm_uuid in results
