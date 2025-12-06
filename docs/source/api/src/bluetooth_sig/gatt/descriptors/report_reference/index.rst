src.bluetooth_sig.gatt.descriptors.report_reference
===================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.report_reference

.. autoapi-nested-parse::

   Report Reference Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.report_reference.ReportReferenceData
   src.bluetooth_sig.gatt.descriptors.report_reference.ReportReferenceDescriptor
   src.bluetooth_sig.gatt.descriptors.report_reference.ReportType


Module Contents
---------------

.. py:class:: ReportReferenceData

   Bases: :py:obj:`msgspec.Struct`


   Report Reference descriptor data.


   .. py:attribute:: report_id
      :type:  int


   .. py:attribute:: report_type
      :type:  int


.. py:class:: ReportReferenceDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Report Reference Descriptor (0x2908).

   Contains report ID and report type information.
   Used in HID (Human Interface Device) profiles.

   Initialize descriptor with resolved information.


   .. py:method:: get_report_id(data: bytes) -> int

      Get the report ID.



   .. py:method:: get_report_type(data: bytes) -> int

      Get the report type.



   .. py:method:: is_feature_report(data: bytes) -> bool

      Check if this is a feature report.



   .. py:method:: is_input_report(data: bytes) -> bool

      Check if this is an input report.



   .. py:method:: is_output_report(data: bytes) -> bool

      Check if this is an output report.



.. py:class:: ReportType

   Bases: :py:obj:`enum.IntEnum`


   Report type values for Report Reference descriptor.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: FEATURE_REPORT
      :value: 3



   .. py:attribute:: INPUT_REPORT
      :value: 1



   .. py:attribute:: OUTPUT_REPORT
      :value: 2



