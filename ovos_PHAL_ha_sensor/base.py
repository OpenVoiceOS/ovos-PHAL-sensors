import abc

from ovos_utils import classproperty


class Sensor:
    unit = ""
    device_id = ""

    @classproperty
    def value(self):
        return None

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__}

    def __repr__(self):
        return f"{self.device_id}({self.value}, {self.unit})"


class Device:

    @classproperty
    def sensors(self):
        return []


class NumericSensor(Sensor):
    unit = "number"


class PercentageSensor(NumericSensor):
    unit = "%"

    @classproperty
    def value(self):
        return False


class BooleanSensor(NumericSensor):
    unit = "bool"

    @classproperty
    def value(self):
        return False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "state_color": True}


class BusSensor(Sensor):
    bus = None
    unit = "bool"

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

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "state_color": True}
