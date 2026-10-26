"""LE Supported Features (Core Spec Vol 6, Part B, Section 4.6)."""

from __future__ import annotations

from enum import IntFlag

import msgspec


class LEFeatureBits(IntFlag):
    """LE Supported Features bit definitions (Core Spec Vol 6, Part B, Section 4.6).

    Byte 0 features (bits 0-7).
    """

    # Byte 0 features
    LE_ENCRYPTION = 0x0001
    CONNECTION_PARAMETERS_REQUEST = 0x0002
    EXTENDED_REJECT_INDICATION = 0x0004
    PERIPHERAL_INITIATED_FEATURES_EXCHANGE = 0x0008
    LE_PING = 0x0010
    LE_DATA_PACKET_LENGTH_EXTENSION = 0x0020
    LL_PRIVACY = 0x0040
    EXTENDED_SCANNER_FILTER_POLICIES = 0x0080

    # Byte 1 features (bits 8-15)
    LE_2M_PHY = 0x0100
    STABLE_MODULATION_INDEX_TX = 0x0200
    STABLE_MODULATION_INDEX_RX = 0x0400
    LE_CODED_PHY = 0x0800
    LE_EXTENDED_ADVERTISING = 0x1000
    LE_PERIODIC_ADVERTISING = 0x2000
    CHANNEL_SELECTION_ALGORITHM_2 = 0x4000
    LE_POWER_CLASS_1 = 0x8000

    # Byte 2 features (bits 16-23)
    MIN_NUMBER_OF_USED_CHANNELS = 0x010000
    CONNECTION_CTE_REQUEST = 0x020000
    CONNECTION_CTE_RESPONSE = 0x040000
    CONNECTIONLESS_CTE_TX = 0x080000
    CONNECTIONLESS_CTE_RX = 0x100000
    ANTENNA_SWITCHING_TX = 0x200000
    ANTENNA_SWITCHING_RX = 0x400000
    RECEIVING_CTE = 0x800000


class LEFeatures(msgspec.Struct, kw_only=True):  # pylint: disable=too-many-public-methods  # One property per LE feature bit
    """LE Supported Features bit field (Core Spec Vol 6, Part B, Section 4.6).

    Attributes:
        raw_value: Raw feature bit field bytes (up to 8 bytes)
    """

    raw_value: bytes

    def _get_features_int(self) -> int:
        """Convert raw bytes to integer for bit checking."""
        return int.from_bytes(self.raw_value, byteorder="little") if self.raw_value else 0

    def _has_feature(self, feature: LEFeatureBits) -> bool:
        """Check if a specific feature bit is set."""
        return bool(self._get_features_int() & feature)

    @property
    def le_encryption(self) -> bool:
        """LE Encryption supported."""
        return self._has_feature(LEFeatureBits.LE_ENCRYPTION)

    @property
    def connection_parameters_request(self) -> bool:
        """Connection Parameters Request Procedure."""
        return self._has_feature(LEFeatureBits.CONNECTION_PARAMETERS_REQUEST)

    @property
    def extended_reject_indication(self) -> bool:
        """Extended Reject Indication."""
        return self._has_feature(LEFeatureBits.EXTENDED_REJECT_INDICATION)

    @property
    def peripheral_initiated_features_exchange(self) -> bool:
        """Peripheral-initiated Features Exchange."""
        return self._has_feature(LEFeatureBits.PERIPHERAL_INITIATED_FEATURES_EXCHANGE)

    @property
    def le_ping(self) -> bool:
        """LE Ping."""
        return self._has_feature(LEFeatureBits.LE_PING)

    @property
    def le_data_packet_length_extension(self) -> bool:
        """LE Data Packet Length Extension."""
        return self._has_feature(LEFeatureBits.LE_DATA_PACKET_LENGTH_EXTENSION)

    @property
    def ll_privacy(self) -> bool:
        """LL Privacy."""
        return self._has_feature(LEFeatureBits.LL_PRIVACY)

    @property
    def extended_scanner_filter_policies(self) -> bool:
        """Extended Scanner Filter Policies."""
        return self._has_feature(LEFeatureBits.EXTENDED_SCANNER_FILTER_POLICIES)

    @property
    def le_2m_phy(self) -> bool:
        """LE 2M PHY."""
        return self._has_feature(LEFeatureBits.LE_2M_PHY)

    @property
    def stable_modulation_index_tx(self) -> bool:
        """Stable Modulation Index - Transmitter."""
        return self._has_feature(LEFeatureBits.STABLE_MODULATION_INDEX_TX)

    @property
    def stable_modulation_index_rx(self) -> bool:
        """Stable Modulation Index - Receiver."""
        return self._has_feature(LEFeatureBits.STABLE_MODULATION_INDEX_RX)

    @property
    def le_coded_phy(self) -> bool:
        """LE Coded PHY."""
        return self._has_feature(LEFeatureBits.LE_CODED_PHY)

    @property
    def le_extended_advertising(self) -> bool:
        """LE Extended Advertising."""
        return self._has_feature(LEFeatureBits.LE_EXTENDED_ADVERTISING)

    @property
    def le_periodic_advertising(self) -> bool:
        """LE Periodic Advertising."""
        return self._has_feature(LEFeatureBits.LE_PERIODIC_ADVERTISING)

    @property
    def channel_selection_algorithm_2(self) -> bool:
        """Channel Selection Algorithm #2."""
        return self._has_feature(LEFeatureBits.CHANNEL_SELECTION_ALGORITHM_2)

    @property
    def le_power_class_1(self) -> bool:
        """LE Power Class 1."""
        return self._has_feature(LEFeatureBits.LE_POWER_CLASS_1)

    @property
    def min_number_of_used_channels(self) -> bool:
        """Minimum Number of Used Channels Procedure."""
        return self._has_feature(LEFeatureBits.MIN_NUMBER_OF_USED_CHANNELS)

    @property
    def connection_cte_request(self) -> bool:
        """Connection CTE Request."""
        return self._has_feature(LEFeatureBits.CONNECTION_CTE_REQUEST)

    @property
    def connection_cte_response(self) -> bool:
        """Connection CTE Response."""
        return self._has_feature(LEFeatureBits.CONNECTION_CTE_RESPONSE)

    @property
    def connectionless_cte_tx(self) -> bool:
        """Connectionless CTE Transmitter."""
        return self._has_feature(LEFeatureBits.CONNECTIONLESS_CTE_TX)

    @property
    def connectionless_cte_rx(self) -> bool:
        """Connectionless CTE Receiver."""
        return self._has_feature(LEFeatureBits.CONNECTIONLESS_CTE_RX)

    @property
    def antenna_switching_tx(self) -> bool:
        """Antenna Switching During CTE Transmission."""
        return self._has_feature(LEFeatureBits.ANTENNA_SWITCHING_TX)

    @property
    def antenna_switching_rx(self) -> bool:
        """Antenna Switching During CTE Reception."""
        return self._has_feature(LEFeatureBits.ANTENNA_SWITCHING_RX)

    @property
    def receiving_cte(self) -> bool:
        """Receiving Constant Tone Extensions."""
        return self._has_feature(LEFeatureBits.RECEIVING_CTE)
