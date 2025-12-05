src.bluetooth_sig.gatt.services.link_loss
=========================================

.. py:module:: src.bluetooth_sig.gatt.services.link_loss

.. autoapi-nested-parse::

   Link Loss Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.link_loss.LinkLossService


Module Contents
---------------

.. py:class:: LinkLossService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Link Loss Service implementation.

   Defines behaviour when a link is lost between two devices.

   Contains characteristics related to link loss alerts:
   - Alert Level - Required


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


