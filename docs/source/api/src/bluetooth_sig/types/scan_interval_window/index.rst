src.bluetooth_sig.types.scan_interval_window
============================================

.. py:module:: src.bluetooth_sig.types.scan_interval_window

.. autoapi-nested-parse::

   Scan Interval Window characteristic data types.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.scan_interval_window.ScanIntervalWindowData


Module Contents
---------------

.. py:class:: ScanIntervalWindowData

   Bases: :py:obj:`msgspec.Struct`


   Scan Interval Window characteristic data.

   Contains scan interval and scan window parameters for BLE scanning.

   .. attribute:: scan_interval

      Scan interval in units of 0.625ms (range: 0x0004-0x4000)

   .. attribute:: scan_window

      Scan window in units of 0.625ms (range: 0x0004-0x4000)
      Must be less than or equal to scan_interval


   .. py:attribute:: HEX_FORMAT_WIDTH
      :value: 6



   .. py:attribute:: SCAN_INTERVAL_MAX
      :value: 16384



   .. py:attribute:: SCAN_INTERVAL_MIN
      :value: 4



   .. py:attribute:: SCAN_WINDOW_MAX
      :value: 16384



   .. py:attribute:: SCAN_WINDOW_MIN
      :value: 4



   .. py:attribute:: UNITS_TO_MS_FACTOR
      :value: 0.625



   .. py:attribute:: scan_interval
      :type:  int


   .. py:property:: scan_interval_ms
      :type: float


      Get scan interval in milliseconds.


   .. py:attribute:: scan_window
      :type:  int


   .. py:property:: scan_window_ms
      :type: float


      Get scan window in milliseconds.


