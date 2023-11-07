import abc
import logging
import os

from ovos_utils.messagebus import FakeBus, Message

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
    os.makedirs(path, exist_ok=True)
    logging.getLogger("urllib3.connectionpool").setLevel("ERROR")
    logging.basicConfig(filename=f"{path}/readings.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger = logging.getLogger('sensor_reading')

    @classmethod
    def sensor_update(cls, sensor):
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
