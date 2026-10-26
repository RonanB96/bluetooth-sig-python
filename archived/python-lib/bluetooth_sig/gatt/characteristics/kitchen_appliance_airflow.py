"""Kitchen Appliance Airflow characteristic (0x2C30)."""

from __future__ import annotations

from .base import BaseCharacteristic
from .templates import ScaledUint16Template


class KitchenApplianceAirflowCharacteristic(BaseCharacteristic[float]):
    """Kitchen Appliance Airflow characteristic (0x2C30).

    org.bluetooth.characteristic.kitchen_appliance_airflow
    """

    _template = ScaledUint16Template.from_letter_method(M=1, d=-3, b=0)
