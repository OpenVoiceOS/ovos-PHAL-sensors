import dataclasses
import socket
import urllib

from ovos_PHAL_sensors.sensors.base import Sensor


@dataclasses.dataclass
class LocalIPSensor(Sensor):
    unique_id: str = "local_ip"
    device_name: str = "network"

    @property
    def value(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "icon": "mdi:ip"}


@dataclasses.dataclass
class ExternalIPSensor(Sensor):
    unique_id: str = "external_ip"
    device_name: str = "network"
    _ip = "0.0.0.0"

    @property
    def value(self):
        try:
            self._ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        except:
            pass
        return self._ip

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "icon": "mdi:ip"}


if __name__ == "__main__":
    print(LocalIPSensor().value)
    print(ExternalIPSensor())
    # external_ip(89.155.204.43, string)
