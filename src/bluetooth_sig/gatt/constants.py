"""Shared constants for GATT characteristics and services.

This module provides commonly used constants throughout the Bluetooth SIG
implementation to avoid duplication and ensure consistency.
"""

from __future__ import annotations

# Data type maximum and minimum values
UINT8_MAX = (1 << 8) - 1  # 255
UINT16_MAX = (1 << 16) - 1  # 65535
UINT24_MAX = (1 << 24) - 1  # 16777215
UINT32_MAX = (1 << 32) - 1  # 4294967295

SINT8_MIN = -(1 << 7)  # -128
SINT8_MAX = (1 << 7) - 1  # 127
SINT16_MIN = -(1 << 15)  # -32768
SINT16_MAX = (1 << 15) - 1  # 32767
SINT24_MIN = -(1 << 23)  # -8388608
SINT24_MAX = (1 << 23) - 1  # 8388607
SINT32_MIN = -(1 << 31)  # -2147483648
SINT32_MAX = (1 << 31) - 1  # 2147483647

# Common measurement ranges
PERCENTAGE_MAX = 100  # Maximum percentage value
ABSOLUTE_ZERO_CELSIUS = -273.15  # Absolute zero temperature in Celsius

# Common resolution values
TEMPERATURE_RESOLUTION = 0.01  # Standard temperature resolution (°C)
PRESSURE_RESOLUTION = 0.1  # Standard pressure resolution (Pa)
HUMIDITY_RESOLUTION = 0.01  # Standard humidity resolution (%)
WIND_SPEED_RESOLUTION = 0.01  # Standard wind speed resolution (m/s)
WIND_DIRECTION_RESOLUTION = 0.01  # Standard wind direction resolution (°)
SOUND_PRESSURE_RESOLUTION = 0.1  # Standard sound pressure resolution (dB)

# IEEE 11073 special values for SFLOAT
IEEE11073_NAN = 0x07FF  # Not a Number
IEEE11073_NRES = 0x0800  # Not a valid result
IEEE11073_POSITIVE_INFINITY = 0x07FE  # +INFINITY
IEEE11073_NEGATIVE_INFINITY = 0x0802  # -INFINITY

# Common unit strings
UNIT_CELSIUS = "°C"
UNIT_FAHRENHEIT = "°F"
UNIT_KELVIN = "K"
UNIT_PERCENT = "%"
UNIT_PPM = "ppm"
UNIT_PASCAL = "Pa"
UNIT_HECTOPASCAL = "hPa"
UNIT_METER_PER_SECOND = "m/s"
UNIT_DEGREE = "°"
UNIT_DECIBEL = "dB"
UNIT_VOLT = "V"
UNIT_AMPERE = "A"
UNIT_WATT = "W"
UNIT_JOULE = "J"
UNIT_KILOJOULE = "kJ"
UNIT_TESLA = "T"
UNIT_MICROTESLA = "µT"
UNIT_LUX = "lx"
UNIT_METER = "m"
UNIT_BEATS_PER_MINUTE = "bpm"
UNIT_DBM = "dBm"

# Common flag bit positions
FLAG_BIT_0 = 1 << 0
FLAG_BIT_1 = 1 << 1
FLAG_BIT_2 = 1 << 2
FLAG_BIT_3 = 1 << 3
FLAG_BIT_4 = 1 << 4
FLAG_BIT_5 = 1 << 5
FLAG_BIT_6 = 1 << 6
FLAG_BIT_7 = 1 << 7

# Heart Rate specific constants
HR_FORMAT_UINT8 = 0
HR_FORMAT_UINT16 = 1
HR_SENSOR_CONTACT_SUPPORTED = 1 << 1
HR_SENSOR_CONTACT_DETECTED = 1 << 2
HR_ENERGY_EXPENDED_PRESENT = 1 << 3
HR_RR_INTERVALS_PRESENT = 1 << 4

# RR interval conversion factor (1/1024 seconds)
RR_INTERVAL_RESOLUTION = 1 / 1024

# Common data validation ranges
MAX_CONCENTRATION_PPM = 65535.0  # Maximum concentration in ppm
MAX_TEMPERATURE_CELSIUS = 1000.0  # Maximum reasonable temperature
MAX_PRESSURE_PA = 200000.0  # Maximum atmospheric pressure (2000 hPa)
MAX_POWER_WATTS = 65535.0  # Maximum power in watts
