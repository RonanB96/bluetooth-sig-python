src.bluetooth_sig.gatt.descriptors.characteristic_user_description
==================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.characteristic_user_description

.. autoapi-nested-parse::

   Characteristic User Description Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.characteristic_user_description.CharacteristicUserDescriptionData
   src.bluetooth_sig.gatt.descriptors.characteristic_user_description.CharacteristicUserDescriptionDescriptor


Module Contents
---------------

.. py:class:: CharacteristicUserDescriptionData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic User Description descriptor data.


   .. py:attribute:: description
      :type:  str


.. py:class:: CharacteristicUserDescriptionDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic User Description Descriptor (0x2901).

   Contains a user-readable description of the characteristic.
   UTF-8 encoded string describing the characteristic's purpose.


   .. py:method:: get_description(data: bytes) -> str

      Get the user description string.



