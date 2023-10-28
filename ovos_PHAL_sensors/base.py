import abc
import string
from dataclasses import dataclass
from typing import Optional, Any

from ovos_utils import classproperty
from unidecode import unidecode

from ovos_PHAL_sensors.loggers import SensorLogger


def _norm(s):
    s = unidecode(s.lower().strip().replace(" ", "_").replace("-", "").replace(".", "_"))
    return "".join([_ for _ in s if _ in string.ascii_letters + string.digits + "_"])


@dataclass
class Sensor:
    unique_id: str
    device_name: str = ""
    unit: str = "string"
    _once: bool = False  # read on launch only
    _slow: bool = True  # cool down period of 15 mins
    _thread_safe: bool = True
    loggers = []

    @classmethod
    def bind_logger(cls, logger: SensorLogger):
        cls.loggers.append(logger)

    @classproperty
    def value(self):
        return None

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "icon": "mdi:alphabetical"
                }

    def __repr__(self):
        return f"{self.unique_id}({self.value}, {self.unit})"

    def sensor_update(self):
        if self.loggers is not None:
            for log in self.loggers:
                log.sensor_update(self)


@dataclass
class NumericSensor(Sensor):
    unit: str = "number"
    _slow: bool = False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": cls.unit,
                "icon": "mdi:numeric"
                }


@dataclass
class PercentageSensor(NumericSensor):
    unit: str = "%"

    @classproperty
    def value(self):
        return False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": cls.unit,
                "icon": "mdi:percent"
                }


@dataclass
class BooleanSensor(Sensor):
    unit: str = "bool"

    @classproperty
    def value(self):
        return False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "device_class": "running",
                "state_color": True}

    def sensor_update(self):
        if self.loggers is not None:
            for log in self.loggers:
                log.binary_sensor_update(self)


@dataclass
class BusSensor(Sensor):
    bus: Optional[Any] = None
    _slow: bus = False

    @classmethod
    def bind(cls, bus):
        cls.bus = bus

    @classproperty
    def value(self):
        return False

    @classmethod
    @abc.abstractmethod
    def register_bus_events(cls):
        pass
