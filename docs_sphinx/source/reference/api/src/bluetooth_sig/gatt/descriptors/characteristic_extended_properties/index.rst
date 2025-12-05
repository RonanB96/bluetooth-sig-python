src.bluetooth_sig.gatt.descriptors.characteristic_extended_properties
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.characteristic_extended_properties

.. autoapi-nested-parse::

   Characteristic Extended Properties Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.characteristic_extended_properties.ExtendedPropertiesFlags
   src.bluetooth_sig.gatt.descriptors.characteristic_extended_properties.CharacteristicExtendedPropertiesData
   src.bluetooth_sig.gatt.descriptors.characteristic_extended_properties.CharacteristicExtendedPropertiesDescriptor


Module Contents
---------------

.. py:class:: ExtendedPropertiesFlags

   Bases: :py:obj:`enum.IntFlag`


   Characteristic Extended Properties flags.


   .. py:attribute:: RELIABLE_WRITE
      :value: 1



   .. py:attribute:: WRITABLE_AUXILIARIES
      :value: 2



.. py:class:: CharacteristicExtendedPropertiesData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Extended Properties descriptor data.


   .. py:attribute:: reliable_write
      :type:  bool


   .. py:attribute:: writable_auxiliaries
      :type:  bool


.. py:class:: CharacteristicExtendedPropertiesDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Extended Properties Descriptor (0x2900).

   Defines extended properties for a characteristic using bit flags.
   Indicates support for reliable writes and writable auxiliaries.


   .. py:method:: supports_reliable_write(data: bytes) -> bool

      Check if reliable write is supported.



   .. py:method:: supports_writable_auxiliaries(data: bytes) -> bool

      Check if writable auxiliaries are supported.



