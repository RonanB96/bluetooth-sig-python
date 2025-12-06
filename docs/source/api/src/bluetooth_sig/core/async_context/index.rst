src.bluetooth_sig.core.async_context
====================================

.. py:module:: src.bluetooth_sig.core.async_context

.. autoapi-nested-parse::

   Async context manager for device parsing sessions.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.core.async_context.AsyncParsingSession


Module Contents
---------------

.. py:class:: AsyncParsingSession(translator: src.bluetooth_sig.core.translator.BluetoothSIGTranslator, ctx: src.bluetooth_sig.types.CharacteristicContext | None = None)

   Async context manager for parsing sessions.

   Maintains parsing context across multiple async operations.

   .. admonition:: Example

      ```python
      async with AsyncParsingSession() as session:
          result1 = await session.parse("2A19", data1)
          result2 = await session.parse("2A6E", data2)
          # Context automatically shared between parses
      ```

   Initialize parsing session.

   :param translator: Translator instance to use for parsing
   :param ctx: Optional initial context


   .. py:method:: parse(uuid: str | src.bluetooth_sig.types.uuid.BluetoothUUID, data: bytes) -> src.bluetooth_sig.gatt.characteristics.base.CharacteristicData
      :async:


      Parse characteristic with accumulated context.

      :param uuid: Characteristic UUID
      :param data: Raw bytes

      :returns: CharacteristicData



   .. py:attribute:: context
      :value: None



   .. py:attribute:: results
      :type:  dict[str, src.bluetooth_sig.gatt.characteristics.base.CharacteristicData]


   .. py:attribute:: translator


