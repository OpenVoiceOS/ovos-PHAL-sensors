import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import PercentageSensor


class BatterySensor(PercentageSensor):
    device_id = "battery_percent"

    @classproperty
    def value(self):
        return round(psutil.sensors_battery().percent, 3)

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "device_class": "battery",
                "unit_of_measurement": cls.unit}


if __name__ == "__main__":
    print(BatterySensor())
    # battery_percent(51.12, %)
