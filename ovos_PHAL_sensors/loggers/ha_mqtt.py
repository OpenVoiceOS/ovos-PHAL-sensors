import platform

from ovos_utils.log import LOG

from ovos_PHAL_sensors.loggers.base import SensorLogger
from ovos_PHAL_sensors.sensors.base import _norm

# ``ha_mqtt_discoverable`` (and its paho-mqtt dependency) is an OPTIONAL extra,
# pulled only by ``pip install ovos-PHAL-sensors[mqtt]``. It is imported lazily
# inside the methods below so that merely importing this module — which happens
# whenever the plugin loads — never requires it. The native OVOS bus logger is
# the always-on path and has no such dependency.


class MQTTUpdater(SensorLogger):
    # Configure the required parameters for the MQTT broker
    mqtt_settings = None
    device_info = None

    @classmethod
    def bind_device(cls, name, mqtt_settings):
        from ha_mqtt_discoverable import DeviceInfo

        cls.mqtt_settings = mqtt_settings
        cls.device_info = DeviceInfo(name=name,
                                     identifiers=[_norm(name)],
                                     sw_version=platform.release(),
                                     model="ovos_PHAL_sensors",
                                     hw_version=platform.machine(),
                                     manufacturer="OpenVoiceOS")

    @classmethod
    def binary_sensor_update(cls, sensor):
        from ha_mqtt_discoverable import Settings
        from ha_mqtt_discoverable.sensors import BinarySensor, BinarySensorInfo

        sensor_info = BinarySensorInfo(**cls._get_kwargs(sensor))
        settings = Settings(mqtt=cls.mqtt_settings, entity=sensor_info)
        s = BinarySensor(settings)
        # Publish an MQTT message HA picks up via discovery.
        if sensor.value:
            s.on()
        else:
            s.off()

    @classmethod
    def sensor_update(cls, sensor):
        from ha_mqtt_discoverable import Settings
        from ha_mqtt_discoverable.sensors import Sensor, SensorInfo

        sensor_info = SensorInfo(**cls._get_kwargs(sensor))
        settings = Settings(mqtt=cls.mqtt_settings, entity=sensor_info)
        s = Sensor(settings)
        s.set_state(sensor.value)

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
