import dataclasses
import socket
import urllib.request

import psutil
from ovos_utils.log import LOG

from ovos_PHAL_sensors.sensors.base import Sensor, NumericSensor


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
            self._ip = urllib.request.urlopen('https://api.ipify.org',
                                              timeout=5).read().decode('utf8')
        except Exception as e:
            LOG.debug(f"failed to fetch external ip: {e}")
        return self._ip

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "icon": "mdi:ip"}


@dataclasses.dataclass
class NetworkBytesSentSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "bytes_sent"
    device_name: str = "network"

    @property
    def value(self):
        counters = psutil.net_io_counters()
        if counters is None:
            return 0
        return round(counters.bytes_sent / 1024 ** 2, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "state_class": "total_increasing",
                "icon": "mdi:upload-network"}


@dataclasses.dataclass
class NetworkBytesRecvSensor(NumericSensor):
    unit: str = "MB"
    unique_id: str = "bytes_recv"
    device_name: str = "network"

    @property
    def value(self):
        counters = psutil.net_io_counters()
        if counters is None:
            return 0
        return round(counters.bytes_recv / 1024 ** 2, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit,
                "state_class": "total_increasing",
                "icon": "mdi:download-network"}


@dataclasses.dataclass
class WifiSignalSensor(NumericSensor):
    unit: str = "dBm"
    unique_id: str = "wifi_signal"
    device_name: str = "network"

    @property
    def value(self):
        try:
            with open("/proc/net/wireless", "r") as f:
                lines = f.readlines()
        except (OSError, IOError) as e:
            LOG.debug(f"failed to read /proc/net/wireless: {e}")
            return 0
        if len(lines) < 3:
            return 0
        try:
            # line format: "iface: status link level noise ..."
            fields = lines[2].split()
            return float(fields[3].rstrip("."))
        except (IndexError, ValueError) as e:
            LOG.debug(f"failed to parse /proc/net/wireless: {e}")
            return 0

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "signal_strength",
                "unit_of_measurement": self.unit,
                "icon": "mdi:wifi"}


if __name__ == "__main__":
    print(LocalIPSensor().value)
    print(ExternalIPSensor())
    print(NetworkBytesSentSensor())
    print(NetworkBytesRecvSensor())
    print(WifiSignalSensor())
    # external_ip(89.155.204.43, string)
