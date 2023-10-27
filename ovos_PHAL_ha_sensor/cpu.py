import os

import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import NumericSensor, PercentageSensor


class CPUCountSensor(NumericSensor):
    unit = "number"
    device_id = "cpu_count"

    @classproperty
    def value(self):
        return os.cpu_count()


class CPUUsageSensor(PercentageSensor):
    device_id = "cpu_percent"

    @classproperty
    def value(self):
        return psutil.cpu_percent(1)


class CPUTemperatureSensor(NumericSensor):
    unit = "°C"
    device_id = "cpu_temperature"

    @classproperty
    def value(self):
        return psutil.sensors_temperatures()['coretemp'][0].current

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": "°C"}


if __name__ == "__main__":
    print(CPUCountSensor())
    print(CPUUsageSensor())
    print(CPUTemperatureSensor())
    # cpu_count(16, number)
    # cpu_percent(1.7, %)
    # cpu_temperature(39.0, °C)
