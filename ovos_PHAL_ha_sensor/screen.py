from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import PercentageSensor

try:
    import screen_brightness_control as sbc
except:
    sbc = None


class ScreenBrightnessSensor(PercentageSensor):
    device_id = "brightness_percent"

    @classproperty
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
