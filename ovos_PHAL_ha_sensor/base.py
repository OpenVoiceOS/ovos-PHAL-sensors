import abc

from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.loggers import SensorLogger


class Sensor:
    device_name = ""
    unit = "string"
    device_id = ""
    _once = False  # read on launch only
    _slow = True  # cool down period of 15 mins
    _thread_safe = True
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
        return f"{self.device_id}({self.value}, {self.unit})"

    def sensor_update(self):
        for log in self.loggers:
            log.sensor_update(self)


class Device:

    @classproperty
    def sensors(self):
        return []


class NumericSensor(Sensor):
    unit = "number"
    _slow = False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": cls.unit,
                "icon": "mdi:numeric"
                }


class PercentageSensor(NumericSensor):
    unit = "%"

    @classproperty
    def value(self):
        return False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "unit_of_measurement": cls.unit,
                "icon": "mdi:percent"
                }


class BooleanSensor(NumericSensor):
    unit = "bool"

    @classproperty
    def value(self):
        return False

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "device_class": "running",
                "state_color": True}

    def sensor_update(self):
        for log in self.loggers:
            log.binary_sensor_update(self)


class BusSensor(Sensor):
    bus = None
    _slow = False

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
