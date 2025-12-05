src.bluetooth_sig.gatt.registry_utils
=====================================

.. py:module:: src.bluetooth_sig.gatt.registry_utils

.. autoapi-nested-parse::

   Common utilities for GATT registries.

   This module contains shared utility classes used by both characteristic and
   service registries to avoid code duplication.



Attributes
----------

.. autoapisummary::

   src.bluetooth_sig.gatt.registry_utils.T


Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.registry_utils.TypeValidator
   src.bluetooth_sig.gatt.registry_utils.ModuleDiscovery


Module Contents
---------------

.. py:class:: TypeValidator

   Utility class for type validation operations.

   Note: Utility class pattern with static methods - pylint disable justified.


   .. py:method:: is_subclass_of(candidate: object, base_class: type) -> typing_extensions.TypeGuard[type]
      :staticmethod:


      Return True when candidate is a subclass of base_class.

      :param candidate: Object to check
      :param base_class: Base class to check against

      :returns: True if candidate is a subclass of base_class



.. py:data:: T

.. py:class:: ModuleDiscovery

   Base class for discovering classes in a package using pkgutil.walk_packages.

   This utility provides a common pattern for discovering and validating classes
   across different GATT packages (characteristics and services).


   .. py:method:: iter_module_names(package_name: str, module_exclusions: set[str]) -> list[str]
      :staticmethod:


      Return sorted module names discovered via pkgutil.walk_packages.

      :param package_name: Fully qualified package name (e.g., "bluetooth_sig.gatt.characteristics")
      :param module_exclusions: Set of module basenames to exclude (e.g., {"__init__", "base"})

      :returns: Sorted list of module names found in the package

      .. rubric:: References

      Python standard library documentation, pkgutil.walk_packages,
      https://docs.python.org/3/library/pkgutil.html#pkgutil.walk_packages



   .. py:method:: discover_classes(module_names: list[str], base_class: type[T], validator: Callable[[Any], bool]) -> list[type[T]]
      :staticmethod:


      Discover all concrete classes in modules that pass validation.

      :param module_names: List of module names to search
      :param base_class: Base class type for filtering
      :param validator: Function to validate if object is a valid subclass

      :returns: Sorted list of discovered classes



