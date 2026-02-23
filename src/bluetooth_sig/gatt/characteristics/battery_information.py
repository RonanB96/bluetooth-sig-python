"""Battery Information characteristic implementation.

Implements the Battery Information characteristic (0x2BEC) from the Battery
Service.  A 16-bit flags field controls the presence of optional fields.
A mandatory Battery Features byte is always present after the flags.

All flag bits use normal logic (1 = present, 0 = absent).

References:
    Bluetooth SIG Battery Service 1.1
    org.bluetooth.characteristic.battery_information (GSS YAML)
"""

from __future__ import annotations

from enum import IntEnum, IntFlag

import msgspec

from ..constants import UINT8_MAX, UINT24_MAX
from ..context import CharacteristicContext
from .base import BaseCharacteristic
from .utils import DataParser, IEEE11073Parser


class BatteryInformationFlags(IntFlag):
    """Battery Information flags as per Bluetooth SIG specification."""

    MANUFACTURE_DATE_PRESENT = 0x0001
    EXPIRATION_DATE_PRESENT = 0x0002
    DESIGNED_CAPACITY_PRESENT = 0x0004
    LOW_ENERGY_PRESENT = 0x0008
    CRITICAL_ENERGY_PRESENT = 0x0010
    BATTERY_CHEMISTRY_PRESENT = 0x0020
    NOMINAL_VOLTAGE_PRESENT = 0x0040
    AGGREGATION_GROUP_PRESENT = 0x0080


class BatteryFeatures(IntFlag):
    """Battery Features bitfield as per Bluetooth SIG specification."""

    REPLACEABLE = 0x01
    RECHARGEABLE = 0x02


class BatteryChemistry(IntEnum):
    """Battery Chemistry enumeration as per Bluetooth SIG specification."""

    UNKNOWN = 0
    ALKALINE = 1
    LEAD_ACID = 2
    LITHIUM_IRON_DISULFIDE = 3
    LITHIUM_MANGANESE_DIOXIDE = 4
    LITHIUM_ION = 5
    LITHIUM_POLYMER = 6
    NICKEL_OXYHYDROXIDE = 7
    NICKEL_CADMIUM = 8
    NICKEL_METAL_HYDRIDE = 9
    SILVER_OXIDE = 10
    ZINC_CHLORIDE = 11
    ZINC_AIR = 12
    ZINC_CARBON = 13
    OTHER = 255


class BatteryInformation(msgspec.Struct, frozen=True, kw_only=True):  # pylint: disable=too-few-public-methods
    """Parsed data from Battery Information characteristic.

    Attributes:
        flags: Raw 16-bit flags field.
        battery_features: Mandatory features bitfield (replaceable,
            rechargeable).
        battery_manufacture_date: Days since epoch (1970-01-01).
            None if absent.
        battery_expiration_date: Days since epoch (1970-01-01).
            None if absent.
        battery_designed_capacity: Designed capacity in kWh (medfloat16).
            None if absent.
        battery_low_energy: Low energy threshold in kWh (medfloat16).
            None if absent.
        battery_critical_energy: Critical energy threshold in kWh
            (medfloat16). None if absent.
        battery_chemistry: Chemistry type. None if absent.
        nominal_voltage: Nominal voltage in volts (medfloat16).
            None if absent.
        battery_aggregation_group: Aggregation group number (0=none,
            1-254=group). None if absent.

    """

    flags: BatteryInformationFlags
    battery_features: BatteryFeatures
    battery_manufacture_date: int | None = None
    battery_expiration_date: int | None = None
    battery_designed_capacity: float | None = None
    battery_low_energy: float | None = None
    battery_critical_energy: float | None = None
    battery_chemistry: BatteryChemistry | None = None
    nominal_voltage: float | None = None
    battery_aggregation_group: int | None = None

    def __post_init__(self) -> None:
        """Validate field ranges."""
        if self.battery_manufacture_date is not None and not 0 <= self.battery_manufacture_date <= UINT24_MAX:
            raise ValueError(f"Manufacture date must be 0-{UINT24_MAX}, got {self.battery_manufacture_date}")
        if self.battery_expiration_date is not None and not 0 <= self.battery_expiration_date <= UINT24_MAX:
            raise ValueError(f"Expiration date must be 0-{UINT24_MAX}, got {self.battery_expiration_date}")
        if self.battery_aggregation_group is not None and not 0 <= self.battery_aggregation_group <= UINT8_MAX:
            raise ValueError(f"Aggregation group must be 0-{UINT8_MAX}, got {self.battery_aggregation_group}")


class BatteryInformationCharacteristic(
    BaseCharacteristic[BatteryInformation],
):
    """Battery Information characteristic (0x2BEC).

    Reports physical battery characteristics including features, dates,
    capacity, chemistry, voltage, and aggregation group.

    Flag-bit assignments (from GSS YAML, 16-bit flags):
        Bit 0: Battery Manufacture Date Present
        Bit 1: Battery Expiration Date Present
        Bit 2: Battery Designed Capacity Present
        Bit 3: Battery Low Energy Present
        Bit 4: Battery Critical Energy Present
        Bit 5: Battery Chemistry Present
        Bit 6: Nominal Voltage Present
        Bit 7: Battery Aggregation Group Present
        Bits 8-15: Reserved for Future Use

    The mandatory Battery Features byte is always present after the flags.

    """

    expected_type = BatteryInformation
    min_length: int = 3  # 2 bytes flags + 1 byte mandatory features
    allow_variable_length: bool = True

    def _decode_value(
        self,
        data: bytearray,
        ctx: CharacteristicContext | None = None,
        *,
        validate: bool = True,
    ) -> BatteryInformation:
        """Parse Battery Information from raw BLE bytes.

        Args:
            data: Raw bytearray from BLE characteristic.
            ctx: Optional context (unused).
            validate: Whether to validate ranges.

        Returns:
            BatteryInformation with all present fields populated.

        """
        flags = BatteryInformationFlags(DataParser.parse_int16(data, 0, signed=False))
        battery_features = BatteryFeatures(DataParser.parse_int8(data, 2, signed=False))
        offset = 3

        # Bit 0 -- Battery Manufacture Date (uint24, days since epoch)
        manufacture_date = None
        if flags & BatteryInformationFlags.MANUFACTURE_DATE_PRESENT:
            manufacture_date = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        # Bit 1 -- Battery Expiration Date (uint24, days since epoch)
        expiration_date = None
        if flags & BatteryInformationFlags.EXPIRATION_DATE_PRESENT:
            expiration_date = DataParser.parse_int24(data, offset, signed=False)
            offset += 3

        # Bit 2 -- Battery Designed Capacity (medfloat16, kWh)
        designed_capacity = None
        if flags & BatteryInformationFlags.DESIGNED_CAPACITY_PRESENT:
            designed_capacity = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Bit 3 -- Battery Low Energy (medfloat16, kWh)
        low_energy = None
        if flags & BatteryInformationFlags.LOW_ENERGY_PRESENT:
            low_energy = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Bit 4 -- Battery Critical Energy (medfloat16, kWh)
        critical_energy = None
        if flags & BatteryInformationFlags.CRITICAL_ENERGY_PRESENT:
            critical_energy = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Bit 5 -- Battery Chemistry (uint8 enum)
        chemistry = None
        if flags & BatteryInformationFlags.BATTERY_CHEMISTRY_PRESENT:
            raw_chem = DataParser.parse_int8(data, offset, signed=False)
            try:
                chemistry = BatteryChemistry(raw_chem)
            except ValueError:
                chemistry = BatteryChemistry.UNKNOWN
            offset += 1

        # Bit 6 -- Nominal Voltage (medfloat16, volts)
        nominal_voltage = None
        if flags & BatteryInformationFlags.NOMINAL_VOLTAGE_PRESENT:
            nominal_voltage = IEEE11073Parser.parse_sfloat(data, offset)
            offset += 2

        # Bit 7 -- Battery Aggregation Group (uint8)
        aggregation_group = None
        if flags & BatteryInformationFlags.AGGREGATION_GROUP_PRESENT:
            aggregation_group = DataParser.parse_int8(data, offset, signed=False)
            offset += 1

        return BatteryInformation(
            flags=flags,
            battery_features=battery_features,
            battery_manufacture_date=manufacture_date,
            battery_expiration_date=expiration_date,
            battery_designed_capacity=designed_capacity,
            battery_low_energy=low_energy,
            battery_critical_energy=critical_energy,
            battery_chemistry=chemistry,
            nominal_voltage=nominal_voltage,
            battery_aggregation_group=aggregation_group,
        )

    def _encode_value(self, data: BatteryInformation) -> bytearray:
        """Encode BatteryInformation back to BLE bytes.

        Args:
            data: BatteryInformation instance.

        Returns:
            Encoded bytearray matching the BLE wire format.

        """
        flags = BatteryInformationFlags(0)

        if data.battery_manufacture_date is not None:
            flags |= BatteryInformationFlags.MANUFACTURE_DATE_PRESENT
        if data.battery_expiration_date is not None:
            flags |= BatteryInformationFlags.EXPIRATION_DATE_PRESENT
        if data.battery_designed_capacity is not None:
            flags |= BatteryInformationFlags.DESIGNED_CAPACITY_PRESENT
        if data.battery_low_energy is not None:
            flags |= BatteryInformationFlags.LOW_ENERGY_PRESENT
        if data.battery_critical_energy is not None:
            flags |= BatteryInformationFlags.CRITICAL_ENERGY_PRESENT
        if data.battery_chemistry is not None:
            flags |= BatteryInformationFlags.BATTERY_CHEMISTRY_PRESENT
        if data.nominal_voltage is not None:
            flags |= BatteryInformationFlags.NOMINAL_VOLTAGE_PRESENT
        if data.battery_aggregation_group is not None:
            flags |= BatteryInformationFlags.AGGREGATION_GROUP_PRESENT

        result = DataParser.encode_int16(int(flags), signed=False)
        result.extend(DataParser.encode_int8(int(data.battery_features), signed=False))

        if data.battery_manufacture_date is not None:
            result.extend(DataParser.encode_int24(data.battery_manufacture_date, signed=False))
        if data.battery_expiration_date is not None:
            result.extend(DataParser.encode_int24(data.battery_expiration_date, signed=False))
        if data.battery_designed_capacity is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.battery_designed_capacity))
        if data.battery_low_energy is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.battery_low_energy))
        if data.battery_critical_energy is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.battery_critical_energy))
        if data.battery_chemistry is not None:
            result.extend(DataParser.encode_int8(int(data.battery_chemistry), signed=False))
        if data.nominal_voltage is not None:
            result.extend(IEEE11073Parser.encode_sfloat(data.nominal_voltage))
        if data.battery_aggregation_group is not None:
            result.extend(DataParser.encode_int8(data.battery_aggregation_group, signed=False))

        return result
