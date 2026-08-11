"""Native message-bus contract: this is the whole point of the plugin.

MessageBusLogger.sensor_update / binary_sensor_update must emit exactly one
Message on a fixed topic with a fixed data shape, so downstream consumers
(HA integrations, dashboards) can rely on it never regressing.
"""
import dataclasses

from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

from ovos_PHAL_sensors.loggers.base import MessageBusLogger
from ovos_PHAL_sensors.sensors.base import Sensor, BooleanSensor

EXPECTED_KEYS = {"state", "sensor_id", "device_name", "name", "attributes"}


@dataclasses.dataclass
class _FakeSensor(Sensor):
    unique_id: str = "my sensor-id"
    device_name: str = "My Device"

    @property
    def value(self):
        return 42

    @property
    def attrs(self):
        return {"friendly_name": "Fake"}


@dataclasses.dataclass
class _FakeBinarySensor(BooleanSensor):
    unique_id: str = "my-binary"
    device_name: str = "My Device"

    @property
    def value(self):
        return True


def _capture(bus, topic):
    seen = []
    bus.on(topic, lambda m: seen.append(m))
    return seen


def test_sensor_update_emits_single_message_on_fixed_topic(monkeypatch):
    bus = FakeBus()
    monkeypatch.setattr(MessageBusLogger, "bus", bus)
    seen = _capture(bus, "ovos.phal.sensor")

    sensor = _FakeSensor()
    MessageBusLogger.sensor_update(sensor)

    assert len(seen) == 1
    msg = seen[0]
    assert isinstance(msg, Message)
    assert msg.msg_type == "ovos.phal.sensor"
    assert set(msg.data.keys()) == EXPECTED_KEYS
    assert msg.data["state"] == 42
    assert msg.data["name"] == "my_sensorid"  # _norm strips spaces/dashes
    assert msg.data["device_name"] == "my_device"
    assert msg.data["sensor_id"] == "my_device_my_sensorid"
    assert msg.data["attributes"] == {"friendly_name": "Fake"}


def test_binary_sensor_update_emits_single_message_on_fixed_topic(monkeypatch):
    bus = FakeBus()
    monkeypatch.setattr(MessageBusLogger, "bus", bus)
    seen = _capture(bus, "ovos.phal.binary_sensor")

    sensor = _FakeBinarySensor()
    MessageBusLogger.binary_sensor_update(sensor)

    assert len(seen) == 1
    msg = seen[0]
    assert msg.msg_type == "ovos.phal.binary_sensor"
    assert set(msg.data.keys()) == EXPECTED_KEYS
    assert msg.data["state"] is True
    # _norm strips dashes entirely (not to underscore): "my-binary" -> "mybinary"
    assert msg.data["name"] == "mybinary"
    assert msg.data["device_name"] == "my_device"
    assert msg.data["sensor_id"] == "my_device_mybinary"


def test_boolean_sensor_routes_through_binary_sensor_update(monkeypatch):
    """BooleanSensor.sensor_update() must dispatch to binary_sensor_update
    on the logger, not sensor_update - otherwise binary sensors would show
    up on the wrong bus topic."""
    bus = FakeBus()
    monkeypatch.setattr(MessageBusLogger, "bus", bus)
    generic_seen = _capture(bus, "ovos.phal.sensor")
    binary_seen = _capture(bus, "ovos.phal.binary_sensor")

    sensor = _FakeBinarySensor()
    sensor.loggers = [MessageBusLogger]
    sensor.sensor_update()  # the dataclass method, not the logger's

    assert len(binary_seen) == 1
    assert len(generic_seen) == 0
