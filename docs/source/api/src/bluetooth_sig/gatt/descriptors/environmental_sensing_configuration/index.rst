src.bluetooth_sig.gatt.descriptors.environmental_sensing_configuration
======================================================================

.. py:module:: src.bluetooth_sig.gatt.descriptors.environmental_sensing_configuration

.. autoapi-nested-parse::

   Environmental Sensing Configuration Descriptor implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.descriptors.environmental_sensing_configuration.ESCFlags
   src.bluetooth_sig.gatt.descriptors.environmental_sensing_configuration.EnvironmentalSensingConfigurationData
   src.bluetooth_sig.gatt.descriptors.environmental_sensing_configuration.EnvironmentalSensingConfigurationDescriptor


Module Contents
---------------

.. py:class:: ESCFlags

   Bases: :py:obj:`enum.IntFlag`


   ESC (Environmental Sensing Configuration) flags.

   Initialize self.  See help(type(self)) for accurate signature.


   .. py:attribute:: APPLICATION_PRESENT
      :value: 16



   .. py:attribute:: MEASUREMENT_PERIOD_PRESENT
      :value: 4



   .. py:attribute:: MEASUREMENT_UNCERTAINTY_PRESENT
      :value: 32



   .. py:attribute:: TRANSMISSION_INTERVAL_PRESENT
      :value: 2



   .. py:attribute:: TRIGGER_LOGIC_VALUE
      :value: 1



   .. py:attribute:: UPDATE_INTERVAL_PRESENT
      :value: 8



.. py:class:: EnvironmentalSensingConfigurationData

   Bases: :py:obj:`msgspec.Struct`


   Environmental Sensing Configuration descriptor data.


   .. py:attribute:: application_present
      :type:  bool


   .. py:attribute:: measurement_period_present
      :type:  bool


   .. py:attribute:: measurement_uncertainty_present
      :type:  bool


   .. py:attribute:: transmission_interval_present
      :type:  bool


   .. py:attribute:: trigger_logic_value
      :type:  bool


   .. py:attribute:: update_interval_present
      :type:  bool


.. py:class:: EnvironmentalSensingConfigurationDescriptor

   Bases: :py:obj:`src.bluetooth_sig.gatt.descriptors.base.BaseDescriptor`


   Environmental Sensing Configuration Descriptor (0x290B).

   Configures environmental sensing measurement parameters.
   Contains various configuration flags for sensor behaviour.


   .. py:method:: has_measurement_period(data: bytes) -> bool

      Check if measurement period is present.



   .. py:method:: has_transmission_interval(data: bytes) -> bool

      Check if transmission interval is present.



   .. py:method:: has_trigger_logic_value(data: bytes) -> bool

      Check if trigger logic value is present.



