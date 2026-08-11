"""A sensor that keeps failing must self-disable after 3 consecutive
failures, and stop being polled afterwards - otherwise one broken sensor
spams the log forever and wastes a worker thread every cycle."""
import dataclasses
from typing import List

from ovos_PHAL_sensors.device import BaseDevice
from ovos_PHAL_sensors.sensors.base import Sensor


@dataclasses.dataclass
class _AlwaysFailsSensor(Sensor):
    unique_id: str = "always_fails"
    device_name: str = "test"
    _slow: bool = False
    _once: bool = False

    calls: List[int] = dataclasses.field(default_factory=list)

    def sensor_update(self):
        self.calls.append(1)
        raise RuntimeError("simulated hardware failure")


class _OneSensorDevice(BaseDevice):
    def __init__(self, name, sensor):
        self._sensor = sensor
        super().__init__(name)

    @property
    def sensors(self) -> List[Sensor]:
        return [self._sensor]


def test_sensor_self_disables_after_three_failures():
    sensor = _AlwaysFailsSensor()
    device = _OneSensorDevice("dev", sensor)

    device.update()
    device.update()
    device.update()

    assert sensor.unique_id in device._disabled_sensors
    assert len(sensor.calls) == 3


def test_disabled_sensor_is_skipped_on_subsequent_updates():
    sensor = _AlwaysFailsSensor()
    device = _OneSensorDevice("dev", sensor)

    for _ in range(3):
        device.update()
    assert len(sensor.calls) == 3

    # further update cycles must NOT call sensor_update again
    device.update()
    device.update()
    assert len(sensor.calls) == 3
