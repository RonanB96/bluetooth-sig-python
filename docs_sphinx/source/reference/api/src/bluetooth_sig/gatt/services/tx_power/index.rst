src.bluetooth_sig.gatt.services.tx_power
========================================

.. py:module:: src.bluetooth_sig.gatt.services.tx_power

.. autoapi-nested-parse::

   Tx Power Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.tx_power.TxPowerService


Module Contents
---------------

.. py:class:: TxPowerService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Tx Power Service implementation.

   Exposes the current transmit power level of a device.

   Contains characteristics related to transmit power:
   - Tx Power Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


