src.bluetooth_sig.gatt.characteristics.utils.parse_trace
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.utils.parse_trace

.. autoapi-nested-parse::

   Parse trace utility for debugging characteristic parsing.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.utils.parse_trace.ParseTrace


Module Contents
---------------

.. py:class:: ParseTrace(enabled: bool = True)

   Manages parse traces with built-in enable/disable logic.

   This class encapsulates the trace collection logic to avoid manual
   if checks throughout the parsing code, improving performance when
   tracing is disabled.

   .. admonition:: Example

      trace = ParseTrace(enabled=True)
      trace.append("Starting parse")
      trace.append("Validation complete")
      result = trace.get_trace()  # Returns list of strings

   Initialize parse trace collector.

   :param enabled: Whether to collect trace messages (default: True)


   .. py:method:: append(message: str) -> None

      Append a message to the trace if tracing is enabled.

      :param message: Trace message to append



   .. py:method:: get_trace() -> list[str]

      Get the collected trace messages.

      :returns: List of trace messages if enabled, empty list otherwise



   .. py:property:: enabled
      :type: bool


      Check if tracing is enabled.

      :returns: True if tracing is enabled, False otherwise


