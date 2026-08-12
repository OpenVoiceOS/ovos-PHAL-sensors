"""PHALSensors.shutdown() must flip running to False and stop the
bluetooth scanner thread, so the plugin doesn't leave a daemon thread
running forever after PHAL tears down the plugin."""
import threading
from unittest.mock import MagicMock

from ovos_utils.fakebus import FakeBus

from ovos_PHAL_sensors import PHALSensors


def _make_plugin():
    bus = FakeBus()
    plugin = PHALSensors.__new__(PHALSensors)  # bypass initialize()/run()
    # PHALPlugin subclasses Thread; its `name` setter asserts
    # Thread.__init__ ran, so satisfy that without running the real
    # PHALPlugin.__init__ (which starts background threads/bus wiring)
    threading.Thread.__init__(plugin, daemon=True)
    plugin.running = True
    plugin.sleep = 5
    plugin.bus = bus
    plugin.name = "phal_sensors"
    plugin.config = {}
    return plugin


def test_shutdown_stops_running_and_bluetooth_scanner(monkeypatch):
    plugin = _make_plugin()

    fake_device = MagicMock()
    fake_device.blue = MagicMock()
    plugin.device = fake_device

    # PHALPlugin.shutdown() (superclass) does bus cleanup we don't care
    # about here - stub it so this stays a unit test of PHALSensors logic
    from ovos_plugin_manager.templates.phal import PHALPlugin
    monkeypatch.setattr(PHALPlugin, "shutdown", lambda self: None)

    plugin.shutdown()

    assert plugin.running is False
    fake_device.blue.stop.assert_called_once()


def test_shutdown_no_crash_when_blue_is_none(monkeypatch):
    plugin = _make_plugin()
    fake_device = MagicMock()
    fake_device.blue = None
    plugin.device = fake_device

    from ovos_plugin_manager.templates.phal import PHALPlugin
    monkeypatch.setattr(PHALPlugin, "shutdown", lambda self: None)

    plugin.shutdown()  # must not raise

    assert plugin.running is False


def test_shutdown_no_crash_when_device_never_initialized(monkeypatch):
    plugin = _make_plugin()
    # simulate shutdown() called before initialize() ever ran
    if hasattr(plugin, "device"):
        del plugin.device

    from ovos_plugin_manager.templates.phal import PHALPlugin
    monkeypatch.setattr(PHALPlugin, "shutdown", lambda self: None)

    plugin.shutdown()  # must not raise

    assert plugin.running is False
