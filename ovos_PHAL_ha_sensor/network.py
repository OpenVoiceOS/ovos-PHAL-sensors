import urllib

from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import Sensor


class ExternalIPSensor(Sensor):
    device_id = "external_ip"
    unit = "string"

    @classproperty
    def value(self):
        return urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')


if __name__ == "__main__":
    print(ExternalIPSensor())
    # external_ip(89.155.204.43, string)
