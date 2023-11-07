import dataclasses
import os.path
import subprocess
import time
from pprint import pprint

from ovos_utils import flatten_list

from ovos_PHAL_sensors.sensors.base import NumericSensor, Sensor, _norm


@dataclasses.dataclass
class SignalLevelSensor(NumericSensor):
    level: int = 0
    device_name: str = "wifi"
    unique_id: str = "signal_level"

    @property
    def value(self):
        return self.level


@dataclasses.dataclass
class ESSIDSensor(Sensor):
    ssid: str = ""
    device_name: str = "wifi"
    unique_id: str = "essid"
    _allow_prefix: bool = False

    @property
    def value(self):
        return self.ssid


def scan_wifi(site_id):
    sensors = []
    # TODO - needs sudo, run as root...
    out = subprocess.check_output("iwlist scan".split(), stderr=subprocess.PIPE).decode("utf-8")
    for l in out.split("\n"):
        l = l.strip()
        if "- Address: " in l:
            addr = l.split("- Address: ")[-1]
        if "Signal level=" in l:
            sig, unit = l.split("Signal level=")[-1].split(" ")
        if "ESSID:" in l:
            ssid = l.split("ESSID:")[-1][1:-1]
            sensors += [
                SignalLevelSensor(unique_id=f"{_norm(addr.replace(':', '_'))}_signal_level",
                                  device_name="wifi_" + site_id,
                                  unit=unit, level=int(sig)),
                ESSIDSensor(device_name="wifi_" + _norm(addr.replace(':', '_')), ssid=ssid)
            ]
    return sensors


class WifiDatasetScanner:
    def __init__(self, site_id, n_readings=50):
        self.site_id = site_id
        self.n_readings = n_readings

    def gather_dataset(self):
        if os.path.isfile(f"{self.site_id}.csv"):
            detections = self.import_csv(f"{self.site_id}.csv")
            print(f"loaded {len(detections)} from {self.site_id}.csv")
        else:
            detections = []
        while len(detections) < self.n_readings:
            sensors = {s.unique_id: s.value for s in scan_wifi(self.site_id) if isinstance(s, SignalLevelSensor)}
            detections.append(sensors)
            print(f"gathered {len(detections)} out of {self.n_readings} readings...")
            pprint(sensors)
            time.sleep(1)
        return detections

    def export_csv(self):
        d = self.gather_dataset()
        with open(f"{self.site_id}.csv", "w") as f:
            keys = list(set(flatten_list(list(_.keys()) for _ in d)))
            header = f"site,{','.join(keys)}\n"
            f.write(header)
            for p in d:
                l = f"{self.site_id},"
                for k in keys:
                    l += f"{p.get(k, 0)},"
                l = l[:-1] + "\n"
                f.write(l)

    def import_csv(self, path):
        readings = []
        with open(path) as f:
            lines = f.read().split("\n")
            keys = lines[0].split(",")[1:]
            for l in set(lines[1:]):
                vals = l.split(",")
                if vals[0] != self.site_id:
                    continue
                d = {k: v for k, v in zip(keys, vals[1:])}
                readings.append(d)
        return readings
