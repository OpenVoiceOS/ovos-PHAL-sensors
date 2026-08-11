"""New diagnostic sensors (CPU freq/load, RPi throttling, network/disk
throughput counters, wifi signal, uptime/process count) must degrade
cleanly on machines lacking the underlying feature - never raise."""
import psutil

from ovos_PHAL_sensors.sensors.cpu import (
    CPUFrequencySensor, LoadAverage1Sensor, LoadAverage5Sensor,
    LoadAverage15Sensor,
)
from ovos_PHAL_sensors.sensors import throttle
from ovos_PHAL_sensors.sensors.throttle import (
    ThrottleStateSensor, UnderVoltageSensor, ThrottledSensor,
)
from ovos_PHAL_sensors.sensors.network import (
    NetworkBytesSentSensor, NetworkBytesRecvSensor, WifiSignalSensor,
)
from ovos_PHAL_sensors.sensors.os_system import UptimeSensor, ProcessCountSensor


# ---------------------------------------------------------------------------
# CPU frequency / load average
# ---------------------------------------------------------------------------

def test_cpu_frequency_sensor_returns_current_freq(monkeypatch):
    class _FakeFreq:
        current = 1800.0

    monkeypatch.setattr(psutil, "cpu_freq", lambda: _FakeFreq())
    assert CPUFrequencySensor().value == 1800.0


def test_cpu_frequency_sensor_guards_none(monkeypatch):
    monkeypatch.setattr(psutil, "cpu_freq", lambda: None)
    assert CPUFrequencySensor().value == 0


def test_cpu_frequency_sensor_guards_none_current(monkeypatch):
    class _FakeFreq:
        current = None

    monkeypatch.setattr(psutil, "cpu_freq", lambda: _FakeFreq())
    assert CPUFrequencySensor().value == 0


def test_load_average_sensors_return_getloadavg_values(monkeypatch):
    import os
    monkeypatch.setattr(os, "getloadavg", lambda: (0.5, 1.5, 2.5))
    assert LoadAverage1Sensor().value == 0.5
    assert LoadAverage5Sensor().value == 1.5
    assert LoadAverage15Sensor().value == 2.5


def test_load_average_sensors_guard_oserror(monkeypatch):
    import os

    def _raise():
        raise OSError("not supported")

    monkeypatch.setattr(os, "getloadavg", _raise)
    assert LoadAverage1Sensor().value == 0
    assert LoadAverage5Sensor().value == 0
    assert LoadAverage15Sensor().value == 0


# ---------------------------------------------------------------------------
# Raspberry Pi throttling
# ---------------------------------------------------------------------------

def test_throttle_state_ok_when_no_bits_set(monkeypatch):
    monkeypatch.setattr(throttle, "get_throttled", lambda: 0x0)
    assert ThrottleStateSensor().value == "ok"
    assert UnderVoltageSensor().value is False
    assert ThrottledSensor().value is False


def test_throttle_state_under_voltage_now_and_occurred(monkeypatch):
    monkeypatch.setattr(throttle, "get_throttled", lambda: 0x50005)
    assert ThrottleStateSensor().value == "under-voltage"
    assert UnderVoltageSensor().value is True
    assert ThrottledSensor().value is True


def test_throttle_state_occurred_bits_only(monkeypatch):
    monkeypatch.setattr(throttle, "get_throttled", lambda: 0x50000)
    assert ThrottleStateSensor().value == "under-voltage (occurred)"
    assert UnderVoltageSensor().value is True
    assert ThrottledSensor().value is True


def test_throttle_sensors_report_na_false_when_vcgencmd_absent(monkeypatch):
    monkeypatch.setattr(throttle, "get_throttled", lambda: None)
    assert ThrottleStateSensor().value == "n/a"
    assert UnderVoltageSensor().value is False
    assert ThrottledSensor().value is False


def test_get_throttled_returns_none_without_vcgencmd(monkeypatch):
    monkeypatch.setattr(throttle, "has_vcgencmd", False)
    assert throttle.get_throttled() is None


# ---------------------------------------------------------------------------
# Network throughput / wifi
# ---------------------------------------------------------------------------

def test_network_bytes_sent_recv_report_mb(monkeypatch):
    class _FakeCounters:
        bytes_sent = 5 * 1024 ** 2
        bytes_recv = 10 * 1024 ** 2

    monkeypatch.setattr(psutil, "net_io_counters", lambda: _FakeCounters())
    assert NetworkBytesSentSensor().value == 5.0
    assert NetworkBytesRecvSensor().value == 10.0


def test_network_bytes_sent_recv_guard_none(monkeypatch):
    monkeypatch.setattr(psutil, "net_io_counters", lambda: None)
    assert NetworkBytesSentSensor().value == 0
    assert NetworkBytesRecvSensor().value == 0


_real_open = open


def test_wifi_signal_sensor_zero_when_proc_missing(monkeypatch):
    def _raise_open(path, *args, **kwargs):
        if path == "/proc/net/wireless":
            raise FileNotFoundError("no such file")
        return _real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _raise_open)
    assert WifiSignalSensor().value == 0


def test_wifi_signal_sensor_zero_when_proc_empty(monkeypatch):
    import io

    def _fake_open(path, *args, **kwargs):
        if path == "/proc/net/wireless":
            return io.StringIO("")
        return _real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _fake_open)
    assert WifiSignalSensor().value == 0


def test_wifi_signal_sensor_parses_signal_level(monkeypatch):
    import io

    content = (
        "Inter-| sta-|   Quality        |   Discarded packets\n"
        " face | tus | link level noise |  nwid  crypt   frag  retry   misc\n"
        " wlan0: 0000   70.  -40.  -256        0      0      0      0      0\n"
    )

    def _fake_open(path, *args, **kwargs):
        if path == "/proc/net/wireless":
            return io.StringIO(content)
        return _real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _fake_open)
    assert WifiSignalSensor().value == -40.0


# ---------------------------------------------------------------------------
# Uptime / process count
# ---------------------------------------------------------------------------

def test_uptime_sensor(monkeypatch):
    import time
    monkeypatch.setattr(psutil, "boot_time", lambda: 100.0)
    monkeypatch.setattr(time, "time", lambda: 250.0)
    assert UptimeSensor().value == 150


def test_process_count_sensor(monkeypatch):
    monkeypatch.setattr(psutil, "pids", lambda: list(range(42)))
    assert ProcessCountSensor().value == 42


# ---------------------------------------------------------------------------
# Gating
# ---------------------------------------------------------------------------

def test_rpi_false_excludes_throttle_sensors():
    from ovos_PHAL_sensors import OVOSDevice
    device = OVOSDevice("x", screen=False, battery=False, memory=False,
                        cpu=False, network=False, fan=False, os=False,
                        apps=False, pa=False, blue=False, wifi=False,
                        rpi=False)
    classes = {type(s) for s in device.sensors}
    assert classes.isdisjoint({ThrottleStateSensor, UnderVoltageSensor, ThrottledSensor})


def test_cpu_true_includes_frequency_and_load_average():
    from ovos_PHAL_sensors import OVOSDevice
    device = OVOSDevice("x", screen=False, battery=False, memory=False,
                        cpu=True, network=False, fan=False, os=False,
                        apps=False, pa=False, blue=False, wifi=False,
                        rpi=False)
    classes = {type(s) for s in device.sensors}
    assert CPUFrequencySensor in classes
    assert LoadAverage1Sensor in classes
    assert LoadAverage5Sensor in classes
    assert LoadAverage15Sensor in classes
