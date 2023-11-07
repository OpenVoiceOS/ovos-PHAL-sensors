import dataclasses

import psutil

from ovos_PHAL_sensors.sensors.base import PercentageSensor


@dataclasses.dataclass
class CpuFanSensor(PercentageSensor):
    unique_id: str = "cpu_fan_percent"
    device_name: str = "fan"

    @property
    def value(self):
        for label, fans in psutil.sensors_fans().items():
            for f in fans:
                if f.label == "cpu_fan":
                    return f.current
        return 0


@dataclasses.dataclass
class GpuFanSensor(PercentageSensor):
    unique_id: str = "gpu_fan_percent"
    device_name: str = "fan"

    @property
    def value(self):
        for label, fans in psutil.sensors_fans().items():
            for f in fans:
                if f.label == "gpu_fan":
                    return f.current
        return 0


if __name__ == "__main__":
    print(CpuFanSensor())
    print(GpuFanSensor())
    # cpu_fan_percent(0, %)
    # gpu_fan_percent(0, %)
