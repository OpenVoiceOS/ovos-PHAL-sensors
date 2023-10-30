import dataclasses
import time
from threading import Thread, Event

from ovos_utils import flatten_list

from ovos_PHAL_sensors.base import BooleanSensor, Sensor, _norm
from ovos_PHAL_sensors.pulse import pa_bluez_sinks, pulse

try:
    import bluetooth
except ImportError:
    bluetooth = None


@dataclasses.dataclass
class BluetoothDevicePresence(BooleanSensor):
    present: bool = False
    unique_id: str = "bluez"
    device_name: str = "bluetooth"

    @property
    def value(self):
        return self.present

    @property
    def attrs(self):
        return {"friendly_name": self.unique_id.replace("_", ":").upper() + " Bluetooth",
                "icon": "mdi:bluetooth",
                "device_class": "presence"}


@dataclasses.dataclass
class BluetoothDeviceName(Sensor):
    friendly_name: str = ""
    unique_id: str = "bluez"
    device_name: str = "bluetooth"

    @property
    def value(self):
        return self.friendly_name

    @property
    def attrs(self):
        return {"friendly_name": self.friendly_name,
                "icon": "mdi:bluetooth"}


@dataclasses.dataclass
class BluetoothSpeakerConnected(Sensor):
    connected: bool = False
    unique_id: str = "pulseaudio"
    device_name: str = "bluetooth"

    @property
    def value(self):
        return self.connected

    @property
    def attrs(self):
        return {"friendly_name": self.unique_id.replace("_connected", "").replace("_", ":").upper() + " Connected",
                "icon": "mdi:bluetooth",
                "device_class": "running",
                "state_color": True}


class BlueScanner(Thread):
    def __init__(self, daemon=True):
        super().__init__(daemon=daemon)
        self.last_seen = {}
        self.lose_time = 60
        self.running = Event()
        self.time_between_scans = 30
        self._sensors = {}

    @property
    def sensors(self):
        sensors = [s for s in self._sensors.values()]
        return flatten_list(sensors)

    def run(self) -> None:
        self.running.set()
        while self.running.is_set():
            self.scan_devices()
            Event().wait(self.time_between_scans)

    def scan_speakers(self):
        if pulse is not None:
            for sink in pa_bluez_sinks():
                mac = sink["name"].split("bluez_sink.")[-1].split(".a2dp_sink")[0]
                a = _norm(mac)
                self.last_seen[a] = time.time()
                if a not in self._sensors:
                    self._sensors[a] = [BluetoothDevicePresence(present=True, unique_id=a),
                                        BluetoothDeviceName(friendly_name=sink["description"], unique_id=a + "_name"),
                                        BluetoothSpeakerConnected(connected=True, unique_id=a + "_connected")]
                else:
                    self._sensors[a][-1].connected = True
                yield self._sensors[a][-1]

    def scan_devices(self):
        if bluetooth is None:
            print("pip install pybluez2 to scan bluetooth devices")
            return
        try:
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
        except OSError:  # seems to happen on turn bluetooth off
            nearby_devices = []
        for addr, name in nearby_devices:
            a = _norm(addr.replace(":", "_"))
            self.last_seen[a] = time.time()
            if a in self._sensors:
                self._sensors[a].present = True
            else:
                self._sensors[a] = [BluetoothDevicePresence(present=True, unique_id=a),
                                    BluetoothDeviceName(friendly_name=name, unique_id=a + "_name"),
                                    BluetoothSpeakerConnected(connected=False, unique_id=a + "_connected")]

        n = time.time()
        for dev, ts in self.last_seen.items():
            if self._sensors[dev][0].present and n - ts > self.lose_time:
                self._sensors[dev][0].present = False


if __name__ == "__main__":
    b = BlueScanner(daemon=False)
    b.start()
