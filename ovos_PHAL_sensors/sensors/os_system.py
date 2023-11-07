import dataclasses
import os
import platform

import psutil

from ovos_PHAL_sensors.sensors.base import Sensor, NumericSensor


@dataclasses.dataclass
class BootTimeSensor(NumericSensor):
    unique_id: str = "boot_time"
    device_name: str = "os"
    unit: str = "unix_time"
    _once: bool = True

    @property
    def value(self):
        return str(psutil.boot_time())

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "icon": "mdi:timeline-clock"
                }


@dataclasses.dataclass
class OSNameSensor(Sensor):
    unique_id: str = "name"
    device_name: str = "os"
    _once: bool = True

    @property
    def value(self):
        return os.name


@dataclasses.dataclass
class OSSystemSensor(Sensor):
    unique_id: str = "system"
    device_name: str = "os"
    _once: bool = True

    @property
    def value(self):
        return platform.system()


@dataclasses.dataclass
class ReleaseSensor(Sensor):
    unique_id: str = "release"
    device_name: str = "os"
    _once: bool = True

    @property
    def value(self):
        return platform.release()


@dataclasses.dataclass
class MachineSensor(Sensor):
    unique_id: str = "machine"
    device_name: str = "os"
    _once: bool = True

    @property
    def value(self):
        return platform.machine()


@dataclasses.dataclass
class ArchitectureSensor(Sensor):
    unique_id: str = "architecture"
    device_name: str = "os"
    _once: bool = True

    @property
    def value(self):
        return str(platform.architecture()[0])


if __name__ == "__main__":
    print(ArchitectureSensor())
    print(BootTimeSensor())
    print(OSNameSensor())
    print(OSSystemSensor())
    print(MachineSensor())
    print(ReleaseSensor())

    # architecture(64bit, string)
    # boot_time(1698249467.0, unix_time)
    # os_name(posix, string)
    # os_system(Linux, string)
    # machine(x86_64, string)
    # release(6.5.5-1-MANJARO, string)
