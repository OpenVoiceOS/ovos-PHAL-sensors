"""Sensors must never raise on hardware-less CI runners: no battery, no
/sys/class/power_supply, no network."""
import urllib.request

import pytest

from ovos_PHAL_sensors.sensors import battery as battery_mod
from ovos_PHAL_sensors.sensors.battery import (
    BatterySensor, BatteryPowerSensor, BatteryCurrentSensor,
    BatteryVoltageSensor, BatteryChargeSensor, BatteryStatusSensor,
    BatteryStoredEnergySensor,
)
from ovos_PHAL_sensors.sensors.network import ExternalIPSensor


def test_battery_sensors_default_sanely_with_no_battery(monkeypatch):
    monkeypatch.setattr(battery_mod, "get_battery_info", lambda: iter([]))

    assert BatterySensor().value == 0
    assert BatteryPowerSensor().value == 0
    assert BatteryCurrentSensor().value == 0
    assert BatteryVoltageSensor().value == 0
    assert BatteryChargeSensor().value == 0
    assert BatteryStoredEnergySensor().value == 0
    assert BatteryStatusSensor().value == "unknown"


def test_get_battery_info_no_crash_when_power_supply_dir_absent(monkeypatch):
    monkeypatch.setattr(battery_mod.os.path, "isdir", lambda p: False)

    result = list(battery_mod.get_battery_info())
    assert result == []


def test_get_battery_info_no_crash_when_dir_present_but_empty(monkeypatch):
    monkeypatch.setattr(battery_mod.os.path, "isdir", lambda p: True)
    monkeypatch.setattr(battery_mod.os, "listdir", lambda p: [])

    result = list(battery_mod.get_battery_info())
    assert result == []


def test_external_ip_sensor_no_crash_on_network_failure(monkeypatch):
    def _raise(*a, **k):
        raise OSError("network unreachable")

    monkeypatch.setattr(urllib.request, "urlopen", _raise)

    sensor = ExternalIPSensor()
    # must not raise
    value = sensor.value
    assert value == "0.0.0.0"  # untouched default, since urlopen failed
