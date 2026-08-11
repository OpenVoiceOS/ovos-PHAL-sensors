import abc
import logging
import os

from ovos_bus_client.message import Message
from ovos_utils.fakebus import FakeBus

from ovos_PHAL_sensors.sensors.base import _norm


class SensorLogger:
    @classmethod
    @abc.abstractmethod
    def sensor_update(cls, sensor):
        pass

    @classmethod
    @abc.abstractmethod
    def binary_sensor_update(cls, sensor):
        pass


class FileSensorLogger(SensorLogger):
    path = os.path.expanduser("~/.local/state/sensors")
    logger = None

    @classmethod
    def init(cls):
        if cls.logger is not None:
            return
        os.makedirs(cls.path, exist_ok=True)
        logger = logging.getLogger('ovos_phal_sensors.readings')
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        handler = logging.FileHandler(f"{cls.path}/readings.log")
        handler.setFormatter(logging.Formatter('%(asctime)s,%(msecs)d %(message)s',
                                               datefmt='%H:%M:%S'))
        logger.addHandler(handler)
        cls.logger = logger

    @classmethod
    def sensor_update(cls, sensor):
        cls.init()
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)
        cls.logger.info(f"{name}_{unique_id} {sensor.value}")

    @classmethod
    def binary_sensor_update(cls, sensor):
        return cls.sensor_update(sensor)


class MessageBusLogger(SensorLogger):
    bus = FakeBus()

    @classmethod
    def sensor_update(cls, sensor):
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{unique_id}",
                              "device_name": name,
                              "name": unique_id,
                              "attributes": sensor.attrs}))

    @classmethod
    def binary_sensor_update(cls, sensor):
        unique_id = _norm(sensor.unique_id)
        name = _norm(sensor.device_name)

        cls.bus.emit(Message("ovos.phal.binary_sensor",
                             {"state": sensor.value,
                              "sensor_id": f"{name}_{unique_id}",
                              "device_name": name,
                              "name": unique_id,
                              "attributes": sensor.attrs}))
