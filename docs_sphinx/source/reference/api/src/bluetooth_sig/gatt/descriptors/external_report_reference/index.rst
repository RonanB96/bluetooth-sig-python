src.bluetooth_sig.gatt.descriptors.external_report_reference
============================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.external_report_reference

.. autoapi-nested-parse::

   External Report Reference Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.external_report_reference.ExternalReportReferenceData
   src.bluetooth_sig.gatt.descriptors.external_report_reference.ExternalReportReferenceDescriptor


Module Contents
---------------

.. py:class:: ExternalReportReferenceData

   Bases: :py:obj:`msgspec.Struct`


   External Report Reference descriptor data.


   .. py:attribute:: external_report_id
      :type:  int


.. py:class:: ExternalReportReferenceDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   External Report Reference Descriptor (0x2907).

   References an external report by ID.
   Used in HID (Human Interface Device) profiles.


   .. py:method:: get_external_report_id(data: bytes) -> int

      Get the external report ID.



