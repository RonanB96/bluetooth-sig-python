src.bluetooth_sig.types.registry.dp_property_ids
================================================

.. py:module:: src.bluetooth_sig.types.registry.dp_property_ids

.. autoapi-nested-parse::

   Types for Bluetooth SIG Device Property IDs registry.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.dp_property_ids.PropertyIdEntry
   src.bluetooth_sig.types.registry.dp_property_ids.PropertyIdsData
   src.bluetooth_sig.types.registry.dp_property_ids.PropertyIdInfo


Module Contents
---------------

.. py:class:: PropertyIdEntry

   Bases: :py:obj:`msgspec.Struct`


   Entry for property IDs from YAML.


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: propertyid
      :type:  str


.. py:class:: PropertyIdsData

   Bases: :py:obj:`msgspec.Struct`


   Top-level data structure for property_ids.yaml.


   .. py:attribute:: propertyids
      :type:  list[PropertyIdEntry]


.. py:class:: PropertyIdInfo

   Bases: :py:obj:`bluetooth_sig.types.registry.BaseUuidInfo`


   Information about a Bluetooth SIG property ID.


   .. py:attribute:: summary
      :type:  str
      :value: ''



