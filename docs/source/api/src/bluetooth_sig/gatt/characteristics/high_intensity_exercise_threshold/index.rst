src.bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold
========================================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold

.. autoapi-nested-parse::

   High Intensity Exercise Threshold characteristic (0x2B4D).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.high_intensity_exercise_threshold.HighIntensityExerciseThresholdCharacteristic


Module Contents
---------------

.. py:class:: HighIntensityExerciseThresholdCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, validation: ValidationConfig | None = None, properties: list[src.bluetooth_sig.types.gatt_enums.GattProperty] | None = None)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   High Intensity Exercise Threshold characteristic (0x2B4D).

   org.bluetooth.characteristic.high_intensity_exercise_threshold

   High Intensity Exercise Threshold characteristic.

   Initialize characteristic with structured configuration.

   :param info: Complete characteristic information (optional for SIG characteristics)
   :param validation: Validation constraints configuration (optional)
   :param properties: Runtime BLE properties discovered from device (optional)


