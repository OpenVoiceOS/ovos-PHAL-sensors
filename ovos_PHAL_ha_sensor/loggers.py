import abc
import json
import string

import requests


class SensorLogger:
    @abc.abstractmethod
    def sensor_update(self, sensor):
        pass

    @abc.abstractmethod
    def binary_sensor_update(self, sensor):
        pass


class HomeAssistantUpdater(SensorLogger):
    ha_url = ""
    ha_token = ""

    @classmethod
    def binary_sensor_update(cls, sensor):
        device_id = sensor.device_id.replace(" ", "_")
        name = sensor.device_name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")

        # print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": sensor.value, "attributes": sensor.attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")

    @classmethod
    def sensor_update(cls, sensor):
        device_id = sensor.device_id.replace(" ", "_")
        name = sensor.device_name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")

        # print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": sensor.value, "attributes": sensor.attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")
