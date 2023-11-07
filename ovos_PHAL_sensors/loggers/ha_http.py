import json

import requests

from ovos_PHAL_sensors.loggers.base import SensorLogger
from ovos_PHAL_sensors.sensors.base import _norm


class HomeAssistantUpdater(SensorLogger):
    ha_url = ""
    ha_token = ""

    @classmethod
    def binary_sensor_update(cls, sensor):

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
