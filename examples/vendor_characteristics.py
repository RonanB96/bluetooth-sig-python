"""Vendor-specific characteristic adapters for Nordic Thingy:52.

This module provides msgspec.Struct-based adapters for Nordic's vendor-specific
GATT characteristics. These follow the same API patterns as SIG characteristics
in bluetooth_sig.gatt.characteristics but for proprietary Nordic UUIDs.

References:
    - Nordic Thingy:52 Firmware Documentation:
      https://nordicsemiconductor.github.io/Nordic-Thingy52-FW/documentation
    - Original BluePy Implementation:
      https://github.com/IanHarvey/bluepy/blob/master/bluepy/thingy52.py

Note:
    These characteristics use Nordic's vendor UUID base:
    EF68XXXX-9B35-4933-9B10-52FFA9740042
"""

from __future__ import annotations

import struct
from typing import Final

import msgspec

# Nordic Thingy:52 vendor UUID base
NORDIC_UUID_BASE: Final[str] = "EF68%04X-9B35-4933-9B10-52FFA9740042"

# Environment Service UUIDs (EF680200-*)
ENVIRONMENT_SERVICE_UUID: Final[str] = NORDIC_UUID_BASE % 0x0200
TEMPERATURE_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0201
PRESSURE_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0202
HUMIDITY_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0203
GAS_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0204
COLOR_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0205

# User Interface Service UUIDs (EF680300-*)
USER_INTERFACE_SERVICE_UUID: Final[str] = NORDIC_UUID_BASE % 0x0300
BUTTON_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0302

# Motion Service UUIDs (EF680400-*)
MOTION_SERVICE_UUID: Final[str] = NORDIC_UUID_BASE % 0x0400
TAP_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0402
ORIENTATION_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0403
QUATERNION_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0404
STEP_COUNTER_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0405
RAW_DATA_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0406
EULER_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0407
ROTATION_MATRIX_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0408
HEADING_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x0409
GRAVITY_VECTOR_CHAR_UUID: Final[str] = NORDIC_UUID_BASE % 0x040A


# ============================================================================
# Environment Service Characteristics
# ============================================================================


class ThingyTemperatureData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 temperature measurement.

    Attributes:
        temperature_celsius: Temperature in degrees Celsius (integer value).
        temperature_decimal: Decimal portion (0-99) for 0.01°C resolution.
    """

    temperature_celsius: int
    temperature_decimal: int


def decode_thingy_temperature(data: bytes) -> ThingyTemperatureData:
    """Decode Nordic Thingy:52 temperature characteristic.

    The temperature is encoded as signed 8-bit integer (whole degrees) followed
    by unsigned 8-bit fractional part (0.01°C resolution).

    Args:
        data: Raw bytes from temperature characteristic (2 bytes).

    Returns:
        Decoded temperature data.

    Raises:
        ValueError: If data length is not exactly 2 bytes.

    Examples:
        >>> data = bytes([0x17, 0x32])  # 23.50°C
        >>> result = decode_thingy_temperature(data)
        >>> result.temperature_celsius
        23
        >>> result.temperature_decimal
        50
    """
    if len(data) != 2:
        raise ValueError(f"Temperature data must be 2 bytes, got {len(data)}")

    temp_int = struct.unpack("<b", data[0:1])[0]  # signed int8
    temp_dec = data[1]  # unsigned int8

    if temp_dec > 99:
        raise ValueError(f"Temperature decimal must be 0-99, got {temp_dec}")

    return ThingyTemperatureData(temperature_celsius=temp_int, temperature_decimal=temp_dec)


class ThingyPressureData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 pressure measurement.

    Attributes:
        pressure_integer: Integer part of pressure in Pascals.
        pressure_decimal: Decimal portion (0-99) for 0.01 Pa resolution.
    """

    pressure_integer: int
    pressure_decimal: int


def decode_thingy_pressure(data: bytes) -> ThingyPressureData:
    """Decode Nordic Thingy:52 pressure characteristic.

    The pressure is encoded as unsigned 32-bit little-endian integer (Pascals)
    followed by unsigned 8-bit decimal part (0.01 Pa resolution).

    Args:
        data: Raw bytes from pressure characteristic (5 bytes).

    Returns:
        Decoded pressure data.

    Raises:
        ValueError: If data length is not exactly 5 bytes.

    Examples:
        >>> data = bytes([0xE0, 0x8A, 0x01, 0x00, 0x32])  # 101088.50 Pa
        >>> result = decode_thingy_pressure(data)
        >>> result.pressure_integer
        101088
        >>> result.pressure_decimal
        50
    """
    if len(data) != 5:
        raise ValueError(f"Pressure data must be 5 bytes, got {len(data)}")

    pressure_int = struct.unpack("<I", data[0:4])[0]  # uint32 little-endian
    pressure_dec = data[4]  # uint8

    if pressure_dec > 99:
        raise ValueError(f"Pressure decimal must be 0-99, got {pressure_dec}")

    return ThingyPressureData(pressure_integer=pressure_int, pressure_decimal=pressure_dec)


class ThingyHumidityData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 humidity measurement.

    Attributes:
        humidity_percent: Relative humidity in percent (0-100).
    """

    humidity_percent: int


def decode_thingy_humidity(data: bytes) -> ThingyHumidityData:
    """Decode Nordic Thingy:52 humidity characteristic.

    The humidity is encoded as unsigned 8-bit integer (0-100%).

    Args:
        data: Raw bytes from humidity characteristic (1 byte).

    Returns:
        Decoded humidity data.

    Raises:
        ValueError: If data length is not exactly 1 byte or value out of range.

    Examples:
        >>> data = bytes([0x41])  # 65%
        >>> result = decode_thingy_humidity(data)
        >>> result.humidity_percent
        65
    """
    if len(data) != 1:
        raise ValueError(f"Humidity data must be 1 byte, got {len(data)}")

    humidity = data[0]

    if humidity > 100:
        raise ValueError(f"Humidity must be 0-100%, got {humidity}")

    return ThingyHumidityData(humidity_percent=humidity)


class ThingyGasData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 gas sensor measurement (eCO2 and TVOC).

    Attributes:
        eco2_ppm: Equivalent CO2 in parts per million (ppm).
        tvoc_ppb: Total Volatile Organic Compounds in parts per billion (ppb).
    """

    eco2_ppm: int
    tvoc_ppb: int


def decode_thingy_gas(data: bytes) -> ThingyGasData:
    """Decode Nordic Thingy:52 gas characteristic (eCO2 and TVOC).

    The gas data is encoded as two unsigned 16-bit little-endian integers:
    - eCO2: Equivalent CO2 in ppm
    - TVOC: Total Volatile Organic Compounds in ppb

    Args:
        data: Raw bytes from gas characteristic (4 bytes).

    Returns:
        Decoded gas sensor data.

    Raises:
        ValueError: If data length is not exactly 4 bytes.

    Examples:
        >>> data = bytes([0x90, 0x01, 0x32, 0x00])  # eCO2: 400 ppm, TVOC: 50 ppb
        >>> result = decode_thingy_gas(data)
        >>> result.eco2_ppm
        400
        >>> result.tvoc_ppb
        50
    """
    if len(data) != 4:
        raise ValueError(f"Gas data must be 4 bytes, got {len(data)}")

    eco2 = struct.unpack("<H", data[0:2])[0]  # uint16 little-endian
    tvoc = struct.unpack("<H", data[2:4])[0]  # uint16 little-endian

    return ThingyGasData(eco2_ppm=eco2, tvoc_ppb=tvoc)


class ThingyColorData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 color sensor measurement (RGBC).

    Attributes:
        red: Red channel value (0-65535).
        green: Green channel value (0-65535).
        blue: Blue channel value (0-65535).
        clear: Clear/ambient light value (0-65535).
    """

    red: int
    green: int
    blue: int
    clear: int


def decode_thingy_color(data: bytes) -> ThingyColorData:
    """Decode Nordic Thingy:52 color characteristic (RGBC).

    The color data is encoded as four unsigned 16-bit little-endian integers
    representing Red, Green, Blue, and Clear (ambient light) channels.

    Args:
        data: Raw bytes from color characteristic (8 bytes).

    Returns:
        Decoded color sensor data.

    Raises:
        ValueError: If data length is not exactly 8 bytes.

    Examples:
        >>> data = bytes([0xFF, 0x00, 0x80, 0x00, 0x40, 0x00, 0x00, 0x01])
        >>> result = decode_thingy_color(data)
        >>> result.red
        255
        >>> result.green
        128
    """
    if len(data) != 8:
        raise ValueError(f"Color data must be 8 bytes, got {len(data)}")

    red = struct.unpack("<H", data[0:2])[0]
    green = struct.unpack("<H", data[2:4])[0]
    blue = struct.unpack("<H", data[4:6])[0]
    clear = struct.unpack("<H", data[6:8])[0]

    return ThingyColorData(red=red, green=green, blue=blue, clear=clear)


# ============================================================================
# User Interface Service Characteristics
# ============================================================================


class ThingyButtonData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 button state.

    Attributes:
        pressed: True if button is pressed, False if released.
    """

    pressed: bool


def decode_thingy_button(data: bytes) -> ThingyButtonData:
    """Decode Nordic Thingy:52 button characteristic.

    The button state is encoded as unsigned 8-bit integer (0=released, 1=pressed).

    Args:
        data: Raw bytes from button characteristic (1 byte).

    Returns:
        Decoded button state.

    Raises:
        ValueError: If data length is not exactly 1 byte or value is invalid.

    Examples:
        >>> data = bytes([0x01])  # Pressed
        >>> result = decode_thingy_button(data)
        >>> result.pressed
        True
    """
    if len(data) != 1:
        raise ValueError(f"Button data must be 1 byte, got {len(data)}")

    state = data[0]

    if state > 1:
        raise ValueError(f"Button state must be 0 or 1, got {state}")

    return ThingyButtonData(pressed=bool(state))


# ============================================================================
# Motion Service Characteristics
# ============================================================================


class ThingyTapData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 tap detection data.

    Attributes:
        direction: Tap direction (0-5: x+, x-, y+, y-, z+, z-).
        count: Tap count (number of taps detected).
    """

    direction: int
    count: int


def decode_thingy_tap(data: bytes) -> ThingyTapData:
    """Decode Nordic Thingy:52 tap characteristic.

    The tap data is encoded as two unsigned 8-bit integers:
    - Direction: 0-5 representing x+, x-, y+, y-, z+, z-
    - Count: Number of taps detected

    Args:
        data: Raw bytes from tap characteristic (2 bytes).

    Returns:
        Decoded tap detection data.

    Raises:
        ValueError: If data length is not exactly 2 bytes or direction invalid.

    Examples:
        >>> data = bytes([0x02, 0x03])  # y+ direction, 3 taps
        >>> result = decode_thingy_tap(data)
        >>> result.direction
        2
        >>> result.count
        3
    """
    if len(data) != 2:
        raise ValueError(f"Tap data must be 2 bytes, got {len(data)}")

    direction = data[0]
    count = data[1]

    if direction > 5:
        raise ValueError(f"Tap direction must be 0-5, got {direction}")

    return ThingyTapData(direction=direction, count=count)


class ThingyOrientationData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 orientation data.

    Attributes:
        orientation: Orientation value (0-2: portrait, landscape, reverse portrait).
    """

    orientation: int


def decode_thingy_orientation(data: bytes) -> ThingyOrientationData:
    """Decode Nordic Thingy:52 orientation characteristic.

    The orientation is encoded as unsigned 8-bit integer:
    - 0: Portrait
    - 1: Landscape
    - 2: Reverse portrait

    Args:
        data: Raw bytes from orientation characteristic (1 byte).

    Returns:
        Decoded orientation data.

    Raises:
        ValueError: If data length is not exactly 1 byte or value invalid.

    Examples:
        >>> data = bytes([0x01])  # Landscape
        >>> result = decode_thingy_orientation(data)
        >>> result.orientation
        1
    """
    if len(data) != 1:
        raise ValueError(f"Orientation data must be 1 byte, got {len(data)}")

    orientation = data[0]

    if orientation > 2:
        raise ValueError(f"Orientation must be 0-2, got {orientation}")

    return ThingyOrientationData(orientation=orientation)


class ThingyQuaternionData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 quaternion data.

    Attributes:
        w: W component (fixed-point, divide by 2^30 for float).
        x: X component (fixed-point, divide by 2^30 for float).
        y: Y component (fixed-point, divide by 2^30 for float).
        z: Z component (fixed-point, divide by 2^30 for float).
    """

    w: int
    x: int
    y: int
    z: int


def decode_thingy_quaternion(data: bytes) -> ThingyQuaternionData:
    """Decode Nordic Thingy:52 quaternion characteristic.

    The quaternion is encoded as four signed 32-bit little-endian integers
    in fixed-point format (divide by 2^30 to get floating-point values).

    Args:
        data: Raw bytes from quaternion characteristic (16 bytes).

    Returns:
        Decoded quaternion data (fixed-point values).

    Raises:
        ValueError: If data length is not exactly 16 bytes.

    Examples:
        >>> data = bytes([0] * 16)  # All zeros
        >>> result = decode_thingy_quaternion(data)
        >>> result.w
        0
    """
    if len(data) != 16:
        raise ValueError(f"Quaternion data must be 16 bytes, got {len(data)}")

    w = struct.unpack("<i", data[0:4])[0]  # int32 little-endian
    x = struct.unpack("<i", data[4:8])[0]
    y = struct.unpack("<i", data[8:12])[0]
    z = struct.unpack("<i", data[12:16])[0]

    return ThingyQuaternionData(w=w, x=x, y=y, z=z)


class ThingyStepCounterData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 step counter data.

    Attributes:
        steps: Total step count.
        time_ms: Time in milliseconds since step counter started.
    """

    steps: int
    time_ms: int


def decode_thingy_step_counter(data: bytes) -> ThingyStepCounterData:
    """Decode Nordic Thingy:52 step counter characteristic.

    The step counter data is encoded as two unsigned 32-bit little-endian integers:
    - Steps: Total step count
    - Time: Milliseconds since counter started

    Args:
        data: Raw bytes from step counter characteristic (8 bytes).

    Returns:
        Decoded step counter data.

    Raises:
        ValueError: If data length is not exactly 8 bytes.

    Examples:
        >>> data = bytes([0x64, 0x00, 0x00, 0x00, 0x10, 0x27, 0x00, 0x00])
        >>> result = decode_thingy_step_counter(data)
        >>> result.steps
        100
        >>> result.time_ms
        10000
    """
    if len(data) != 8:
        raise ValueError(f"Step counter data must be 8 bytes, got {len(data)}")

    steps = struct.unpack("<I", data[0:4])[0]  # uint32
    time_ms = struct.unpack("<I", data[4:8])[0]  # uint32

    return ThingyStepCounterData(steps=steps, time_ms=time_ms)


class ThingyRawMotionData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 raw motion sensor data (accelerometer, gyroscope, compass).

    Attributes:
        accel_x: Accelerometer X-axis (raw 16-bit value).
        accel_y: Accelerometer Y-axis (raw 16-bit value).
        accel_z: Accelerometer Z-axis (raw 16-bit value).
        gyro_x: Gyroscope X-axis (raw 16-bit value).
        gyro_y: Gyroscope Y-axis (raw 16-bit value).
        gyro_z: Gyroscope Z-axis (raw 16-bit value).
        compass_x: Compass X-axis (raw 16-bit value).
        compass_y: Compass Y-axis (raw 16-bit value).
        compass_z: Compass Z-axis (raw 16-bit value).
    """

    accel_x: int
    accel_y: int
    accel_z: int
    gyro_x: int
    gyro_y: int
    gyro_z: int
    compass_x: int
    compass_y: int
    compass_z: int


def decode_thingy_raw_motion(data: bytes) -> ThingyRawMotionData:
    """Decode Nordic Thingy:52 raw motion data characteristic.

    The raw motion data contains 9 signed 16-bit little-endian integers:
    - Accelerometer (x, y, z)
    - Gyroscope (x, y, z)
    - Compass/Magnetometer (x, y, z)

    Args:
        data: Raw bytes from raw motion characteristic (18 bytes).

    Returns:
        Decoded raw motion sensor data.

    Raises:
        ValueError: If data length is not exactly 18 bytes.

    Examples:
        >>> data = bytes([0] * 18)
        >>> result = decode_thingy_raw_motion(data)
        >>> result.accel_x
        0
    """
    if len(data) != 18:
        raise ValueError(f"Raw motion data must be 18 bytes, got {len(data)}")

    accel_x = struct.unpack("<h", data[0:2])[0]  # int16
    accel_y = struct.unpack("<h", data[2:4])[0]
    accel_z = struct.unpack("<h", data[4:6])[0]
    gyro_x = struct.unpack("<h", data[6:8])[0]
    gyro_y = struct.unpack("<h", data[8:10])[0]
    gyro_z = struct.unpack("<h", data[10:12])[0]
    compass_x = struct.unpack("<h", data[12:14])[0]
    compass_y = struct.unpack("<h", data[14:16])[0]
    compass_z = struct.unpack("<h", data[16:18])[0]

    return ThingyRawMotionData(
        accel_x=accel_x,
        accel_y=accel_y,
        accel_z=accel_z,
        gyro_x=gyro_x,
        gyro_y=gyro_y,
        gyro_z=gyro_z,
        compass_x=compass_x,
        compass_y=compass_y,
        compass_z=compass_z,
    )


class ThingyEulerData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 Euler angles data.

    Attributes:
        roll: Roll angle in degrees (fixed-point, divide by 65536 for float).
        pitch: Pitch angle in degrees (fixed-point, divide by 65536 for float).
        yaw: Yaw angle in degrees (fixed-point, divide by 65536 for float).
    """

    roll: int
    pitch: int
    yaw: int


def decode_thingy_euler(data: bytes) -> ThingyEulerData:
    """Decode Nordic Thingy:52 Euler angles characteristic.

    The Euler angles are encoded as three signed 32-bit little-endian integers
    in fixed-point format (divide by 65536 to get degrees).

    Args:
        data: Raw bytes from Euler characteristic (12 bytes).

    Returns:
        Decoded Euler angles (fixed-point values).

    Raises:
        ValueError: If data length is not exactly 12 bytes.

    Examples:
        >>> data = bytes([0] * 12)
        >>> result = decode_thingy_euler(data)
        >>> result.roll
        0
    """
    if len(data) != 12:
        raise ValueError(f"Euler data must be 12 bytes, got {len(data)}")

    roll = struct.unpack("<i", data[0:4])[0]
    pitch = struct.unpack("<i", data[4:8])[0]
    yaw = struct.unpack("<i", data[8:12])[0]

    return ThingyEulerData(roll=roll, pitch=pitch, yaw=yaw)


class ThingyRotationMatrixData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 rotation matrix data (3x3 matrix).

    Attributes:
        m11: Matrix element [1,1] (fixed-point, divide by 32768 for float).
        m12: Matrix element [1,2].
        m13: Matrix element [1,3].
        m21: Matrix element [2,1].
        m22: Matrix element [2,2].
        m23: Matrix element [2,3].
        m31: Matrix element [3,1].
        m32: Matrix element [3,2].
        m33: Matrix element [3,3].
    """

    m11: int
    m12: int
    m13: int
    m21: int
    m22: int
    m23: int
    m31: int
    m32: int
    m33: int


def decode_thingy_rotation_matrix(data: bytes) -> ThingyRotationMatrixData:
    """Decode Nordic Thingy:52 rotation matrix characteristic.

    The rotation matrix is encoded as nine signed 16-bit little-endian integers
    representing a 3x3 rotation matrix in fixed-point format.

    Args:
        data: Raw bytes from rotation matrix characteristic (18 bytes).

    Returns:
        Decoded rotation matrix (fixed-point values).

    Raises:
        ValueError: If data length is not exactly 18 bytes.

    Examples:
        >>> data = bytes([0] * 18)
        >>> result = decode_thingy_rotation_matrix(data)
        >>> result.m11
        0
    """
    if len(data) != 18:
        raise ValueError(f"Rotation matrix data must be 18 bytes, got {len(data)}")

    m11 = struct.unpack("<h", data[0:2])[0]
    m12 = struct.unpack("<h", data[2:4])[0]
    m13 = struct.unpack("<h", data[4:6])[0]
    m21 = struct.unpack("<h", data[6:8])[0]
    m22 = struct.unpack("<h", data[8:10])[0]
    m23 = struct.unpack("<h", data[10:12])[0]
    m31 = struct.unpack("<h", data[12:14])[0]
    m32 = struct.unpack("<h", data[14:16])[0]
    m33 = struct.unpack("<h", data[16:18])[0]

    return ThingyRotationMatrixData(
        m11=m11,
        m12=m12,
        m13=m13,
        m21=m21,
        m22=m22,
        m23=m23,
        m31=m31,
        m32=m32,
        m33=m33,
    )


class ThingyHeadingData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 compass heading data.

    Attributes:
        heading: Compass heading in degrees (fixed-point, divide by 65536 for float).
    """

    heading: int


def decode_thingy_heading(data: bytes) -> ThingyHeadingData:
    """Decode Nordic Thingy:52 heading characteristic.

    The heading is encoded as signed 32-bit little-endian integer in fixed-point
    format (divide by 65536 to get degrees).

    Args:
        data: Raw bytes from heading characteristic (4 bytes).

    Returns:
        Decoded heading (fixed-point value).

    Raises:
        ValueError: If data length is not exactly 4 bytes.

    Examples:
        >>> data = bytes([0x00, 0x00, 0x01, 0x00])  # 65536 = 1 degree
        >>> result = decode_thingy_heading(data)
        >>> result.heading
        65536
    """
    if len(data) != 4:
        raise ValueError(f"Heading data must be 4 bytes, got {len(data)}")

    heading = struct.unpack("<i", data[0:4])[0]

    return ThingyHeadingData(heading=heading)


class ThingyGravityVectorData(msgspec.Struct, frozen=True):
    """Nordic Thingy:52 gravity vector data.

    Attributes:
        x: X component of gravity vector (m/s²).
        y: Y component of gravity vector (m/s²).
        z: Z component of gravity vector (m/s²).
    """

    x: float
    y: float
    z: float


def decode_thingy_gravity_vector(data: bytes) -> ThingyGravityVectorData:
    """Decode Nordic Thingy:52 gravity vector characteristic.

    The gravity vector is encoded as three 32-bit little-endian floats
    representing acceleration in m/s² for each axis.

    Args:
        data: Raw bytes from gravity vector characteristic (12 bytes).

    Returns:
        Decoded gravity vector.

    Raises:
        ValueError: If data length is not exactly 12 bytes.

    Examples:
        >>> data = bytes([0] * 12)
        >>> result = decode_thingy_gravity_vector(data)
        >>> result.x
        0.0
    """
    if len(data) != 12:
        raise ValueError(f"Gravity vector data must be 12 bytes, got {len(data)}")

    x = struct.unpack("<f", data[0:4])[0]
    y = struct.unpack("<f", data[4:8])[0]
    z = struct.unpack("<f", data[8:12])[0]

    return ThingyGravityVectorData(x=x, y=y, z=z)
