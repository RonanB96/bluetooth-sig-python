"""Tests for OTS Feature characteristic (0x2ABD)."""

from __future__ import annotations

import pytest

from bluetooth_sig.gatt.characteristics.ots_feature import (
    OACPFeatures,
    OLCPFeatures,
    OTSFeatureCharacteristic,
    OTSFeatureData,
)
from tests.gatt.characteristics.test_characteristic_common import CharacteristicTestData, CommonCharacteristicTests


class TestOTSFeature(CommonCharacteristicTests):
    """Test suite for OTS Feature characteristic."""

    @pytest.fixture
    def characteristic(self) -> OTSFeatureCharacteristic:
        return OTSFeatureCharacteristic()

    @pytest.fixture
    def expected_uuid(self) -> str:
        return "2ABD"

    @pytest.fixture
    def valid_test_data(self) -> list[CharacteristicTestData]:
        return [
            CharacteristicTestData(
                bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
                OTSFeatureData(oacp_features=OACPFeatures(0), olcp_features=OLCPFeatures(0)),
                "No features",
            ),
            CharacteristicTestData(
                bytearray([0x13, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00]),
                OTSFeatureData(
                    oacp_features=OACPFeatures.CREATE | OACPFeatures.DELETE | OACPFeatures.READ,
                    olcp_features=OLCPFeatures.GO_TO | OLCPFeatures.ORDER | OLCPFeatures.REQUEST_NUMBER_OF_OBJECTS,
                ),
                "Create+Delete+Read, GoTo+Order+NumReq",
            ),
        ]

    def test_oacp_all_bits(self) -> None:
        """Verify all 10 OACP feature bits are defined."""
        expected = {
            "CREATE",
            "DELETE",
            "CALCULATE_CHECKSUM",
            "EXECUTE",
            "READ",
            "WRITE",
            "APPEND",
            "TRUNCATE",
            "PATCH",
            "ABORT",
        }
        actual = {m.name for m in OACPFeatures if m.value != 0}
        assert actual == expected

    def test_olcp_all_bits(self) -> None:
        """Verify all 4 OLCP feature bits are defined."""
        expected = {"GO_TO", "ORDER", "REQUEST_NUMBER_OF_OBJECTS", "CLEAR_MARKING"}
        actual = {m.name for m in OLCPFeatures if m.value != 0}
        assert actual == expected

    def test_roundtrip(self, characteristic: OTSFeatureCharacteristic) -> None:
        """Test encode/decode roundtrip."""
        data = OTSFeatureData(
            oacp_features=OACPFeatures.CREATE | OACPFeatures.READ | OACPFeatures.WRITE,
            olcp_features=OLCPFeatures.GO_TO | OLCPFeatures.CLEAR_MARKING,
        )
        encoded = characteristic.build_value(data)
        result = characteristic.parse_value(encoded)
        assert result.oacp_features == data.oacp_features
        assert result.olcp_features == data.olcp_features

    def test_expected_length(self, characteristic: OTSFeatureCharacteristic) -> None:
        """Verify expected length is 8 bytes."""
        assert characteristic.expected_length == 8
