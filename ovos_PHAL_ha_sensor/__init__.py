import json
import string
from threading import Event
from typing import Set

import requests
from ovos_plugin_manager.templates.phal import PHALPlugin
from ovos_utils.messagebus import FakeBus

from ovos_PHAL_ha_sensor.base import Device, Sensor, BooleanSensor, BusSensor
from ovos_PHAL_ha_sensor.battery import BatterySensor
from ovos_PHAL_ha_sensor.cpu import CPUCountSensor, \
    CPUTemperatureSensor, CPUUsageSensor
from ovos_PHAL_ha_sensor.fan import CpuFanSensor, GpuFanSensor
from ovos_PHAL_ha_sensor.memory import SwapTotalSensor, SwapUsageSensor, \
    DiskPercentSensor, DiskTotalSensor, DiskUsageSensor, \
    MemoryTotalSensor, MemoryUsageSensor
from ovos_PHAL_ha_sensor.network import ExternalIPSensor
from ovos_PHAL_ha_sensor.screen import ScreenBrightnessSensor
from ovos_PHAL_ha_sensor.os_system import MachineSensor, ArchitectureSensor, OSSystemSensor, \
    OSNameSensor, ReleaseSensor, BootTimeSensor
from ovos_PHAL_ha_sensor.procs import SystemdSensor, DBUSDaemonSensor, KDEConnectSensor, \
    PipewireSensor, PulseAudioSensor, PlasmaShellSensor, FirefoxSensor, SpotifySensor, \
    MiniDLNASensor, UPMPDCliSensor
from ovos_PHAL_ha_sensor.pulse import PAVersionSensor, PAHostnameSensor, PAPlaybackSensor, PAChannelCountSensor, \
    PADefaultSinkSensor, PADefaultSourceSensor, PANowPlayingSensor,\
    PABluezActiveSensor, PABluezConnectedSensor


class OVOSDevice(Device):
    ha_url = ""
    ha_token = ""
    bus = FakeBus()

    def __init__(self, name, screen=False, battery=False,
                 memory=True, cpu=True, network=True, fan=False,
                 os=True, apps=True, pa=True):
        self.name = name
        self.screen = screen
        self.battery = battery
        self.cpu = cpu
        self.memory = memory
        self.network = network
        self.fan = fan
        self.os = os
        self.apps = apps
        self.pa = pa

    @classmethod
    def bind(cls, ha_url, ha_token, bus=None):
        cls.ha_url = ha_url
        cls.ha_token = ha_token
        if bus:
            cls.bus = bus
            BusSensor.bind(bus)

    @property
    def sensors(self) -> Set[Sensor]:
        sensors = []
        if self.pa:
            sensors += [PAHostnameSensor(),  PAVersionSensor(), PAChannelCountSensor(),
                        PAPlaybackSensor(), PABluezActiveSensor(), PABluezConnectedSensor(), PANowPlayingSensor(),
                        PADefaultSourceSensor(), PADefaultSinkSensor()]
        if self.os:
            sensors += [OSNameSensor(), OSSystemSensor(),
                        BootTimeSensor(), ReleaseSensor(),
                        MachineSensor(), ArchitectureSensor()]
        if self.apps:
            sensors += [SystemdSensor(), DBUSDaemonSensor(), KDEConnectSensor(),
                        PipewireSensor(), PlasmaShellSensor(), PulseAudioSensor(),
                        FirefoxSensor(), SpotifySensor(), MiniDLNASensor(), UPMPDCliSensor()]
        if self.memory:
            sensors += [
                MemoryTotalSensor(),
                MemoryUsageSensor(),
                SwapUsageSensor(),
                SwapTotalSensor(),
                DiskUsageSensor(),
                DiskPercentSensor(),
                DiskTotalSensor()
            ]
        if self.cpu:
            sensors += [
                CPUTemperatureSensor(),
                CPUUsageSensor(),
                CPUCountSensor()
            ]
        if self.network:
            sensors += [ExternalIPSensor()]
        if self.screen:
            sensors += [ScreenBrightnessSensor()]
        if self.battery:
            sensors += [BatterySensor()]
        if self.fan:
            sensors += [CpuFanSensor(), GpuFanSensor()]
        return set(sensors)

    def ha_binary_sensor_update(self, device_id, state="on",
                                attrs=None):
        device_id = device_id.replace(" ", "_")
        name = self.name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")
        attrs = attrs or {"friendly_name": device_id,
                          "state_color": True,
                          "device_class": "presence"}
        print("updating:", device_id, f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}")

        try:
            response = requests.post(
                f"{self.ha_url}/api/states/binary_sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {self.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": state, "attributes": attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")

    def ha_sensor_update(self, device_id, state="on", attrs=None):
        attrs = attrs or {"friendly_name": device_id,
                          "state_color": True}
        device_id = device_id.replace(" ", "_")
        name = self.name.lower()
        for s in string.punctuation + string.whitespace:
            device_id = device_id.replace(s, "_")
            name = name.replace(s, "_")
        print("updating:", device_id, f"{self.ha_url}/api/states/sensor.ovos_{name}_{device_id}")
        try:
            response = requests.post(
                f"{self.ha_url}/api/states/sensor.ovos_{name}_{device_id}",
                headers={
                    "Authorization": f"Bearer {self.ha_token}",
                    "content-type": "application/json",
                },
                data=json.dumps({"state": state, "attributes": attrs}),
            )
            print(response.text)
        except:
            print("failed to push data to HA")

    def update(self):
        for sensor in self.sensors:
            try:
                if isinstance(sensor, BooleanSensor):
                    self.ha_binary_sensor_update(sensor.device_id,
                                                 state=str(sensor.value),
                                                 attrs=sensor.attrs)
                else:
                    self.ha_sensor_update(sensor.device_id,
                                          state=str(sensor.value),
                                          attrs=sensor.attrs)
            except Exception as e:
                print(e)


class HAHttpSensor(PHALPlugin):
    def __init__(self, bus, name="http_sensor", config=None):
        self.running = False
        self.sleep = 60
        super().__init__(bus, name, config or {})

    def initialize(self):
        self.ha_url = self.config.get("host")
        self.ha_token = self.config.get("token")
        self.name = self.config.get("name", "OVOSDevice")
        self.sleep = self.config.get("time_between_checks", 60)
        if not self.ha_url or not self.ha_url:
            raise ValueError("missing homeassistant credentials")
        OVOSDevice.bind(self.ha_url, self.ha_token, self.bus)
        self.device = OVOSDevice(self.name,
                                 screen=self.config.get("screen_sensors", False),
                                 battery=self.config.get("battery_sensors", False),
                                 cpu=self.config.get("cpu_sensors", True),
                                 memory=self.config.get("memory_sensors", True),
                                 network=self.config.get("network_sensors", True),
                                 os=self.config.get("os_sensors", True))

    def run(self):
        self.initialize()
        self.running = True
        while self.running:
            self.device.update()
            Event().wait(self.sleep)


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus
    from ovos_utils import wait_for_exit_signal

    config = {
        "name": "pc_do_miro",
        "host": "http://192.168.1.8:8123",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2NGZmODYxY2M3ZDE0ZDZmODQ5MTMxNDgwODAyMmRmMiIsImlhdCI6MTY5ODM3ODk3NSwiZXhwIjoyMDEzNzM4OTc1fQ.PKPbyAw5dYPxZaLexy_Ed_U3OYRJeZI4DOKPljmE3Ow"
    }
    sensor = HAHttpSensor(bus=FakeBus(), config=config)
    wait_for_exit_signal()
