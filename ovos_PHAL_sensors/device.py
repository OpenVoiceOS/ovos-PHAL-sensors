import abc
import concurrent.futures
import time
from typing import List

from ovos_config import Configuration

from ovos_PHAL_sensors.loggers import MessageBusLogger, FileSensorLogger
from ovos_PHAL_sensors.loggers.ha_http import HomeAssistantUpdater
from ovos_PHAL_sensors.sensors.base import Sensor, BusSensor


class BaseDevice:
    """ A device is a collection of sensors
    a prefix gets added to the sensors unique_id for this device """

    def __init__(self, name, prefix=True):
        self.name = name
        self._readings = {}
        self._ts = {}
        self._workers = 6
        self.prefix = prefix

    @classmethod
    def bind(cls, name, ha_url, ha_token, bus=None,
             disable_bus=False, disable_ha=False, disable_file_logger=True):
        Sensor.device_name = name

        # setup home assistant
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
            if not disable_ha:
                Sensor.bind_logger(HomeAssistantUpdater)
        if not disable_file_logger:
            Sensor.bind_logger(FileSensorLogger)

        # connect messagebus
        if bus:
            cls.bus = bus
            BusSensor.bind(bus)
            MessageBusLogger.bus = bus
            if not disable_bus:
                Sensor.bind_logger(MessageBusLogger)

    @property
    @abc.abstractmethod
    def sensors(self) -> List[Sensor]:
        return []

    def _parallel_readings(self, do_reading):
        results = {}

        # do the work in parallel instead of sequentially
        with concurrent.futures.ThreadPoolExecutor(max_workers=self._workers) as executor:

            matchers = {}
            # create a unique wrapper for each worker with their arguments
            for sensor in self.sensors:
                if self.prefix and sensor._allow_prefix:
                    sensor.device_name = f"{self.name}_{sensor.device_name}"

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
