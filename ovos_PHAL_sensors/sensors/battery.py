import dataclasses
import os

from ovos_PHAL_sensors.sensors.base import PercentageSensor, NumericSensor, Sensor


def get_battery_info():
    # https://www.kernel.org/doc/html/latest/power/power_supply_class.html
    path = "/sys/class/power_supply/"
    if not os.path.isdir(path):
        return
    for b in os.listdir(path):
        try:
            with open(f"{path}{b}/uevent") as f:
                data = f.read()
        except OSError:
            continue
        voltage = 0
        is_battery = False
        current = 0
        power = 0
        charge = 0
        cap = 0
        status = ""
        name = b
        for l in data.split("\n"):
            try:
                k, v = l.split("=")
            except ValueError:
                continue
            # µV, µA, µAh, µWh
            if k == "POWER_SUPPLY_TYPE" and v == "Battery":
                is_battery = True
            if k == "POWER_SUPPLY_VOLTAGE_NOW":
                voltage = int(v) / 1000000  # µV
            if k == "POWER_SUPPLY_CURRENT_NOW":
                current = int(v) / 1000000  # µA
            if k == "POWER_SUPPLY_POWER_NOW":
                power = int(v) / 1000000  # µW
            if k == "POWER_SUPPLY_CHARGE_NOW":
                charge = int(v) / 1000000  # µAh
            if k == "POWER_SUPPLY_CAPACITY":
                cap = int(v)  # %
            if k == "POWER_SUPPLY_STATUS":
                status = v
            if k == "POWER_SUPPLY_NAME":
                name = v

        if is_battery:
            power = power or voltage * current
            yield {
                "capacity": cap,
                "voltage": voltage,
                "current": current,
                "power": power,
                "charge": charge,
                "status": status,
                "name": name
            }


@dataclasses.dataclass
class BatterySensor(PercentageSensor):
    unique_id: str = "percent"
    device_name: str = "battery"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        return round(batteries[0]["capacity"], 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "battery",
                "unit_of_measurement": self.unit}


@dataclasses.dataclass
class BatteryPowerSensor(NumericSensor):
    """ negative if battery is discharging"""
    unique_id: str = "power"
    device_name: str = "battery"
    unit: str = "W"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        battery = batteries[0]
        c = round(battery["power"], 3)
        if battery["status"] == "Discharging":
            return c * -1
        return c

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "power",
                "unit_of_measurement": self.unit}


@dataclasses.dataclass
class BatteryCurrentSensor(NumericSensor):
    """ negative if battery is discharging"""
    unique_id: str = "current"
    device_name: str = "battery"
    unit: str = "A"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        battery = batteries[0]
        c = round(battery["current"], 3)
        if battery["status"] == "Discharging":
            return c * -1
        return c

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "current",
                "unit_of_measurement": self.unit}


@dataclasses.dataclass
class BatteryVoltageSensor(NumericSensor):
    unique_id: str = "voltage"
    device_name: str = "battery"
    unit: str = "V"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        return round(batteries[0]["voltage"], 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "voltage",
                "unit_of_measurement": self.unit}


@dataclasses.dataclass
class BatteryChargeSensor(NumericSensor):
    unique_id: str = "charge"
    device_name: str = "battery"
    unit: str = "Ah"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        return round(batteries[0]["charge"], 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "unit_of_measurement": self.unit}


@dataclasses.dataclass
class BatteryStatusSensor(Sensor):
    unique_id: str = "status"
    device_name: str = "battery"
    unit: str = ""

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return "unknown"
        return batteries[0]["status"]

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "battery"}


@dataclasses.dataclass
class BatteryStoredEnergySensor(NumericSensor):
    unique_id: str = "stored_energy"
    device_name: str = "battery"
    unit: str = "kWh"

    @property
    def value(self):
        batteries = list(get_battery_info())
        if not batteries:
            return 0
        battery = batteries[0]
        # charge (Ah) * voltage (V) = Wh, convert to kWh
        return round(battery["charge"] * battery["voltage"] / 1000, 3)

    @property
    def attrs(self):
        return {"friendly_name": self.__class__.__name__,
                "device_class": "energy_storage",
                "unit_of_measurement": self.unit}


if __name__ == "__main__":
    print(BatterySensor().value, "%")
    print(BatteryPowerSensor().value, "W")
    print(BatteryCurrentSensor().value, "A")
    print(BatteryVoltageSensor().value, "V")
    print(BatteryChargeSensor().value, "Ah")
    print(BatteryStoredEnergySensor().value, "kWh")
    print(BatteryStatusSensor().value)
    # battery_percent(51.12, %)
    print(list(get_battery_info()))
