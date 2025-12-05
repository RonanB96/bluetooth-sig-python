src.bluetooth_sig.types.base_types
==================================

.. py:module:: src.bluetooth_sig.types.base_types

.. autoapi-nested-parse::

   Base data types shared across the library.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.base_types.SIGInfo


Module Contents
---------------

.. py:class:: SIGInfo

   Bases: :py:obj:`msgspec.Struct`


   Base information about Bluetooth SIG characteristics or services.


   .. py:attribute:: uuid
      :type:  src.bluetooth_sig.types.uuid.BluetoothUUID


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: id
      :type:  str
      :value: ''



