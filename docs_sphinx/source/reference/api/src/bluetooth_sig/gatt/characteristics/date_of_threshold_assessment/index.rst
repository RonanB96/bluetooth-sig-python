src.bluetooth_sig.gatt.characteristics.date_of_threshold_assessment
===================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.date_of_threshold_assessment

.. autoapi-nested-parse::

   Date of Threshold Assessment characteristic (0x2A86).



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.date_of_threshold_assessment.DateOfThresholdAssessmentData


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.date_of_threshold_assessment.DateOfThresholdAssessmentCharacteristic


Module Contents
---------------

.. py:data:: DateOfThresholdAssessmentData

.. py:class:: DateOfThresholdAssessmentCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Date of Threshold Assessment characteristic (0x2A86).

   org.bluetooth.characteristic.date_of_threshold_assessment

   Date of Threshold Assessment characteristic.


   .. py:method:: decode_value(data: bytearray, ctx: src.bluetooth_sig.gatt.context.CharacteristicContext | None = None) -> DateOfThresholdAssessmentData

      Decode Date of Threshold Assessment from raw bytes.

      :param data: Raw bytes from BLE characteristic (4 bytes)
      :param ctx: Optional context for parsing

      :returns: DateOfThresholdAssessmentData with year, month, day

      :raises InsufficientDataError: If data length is not exactly 4 bytes



   .. py:method:: encode_value(data: DateOfThresholdAssessmentData) -> bytearray

      Encode Date of Threshold Assessment to bytes.

      :param data: DateOfThresholdAssessmentData to encode

      :returns: Encoded bytes (4 bytes)

      :raises ValueRangeError: If year, month, or day are out of valid range



