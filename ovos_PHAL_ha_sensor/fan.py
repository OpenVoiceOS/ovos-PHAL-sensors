import psutil
from ovos_utils import classproperty

from ovos_PHAL_ha_sensor.base import PercentageSensor


class CpuFanSensor(PercentageSensor):
    device_id = "cpu_fan_percent"

    @classproperty
    def value(self):
        for label, fans in psutil.sensors_fans().items():
            for f in fans:
                if f.label == "cpu_fan":
                    return f.current
        return psutil.sensors_fans()


class GpuFanSensor(PercentageSensor):
    device_id = "gpu_fan_percent"

    @classproperty
    def value(self):
        for label, fans in psutil.sensors_fans().items():
            for f in fans:
                if f.label == "gpu_fan":
                    return f.current
        return psutil.sensors_fans()


if __name__ == "__main__":
    print(CpuFanSensor())
    print(GpuFanSensor())
    # cpu_fan_percent(0, %)
    # gpu_fan_percent(0, %)
