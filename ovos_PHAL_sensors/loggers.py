import abc
import json

import requests
from ovos_utils.messagebus import FakeBus, Message


class SensorLogger:
    @classmethod
    @abc.abstractmethod
    def sensor_update(cls, sensor):
        pass

    @classmethod
    @abc.abstractmethod
    def binary_sensor_update(cls, sensor):
        pass


class MessageBusLogger(SensorLogger):
    bus = FakeBus()

    @classmethod
    def sensor_update(cls, sensor):
        from ovos_PHAL_sensors.base import _norm
        device_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{device_id}",
                              "device_name": name,
                              "name": device_id,
                              "attributes": sensor.attrs}))

    @classmethod
    def binary_sensor_update(cls, sensor):
        from ovos_PHAL_sensors.base import _norm
        device_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.binary_sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{device_id}",
                              "device_name": name,
                              "name": device_id,
                              "attributes": sensor.attrs}))


class HomeAssistantUpdater(SensorLogger):
    ha_url = ""
    ha_token = ""

    @classmethod
    def binary_sensor_update(cls, sensor):

        from ovos_PHAL_sensors.base import _norm
        device_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        # print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": "on" if sensor.value else "off",
                                 "attributes": sensor.attrs}),
            ).json()
            print(response)
        except:
            print(f"failed to push data to {cls.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}", sensor.attrs)

    @classmethod
    def sensor_update(cls, sensor):

        from ovos_PHAL_sensors.base import _norm
        device_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        # print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": sensor.value,
                                 "attributes": sensor.attrs}),
            )
            print(response.text)
        except:
            print(f"failed to push data to HA /sensor.ovos_{name}_{device_id}", sensor.attrs)
