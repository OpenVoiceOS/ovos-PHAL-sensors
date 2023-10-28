import dataclasses
import urllib

from ovos_utils import classproperty

from ovos_PHAL_sensors.base import Sensor


@dataclasses.dataclass
class ExternalIPSensor(Sensor):
    unique_id: str = "external_ip"
    device_name: str = "network"

    @classproperty
    def value(self):
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')

    @classproperty
    def attrs(cls):
        return {"friendly_name": cls.__name__,
                "icon": "mdi:ip"}


if __name__ == "__main__":
    print(ExternalIPSensor())
    # external_ip(89.155.204.43, string)
