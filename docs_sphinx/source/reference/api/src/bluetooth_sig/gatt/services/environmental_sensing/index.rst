src.bluetooth_sig.gatt.services.environmental_sensing
=====================================================

.. py:module:: src.bluetooth_sig.gatt.services.environmental_sensing

.. autoapi-nested-parse::

   Environmental Sensing Service implementation.



Classes
-------

.. autoapisummary::

   src.bluetooth_sig.gatt.services.environmental_sensing.EnvironmentalSensingService


Module Contents
---------------

.. py:class:: EnvironmentalSensingService

   Bases: :py:obj:`src.bluetooth_sig.gatt.services.base.BaseGattService`


   Environmental Sensing Service implementation (0x181A).

   Used for environmental monitoring devices including weather stations,
   air quality sensors, and comprehensive environmental monitoring systems.
   Supports a wide range of environmental measurements including:
   - Traditional weather measurements (temperature, humidity, pressure)
   - Air quality metrics (gas concentrations, particulate matter)
   - Advanced environmental conditions (wind, elevation, trends)

   Contains comprehensive characteristics for environmental sensing including:
   - Temperature - Optional
   - Humidity - Optional
   - Pressure - Optional
   - Dew Point - Optional
   - Heat Index - Optional
   - Wind Chill - Optional
   - True Wind Speed - Optional
   - True Wind Direction - Optional
   - Apparent Wind Speed - Optional
   - Apparent Wind Direction - Optional
   - CO2 Concentration - Optional
   - VOC Concentration - Optional
   - Non-Methane VOC Concentration - Optional
   - Ammonia Concentration - Optional
   - Methane Concentration - Optional
   - Nitrogen Dioxide Concentration - Optional
   - Ozone Concentration - Optional
   - PM1 Concentration - Optional
   - PM2.5 Concentration - Optional
   - PM10 Concentration - Optional
   - Sulfur Dioxide Concentration - Optional
   - Elevation - Optional
   - Barometric Pressure Trend - Optional
   - Pollen Concentration - Optional
   - Rainfall - Optional


   .. py:attribute:: service_characteristics
      :type:  ClassVar[dict[src.bluetooth_sig.gatt.characteristics.registry.CharacteristicName, bool]]


