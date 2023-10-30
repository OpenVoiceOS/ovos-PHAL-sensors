import dataclasses

import psutil
from ovos_utils import classproperty

from ovos_PHAL_sensors.base import PercentageSensor


@dataclasses.dataclass
class BatterySensor(PercentageSensor):
    unique_id: str = "percent"
    device_name: str = "battery"

    @property
    def value(self):
        return round(psutil.sensors_battery().percent, 3)

    @property
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "device_class": "battery",
                "unit_of_measurement": cls.unit}


if __name__ == "__main__":
    print(BatterySensor())
    # battery_percent(51.12, %)
