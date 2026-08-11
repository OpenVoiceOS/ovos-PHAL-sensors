"""FileSensorLogger must be lazy: importing it (or the whole package) must
not touch the filesystem or attach a logging handler. Only an explicit
.init() (or the first sensor_update) may do that - and its logger must not
propagate to the root logger, or it would hijack every other log line."""
import dataclasses
import logging
import shutil

import pytest

from ovos_PHAL_sensors.loggers.base import FileSensorLogger
from ovos_PHAL_sensors.sensors.base import Sensor


@dataclasses.dataclass
class _FakeSensor(Sensor):
    unique_id: str = "s1"
    device_name: str = "dev"

    @property
    def value(self):
        return 1


def _our_file_handlers(logger):
    """Filter out handlers other tools (e.g. pytest's own log capturing)
    may have attached to this named logger, so assertions only look at
    handlers FileSensorLogger itself is responsible for."""
    return [h for h in logger.handlers if isinstance(h, logging.FileHandler)]


@pytest.fixture(autouse=True)
def _reset_file_logger(tmp_path, monkeypatch):
    # isolate from the real ~/.local/state/sensors and from any state
    # a previous test left on the FileSensorLogger class
    monkeypatch.setattr(FileSensorLogger, "path", str(tmp_path / "sensors"))
    monkeypatch.setattr(FileSensorLogger, "logger", None)

    logger = logging.getLogger("ovos_phal_sensors.readings")
    for h in _our_file_handlers(logger):
        logger.removeHandler(h)

    yield

    for h in _our_file_handlers(logger):
        logger.removeHandler(h)


def test_import_alone_does_not_create_dir_or_logger(tmp_path):
    import ovos_PHAL_sensors.loggers.base  # noqa: F401 - re-import is a no-op

    assert not (tmp_path / "sensors").exists()
    assert FileSensorLogger.logger is None


def test_init_creates_dir_and_attaches_handler(tmp_path):
    FileSensorLogger.init()

    assert (tmp_path / "sensors").is_dir()
    assert FileSensorLogger.logger is not None
    assert len(_our_file_handlers(FileSensorLogger.logger)) == 1


def test_logger_does_not_propagate_to_root():
    FileSensorLogger.init()
    assert FileSensorLogger.logger.propagate is False


def test_first_sensor_update_lazily_initializes(tmp_path):
    assert FileSensorLogger.logger is None
    FileSensorLogger.sensor_update(_FakeSensor())
    assert (tmp_path / "sensors").is_dir()
    assert FileSensorLogger.logger is not None
