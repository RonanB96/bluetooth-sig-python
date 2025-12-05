src.bluetooth_sig.types.registry.gss_characteristic
===================================================

.. py:module:: src.bluetooth_sig.types.registry.gss_characteristic

.. autoapi-nested-parse::

   Types for Bluetooth SIG GSS Characteristic registry.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.gss_characteristic.FieldSpec
   src.bluetooth_sig.types.registry.gss_characteristic.CharacteristicSpec
   src.bluetooth_sig.types.registry.gss_characteristic.GssCharacteristicData


Module Contents
---------------

.. py:class:: FieldSpec

   Bases: :py:obj:`msgspec.Struct`


   Specification for a field in a characteristic structure.


   .. py:attribute:: field
      :type:  str


   .. py:attribute:: type
      :type:  str


   .. py:attribute:: size
      :type:  str


   .. py:attribute:: description
      :type:  str


.. py:class:: CharacteristicSpec

   Bases: :py:obj:`msgspec.Struct`


   Specification for a Bluetooth SIG characteristic from GSS.


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: structure
      :type:  list[FieldSpec]


.. py:class:: GssCharacteristicData

   Bases: :py:obj:`msgspec.Struct`


   Top-level data structure for GSS characteristic YAML files.


   .. py:attribute:: characteristic
      :type:  CharacteristicSpec


