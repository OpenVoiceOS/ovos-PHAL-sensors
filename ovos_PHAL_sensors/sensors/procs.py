import getpass
import os
from dataclasses import dataclass

import psutil

from ovos_PHAL_sensors.sensors.base import BooleanSensor


def get_procs():
    return {p.pid: p.info['name']
            for p in psutil.process_iter(['name', 'username'])
            if p.info['username'] == getpass.getuser()}


def _find_proc(name):
    for p in psutil.process_iter(["name", "exe", "cmdline"]):
        if name == p.info['name'] or \
                p.info['exe'] and os.path.basename(p.info['exe']) == name or \
                p.info['cmdline'] and p.info['cmdline'][0] == name:
            return p


@dataclass
class SystemdSensor(BooleanSensor):
    unique_id: str = "systemd_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("systemd"))


@dataclass
class DBUSDaemonSensor(BooleanSensor):
    unique_id: str = "dbus_daemon_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("dbus-daemon"))


@dataclass
class KDEConnectSensor(BooleanSensor):
    unique_id: str = "kdeconnect_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("kdeconnectd"))


@dataclass
class PulseAudioSensor(BooleanSensor):
    unique_id: str = "pulseaudio_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("pulseaudio"))


@dataclass
class PipewireSensor(BooleanSensor):
    unique_id: str = "pipewire_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("pipewire"))


@dataclass
class PlasmaShellSensor(BooleanSensor):
    unique_id: str = "plasmashell_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("plasmashell"))


@dataclass
class FirefoxSensor(BooleanSensor):
    unique_id: str = "firefox_running"
    device_name: str = "os"

    @property
    def value(self):
        return bool(_find_proc("firefox"))


@dataclass
class SpotifySensor(BooleanSensor):
    unique_id: str = "spotify_running"
    device_name: str = "os"

    @property
    def value(self):
        p = _find_proc("spotify") or \
            _find_proc("rasspotify") or \
            _find_proc("librespot") or \
            _find_proc("spotifyd")
        return bool(p)


@dataclass
class MiniDLNASensor(BooleanSensor):
    unique_id: str = "minidlnad_running"
    device_name: str = "os"

    @property
    def value(self):
        p = _find_proc("minidlnad")
        return bool(p)


@dataclass
class UPMPDCliSensor(BooleanSensor):
    unique_id: str = "upmpdcli_running"
    device_name: str = "os"

    @property
    def value(self):
        p = _find_proc("upmpdcli")
        return bool(p)


if __name__ == "__main__":
    print(SystemdSensor())
    print(DBUSDaemonSensor())
    print(KDEConnectSensor())
    print(PulseAudioSensor())
    print(PipewireSensor())
    print(PlasmaShellSensor())
    print(FirefoxSensor())
    print(SpotifySensor())
    print(MiniDLNASensor())
    print(UPMPDCliSensor())
    # systemd_running(True, bool)
    # dbus_daemon_running(True, bool)
    # kdeconnect_running(True, bool)
    # pulseaudio_running(True, bool)
    # pipewire_running(True, bool)
    # plasmashell_running(True, bool)
    # firefox_running(True, bool)
    # spotify_running(False, bool)
    # minidlnad_running(False, bool)
    # upmpdcli_running(False, bool)
