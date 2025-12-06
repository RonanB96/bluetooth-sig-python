src.bluetooth_sig.gatt.characteristics.utils.data_validator
===========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.data_validator

.. autoapi-nested-parse::

   Data validation and integrity checking utilities.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.data_validator.DataValidator


Module Contents
---------------

.. py:class:: DataValidator

   Utility class for data validation and integrity checking.


   .. py:method:: validate_concentration_range(value: float, max_ppm: float = MAX_CONCENTRATION_PPM) -> None
      :staticmethod:


      Validate concentration value is in acceptable range.



   .. py:method:: validate_data_length(data: bytearray, expected_min: int, expected_max: int | None = None) -> None
      :staticmethod:


      Validate data length against expected range.



   .. py:method:: validate_enum_value(value: int, enum_class: type[enum.IntEnum]) -> None
      :staticmethod:


      Validate that a value is a valid member of an IntEnum.



   .. py:method:: validate_percentage(value: int | float, allow_over_100: bool = False) -> None
      :staticmethod:


      Validate percentage value (0-100% or 0-200% for some characteristics).



   .. py:method:: validate_power_range(value: int | float, max_watts: float = MAX_POWER_WATTS) -> None
      :staticmethod:


      Validate power measurement range.



   .. py:method:: validate_range(value: int | float, min_val: int | float, max_val: int | float) -> None
      :staticmethod:


      Validate that a value is within the specified range.



   .. py:method:: validate_temperature_range(value: float, min_celsius: float = ABSOLUTE_ZERO_CELSIUS, max_celsius: float = MAX_TEMPERATURE_CELSIUS) -> None
      :staticmethod:


      Validate temperature is in physically reasonable range.



