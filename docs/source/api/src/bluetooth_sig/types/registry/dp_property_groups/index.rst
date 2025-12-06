src.bluetooth_sig.types.registry.dp_property_groups
===================================================

.. py:module:: src.bluetooth_sig.types.registry.dp_property_groups

.. autoapi-nested-parse::

   Types for Bluetooth SIG Device Property Groups registry.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.registry.dp_property_groups.PropertyGroupEntry
   src.bluetooth_sig.types.registry.dp_property_groups.PropertyGroupInfo
   src.bluetooth_sig.types.registry.dp_property_groups.PropertyGroupsData


Module Contents
---------------

.. py:class:: PropertyGroupEntry

   Bases: :py:obj:`msgspec.Struct`


   Entry for property groups from YAML.


   .. py:attribute:: description
      :type:  str


   .. py:attribute:: identifier
      :type:  str


   .. py:attribute:: name
      :type:  str


.. py:class:: PropertyGroupInfo

   Bases: :py:obj:`bluetooth_sig.types.registry.BaseUuidInfo`


   Information about a Bluetooth SIG property group.


   .. py:attribute:: description
      :type:  str
      :value: ''



   .. py:attribute:: summary
      :type:  str
      :value: ''



.. py:class:: PropertyGroupsData

   Bases: :py:obj:`msgspec.Struct`


   Top-level data structure for property_groups.yaml.


   .. py:attribute:: groups
      :type:  list[PropertyGroupEntry]


