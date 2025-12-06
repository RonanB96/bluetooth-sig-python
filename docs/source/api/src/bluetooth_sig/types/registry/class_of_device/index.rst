src.bluetooth_sig.types.registry.class_of_device
================================================

.. py:module:: src.bluetooth_sig.types.registry.class_of_device

.. autoapi-nested-parse::

   Class of Device data structures for Classic Bluetooth.

   This module provides data structures for representing and decoding the 24-bit
   Class of Device (CoD) field used in Classic Bluetooth for device classification.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.class_of_device.ClassOfDeviceInfo
   src.bluetooth_sig.types.registry.class_of_device.CodServiceClassInfo
   src.bluetooth_sig.types.registry.class_of_device.MajorDeviceClassInfo
   src.bluetooth_sig.types.registry.class_of_device.MinorDeviceClassInfo


Module Contents
---------------

.. py:class:: ClassOfDeviceInfo

   Bases: :py:obj:`msgspec.Struct`


   Decoded Class of Device information.

   Represents the decoded classification information from a 24-bit CoD field,
   including major/minor device classes and service classes.

   .. attribute:: major_class

      Major device class name (e.g., "Computer", "Phone")

   .. attribute:: minor_class

      Minor device class name (e.g., "Laptop", "Smartphone"), or None

   .. attribute:: service_classes

      List of service class names (e.g., ["Networking", "Audio"])

   .. attribute:: raw_value

      Original 24-bit CoD value


   .. py:property:: full_description
      :type: str


      Get full device description combining major, minor, and services.

      :returns: Laptop (Networking, Audio)"
      :rtype: Human-readable description like "Computer

      .. admonition:: Examples

         >>> info = ClassOfDeviceInfo(
         ...     major_class=[MajorDeviceClassInfo(value=1, name="Computer")],
         ...     minor_class=[MinorDeviceClassInfo(value=3, name="Laptop", major_class=1)],
         ...     service_classes=["Networking"],
         ...     raw_value=0x02010C,
         ... )
         >>> info.full_description
         'Computer: Laptop (Networking)'


   .. py:attribute:: major_class
      :type:  list[MajorDeviceClassInfo] | None


   .. py:attribute:: minor_class
      :type:  list[MinorDeviceClassInfo] | None


   .. py:attribute:: raw_value
      :type:  int


   .. py:attribute:: service_classes
      :type:  list[str]


.. py:class:: CodServiceClassInfo

   Bases: :py:obj:`msgspec.Struct`


   Service class information from Class of Device field.

   .. attribute:: bit_position

      Bit position in the CoD field (13-23)

   .. attribute:: name

      Human-readable service class name


   .. py:attribute:: bit_position
      :type:  int


   .. py:attribute:: name
      :type:  str


.. py:class:: MajorDeviceClassInfo

   Bases: :py:obj:`msgspec.Struct`


   Major device class information from Class of Device field.

   .. attribute:: value

      Major device class value (0-31, 5 bits)

   .. attribute:: name

      Human-readable major device class name


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  int


.. py:class:: MinorDeviceClassInfo

   Bases: :py:obj:`msgspec.Struct`


   Minor device class information from Class of Device field.

   .. attribute:: value

      Minor device class value (0-63, 6 bits)

   .. attribute:: name

      Human-readable minor device class name

   .. attribute:: major_class

      Major device class this minor class belongs to


   .. py:attribute:: major_class
      :type:  int


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  int


