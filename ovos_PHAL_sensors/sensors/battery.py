import dataclasses

import psutil
from ovos_PHAL_sensors.sensors.base import PercentageSensor


@dataclasses.dataclass
class BatterySensor(PercentageSensor):
    unique_id: str = "percent"
    device_name: str = "battery"

    @property
    def value(self):
        battery = psutil.sensors_battery()
        if battery is None:
            return 0
        return round(battery.percent, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "battery",
                "unit_of_measurement": self.unit}


if __name__ == "__main__":
    print(BatterySensor())
    # battery_percent(51.12, %)
