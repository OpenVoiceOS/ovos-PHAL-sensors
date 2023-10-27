import getpass
import os

import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import BooleanSensor


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


class SystemdSensor(BooleanSensor):
    device_id = "systemd_running"

    @classproperty
    def value(self):
        return bool(_find_proc("systemd"))


class DBUSDaemonSensor(BooleanSensor):
    device_id = "dbus_daemon_running"

    @classproperty
    def value(self):
        return bool(_find_proc("dbus-daemon"))


class KDEConnectSensor(BooleanSensor):
    device_id = "kdeconnect_running"

    @classproperty
    def value(self):
        return bool(_find_proc("kdeconnectd"))


class PulseAudioSensor(BooleanSensor):
    device_id = "pulseaudio_running"

    @classproperty
    def value(self):
        return bool(_find_proc("pulseaudio"))


class PipewireSensor(BooleanSensor):
    device_id = "pipewire_running"

    @classproperty
    def value(self):
        return bool(_find_proc("pipewire"))


class PlasmaShellSensor(BooleanSensor):
    device_id = "plasmashell_running"

    @classproperty
    def value(self):
        return bool(_find_proc("plasmashell"))


class FirefoxSensor(BooleanSensor):
    device_id = "firefox_running"

    @classproperty
    def value(self):
        return bool(_find_proc("firefox"))


class SpotifySensor(BooleanSensor):
    device_id = "spotify_running"

    @classproperty
    def value(self):
        p = _find_proc("spotify") or \
            _find_proc("rasspotify") or \
            _find_proc("librespot") or \
            _find_proc("spotifyd")
        return bool(p)


class MiniDLNASensor(BooleanSensor):
    device_id = "minidlnad_running"

    @classproperty
    def value(self):
        p = _find_proc("minidlnad")
        return bool(p)


class UPMPDCliSensor(BooleanSensor):
    device_id = "upmpdcli_running"

    @classproperty
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
