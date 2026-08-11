"""OVOSDevice must gate which sensor classes appear in .sensors strictly
by the constructor flags - a leaked sensor when a category is disabled
would silently over-report to Home Assistant / the bus."""
from ovos_PHAL_sensors import OVOSDevice
from ovos_PHAL_sensors.sensors.cpu import CPUCountSensor, CPUTemperatureSensor, CPUUsageSensor
from ovos_PHAL_sensors.sensors.battery import (
    BatterySensor, BatteryChargeSensor, BatteryCurrentSensor,
    BatteryStoredEnergySensor, BatteryPowerSensor, BatteryStatusSensor,
    BatteryVoltageSensor,
)

CPU_CLASSES = (CPUCountSensor, CPUTemperatureSensor, CPUUsageSensor)
BATTERY_CLASSES = (BatterySensor, BatteryChargeSensor, BatteryCurrentSensor,
                    BatteryStoredEnergySensor, BatteryPowerSensor,
                    BatteryStatusSensor, BatteryVoltageSensor)


def _all_disabled_device(name="x", **overrides):
    kwargs = dict(screen=False, battery=False, memory=False, cpu=False,
                  network=False, fan=False, os=False, apps=False,
                  pa=False, blue=False, wifi=False)
    kwargs.update(overrides)
    return OVOSDevice(name, **kwargs)


def test_cpu_and_battery_off_excludes_their_sensor_classes():
    device = _all_disabled_device(cpu=False, battery=False)
    classes = {type(s) for s in device.sensors}

    assert classes.isdisjoint(CPU_CLASSES)
    assert classes.isdisjoint(BATTERY_CLASSES)
    assert device.sensors == []


def test_cpu_and_battery_on_includes_their_sensor_classes():
    device = _all_disabled_device(cpu=True, battery=True)
    classes = {type(s) for s in device.sensors}

    assert classes.issuperset(CPU_CLASSES)
    assert classes.issuperset(BATTERY_CLASSES)


def test_each_category_flag_independently_gates_its_sensors():
    # memory on, everything else off
    device = _all_disabled_device(memory=True)
    classes = {type(s) for s in device.sensors}
    assert len(classes) > 0
    assert classes.isdisjoint(CPU_CLASSES)
    assert classes.isdisjoint(BATTERY_CLASSES)

    # network on, everything else off
    device = _all_disabled_device(network=True)
    from ovos_PHAL_sensors.sensors.network import ExternalIPSensor, LocalIPSensor
    classes = {type(s) for s in device.sensors}
    assert classes == {ExternalIPSensor, LocalIPSensor}


def test_optional_hardware_sensors_absent_when_deps_missing():
    """pulse/blue/screen are gated on optional 3rd-party libs that are not
    installed on a headless CI runner - OVOSDevice must force those flags
    off rather than crash when the flag is requested True."""
    from ovos_PHAL_sensors.sensors.extra.blue import bluetooth
    from ovos_PHAL_sensors.sensors.extra.pulse import pulse
    from ovos_PHAL_sensors.sensors.extra.screen import sbc

    device = OVOSDevice("x", pa=True, blue=True, screen=True,
                        battery=False, cpu=False, memory=False,
                        network=False, fan=False, os=False, apps=False)
    # must not have raised constructing OVOSDevice; sensors must be listable
    sensors = device.sensors

    if bluetooth is None:
        assert device.blue is None
    if pulse is None:
        assert device.pa is False
    if sbc is None:
        assert device.screen is False
    assert isinstance(sensors, list)
