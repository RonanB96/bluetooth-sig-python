src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format
=====================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format

.. autoapi-nested-parse::

   Characteristic Presentation Format Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.CharacteristicPresentationFormatData
   src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.CharacteristicPresentationFormatDescriptor
   src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.FormatNamespace
   src.bluetooth_sig.gatt.descriptors.characteristic_presentation_format.FormatType


Module Contents
---------------

.. py:class:: CharacteristicPresentationFormatData

   Bases: :py:obj:`msgspec.Struct`


   Characteristic Presentation Format descriptor data.


   .. py:attribute:: description
      :type:  int


   .. py:attribute:: exponent
      :type:  int


   .. py:attribute:: format
      :type:  int


   .. py:attribute:: namespace
      :type:  int


   .. py:attribute:: unit
      :type:  int


.. py:class:: CharacteristicPresentationFormatDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Characteristic Presentation Format Descriptor (0x2904).

   Describes how characteristic values should be presented to users.
   Contains format, exponent, unit, namespace, and description information.


   .. py:method:: get_description(data: bytes) -> int

      Get the description identifier.



   .. py:method:: get_exponent(data: bytes) -> int

      Get the exponent for scaling.



   .. py:method:: get_format_type(data: bytes) -> int

      Get the format type.



   .. py:method:: get_namespace(data: bytes) -> int

      Get the namespace identifier.



   .. py:method:: get_unit(data: bytes) -> int

      Get the unit identifier.



.. py:class:: FormatNamespace

   Bases: :py:obj:`enum.IntEnum`


   Format namespace values for Characteristic Presentation Format.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BLUETOOTH_SIG_ASSIGNED_NUMBERS
      :value: 1



   .. py:attribute:: RESERVED
      :value: 2



.. py:class:: FormatType

   Bases: :py:obj:`enum.IntEnum`


   Format type values for Characteristic Presentation Format.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: BOOLEAN
      :value: 1



   .. py:attribute:: DUINT16
      :value: 24



   .. py:attribute:: FLOAT
      :value: 23



   .. py:attribute:: FLOAT32
      :value: 20



   .. py:attribute:: FLOAT64
      :value: 21



   .. py:attribute:: SFLOAT
      :value: 22



   .. py:attribute:: SINT12
      :value: 13



   .. py:attribute:: SINT128
      :value: 19



   .. py:attribute:: SINT16
      :value: 14



   .. py:attribute:: SINT24
      :value: 15



   .. py:attribute:: SINT32
      :value: 16



   .. py:attribute:: SINT48
      :value: 17



   .. py:attribute:: SINT64
      :value: 18



   .. py:attribute:: SINT8
      :value: 12



   .. py:attribute:: STRUCT
      :value: 27



   .. py:attribute:: UINT12
      :value: 5



   .. py:attribute:: UINT128
      :value: 11



   .. py:attribute:: UINT16
      :value: 6



   .. py:attribute:: UINT2
      :value: 2



   .. py:attribute:: UINT24
      :value: 7



   .. py:attribute:: UINT32
      :value: 8



   .. py:attribute:: UINT4
      :value: 3



   .. py:attribute:: UINT48
      :value: 9



   .. py:attribute:: UINT64
      :value: 10



   .. py:attribute:: UINT8
      :value: 4



   .. py:attribute:: UTF16S
      :value: 26



   .. py:attribute:: UTF8S
      :value: 25



