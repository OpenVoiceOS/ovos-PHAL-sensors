import concurrent.futures
import time
from threading import Event
from typing import List

from ovos_config import Configuration
from ovos_plugin_manager.templates.phal import PHALPlugin

from ovos_PHAL_sensors.base import Sensor, BooleanSensor, BusSensor
from ovos_PHAL_sensors.battery import BatterySensor
from ovos_PHAL_sensors.cpu import CPUCountSensor, \
    CPUTemperatureSensor, CPUUsageSensor
from ovos_PHAL_sensors.fan import CpuFanSensor, GpuFanSensor
from ovos_PHAL_sensors.inventory import Inventory
from ovos_PHAL_sensors.loggers import HomeAssistantUpdater, MessageBusLogger
from ovos_PHAL_sensors.memory import SwapTotalSensor, SwapUsageSensor, \
    DiskPercentSensor, DiskTotalSensor, DiskUsageSensor, \
    MemoryTotalSensor, MemoryUsageSensor
from ovos_PHAL_sensors.network import ExternalIPSensor
from ovos_PHAL_sensors.os_system import MachineSensor, ArchitectureSensor, OSSystemSensor, \
    OSNameSensor, ReleaseSensor, BootTimeSensor
from ovos_PHAL_sensors.prices import HipermercadosPortugal
from ovos_PHAL_sensors.procs import SystemdSensor, DBUSDaemonSensor, KDEConnectSensor, \
    PipewireSensor, PulseAudioSensor, PlasmaShellSensor, FirefoxSensor, SpotifySensor, \
    MiniDLNASensor, UPMPDCliSensor
from ovos_PHAL_sensors.pulse import PAVersionSensor, PAHostnameSensor, PAPlaybackSensor, PAChannelCountSensor, \
    PADefaultSinkSensor, PADefaultSourceSensor, PANowPlayingSensor, \
    PABluezActiveSensor, PABluezConnectedSensor
from ovos_PHAL_sensors.screen import ScreenBrightnessSensor


class OVOSDevice:

    def __init__(self, name, screen=True, battery=True,
                 memory=True, cpu=True, network=True, fan=True,
                 os=True, apps=True, pa=True, hipermercados=False,
                 inventory=False):
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
        self.hiper = hipermercados
        self.inventory = inventory

        self._readings = {}
        self._ts = {}
        self._workers = 6

    @classmethod
    def bind(cls, name, ha_url, ha_token, bus=None):
        Sensor.device_name = name
        if not ha_token or not ha_url:  # check HA plugin config
            cfg = Configuration().get("PHAL", {}).get(
                "ovos-PHAL-plugin-homeassistant", {})
            if "api_key" in cfg and not ha_token:
                ha_token = cfg["api_key"]
            if "host" in cfg and not ha_url:
                ha_url = cfg["host"]

        if ha_url and ha_token:
            HomeAssistantUpdater.ha_url = ha_url
            HomeAssistantUpdater.ha_token = ha_token
            Sensor.bind_logger(HomeAssistantUpdater)
        if bus:
            cls.bus = bus
            BusSensor.bind(bus)
            MessageBusLogger.bus = bus
            Sensor.bind_logger(MessageBusLogger)

    @property
    def sensors(self) -> List[Sensor]:
        sensors = []
        if self.pa:
            sensors += [PAHostnameSensor(), PAVersionSensor(), PAChannelCountSensor(),
                        PAPlaybackSensor(), PABluezActiveSensor(), PABluezConnectedSensor(),
                        PANowPlayingSensor(),
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

        for s in sensors:
            s.device_name = f"{self.name}_{s.device_name}"

        if self.hiper:
            sensors += HipermercadosPortugal().sensors
        if self.inventory:
            sensors += Inventory().sensors
        return sensors

    def _parallel_readings(self, do_reading):
        results = {}

        # do the work in parallel instead of sequentially
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._workers) as executor:

            matchers = {}
            # create a unique wrapper for each worker with their arguments
            for sensor in self.sensors:
                if sensor._thread_safe:
                    def do_thing(u=sensor):
                        return do_reading(u)

                    matchers[sensor.unique_id] = do_thing

            # Start the operations and mark each future with its source
            future_to_source = {
                executor.submit(func): device_id
                for device_id, func in matchers.items()
            }

            # retrieve results as they come
            for future in concurrent.futures.as_completed(future_to_source):
                future.result()

        # do sequential read for non thread safe sensors
        for sensor in self.sensors:
            if not sensor._thread_safe:
                do_reading(sensor)
        return results

    def update(self):

        def get_reading(sensor):
            if sensor.unique_id not in self._readings:
                self._readings[sensor.unique_id] = sensor.value
                self._ts[sensor.unique_id] = time.time()
                old = None
            else:
                if sensor._once:
                    # print("skipping", sensor.unique_id)
                    return  # doesnt change
                if sensor._slow and time.time() - self._ts[sensor.unique_id] < 15 * 60:
                    # print("skipping", sensor.unique_id)
                    return  # track timestamp and do once/hour
                old = self._readings[sensor.unique_id]

            if old is None or old != sensor.value:
                try:
                    sensor.sensor_update()
                    self._ts[sensor.unique_id] = time.time()
                except Exception as e:
                    print(e)

        self._parallel_readings(get_reading)


class PHALSensors(PHALPlugin):
    def __init__(self, bus, name="phal_sensors", config=None):
        self.running = False
        self.sleep = 5
        super().__init__(bus, name, config or {})

    def initialize(self):
        self.ha_url = self.config.get("host")
        self.ha_token = self.config.get("token")
        self.name = self.config.get("name", "OVOSDevice")
        self.sleep = self.config.get("time_between_checks", 5)
        OVOSDevice.bind(self.name, self.ha_url, self.ha_token, self.bus)
        self.device = OVOSDevice(self.name,
                                 screen=self.config.get("screen_sensors", True),
                                 battery=self.config.get("battery_sensors", True),
                                 cpu=self.config.get("cpu_sensors", True),
                                 memory=self.config.get("memory_sensors", True),
                                 network=self.config.get("network_sensors", True),
                                 fan=self.config.get("fan_sensors", True),
                                 os=self.config.get("os_sensors", True),
                                 apps=self.config.get("app_sensors", True),
                                 pa=self.config.get("pulseaudio_sensors", True),
                                 inventory=self.config.get("inventory", False),
                                 hipermercados=self.config.get("hipermercados", False))

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
    sensor = PHALSensors(bus=FakeBus(), config=config)
    wait_for_exit_signal()
