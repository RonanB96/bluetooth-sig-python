src.bluetooth_sig.gatt.services.generic_access
==============================================

.. py:module:: src.bluetooth_sig.gatt.services.generic_access

.. autoapi-nested-parse::

   Generic Access Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.generic_access.GenericAccessService


Module Contents
---------------

.. py:class:: GenericAccessService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Generic Access Service implementation.

   Contains characteristics that expose basic device access information:
   - Device Name - Required
   - Appearance - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


