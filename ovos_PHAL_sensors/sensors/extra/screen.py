import dataclasses

from ovos_PHAL_sensors.sensors.base import PercentageSensor

try:
    import screen_brightness_control as sbc
except:
    sbc = None


@dataclasses.dataclass
class ScreenBrightnessSensor(PercentageSensor):
    unique_id: str = "brightness_percent"
    device_name: str = "screen"

    @property
    def value(self):
        if sbc is not None:
            return sbc.get_brightness()[0]

    def set(self, value):
        if sbc is not None:
            sbc.set_brightness(value, display=0)
            return True


if __name__ == "__main__":
    print(ScreenBrightnessSensor())
    # brightness_percent(53, %)
