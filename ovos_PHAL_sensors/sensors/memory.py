import dataclasses
import shutil

import psutil

from ovos_PHAL_sensors.sensors.base import NumericSensor, PercentageSensor


@dataclasses.dataclass
class DiskTotalSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "disk_total"
    device_name: str = "memory"
    _once: bool = True

    @property
    def value(self):
        return round(shutil.disk_usage("/")[0] / 1024 ** 2, 3)


@dataclasses.dataclass
class DiskUsageSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "disk_usage"
    device_name: str = "memory"
    _slow: bool = True

    @property
    def value(self):
        return round(shutil.disk_usage("/")[1] / 1024 ** 2, 3)


@dataclasses.dataclass
class DiskPercentSensor(PercentageSensor):
    unique_id: str = "disk_percent"
    device_name: str = "memory"
    _slow: bool = True

    @property
    def value(self):
        return round(DiskUsageSensor().value * 100 / DiskTotalSensor().value, 2)


@dataclasses.dataclass
class MemoryUsageSensor(PercentageSensor):
    unique_id: str = "usage_percent"
    device_name: str = "memory"

    @property
    def value(self):
        return psutil.virtual_memory()[2]


@dataclasses.dataclass
class MemoryTotalSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "total"
    device_name: str = "memory"
    _once: bool = True

    @property
    def value(self):
        return round(psutil.virtual_memory()[0] / 1024 ** 2, 3)


@dataclasses.dataclass
class SwapUsageSensor(PercentageSensor):
    unique_id: str = "swap_percent"
    device_name: str = "memory"
    _slow: bool = True

    @property
    def value(self):
        return psutil.swap_memory()[3]


@dataclasses.dataclass
class SwapTotalSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "swap_total"
    device_name: str = "memory"
    _once: bool = True

    @property
    def value(self):
        return round(psutil.swap_memory()[0] / 1024 ** 2, 3)


@dataclasses.dataclass
class DiskReadBytesSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "disk_read_bytes"
    device_name: str = "memory"

    @property
    def value(self):
        counters = psutil.disk_io_counters()
        if counters is None:
            return 0
        return round(counters.read_bytes / 1024 ** 2, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "state_class": "total_increasing",
                "icon": "mdi:disc-player"}


@dataclasses.dataclass
class DiskWriteBytesSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "disk_write_bytes"
    device_name: str = "memory"

    @property
    def value(self):
        counters = psutil.disk_io_counters()
        if counters is None:
            return 0
        return round(counters.write_bytes / 1024 ** 2, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "state_class": "total_increasing",
                "icon": "mdi:content-save"}


if __name__ == "__main__":
    print(DiskTotalSensor())
    print(DiskUsageSensor())
    print(DiskPercentSensor())

    print(MemoryTotalSensor())
    print(MemoryUsageSensor())

    print(SwapTotalSensor())
    print(SwapUsageSensor())

    print(DiskReadBytesSensor())
    print(DiskWriteBytesSensor())

    # disk_total(1006662447104, MB)
    # disk_usage(897607532544, MB)
    # disk_percent(89.17, %)
    # memory_total(33368371200, MB)
    # memory_percent(52.0, %)
    # swap_total(0, MB)
    # swap_percent(0.0, %)
