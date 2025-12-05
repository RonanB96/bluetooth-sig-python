src.bluetooth_sig.gatt.resolver
===============================

.. py:module:: src.bluetooth_sig.gatt.resolver

.. autoapi-nested-parse::

   Shared SIG resolver utilities for characteristics and services.

   This module provides common name resolution and normalization logic to avoid
   duplication between characteristic and service resolvers.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.resolver.TInfo


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.resolver.NameNormalizer
   src.bluetooth_sig.gatt.resolver.NameVariantGenerator
   src.bluetooth_sig.gatt.resolver.RegistrySearchStrategy
   src.bluetooth_sig.gatt.resolver.CharacteristicRegistrySearch
   src.bluetooth_sig.gatt.resolver.ServiceRegistrySearch
   src.bluetooth_sig.gatt.resolver.DescriptorRegistrySearch


Module Contents
---------------

.. py:data:: TInfo

.. py:class:: NameNormalizer

   Utilities for normalizing class names to various Bluetooth SIG formats.

   This class provides name transformation functions that are common to both
   characteristic and service resolution.


   .. py:method:: camel_case_to_display_name(name: str) -> str
      :staticmethod:


      Convert camelCase class name to space-separated display name.

      Uses regex to find word boundaries at capital letters and numbers.

      :param name: CamelCase name (e.g., "VOCConcentration", "BatteryLevel", "ApparentEnergy32")

      :returns: Space-separated display name (e.g., "VOC Concentration", "Battery Level", "Apparent Energy 32")

      .. admonition:: Examples

         >>> NameNormalizer.camel_case_to_display_name("VOCConcentration")
         "VOC Concentration"
         >>> NameNormalizer.camel_case_to_display_name("CO2Concentration")
         "CO2 Concentration"
         >>> NameNormalizer.camel_case_to_display_name("BatteryLevel")
         "Battery Level"
         >>> NameNormalizer.camel_case_to_display_name("ApparentEnergy32")
         "Apparent Energy 32"



   .. py:method:: remove_suffix(name: str, suffix: str) -> str
      :staticmethod:


      Remove suffix from name if present.

      :param name: Original name
      :param suffix: Suffix to remove (e.g., "Characteristic", "Service")

      :returns: Name without suffix, or original name if suffix not present



   .. py:method:: to_org_format(words: list[str], entity_type: str) -> str
      :staticmethod:


      Convert words to org.bluetooth format.

      :param words: List of words from name split
      :param entity_type: Type of entity ("characteristic" or "service")

      :returns: Org format string (e.g., "org.bluetooth.characteristic.battery_level")



   .. py:method:: snake_case_to_camel_case(s: str) -> str
      :staticmethod:


      Convert snake_case to CamelCase with acronym handling (for test file mapping).



.. py:class:: NameVariantGenerator

   Generates name variants for registry lookups.

   Produces all possible name formats that might match registry entries,
   ordered by likelihood of success.


   .. py:method:: generate_characteristic_variants(class_name: str, explicit_name: str | None = None) -> list[str]
      :staticmethod:


      Generate all name variants to try for characteristic resolution.

      :param class_name: The __name__ of the characteristic class
      :param explicit_name: Optional explicit name override

      :returns: List of name variants ordered by likelihood of success



   .. py:method:: generate_service_variants(class_name: str, explicit_name: str | None = None) -> list[str]
      :staticmethod:


      Generate all name variants to try for service resolution.

      :param class_name: The __name__ of the service class
      :param explicit_name: Optional explicit name override

      :returns: List of name variants ordered by likelihood of success



   .. py:method:: generate_descriptor_variants(class_name: str, explicit_name: str | None = None) -> list[str]
      :staticmethod:


      Generate all name variants to try for descriptor resolution.

      :param class_name: The __name__ of the descriptor class
      :param explicit_name: Optional explicit name override

      :returns: List of name variants ordered by likelihood of success



.. py:class:: RegistrySearchStrategy

   Bases: :py:obj:`Generic`\ [\ :py:obj:`TInfo`\ ]


   Base strategy for searching registry with name variants.

   This class implements the Template Method pattern, allowing subclasses
   to customize the search behaviour for different entity types.


   .. py:method:: search(class_obj: type, explicit_name: str | None = None) -> TInfo | None

      Search registry using name variants.

      :param class_obj: The class to resolve info for
      :param explicit_name: Optional explicit name override

      :returns: Resolved info object or None if not found



.. py:class:: CharacteristicRegistrySearch

   Bases: :py:obj:`RegistrySearchStrategy`\ [\ :py:obj:`src.bluetooth_sig.types.CharacteristicInfo`\ ]


   Registry search strategy for characteristics.


.. py:class:: ServiceRegistrySearch

   Bases: :py:obj:`RegistrySearchStrategy`\ [\ :py:obj:`src.bluetooth_sig.types.ServiceInfo`\ ]


   Registry search strategy for services.


.. py:class:: DescriptorRegistrySearch

   Bases: :py:obj:`RegistrySearchStrategy`\ [\ :py:obj:`src.bluetooth_sig.types.DescriptorInfo`\ ]


   Registry search strategy for descriptors.


