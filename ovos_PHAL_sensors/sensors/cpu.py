import dataclasses
import os

import psutil

from ovos_PHAL_sensors.sensors.base import NumericSensor, PercentageSensor


@dataclasses.dataclass
class CPUCountSensor(NumericSensor):
    unit: str = ""
    unique_id: str = "count"
    device_name: str = "cpu"
    _once: bool = True

    @property
    def value(self):
        return os.cpu_count()


@dataclasses.dataclass
class CPUUsageSensor(PercentageSensor):
    unique_id: str = "usage_percent"
    device_name: str = "cpu"

    @property
    def value(self):
        return psutil.cpu_percent(1)


@dataclasses.dataclass
class CPUTemperatureSensor(NumericSensor):
    unit: str = "°C"
    unique_id: str = "temperature"
    device_name: str = "cpu"

    @property
    def value(self):
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:  # x86
            return temps['coretemp'][0].current
        if "cpu_thermal" in temps:  # rpi
            return temps['cpu_thermal'][0].current
        return 0

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "temperature",
                "unit_of_measurement": "°C"}


@dataclasses.dataclass
class CPUFrequencySensor(NumericSensor):
    unit: str = "MHz"
    unique_id: str = "frequency"
    device_name: str = "cpu"

    @property
    def value(self):
        freq = psutil.cpu_freq()
        if freq is None or freq.current is None:
            return 0
        return freq.current


@dataclasses.dataclass
class LoadAverage1Sensor(NumericSensor):
    unit: str = "load"
    unique_id: str = "load_average_1"
    device_name: str = "cpu"

    @property
    def value(self):
        try:
            return os.getloadavg()[0]
        except OSError:
            return 0


@dataclasses.dataclass
class LoadAverage5Sensor(NumericSensor):
    unit: str = "load"
    unique_id: str = "load_average_5"
    device_name: str = "cpu"

    @property
    def value(self):
        try:
            return os.getloadavg()[1]
        except OSError:
            return 0


@dataclasses.dataclass
class LoadAverage15Sensor(NumericSensor):
    unit: str = "load"
    unique_id: str = "load_average_15"
    device_name: str = "cpu"

    @property
    def value(self):
        try:
            return os.getloadavg()[2]
        except OSError:
            return 0


if __name__ == "__main__":
    print(CPUCountSensor())
    print(CPUUsageSensor())
    print(CPUTemperatureSensor())
    print(CPUFrequencySensor())
    print(LoadAverage1Sensor())
    print(LoadAverage5Sensor())
    print(LoadAverage15Sensor())
    # cpu_count(16, number)
    # cpu_percent(1.7, %)
    # cpu_temperature(39.0, °C)
