src.bluetooth_sig.types.location
================================

.. py:module:: src.bluetooth_sig.types.location

.. autoapi-nested-parse::

   Location and Navigation types and enumerations.

   Provides common types used across location and navigation related characteristics.
   Based on Bluetooth SIG GATT Specification for Location and Navigation Service (0x1819).



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.location.PositionStatus


Module Contents
---------------

.. py:class:: PositionStatus

   Bases: :py:obj:`enum.IntEnum`


   Position status enumeration.

   Used by Navigation and Position Quality characteristics to indicate
   the status/quality of position data.

   Per Bluetooth SIG Location and Navigation Service specification.


   .. py:attribute:: NO_POSITION
      :value: 0



   .. py:attribute:: POSITION_OK
      :value: 1



   .. py:attribute:: ESTIMATED_POSITION
      :value: 2



   .. py:attribute:: LAST_KNOWN_POSITION
      :value: 3



