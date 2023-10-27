import abc
import json
import string

import requests
from ovos_utils import classproperty


class Sensor:
    device_name = ""
    ha_url = ""
    ha_token = ""
    unit = "string"
    device_id = ""
    _once = False  # read on launch only
    _slow = True  # cool down period of 15 mins
    _thread_safe = True

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

    def ha_sensor_update(self):
        device_id = self.device_id.replace(" ", "_")
        name = self.device_name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")
        # print("updating:", device_id, f"{self.ha_url}/api/states/sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{self.ha_url}/api/states/sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {self.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": self.value, "attributes": self.attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")


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

    def ha_sensor_update(self):
        device_id = self.device_id.replace(" ", "_")
        name = self.device_name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")

        # print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {self.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": self.value, "attributes": self.attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")


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
