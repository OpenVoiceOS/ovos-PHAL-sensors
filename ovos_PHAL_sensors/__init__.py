from threading import Event
from typing import List

from ovos_plugin_manager.templates.phal import PHALPlugin

from ovos_PHAL_sensors.device import BaseDevice
from ovos_PHAL_sensors.loggers import MessageBusLogger, FileSensorLogger
from ovos_PHAL_sensors.loggers.ha_http import HomeAssistantUpdater
from ovos_PHAL_sensors.sensors.base import Sensor, BusSensor
from ovos_PHAL_sensors.sensors.battery import BatterySensor, BatteryPowerSensor, BatteryStatusSensor, \
    BatteryChargeSensor, BatteryCurrentSensor, BatteryVoltageSensor, BatteryStoredEnergySensor
from ovos_PHAL_sensors.sensors.cpu import CPUCountSensor, \
    CPUTemperatureSensor, CPUUsageSensor, CPUFrequencySensor, \
    LoadAverage1Sensor, LoadAverage5Sensor, LoadAverage15Sensor
from ovos_PHAL_sensors.sensors import throttle
from ovos_PHAL_sensors.sensors.throttle import ThrottleStateSensor, \
    UnderVoltageSensor, ThrottledSensor
from ovos_PHAL_sensors.sensors.extra.blue import BlueScanner, bluetooth
from ovos_PHAL_sensors.sensors.extra.pulse import PAVersionSensor, PAHostnameSensor, PAPlaybackSensor, \
    PAChannelCountSensor, \
    PADefaultSinkSensor, PADefaultSourceSensor, PANowPlayingSensor, \
    PABluezActiveSensor, PABluezConnectedSensor, PAAudioPlayingSensor, pulse
from ovos_PHAL_sensors.sensors.extra.screen import ScreenBrightnessSensor, sbc
from ovos_PHAL_sensors.sensors.fan import CpuFanSensor, GpuFanSensor
from ovos_PHAL_sensors.sensors.memory import SwapTotalSensor, SwapUsageSensor, \
    DiskPercentSensor, DiskTotalSensor, DiskUsageSensor, \
    MemoryTotalSensor, MemoryUsageSensor, DiskReadBytesSensor, DiskWriteBytesSensor
from ovos_PHAL_sensors.sensors.network import ExternalIPSensor, LocalIPSensor, \
    NetworkBytesSentSensor, NetworkBytesRecvSensor, WifiSignalSensor
from ovos_PHAL_sensors.sensors.os_system import MachineSensor, ArchitectureSensor, OSSystemSensor, \
    OSNameSensor, ReleaseSensor, BootTimeSensor, UptimeSensor, ProcessCountSensor
from ovos_PHAL_sensors.sensors.procs import SystemdSensor, DBUSDaemonSensor, KDEConnectSensor, \
    PipewireSensor, PulseAudioSensor, PlasmaShellSensor, FirefoxSensor, SpotifySensor, \
    MiniDLNASensor, UPMPDCliSensor


class OVOSDevice(BaseDevice):

    def __init__(self, name, screen=True, battery=True,
                 memory=True, cpu=True, network=True, fan=True,
                 os=True, apps=True, pa=True, blue=True, wifi=False,
                 rpi=True):
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
        self.rpi = rpi
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
                        MachineSensor(), ArchitectureSensor(),
                        UptimeSensor(), ProcessCountSensor()]
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
                DiskTotalSensor(),
                DiskReadBytesSensor(),
                DiskWriteBytesSensor()
            ]
        if self.cpu:
            sensors += [
                CPUTemperatureSensor(),
                CPUUsageSensor(),
                CPUCountSensor(),
                CPUFrequencySensor(),
                LoadAverage1Sensor(),
                LoadAverage5Sensor(),
                LoadAverage15Sensor()
            ]
        if self.rpi and throttle.has_vcgencmd:
            sensors += [
                ThrottleStateSensor(),
                UnderVoltageSensor(),
                ThrottledSensor()
            ]
        if self.network:
            sensors += [ExternalIPSensor(), LocalIPSensor(),
                        NetworkBytesSentSensor(), NetworkBytesRecvSensor(),
                        WifiSignalSensor()]
        if self.screen:
            sensors += [ScreenBrightnessSensor()]
        if self.battery:
            sensors += [BatterySensor(), BatteryChargeSensor(), BatteryCurrentSensor(),
                        BatteryStoredEnergySensor(),
                        BatteryPowerSensor(), BatteryStatusSensor(), BatteryVoltageSensor()]
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
                        disable_ha=self.config.get("disable_ha", True),
                        disable_mqtt=self.config.get("disable_mqtt", False),
                        disable_file_logger=self.config.get("disable_filelog", True),
                        mqtt_config=self.config.get("mqtt_config") or {})
        self.device = OVOSDevice(self.name,
                                 screen=self.config.get("screen_sensors", True),
                                 battery=self.config.get("battery_sensors", True),
                                 cpu=self.config.get("cpu_sensors", True),
                                 memory=self.config.get("memory_sensors", True),
                                 network=self.config.get("network_sensors", True),
                                 wifi=self.config.get("wifi_sensors", False),
                                 fan=self.config.get("fan_sensors", True),
                                 os=self.config.get("os_sensors", True),
                                 apps=self.config.get("app_sensors", True),
                                 blue=self.config.get("bluetooth_sensors", True),
                                 pa=self.config.get("pulseaudio_sensors", True),
                                 rpi=self.config.get("rpi_sensors", True))

    def run(self):
        self.initialize()
        self.running = True
        while self.running:
            self.device.update()
            Event().wait(self.sleep)

    def shutdown(self):
        self.running = False
        device = getattr(self, "device", None)
        if device is not None and device.blue is not None:
            device.blue.stop()
        super().shutdown()
