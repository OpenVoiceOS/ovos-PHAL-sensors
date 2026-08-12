"""Import smoke tests.

These would have caught the "archival" bug: the plugin must import with
zero optional dependencies installed (ha_mqtt_discoverable, pybluez2,
pulsectl, screen-brightness-control) and must NOT touch the filesystem
just by being imported.
"""
import shutil
import subprocess
import sys
from pathlib import Path

STATE_DIR = Path.home() / ".local" / "state" / "sensors"


def test_import_does_not_require_optional_deps():
    """ha_mqtt_discoverable is not installed in this venv; importing the
    top-level package must still succeed (it is only imported lazily,
    inside BaseDevice.bind, when mqtt is actually enabled)."""
    import pytest
    try:
        import ha_mqtt_discoverable  # noqa: F401
    except ModuleNotFoundError:
        pass  # expected - proves the dep is genuinely absent
    else:
        pytest.fail(
            "ha_mqtt_discoverable is installed in this venv; the "
            "no-optional-deps import guarantee cannot be exercised here. "
            "Run this test in a clean venv without the 'mqtt' extra."
        )

    import ovos_PHAL_sensors  # noqa: F401
    import ovos_PHAL_sensors.device  # noqa: F401
    import ovos_PHAL_sensors.loggers  # noqa: F401
    import ovos_PHAL_sensors.sensors.battery  # noqa: F401


def test_import_does_not_create_state_dir(tmp_path, monkeypatch):
    """Merely importing the package (and its loggers) must not create
    ~/.local/state/sensors - that directory is only created lazily by
    FileSensorLogger.init(), which only runs when a sensor reading is
    actually logged to file."""
    if STATE_DIR.exists():
        shutil.rmtree(STATE_DIR)
    assert not STATE_DIR.exists()

    # Import fresh in a subprocess so we don't rely on prior imports in
    # this test process (which could have already created the dir via
    # an earlier, unrelated test) and so we get a clean, real-world
    # "cold start" import.
    code = (
        "import ovos_PHAL_sensors\n"
        "import ovos_PHAL_sensors.loggers\n"
        "import ovos_PHAL_sensors.loggers.base\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr

    assert not STATE_DIR.exists(), (
        "importing ovos_PHAL_sensors must not create "
        f"{STATE_DIR} as a side effect of import"
    )
