src.bluetooth_sig.types.gatt_services
=====================================

.. py:module:: src.bluetooth_sig.types.gatt_services

.. autoapi-nested-parse::

   GATT service typing definitions.

   Strong typing for GATT services - no flexible dicts allowed!
   NO LEGACY CODE SUPPORT - development phase only.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.types.gatt_services.CharacteristicTypeVar
   src.bluetooth_sig.types.gatt_services.CharacteristicCollection
   src.bluetooth_sig.types.gatt_services.ServiceDiscoveryData


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.types.gatt_services.CharacteristicSpec


Functions
---------

.. autoapisummary::

   src.bluetooth_sig.types.gatt_services.characteristic


Module Contents
---------------

.. py:data:: CharacteristicTypeVar

.. py:class:: CharacteristicSpec

   Bases: :py:obj:`msgspec.Struct`, :py:obj:`Generic`\ [\ :py:obj:`CharacteristicTypeVar`\ ]


   Specification for a single characteristic with strong typing.

   This provides compile-time type safety and IDE autocompletion
   for service characteristic definitions.

   Note: The characteristic name is derived from the dictionary key,
   eliminating redundancy and following DRY principles.


   .. py:attribute:: char_class
      :type:  type[CharacteristicTypeVar]


   .. py:attribute:: required
      :type:  bool
      :value: False



   .. py:attribute:: conditional
      :type:  bool
      :value: False



   .. py:attribute:: condition
      :type:  str
      :value: ''



.. py:function:: characteristic(name: src.bluetooth_sig.types.gatt_enums.CharacteristicName, required: bool = False) -> CharacteristicSpec[src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic]

   Create a CharacteristicSpec using the central registry for class mapping.

   This eliminates the need to manually specify the characteristic class
   by automatically resolving it from the CharacteristicName enum.

   :param name: The characteristic name enum
   :param required: Whether this characteristic is required

   :returns: A CharacteristicSpec with the appropriate class from the registry


.. py:data:: CharacteristicCollection

   Maps characteristic names (enums) to their specifications - STRONG TYPING ONLY.

.. py:data:: ServiceDiscoveryData

   Service UUID -> characteristic discovery information.

   :type: Service discovery data

