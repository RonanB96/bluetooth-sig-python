src.bluetooth_sig.types.registry.formattypes
============================================

.. py:module:: src.bluetooth_sig.types.registry.formattypes

.. autoapi-nested-parse::

   Types for Bluetooth SIG Format Types registry.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.formattypes.FormatTypeInfo


Module Contents
---------------

.. py:class:: FormatTypeInfo

   Bases: :py:obj:`msgspec.Struct`


   Information about a Bluetooth characteristic format type.


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: exponent
      :type:  bool


   .. py:attribute:: short_name
      :type:  str


   .. py:attribute:: size
      :type:  int


   .. py:attribute:: value
      :type:  int


