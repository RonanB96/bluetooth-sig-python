src.bluetooth_sig.registry.company_identifiers.company_identifiers_registry
===========================================================================

.. py:module:: src.bluetooth_sig.registry.company_identifiers.company_identifiers_registry

.. autoapi-nested-parse::

   Company Identifiers Registry for Bluetooth SIG manufacturer IDs.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.registry.company_identifiers.company_identifiers_registry.company_identifiers_registry


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.registry.company_identifiers.company_identifiers_registry.CompanyIdentifierInfo
   src.bluetooth_sig.registry.company_identifiers.company_identifiers_registry.CompanyIdentifiersRegistry


Module Contents
---------------

.. py:class:: CompanyIdentifierInfo

   Bases: :py:obj:`msgspec.Struct`


   Information about a Bluetooth SIG company identifier.


   .. py:attribute:: id
      :type:  int


   .. py:attribute:: name
      :type:  str


.. py:class:: CompanyIdentifiersRegistry

   Bases: :py:obj:`bluetooth_sig.registry.base.BaseGenericRegistry`\ [\ :py:obj:`CompanyIdentifierInfo`\ ]


   Registry for Bluetooth SIG company identifiers with lazy loading.

   This registry resolves manufacturer company IDs to company names from
   the official Bluetooth SIG assigned numbers. Data is lazily loaded on
   first access for performance.

   Thread-safe: Multiple threads can safely access the registry concurrently.


   .. py:method:: get_company_name(company_id: int) -> str | None

      Get company name by ID (lazy loads on first call).

      :param company_id: Manufacturer company identifier (e.g., 0x004C for Apple)

      :returns: Company name or None if not found

      .. admonition:: Examples

         >>> registry = CompanyIdentifiersRegistry()
         >>> registry.get_company_name(0x004C)
         'Apple, Inc.'
         >>> registry.get_company_name(0x0006)
         'Microsoft'
         >>> registry.get_company_name(0x00E0)
         'Google'
         >>> registry.get_company_name(0xFFFF)  # Unknown ID
         None



.. py:data:: company_identifiers_registry

