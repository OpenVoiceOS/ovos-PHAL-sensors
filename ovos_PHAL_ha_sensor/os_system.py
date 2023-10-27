import os
import platform

import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import Sensor, NumericSensor


class BootTimeSensor(NumericSensor):
    device_id = "boot_time"
    unit = "unix_time"
    _once = True

    @classproperty
    def value(self):
        return str(psutil.boot_time())

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": cls.unit,
                "icon": "mdi:timeline-clock"
                }


class OSNameSensor(Sensor):
    device_id = "os_name"
    unit = "string"
    _once = True

    @classproperty
    def value(self):
        return os.name


class OSSystemSensor(Sensor):
    device_id = "os_system"
    unit = "string"
    _once = True

    @classproperty
    def value(self):
        return platform.system()


class ReleaseSensor(Sensor):
    device_id = "release"
    unit = "string"
    _once = True

    @classproperty
    def value(self):
        return platform.release()


class MachineSensor(Sensor):
    device_id = "machine"
    unit = "string"
    _once = True

    @classproperty
    def value(self):
        return platform.machine()


class ArchitectureSensor(Sensor):
    device_id = "architecture"
    unit = "string"
    _once = True

    @classproperty
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
