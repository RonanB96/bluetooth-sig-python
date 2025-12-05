src.bluetooth_sig.gatt.validation
=================================

.. py:module:: src.bluetooth_sig.gatt.validation

.. autoapi-nested-parse::

   Enhanced validation utilities for strict type checking and data validation.

   This module provides additional validation capabilities beyond the basic
   utils, focusing on strict type safety and comprehensive data integrity
   checks.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.validation.T
   src.bluetooth_sig.gatt.validation.HEART_RATE_VALIDATOR
   src.bluetooth_sig.gatt.validation.BATTERY_VALIDATOR
   src.bluetooth_sig.gatt.validation.TEMPERATURE_VALIDATOR


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.validation.ValidationRule
   src.bluetooth_sig.gatt.validation.StrictValidator
   src.bluetooth_sig.gatt.validation.CommonValidators


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.gatt.validation.create_range_validator
   src.bluetooth_sig.gatt.validation.validate_measurement_data


Module Contents
---------------

.. py:data:: T

.. py:class:: ValidationRule

   Bases: :py:obj:`msgspec.Struct`


   Represents a validation rule with optional custom validator.


   .. py:attribute:: field_name
      :type:  str


   .. py:attribute:: expected_type
      :type:  type | tuple[type, Ellipsis]


   .. py:attribute:: min_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: max_value
      :type:  int | float | None
      :value: None



   .. py:attribute:: custom_validator
      :type:  Callable[[Any], bool] | None
      :value: None



   .. py:attribute:: error_message
      :type:  str | None
      :value: None



   .. py:method:: validate(value: Any) -> None

      Apply this validation rule to a value.



.. py:class:: StrictValidator

   Bases: :py:obj:`msgspec.Struct`


   Strict validation engine for complex data structures.


   .. py:attribute:: rules
      :type:  dict[str, ValidationRule]


   .. py:method:: add_rule(rule: ValidationRule) -> None

      Add a validation rule.



   .. py:method:: validate_dict(data: dict[str, Any]) -> None

      Validate a dictionary against all rules.



   .. py:method:: validate_object(obj: Any) -> None

      Validate an object's attributes against all rules.



.. py:class:: CommonValidators

   Collection of commonly used validation functions.


   .. py:method:: is_positive(value: int | float) -> bool
      :staticmethod:


      Check if value is positive.



   .. py:method:: is_non_negative(value: int | float) -> bool
      :staticmethod:


      Check if value is non-negative.



   .. py:method:: is_valid_percentage(value: int | float) -> bool
      :staticmethod:


      Check if value is a valid percentage (0-100).



   .. py:method:: is_valid_extended_percentage(value: int | float) -> bool
      :staticmethod:


      Check if value is a valid extended percentage (0-200).



   .. py:method:: is_physical_temperature(value: float) -> bool
      :staticmethod:


      Check if temperature is physically reasonable.



   .. py:method:: is_valid_concentration(value: float) -> bool
      :staticmethod:


      Check if concentration is in valid range.



   .. py:method:: is_valid_power(value: int | float) -> bool
      :staticmethod:


      Check if power value is reasonable.



   .. py:method:: is_valid_heart_rate(value: int) -> bool
      :staticmethod:


      Check if heart rate is in human range.



   .. py:method:: is_valid_battery_level(value: int) -> bool
      :staticmethod:


      Check if battery level is valid percentage.



   .. py:method:: is_ieee11073_special_value(value: int) -> bool
      :staticmethod:


      Check if value is a valid IEEE 11073 special value.



.. py:data:: HEART_RATE_VALIDATOR

.. py:data:: BATTERY_VALIDATOR

.. py:data:: TEMPERATURE_VALIDATOR

.. py:function:: create_range_validator(field_name: str, expected_type: type, min_value: int | float | None = None, max_value: int | float | None = None, custom_validator: Callable[[Any], bool] | None = None) -> StrictValidator

   Factory function to create a validator for a specific range.


.. py:function:: validate_measurement_data(data: dict[str, Any], measurement_type: str) -> dict[str, Any]

   Validate measurement data based on type and return validated data.


