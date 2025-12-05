src.bluetooth_sig.gatt.services.user_data
=========================================

.. py:module:: src.bluetooth_sig.gatt.services.user_data

.. autoapi-nested-parse::

   User Data Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.user_data.UserDataService


Module Contents
---------------

.. py:class:: UserDataService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   User Data Service implementation.

   Contains characteristics related to user profile and fitness data:
   - First Name - Optional
   - Last Name - Optional
   - Email Address - Optional
   - Age - Optional
   - Date of Birth - Optional
   - Gender - Optional
   - Weight - Optional
   - Height - Optional
   - VO2 Max - Optional
   - Heart Rate Max - Optional
   - Resting Heart Rate - Optional
   - Maximum Recommended Heart Rate - Optional
   - Aerobic Threshold - Optional
   - Anaerobic Threshold - Optional
   - Sport Type for Aerobic and Anaerobic Thresholds - Optional
   - Date of Threshold Assessment - Optional
   - Waist Circumference - Optional
   - Hip Circumference - Optional
   - Fat Burn Heart Rate Lower Limit - Optional
   - Fat Burn Heart Rate Upper Limit - Optional
   - Aerobic Heart Rate Lower Limit - Optional
   - Aerobic Heart Rate Upper Limit - Optional
   - Anaerobic Heart Rate Lower Limit - Optional
   - Anaerobic Heart Rate Upper Limit - Optional
   - Two Zone Heart Rate Limits - Optional
   - Three Zone Heart Rate Limits - Optional
   - Four Zone Heart Rate Limits - Optional
   - Five Zone Heart Rate Limits - Optional
   - High Intensity Exercise Threshold - Optional
   - Activity Goal - Optional
   - Sedentary Interval Notification - Optional
   - Caloric Intake - Optional
   - Stride Length - Optional
   - Preferred Units - Optional
   - Language - Optional
   - Handedness - Optional
   - Device Wearing Position - Optional
   - Middle Name - Optional
   - High Resolution Height - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


