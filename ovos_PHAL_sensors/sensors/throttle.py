import dataclasses
import shutil
import subprocess

from ovos_utils.log import LOG

from ovos_PHAL_sensors.sensors.base import Sensor, BooleanSensor

has_vcgencmd = shutil.which("vcgencmd") is not None

UNDER_VOLTAGE_NOW = 1 << 0
FREQ_CAPPED_NOW = 1 << 1
THROTTLED_NOW = 1 << 2
SOFT_TEMP_LIMIT_NOW = 1 << 3
UNDER_VOLTAGE_OCCURRED = 1 << 16
FREQ_CAPPED_OCCURRED = 1 << 17
THROTTLED_OCCURRED = 1 << 18
SOFT_TEMP_LIMIT_OCCURRED = 1 << 19


def get_throttled():
    """Run `vcgencmd get_throttled` and return the parsed bitmask,
    or None if vcgencmd is unavailable or fails."""
    if not has_vcgencmd:
        return None
    try:
        out = subprocess.check_output(["vcgencmd", "get_throttled"],
                                      timeout=5).decode("utf-8").strip()
        # format: throttled=0x50005
        value = out.split("=")[-1]
        return int(value, 16)
    except Exception as e:
        LOG.debug(f"failed to read vcgencmd get_throttled: {e}")
        return None


@dataclasses.dataclass
class ThrottleStateSensor(Sensor):
    unique_id: str = "throttle_state"
    device_name: str = "cpu"

    @property
    def value(self):
        throttled = get_throttled()
        if throttled is None:
            return "n/a"
        if throttled & UNDER_VOLTAGE_NOW:
            return "under-voltage"
        if throttled & THROTTLED_NOW:
            return "throttled"
        if throttled & FREQ_CAPPED_NOW:
            return "freq-capped"
        if throttled & SOFT_TEMP_LIMIT_NOW:
            return "soft-temp-limit"
        if throttled & (UNDER_VOLTAGE_OCCURRED | FREQ_CAPPED_OCCURRED |
                        THROTTLED_OCCURRED | SOFT_TEMP_LIMIT_OCCURRED):
            return "under-voltage (occurred)"
        return "ok"

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "icon": "mdi:thermometer-alert"}


@dataclasses.dataclass
class UnderVoltageSensor(BooleanSensor):
    unique_id: str = "under_voltage"
    device_name: str = "cpu"

    @property
    def value(self):
        throttled = get_throttled()
        if throttled is None:
            return False
        return bool(throttled & UNDER_VOLTAGE_OCCURRED)


@dataclasses.dataclass
class ThrottledSensor(BooleanSensor):
    unique_id: str = "throttled"
    device_name: str = "cpu"

    @property
    def value(self):
        throttled = get_throttled()
        if throttled is None:
            return False
        return bool(throttled & THROTTLED_OCCURRED)


if __name__ == "__main__":
    print(ThrottleStateSensor())
    print(UnderVoltageSensor())
    print(ThrottledSensor())
