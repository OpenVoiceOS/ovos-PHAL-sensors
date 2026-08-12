import json

from ovos_utils.log import LOG

from ovos_PHAL_sensors.loggers.base import SensorLogger
from ovos_PHAL_sensors.sensors.base import _norm

# ``requests`` is an OPTIONAL extra, pulled only by ``pip install
# ovos-PHAL-sensors[ha]``. It is imported lazily inside the methods below so
# that merely importing this module never requires it.


class HomeAssistantUpdater(SensorLogger):
    ha_url = ""
    ha_token = ""

    @classmethod
    def binary_sensor_update(cls, sensor):
        import requests

        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/binary_sensor.ovos_{name}_{unique_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": "on" if sensor.value else "off",
                                 "attributes": sensor.attrs}),
                timeout=(3.05, 5),
            ).json()
            LOG.debug(response)
        except Exception:
            LOG.debug(f"failed to push data to {cls.ha_url}/api/states/binary_sensor.ovos_{name}_{unique_id} {sensor.attrs}")

    @classmethod
    def sensor_update(cls, sensor):
        import requests

        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        try:
            response = requests.post(
                f"{cls.ha_url}/api/states/sensor.ovos_{name}_{unique_id}",
                headers={
                    "Authorization": f"Bearer {cls.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": sensor.value,
                                 "attributes": sensor.attrs}),
                timeout=(3.05, 5),
            )
            LOG.debug(response.text)
        except Exception:
            LOG.debug(f"failed to push data to HA /sensor.ovos_{name}_{unique_id} {sensor.attrs}")
