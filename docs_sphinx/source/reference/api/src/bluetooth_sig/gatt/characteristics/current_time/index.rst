src.bluetooth_sig.gatt.characteristics.current_time
===================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.current_time

.. autoapi-nested-parse::

   Current Time characteristic (0x2A2B) implementation.

   Represents exact time with date, time, fractions, and adjustment reasons.
   Used by Current Time Service (0x1805).

   Based on Bluetooth SIG GATT Specification:
   - Current Time: 10 bytes (Date Time + Day of Week + Fractions256 + Adjust Reason)
   - Date Time: Year (uint16) + Month + Day + Hours + Minutes + Seconds (7 bytes)
   - Day of Week: uint8 (1=Monday to 7=Sunday, 0=Unknown)
   - Fractions256: uint8 (0-255, representing 1/256 fractions of a second)
   - Adjust Reason: uint8 bitfield (Manual Update, External Reference, Time Zone, DST)



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.current_time.CurrentTimeCharacteristic


Module Contents
---------------

.. py:class:: CurrentTimeCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Current Time characteristic (0x2A2B).

   Represents exact time with date, time, fractions, and adjustment reasons.
   Used by Current Time Service (0x1805).

   Structure (10 bytes):
   - Year: uint16 (1582-9999, 0=unknown)
   - Month: uint8 (1-12, 0=unknown)
   - Day: uint8 (1-31, 0=unknown)
   - Hours: uint8 (0-23)
   - Minutes: uint8 (0-59)
   - Seconds: uint8 (0-59)
   - Day of Week: uint8 (0=unknown, 1=Monday...7=Sunday)
   - Fractions256: uint8 (0-255, representing 1/256 fractions of a second)
   - Adjust Reason: uint8 bitfield


