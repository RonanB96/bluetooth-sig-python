src.bluetooth_sig.types.registry.descriptor_types
=================================================

.. py:module:: src.bluetooth_sig.types.registry.descriptor_types

.. autoapi-nested-parse::

   Data types for Bluetooth SIG descriptors.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.descriptor_types.DescriptorData
   src.bluetooth_sig.types.registry.descriptor_types.DescriptorInfo


Module Contents
---------------

.. py:class:: DescriptorData

   Bases: :py:obj:`msgspec.Struct`


   Parsed descriptor data with validation results.


   .. py:attribute:: error_message
      :type:  str
      :value: ''



   .. py:attribute:: info
      :type:  DescriptorInfo


   .. py:property:: name
      :type: str


      Get the descriptor name from info.


   .. py:attribute:: parse_success
      :type:  bool
      :value: False



   .. py:attribute:: raw_data
      :type:  bytes
      :value: b''



   .. py:property:: uuid
      :type: bluetooth_sig.types.uuid.BluetoothUUID


      Get the descriptor UUID from info.


   .. py:attribute:: value
      :type:  Any | None
      :value: None



.. py:class:: DescriptorInfo

   Bases: :py:obj:`bluetooth_sig.types.base_types.SIGInfo`


   Information about a Bluetooth descriptor.


   .. py:attribute:: data_format
      :type:  str
      :value: ''



   .. py:attribute:: has_structured_data
      :type:  bool
      :value: False



