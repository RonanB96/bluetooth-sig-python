src.bluetooth_sig.gatt.descriptors.base
=======================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.base

.. autoapi-nested-parse::

   Base class for GATT descriptors.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.base.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor
   src.bluetooth_sig.gatt.descriptors.base.RangeDescriptorMixin


Module Contents
---------------

.. py:class:: BaseDescriptor

   Bases: :py:obj:`abc.ABC`


   Base class for all GATT descriptors.

   Automatically resolves UUID and name from Bluetooth SIG registry.
   Provides parsing capabilities for descriptor values.

   .. attribute:: _descriptor_name

      Optional explicit descriptor name for registry lookup.

   .. attribute:: _writable

      Whether this descriptor type supports write operations.
      Override to True in writable descriptor subclasses (CCCD, SCCD).

   .. note::

      Most descriptors are read-only per Bluetooth SIG specification.
      Some like CCCD (0x2902) and SCCD (0x2903) support writes.

   Initialize descriptor with resolved information.


   .. py:method:: is_writable() -> bool

      Check if descriptor type supports write operations.

      :returns: True if descriptor type supports writes, False otherwise.

      .. note::

         Only checks descriptor type, not runtime permissions or security.
         Example writable descriptors (CCCD, SCCD) override `_writable = True`.



   .. py:method:: parse_value(data: bytes) -> src.bluetooth_sig.types.DescriptorData

      Parse raw descriptor data into structured format.

      :param data: Raw bytes from the descriptor read

      :returns: DescriptorData object with parsed value and metadata



   .. py:property:: info
      :type: src.bluetooth_sig.types.DescriptorInfo


      Get the descriptor information.


   .. py:property:: name
      :type: str


      Get the descriptor name.


   .. py:property:: uuid
      :type: src.bluetooth_sig.types.uuid.BluetoothUUID


      Get the descriptor UUID.


.. py:class:: RangeDescriptorMixin

   Mixin for descriptors that provide min/max value validation.


   .. py:method:: get_max_value(data: bytes) -> int | float

      Get the maximum valid value.

      :param data: Raw descriptor data

      :returns: Maximum valid value for the characteristic



   .. py:method:: get_min_value(data: bytes) -> int | float

      Get the minimum valid value.

      :param data: Raw descriptor data

      :returns: Minimum valid value for the characteristic



   .. py:method:: is_value_in_range(data: bytes, value: int | float) -> bool

      Check if a value is within the valid range.

      :param data: Raw descriptor data
      :param value: Value to check

      :returns: True if value is within [min_value, max_value] range



.. py:data:: logger

