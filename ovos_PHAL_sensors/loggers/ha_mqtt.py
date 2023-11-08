import platform

from ha_mqtt_discoverable import Settings, DeviceInfo
from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo, Sensor, SensorInfo

from ovos_PHAL_sensors.loggers.base import SensorLogger
from ovos_PHAL_sensors.sensors.base import _norm


class MQTTUpdater(SensorLogger):
    # Configure the required parameters for the MQTT broker
    mqtt_settings = None
    device_info = None

    @classmethod
    def bind_device(cls, name, mqtt_settings: Settings.MQTT):
        cls.mqtt_settings = mqtt_settings
        cls.device_info = DeviceInfo(name=name,
                                     identifiers=[_norm(name)],
                                     sw_version=platform.release(),
                                     model="ovos_PHAL_sensors",
                                     hw_version=platform.machine(),
                                     manufacturer="OpenVoiceOS")

    @classmethod
    def binary_sensor_update(cls, sensor):
        sensor_info = BinarySensorInfo(**cls._get_kwargs(sensor))

        settings = Settings(mqtt=cls.mqtt_settings, entity=sensor_info)

        # Instantiate the sensor
        s = BinarySensor(settings)
        print(s)

        # Change the state of the sensor, publishing an MQTT message that gets picked up by HA
        if sensor.value:
            s.on()
        else:
            s.off()

    @classmethod
    def sensor_update(cls, sensor):

        sensor_info = SensorInfo(**cls._get_kwargs(sensor))

        settings = Settings(mqtt=cls.mqtt_settings, entity=sensor_info)

        # Instantiate the sensor
        s = Sensor(settings)
        s.set_state(sensor.value)
        print(s, sensor.value)

    @classmethod
    def _get_kwargs(cls, sensor):
        unique_id = f"mqtt_{_norm(sensor.device_name)}_{_norm(sensor.unique_id)}"

        kwargs = dict(name=sensor.attrs.get("friendly_name", sensor.unique_id),
                      unique_id=unique_id,
                      object_id=unique_id,
                      enabled_by_default=True,
                      force_update=True,
                      icon=sensor.attrs.get("icon"),
                      unit_of_measurement=sensor.attrs.get("unit_of_measurement"),
                      device_class=sensor.attrs.get("device_class"),
                      qos=1)
        if cls.device_info:
            kwargs["device"] = cls.device_info
        return kwargs
