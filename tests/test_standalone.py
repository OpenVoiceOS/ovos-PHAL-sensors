"""The standalone daemon must run WITHOUT OVOS (FakeBus) for HA/MQTT-only use,
and connect to the real bus when OVOS is present."""
from ovos_utils.fakebus import FakeBus

from ovos_PHAL_sensors.__main__ import _standalone_bus


def test_standalone_config_uses_fakebus():
    assert isinstance(_standalone_bus({"standalone": True}), FakeBus)
    assert isinstance(_standalone_bus({"disable_bus": True}), FakeBus)


def test_falls_back_to_fakebus_when_no_bus(monkeypatch):
    # No OVOS messagebus reachable -> must not hang, must fall back to FakeBus
    import ovos_bus_client

    class DeadBus:
        def __init__(self, *a, **k):
            import threading
            self.connected_event = threading.Event()  # never set -> not connected

        def run_in_thread(self):
            pass

        def close(self):
            pass

    monkeypatch.setattr(ovos_bus_client, "MessageBusClient", DeadBus)
    # wait(5) would be slow; shrink by monkeypatching the event wait via a tiny bus
    bus = _standalone_bus({})
    assert isinstance(bus, FakeBus)
