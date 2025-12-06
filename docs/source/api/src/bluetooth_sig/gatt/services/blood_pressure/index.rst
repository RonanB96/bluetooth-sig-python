src.bluetooth_sig.gatt.services.blood_pressure
==============================================

.. py:module:: src.bluetooth_sig.gatt.services.blood_pressure

.. autoapi-nested-parse::

   Blood Pressure Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.blood_pressure.BloodPressureService


Module Contents
---------------

.. py:class:: BloodPressureService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Blood Pressure Service implementation.

   Contains characteristics related to blood pressure measurement:
   - Blood Pressure Measurement - Required
   - Intermediate Cuff Pressure - Optional
   - Blood Pressure Feature - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


