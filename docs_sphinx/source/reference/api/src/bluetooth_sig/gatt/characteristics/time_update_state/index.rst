src.bluetooth_sig.gatt.characteristics.time_update_state
========================================================

.. py:module:: src.bluetooth_sig.gatt.characteristics.time_update_state

.. autoapi-nested-parse::

   Time Update State characteristic (0x2A17) implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.characteristics.time_update_state.TimeUpdateState
   src.bluetooth_sig.gatt.characteristics.time_update_state.TimeUpdateCurrentState
   src.bluetooth_sig.gatt.characteristics.time_update_state.TimeUpdateResult
   src.bluetooth_sig.gatt.characteristics.time_update_state.TimeUpdateStateCharacteristic


Module Contents
---------------

.. py:class:: TimeUpdateState

   Bases: :py:obj:`msgspec.Struct`


   Time Update State data structure.


   .. py:attribute:: current_state
      :type:  TimeUpdateCurrentState


   .. py:attribute:: result
      :type:  TimeUpdateResult


.. py:class:: TimeUpdateCurrentState

   Bases: :py:obj:`enum.IntEnum`


   Time Update Current State values.


   .. py:attribute:: IDLE
      :value: 0



   .. py:attribute:: PENDING
      :value: 1



   .. py:attribute:: UPDATING
      :value: 2



.. py:class:: TimeUpdateResult

   Bases: :py:obj:`enum.IntEnum`


   Time Update Result values.


   .. py:attribute:: SUCCESSFUL
      :value: 0



   .. py:attribute:: CANCELED
      :value: 1



   .. py:attribute:: NO_CONNECTION_TO_REFERENCE
      :value: 2



   .. py:attribute:: REFERENCE_RESPONDED_WITH_ERROR
      :value: 3



   .. py:attribute:: TIMEOUT
      :value: 4



   .. py:attribute:: UPDATE_NOT_ATTEMPTED_AFTER_RESET
      :value: 5



.. py:class:: TimeUpdateStateCharacteristic

   Bases: :py:obj:`src.bluetooth_sig.gatt.characteristics.base.BaseCharacteristic`


   Time Update State characteristic.

   Indicates the current state of time update operations.

   Value: 2 bytes
   - Current State: uint8 (0=Idle, 1=Pending, 2=Updating)
   - Result: uint8 (0=Successful, 1=Canceled, etc.)


   .. py:method:: decode_value(data: bytearray, ctx: bluetooth_sig.types.context.CharacteristicContext | None = None) -> TimeUpdateState

      Decode the raw data to TimeUpdateState.



   .. py:method:: encode_value(data: TimeUpdateState) -> bytearray

      Encode TimeUpdateState to bytes.



