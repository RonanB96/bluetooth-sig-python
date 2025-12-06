src.bluetooth_sig.types.registry.dp_property
============================================

.. py:module:: src.bluetooth_sig.types.registry.dp_property

.. autoapi-nested-parse::

   Types for Bluetooth SIG Device Property registry.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.dp_property.DpPropertyData
   src.bluetooth_sig.types.registry.dp_property.PropertySpec


Module Contents
---------------

.. py:class:: DpPropertyData

   Bases: :py:obj:`msgspec.Struct`


   Top-level data structure for DP property YAML files.


   .. py:attribute:: property
      :type:  PropertySpec


.. py:class:: PropertySpec

   Bases: :py:obj:`msgspec.Struct`


   Specification for a Bluetooth SIG property from DP.


   .. py:attribute:: characteristic
      :type:  str


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: group
      :type:  str


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: name
      :type:  str


