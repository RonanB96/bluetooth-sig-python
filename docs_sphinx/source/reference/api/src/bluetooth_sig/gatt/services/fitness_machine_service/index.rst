src.bluetooth_sig.gatt.services.fitness_machine_service
=======================================================

.. py:module:: src.bluetooth_sig.gatt.services.fitness_machine_service

.. autoapi-nested-parse::

   Fitness Machine Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.fitness_machine_service.FitnessMachineService


Module Contents
---------------

.. py:class:: FitnessMachineService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Fitness Machine Service implementation.

   Contains characteristics related to fitness machines:
   - Fitness Machine Feature - Mandatory
   - Treadmill Data - Optional
   - Cross Trainer Data - Optional
   - Step Climber Data - Optional
   - Stair Climber Data - Optional
   - Rower Data - Optional
   - Indoor Bike Data - Optional
   - Training Status - Optional
   - Supported Speed Range - Optional
   - Supported Inclination Range - Optional
   - Supported Resistance Level Range - Optional
   - Supported Heart Rate Range - Optional
   - Supported Power Range - Optional
   - Fitness Machine Control Point - Optional
   - Fitness Machine Status - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


