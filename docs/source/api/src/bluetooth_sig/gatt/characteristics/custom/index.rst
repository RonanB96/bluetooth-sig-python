src.bluetooth_sig.gatt.characteristics.custom
=============================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.custom

.. autoapi-nested-parse::

   Custom characteristic base class with auto-registration support.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.custom.CustomBaseCharacteristic


Module Contents
---------------

.. py:class:: CustomBaseCharacteristic(info: src.bluetooth_sig.types.CharacteristicInfo | None = None, auto_register: bool = True)

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Helper base class for custom characteristic implementations.

   This class provides a wrapper around physical BLE characteristics that are not
   defined in the Bluetooth SIG specification. It supports both manual info passing
   and automatic class-level _info binding via __init_subclass__.

   Auto-Registration:
       Custom characteristics automatically register themselves with the global
       BluetoothSIGTranslator singleton when first instantiated. No manual
       registration needed!

   .. admonition:: Examples

      >>> from bluetooth_sig.types.data_types import CharacteristicInfo
      >>> from bluetooth_sig.types.uuid import BluetoothUUID
      >>> class MyCharacteristic(CustomBaseCharacteristic):
      ...     _info = CharacteristicInfo(uuid=BluetoothUUID("AAAA"), name="My Char")
      >>> # Auto-registers with singleton on first instantiation
      >>> char = MyCharacteristic()  # Auto-registered!
      >>> # Now accessible via the global translator
      >>> from bluetooth_sig import BluetoothSIGTranslator
      >>> translator = BluetoothSIGTranslator.get_instance()
      >>> result = translator.parse_characteristic("AAAA", b"\x42")

   Initialize a custom characteristic with automatic _info resolution and registration.

   :param info: Optional override for class-configured _info
   :param auto_register: If True (default), automatically register with global translator singleton

   :raises ValueError: If no valid info available from class or parameter

   .. admonition:: Examples

      >>> # Simple usage - auto-registers with global translator
      >>> char = MyCharacteristic()  # Auto-registered!
      >>> # Opt-out of auto-registration if needed
      >>> char = MyCharacteristic(auto_register=False)


   .. py:method:: get_configured_info() -> src.bluetooth_sig.types.CharacteristicInfo | None
      :classmethod:


      Get the class-level configured CharacteristicInfo.

      :returns: CharacteristicInfo if configured, None otherwise



