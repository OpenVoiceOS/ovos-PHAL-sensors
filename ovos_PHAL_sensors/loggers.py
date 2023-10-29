import abc
import json
import logging
import os

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


class FileSensorLogger(SensorLogger):
    path = os.path.expanduser("~/.local/state/sensors")
    os.makedirs(path, exist_ok=True)
    logging.getLogger("urllib3.connectionpool").setLevel("ERROR")
    logging.basicConfig(filename=f"{path}/readings.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger('sensor_reading')

    @classmethod
    def sensor_update(cls, sensor):
        from ovos_PHAL_sensors.base import _norm
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)
        cls.logger.info(f"{name}_{unique_id} {sensor.value}")

    @classmethod
    def binary_sensor_update(cls, sensor):
        return cls.sensor_update(sensor)


class MessageBusLogger(SensorLogger):
    bus = FakeBus()

    @classmethod
    def sensor_update(cls, sensor):
        from ovos_PHAL_sensors.base import _norm
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{unique_id}",
                              "device_name": name,
                              "name": unique_id,
                              "attributes": sensor.attrs}))

    @classmethod
    def binary_sensor_update(cls, sensor):
        from ovos_PHAL_sensors.base import _norm
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.binary_sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{unique_id}",
                              "device_name": name,
                              "name": unique_id,
                              "attributes": sensor.attrs}))


class HomeAssistantUpdater(SensorLogger):
    ha_url = ""
    ha_token = ""

    @classmethod
    def binary_sensor_update(cls, sensor):

        from ovos_PHAL_sensors.base import _norm
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        # print("updating:", unique_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{unique_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/binary_sensor.ovos_{name}_{unique_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": "on" if sensor.value else "off",
                                 "attributes": sensor.attrs}),
            ).json()
            print(response)
        except:
            print(f"failed to push data to {cls.ha_url}/api/states/binary_sensor.ovos_{name}_{unique_id}", sensor.attrs)

    @classmethod
    def sensor_update(cls, sensor):

        from ovos_PHAL_sensors.base import _norm
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        # print("updating:", unique_id, f"{self.ha_url}/api/states/sensor.ovos_{name}_{unique_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/sensor.ovos_{name}_{unique_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": sensor.value,
                                 "attributes": sensor.attrs}),
            )
            print(response.text)
        except:
            print(f"failed to push data to HA /sensor.ovos_{name}_{unique_id}", sensor.attrs)
