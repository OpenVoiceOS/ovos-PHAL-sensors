from threading import Event
from typing import List

from ovos_plugin_manager.templates.phal import PHALPlugin

from ovos_PHAL_sensors.device import BaseDevice
from ovos_PHAL_sensors.device import BaseDevice
from ovos_PHAL_sensors.loggers import MessageBusLogger, FileSensorLogger
from ovos_PHAL_sensors.loggers.ha_http import HomeAssistantUpdater
from ovos_PHAL_sensors.sensors.base import Sensor, BusSensor
from ovos_PHAL_sensors.sensors.battery import BatterySensor
from ovos_PHAL_sensors.sensors.cpu import CPUCountSensor, \
    CPUTemperatureSensor, CPUUsageSensor
from ovos_PHAL_sensors.sensors.extra.blue import BlueScanner, bluetooth
from ovos_PHAL_sensors.sensors.extra.pulse import PAVersionSensor, PAHostnameSensor, PAPlaybackSensor, \
    PAChannelCountSensor, \
    PADefaultSinkSensor, PADefaultSourceSensor, PANowPlayingSensor, \
    PABluezActiveSensor, PABluezConnectedSensor, PAAudioPlayingSensor, pulse
from ovos_PHAL_sensors.sensors.extra.screen import ScreenBrightnessSensor, sbc
from ovos_PHAL_sensors.sensors.fan import CpuFanSensor, GpuFanSensor
from ovos_PHAL_sensors.sensors.memory import SwapTotalSensor, SwapUsageSensor, \
    DiskPercentSensor, DiskTotalSensor, DiskUsageSensor, \
    MemoryTotalSensor, MemoryUsageSensor
from ovos_PHAL_sensors.sensors.network import ExternalIPSensor, LocalIPSensor
from ovos_PHAL_sensors.sensors.os_system import MachineSensor, ArchitectureSensor, OSSystemSensor, \
    OSNameSensor, ReleaseSensor, BootTimeSensor
from ovos_PHAL_sensors.sensors.procs import SystemdSensor, DBUSDaemonSensor, KDEConnectSensor, \
    PipewireSensor, PulseAudioSensor, PlasmaShellSensor, FirefoxSensor, SpotifySensor, \
    MiniDLNASensor, UPMPDCliSensor


class OVOSDevice(BaseDevice):

    def __init__(self, name, screen=True, battery=True,
                 memory=True, cpu=True, network=True, fan=True,
                 os=True, apps=True, pa=True, blue=True, wifi=True):
        if pulse is None:
            pa = False
        if bluetooth is None:
            blue = False
        if sbc is None:
            screen = False
        # TODO - if is_docker -> disable apps
        self.screen = screen
        self.battery = battery
        self.cpu = cpu
        self.memory = memory
        self.network = network
        self.fan = fan
        self.os = os
        self.apps = apps
        self.wifi = wifi
        if blue:
            self.blue = BlueScanner(daemon=True, device_name=name)
            self.blue.start()
        else:
            self.blue = None
        self.pa = pa

        super().__init__(name)

    @property
    def sensors(self) -> List[Sensor]:
        # TODO - plugins
        sensors = []
        if self.pa:
            sensors += [PAHostnameSensor(), PAVersionSensor(), PAChannelCountSensor(),
                        PAPlaybackSensor(), PABluezActiveSensor(), PABluezConnectedSensor(),
                        PANowPlayingSensor(), PAAudioPlayingSensor(),
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
            sensors += [ExternalIPSensor(), LocalIPSensor()]
        if self.screen:
            sensors += [ScreenBrightnessSensor()]
        if self.battery:
            sensors += [BatterySensor()]
        if self.fan:
            sensors += [CpuFanSensor(), GpuFanSensor()]

        if self.blue is not None:
            sensors += self.blue.sensors
        if self.wifi:
            from ovos_PHAL_sensors.sensors.extra.wifiscan import scan_wifi
            sensors += scan_wifi(self.name)
        return sensors


class PHALSensors(PHALPlugin):
    def __init__(self, bus, name="phal_sensors", config=None):
        self.running = False
        self.sleep = 5
        super().__init__(bus, name, config or {})

    def initialize(self):
        self.ha_url = self.config.get("ha_host")
        self.ha_token = self.config.get("ha_token")
        self.name = self.config.get("name", "OVOSDevice")
        self.sleep = self.config.get("time_between_checks", 5)
        OVOSDevice.bind(self.name, self.ha_url, self.ha_token, self.bus,
                        disable_bus=self.config.get("disable_bus", False),
                        disable_ha=self.config.get("disable_ha", False),
                        disable_file_logger=self.config.get("disable_filelog", True))
        self.device = OVOSDevice(self.name,
                                 screen=self.config.get("screen_sensors", True),
                                 battery=self.config.get("battery_sensors", True),
                                 cpu=self.config.get("cpu_sensors", True),
                                 memory=self.config.get("memory_sensors", True),
                                 network=self.config.get("network_sensors", True),
                                 fan=self.config.get("fan_sensors", True),
                                 os=self.config.get("os_sensors", True),
                                 apps=self.config.get("app_sensors", True),
                                 blue=self.config.get("bluetooth_sensors", True),
                                 pa=self.config.get("pulseaudio_sensors", True))

    def run(self):
        self.initialize()
        self.running = True
        while self.running:
            self.device.update()
            Event().wait(self.sleep)
