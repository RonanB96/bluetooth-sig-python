src.bluetooth_sig.utils
=======================

.. py:module:: src.bluetooth_sig.utils

.. autoapi-nested-parse::

   Utility helpers exposed by ``bluetooth_sig.utils``.

   This module re-exports common RSSI utilities.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /reference/api/src/bluetooth_sig/utils/profiling/index
   /reference/api/src/bluetooth_sig/utils/rssi_utils/index


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.utils.get_rssi_quality


Package Contents
----------------

.. py:function:: get_rssi_quality(rssi: int) -> str

   Get human-readable RSSI signal quality description.

   :param rssi: RSSI value in dBm

   :returns: Human-readable quality description


