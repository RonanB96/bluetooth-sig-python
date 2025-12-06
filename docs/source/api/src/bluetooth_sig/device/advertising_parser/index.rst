src.bluetooth_sig.device.advertising_parser
===========================================

.. py:module:: src.bluetooth_sig.device.advertising_parser

.. autoapi-nested-parse::

   Advertising data parser for BLE devices.

   This module provides a dedicated parser for BLE advertising data
   packets, extracting device information, manufacturer data, and service
   UUIDs from both legacy and extended advertising formats.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.device.advertising_parser.logger


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.device.advertising_parser.AdvertisingParser


Module Contents
---------------

.. py:class:: AdvertisingParser

   Parser for BLE advertising data packets.

   Handles both legacy and extended advertising PDU formats, extracting
   device information, manufacturer data, and service UUIDs.


   .. py:method:: parse_advertising_data(raw_data: bytes) -> src.bluetooth_sig.types.AdvertisingData

      Parse raw advertising data and return structured information.

      :param raw_data: Raw bytes from BLE advertising packet

      :returns: AdvertisingData with parsed information



.. py:data:: logger

