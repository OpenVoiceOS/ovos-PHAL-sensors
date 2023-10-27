import shutil

import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import NumericSensor, PercentageSensor


class DiskTotalSensor(NumericSensor):
    unit = "MB"
    device_id = "disk_total"

    @classproperty
    def value(self):
        return shutil.disk_usage("/")[0]


class DiskUsageSensor(NumericSensor):
    unit = "MB"
    device_id = "disk_usage"

    @classproperty
    def value(self):
        return shutil.disk_usage("/")[1]


class DiskPercentSensor(PercentageSensor):
    device_id = "disk_percent"

    @classproperty
    def value(self):
        return round(DiskUsageSensor().value * 100 / DiskTotalSensor().value, 2)


class MemoryUsageSensor(PercentageSensor):
    device_id = "memory_percent"

    @classproperty
    def value(self):
        return psutil.virtual_memory()[2]


class MemoryTotalSensor(NumericSensor):
    unit = "MB"
    device_id = "memory_total"

    @classproperty
    def value(self):
        return psutil.virtual_memory()[0]


class SwapUsageSensor(PercentageSensor):
    device_id = "swap_percent"

    @classproperty
    def value(self):
        return psutil.swap_memory()[3]


class SwapTotalSensor(NumericSensor):
    unit = "MB"
    device_id = "swap_total"

    @classproperty
    def value(self):
        return psutil.swap_memory()[0]


if __name__ == "__main__":
    print(DiskTotalSensor())
    print(DiskUsageSensor())
    print(DiskPercentSensor())

    print(MemoryTotalSensor())
    print(MemoryUsageSensor())

    print(SwapTotalSensor())
    print(SwapUsageSensor())

    # disk_total(1006662447104, MB)
    # disk_usage(897607532544, MB)
    # disk_percent(89.17, %)
    # memory_total(33368371200, MB)
    # memory_percent(52.0, %)
    # swap_total(0, MB)
    # swap_percent(0.0, %)
