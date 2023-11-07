import abc
import string
from dataclasses import dataclass
from typing import Optional, Any

from unidecode import unidecode


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
    _allow_prefix: bool = True
    loggers = []

    @classmethod
    def bind_logger(cls, logger):
        cls.loggers.append(logger)

    @property
    def value(self):
        return None

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
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

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "icon": "mdi:numeric"
                }


@dataclass
class PercentageSensor(NumericSensor):
    unit: str = "%"

    @property
    def value(self):
        return False

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "icon": "mdi:percent"
                }


@dataclass
class BooleanSensor(Sensor):
    unit: str = "bool"

    @property
    def value(self):
        return False

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
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

    @property
    def value(self):
        return False

    @classmethod
    @abc.abstractmethod
    def register_bus_events(cls):
        pass
