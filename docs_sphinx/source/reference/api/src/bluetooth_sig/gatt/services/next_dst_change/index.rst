src.bluetooth_sig.gatt.services.next_dst_change
===============================================

.. py:module:: src.bluetooth_sig.gatt.services.next_dst_change

.. autoapi-nested-parse::

   Next DST Change Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.next_dst_change.NextDstChangeService


Module Contents
---------------

.. py:class:: NextDstChangeService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Next DST Change Service implementation.

   Exposes the date and time of the next Daylight Saving Time change.

   Contains characteristics related to DST changes:
   - Time with DST - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


