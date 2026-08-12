import atexit
from dataclasses import dataclass

from ovos_PHAL_sensors.sensors.base import BooleanSensor, Sensor, NumericSensor

try:
    import pulsectl
except ImportError:
    pulsectl = None

# ``pulsectl`` is an OPTIONAL extra, pulled only by ``pip install
# ovos-PHAL-sensors[pulse]``. The client is opened lazily on first use via
# ``_get_pulse`` instead of at import time, so importing this module never
# talks to PulseAudio nor requires the dependency to be installed.
pulse = None if pulsectl is None else True  # kept for `pulse is None` checks elsewhere
_pulse_clients = {}


def _get_pulse(name="ovos"):
    """lazily create (and cache) a pulsectl.Pulse client for `name`"""
    if pulsectl is None:
        return None
    if name not in _pulse_clients:
        client = pulsectl.Pulse(name)
        _pulse_clients[name] = client

        def _close(c=client):
            try:
                c.close()
            except Exception:
                pass

        atexit.register(_close)
    return _pulse_clients[name]


def pa_list_cards():
    sinks = []
    pulse = _get_pulse()
    for s in pulse.card_list():
        sinks.append({
            "index": s.index,
            "profile": s.profile_active.name,
            "name": s.name,
            "card_name": s.proplist.get("alsa.card_name") or s.name,
            "description": s.proplist.get("device.description", ""),
            "form_factor": s.proplist.get("device.form_factor", "unknown")
        })
    return sinks


def pa_list_sources():
    sinks = []
    pulse = _get_pulse()
    for s in pulse.source_list():
        volumes = [v * 100 for v in s.volume.__dict__["values"]]

        sinks.append({
            "index": s.index,
            "mute": s.mute,
            "name": s.name,
            "card": s.card,
            "channel_count": s.channel_count,
            "channel_list": s.channel_list,
            "driver": s.driver,
            "description": s.description,
            "state": str(s.state).split("state=")[-1][:-1],
            "volumes": volumes
        })
    return sinks


def pa_list_sinks():
    sinks = []
    pulse = _get_pulse()
    for s in pulse.sink_list():
        volumes = [v * 100 for v in s.volume.__dict__["values"]]

        sinks.append({
            "index": s.index,
            "mute": s.mute,
            "name": s.name,
            "card": s.card,
            "channel_count": s.channel_count,
            "channel_list": s.channel_list,
            "driver": s.driver,
            "description": s.description,
            "state": str(s.state).split("state=")[-1][:-1],
            "volumes": volumes
        })
    return sinks


def pa_list_input_sinks():
    sinks = []
    pulse = _get_pulse()
    for s in pulse.sink_input_list():
        volumes = [v * 100 for v in s.volume.__dict__["values"]]
        sinks.append({
            "index": s.index,
            "mute": s.mute,
            "name": s.name,
            "playing": 1 if not s.corked else 0,
            "media_name": s.proplist.get("media.name") or "",
            "application": s.proplist.get('application.name') or
                           s.proplist.get('application.binary') or
                           s.proplist.get('application.icon_name') or "",
            "sink": s.sink,
            "channel_count": s.channel_count,
            "channel_list": s.channel_list,
            "driver": s.driver,
            "volumes": volumes
        })
    return sinks


def pa_active_sinks():
    pulse = _get_pulse()
    return [str(s.sink) for s in pulse.sink_input_list()
            if not s.corked]


def pa_bluez_sinks(client=None):
    sinks = []
    pulse = client or _get_pulse()
    for s in pulse.sink_list():
        if s.driver != "module-bluez5-device.c":
            continue

        volumes = [v * 100 for v in s.volume.__dict__["values"]]

        sinks.append({
            "index": s.index,
            "mute": s.mute,
            "name": s.name,
            "card": s.card,
            "channel_count": s.channel_count,
            "channel_list": s.channel_list,
            "driver": s.driver,
            "description": s.description,
            "state": str(s.state).split("state=")[-1][:-1],
            "volumes": volumes
        })

    return sinks


@dataclass
class PAVersionSensor(Sensor):
    unique_id: str = "version"
    device_name: str = "pulseaudio"
    _once: bool = True
    _thread_safe: bool = False

    @property
    def value(self):
        return _get_pulse().server_info().server_version


@dataclass
class PAChannelCountSensor(NumericSensor):
    unique_id: str = "channel_count"
    device_name: str = "pulseaudio"
    _once: bool = True
    _thread_safe: bool = False

    @property
    def value(self):
        return _get_pulse().server_info().channel_count


@dataclass
class PADefaultSinkSensor(Sensor):
    unique_id: str = "default_sink"
    device_name: str = "pulseaudio"
    unit: str = "string"
    _slow: bool = False
    _thread_safe: bool = False

    @property
    def value(self):
        return _get_pulse().server_info().default_sink_name


@dataclass
class PADefaultSourceSensor(Sensor):
    unique_id: str = "default_source"
    device_name: str = "pulseaudio"
    unit: str = "string"
    _slow: bool = False
    _thread_safe: bool = False

    @property
    def value(self):
        return _get_pulse().server_info().default_source_name


@dataclass
class PAHostnameSensor(Sensor):
    unique_id: str = "hostname"
    device_name: str = "pulseaudio"
    _once: bool = True
    _thread_safe: bool = False

    @property
    def value(self):
        return _get_pulse().server_info().host_name


@dataclass
class PAPlaybackSensor(BooleanSensor):
    unique_id: str = "is_playing"
    device_name: str = "pulseaudio"
    _thread_safe: bool = False

    @property
    def value(self):
        return any(not s.corked for s in _get_pulse().sink_input_list())


@dataclass
class PANowPlayingSensor(Sensor):
    unique_id: str = "now_playing"
    device_name: str = "pulseaudio"
    _thread_safe: bool = False
    _slow: bool = False

    @property
    def value(self):
        now_playing_str = ""
        for s in _get_pulse().sink_input_list():
            if not s.corked:
                now_playing_str += s.name + "\n"
        return now_playing_str.strip()


@dataclass
class PAAudioPlayingSensor(BooleanSensor):
    unique_id: str = "is_playing"
    device_name: str = "pulseaudio"
    _thread_safe: bool = False
    _slow: bool = False

    @property
    def value(self):
        return bool(PANowPlayingSensor().value)


@dataclass
class PABluezConnectedSensor(BooleanSensor):
    unique_id: str = "bluez_connected"
    device_name: str = "pulseaudio"
    _thread_safe: bool = False

    @property
    def value(self):
        for s in _get_pulse().sink_list():
            if s.driver == "module-bluez5-device.c":
                return True
        return False


@dataclass
class PABluezActiveSensor(BooleanSensor):
    unique_id: str = "bluez_active"
    device_name: str = "pulseaudio"
    _thread_safe: bool = False

    @property
    def value(self):
        pulse = _get_pulse()
        actives = [s.sink for s in pulse.sink_input_list()
                   if not s.corked]
        for s in pulse.sink_list():
            if s.driver == "module-bluez5-device.c":
                if s.index in actives:
                    return True
        return False


if __name__ == "__main__":
    print(PAVersionSensor().value)
    print(PAChannelCountSensor().value)
    print(PADefaultSinkSensor().value)
    print(PADefaultSourceSensor().value)
    print(PAHostnameSensor().value)
    print(PAPlaybackSensor().value)
    print(PANowPlayingSensor().value)
    print(PAAudioPlayingSensor().value)
    print(PABluezConnectedSensor().value)
    print(PABluezActiveSensor().value)

    # pa_version(16.1, string)
    # pa_channel_count(2, number)
    # pa_default_sink(alsa_output.pci-0000_00_1f.3.analog-stereo, string)
    # pa_default_source(alsa_input.pci-0000_00_1f.3.analog-stereo, string)
    # pa_hostname(miro-asustufgamingf15fx506hmfx506hm, string)
    # pa_is_playing(False, bool)
    # pa_now_playing(, string)
    # pa_bluez_connected(False, bool)
    # pa_bluez_active(False, bool)
