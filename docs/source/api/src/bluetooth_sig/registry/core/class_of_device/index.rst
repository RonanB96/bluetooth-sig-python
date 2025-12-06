src.bluetooth_sig.registry.core.class_of_device
===============================================

.. py:module:: src.bluetooth_sig.registry.core.class_of_device

.. autoapi-nested-parse::

   Registry for Class of Device decoding.

   This module provides a registry for decoding 24-bit Class of Device (CoD)
   values from Classic Bluetooth into human-readable device classifications
   including major/minor device classes and service classes.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.core.class_of_device.class_of_device_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.core.class_of_device.ClassOfDeviceRegistry
   src.bluetooth_sig.registry.core.class_of_device.CoDBitMask
   src.bluetooth_sig.registry.core.class_of_device.CoDBitShift


Module Contents
---------------

.. py:class:: ClassOfDeviceRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseGenericRegistry`\ [\ :py:obj:`bluetooth_sig.types.registry.class_of_device.ClassOfDeviceInfo`\ ]


   Registry for Class of Device decoding with lazy loading.

   This registry loads Class of Device mappings from the Bluetooth SIG
   assigned_numbers YAML file and provides methods to decode 24-bit CoD
   values into human-readable device classification information.

   The registry uses lazy loading - the YAML file is only parsed on the first
   decode call. This improves startup time and reduces memory usage when the
   registry is not needed.

   CoD Structure (24 bits):
       Bits 23-13: Service Class (11 bits, bit mask)
       Bits 12-8:  Major Device Class (5 bits)
       Bits 7-2:   Minor Device Class (6 bits)
       Bits 1-0:   Format Type (always 0b00)

   Thread Safety:
       This registry is thread-safe. Multiple threads can safely call
       decode_class_of_device() concurrently.

   .. admonition:: Example

      >>> registry = ClassOfDeviceRegistry()
      >>> info = registry.decode_class_of_device(0x02010C)
      >>> print(info.full_description)  # "Computer: Laptop (Networking)"
      >>> print(info.major_class)  # "Computer"
      >>> print(info.minor_class)  # "Laptop"
      >>> print(info.service_classes)  # ["Networking"]

   Initialize the registry with lazy loading.


   .. py:method:: decode_class_of_device(cod: int) -> bluetooth_sig.types.registry.class_of_device.ClassOfDeviceInfo

      Decode 24-bit Class of Device value.

      Extracts and decodes the major/minor device classes and service classes
      from a 24-bit CoD value. Lazy loads the registry data on first call.

      :param cod: 24-bit Class of Device value from advertising data

      :returns: ClassOfDeviceInfo with decoded device classification

      .. admonition:: Examples

         >>> registry = ClassOfDeviceRegistry()
         >>> # Computer (major=1), Laptop (minor=3), Networking service (bit 17)
         >>> info = registry.decode_class_of_device(0x02010C)
         >>> info.major_class
         'Computer (desktop, notebook, PDA, organizer, ...)'
         >>> info.minor_class
         'Laptop'
         >>> info.service_classes
         ['Networking (LAN, Ad hoc, ...)']



.. py:class:: CoDBitMask

   Bases: :py:obj:`enum.IntFlag`


   Bit masks for extracting Class of Device fields.

   CoD Structure (24 bits):
       Bits 23-13: Service Class (11 bits, bit mask)
       Bits 12-8:  Major Device Class (5 bits)
       Bits 7-2:   Minor Device Class (6 bits)
       Bits 1-0:   Format Type (always 0b00)

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: FORMAT_TYPE
      :value: 3



   .. py:attribute:: MAJOR_CLASS
      :value: 7936



   .. py:attribute:: MINOR_CLASS
      :value: 252



   .. py:attribute:: SERVICE_CLASS
      :value: 16769024



.. py:class:: CoDBitShift

   Bases: :py:obj:`enum.IntEnum`


   Bit shift values for Class of Device fields.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: MAJOR_CLASS
      :value: 8



   .. py:attribute:: MINOR_CLASS
      :value: 2



   .. py:attribute:: SERVICE_CLASS
      :value: 13



.. py:data:: class_of_device_registry

