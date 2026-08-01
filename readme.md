# PHAL Sensors

This plugin reads sensor data from an OVOS device and sends it to other systems. It supports three outputs:

- Messagebus events
- Home Assistant
- MQTT

Each sensor gets a unique identifier in the format `sensor.ovos_{name}_{sensor_id}`.

![imagem](https://github.com/OpenVoiceOS/ovos-PHAL-sensors/assets/33701864/c13e694c-1b3d-4cb1-bae6-5c851560b135)

## Install

```bash
pip install ovos-PHAL-sensors
```

Some sensors need extra packages:

- pulseaudio sensors: `pip install pulsectl`
- screen sensors: `pip install screen-brightness-control`
- bluetooth sensors: `pip install pybluez2`
- the MQTT sensor logger: `pip install ha-mqtt-discoverable`

## Config

```json
{
  "PHAL": {
    "ovos-PHAL-sensors": {
      "name": "my_phal_device",
      "time_between_checks": 15,
      "screen_sensors": true,
      "battery_sensors": true,
      "cpu_sensors": true,
      "memory_sensors": true,
      "network_sensors": true,
      "fan_sensors": true,
      "os_sensors": true,
      "apps_sensors": true,
      "pulseaudio_sensors": true,
      "bluetooth_sensors": true,
      "disable_bus": false,
      "disable_ha": false,
      "disable_filelog": true,
      "mqtt_config": {"host":  "192.168.1.8", "port": 1883},
      "ha_host": "http://192.168.1.8:8123",
      "ha_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2NGZmODYxY2M3ZDE0ZDZmODQ5..."
    }
  }
}
```

- `name`: the device name the sensors belong to
- `time_between_checks`: time to wait between sensor readings
- `disable_bus`: set to `true` to stop sending readings to the messagebus
- `disable_ha`: set to `true` to stop sending readings to Home Assistant
- `disable_filelog`: set to `true` to stop logging readings to a file
- `ha_host` (optional): the Home Assistant URL. Defaults to the host set in [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant), if configured there.
- `ha_token` (optional): the Home Assistant long-lived access token. Defaults to the token set in [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant), if configured there.
- `mqtt_config` (optional):
```
        host: str
        port: Optional[int] = 1883
        username: Optional[str] = None
        password: Optional[str] = None
        client_name: Optional[str] = None
        tls_key: Optional[str] = None
        tls_certfile: Optional[str] = None
        tls_ca_cert: Optional[str] = None

        discovery_prefix: str = "homeassistant"
        """The root of the topic tree where HA is listening for messages"""
        state_prefix: str = "hmd"
        """The root of the topic tree ha-mqtt-discovery publishes its state messages"""
```

## Sensor loggers

The plugin ships four sensor data loggers:

- HomeAssistant HTTP: sends readings to Home Assistant when `ha_host` and `ha_token` are set
- Messagebus: emits readings as bus messages
- FileLogger: saves readings to `~/.local/state/sensors/readings.log`
- MQTT: sends readings to MQTT, compatible with Home Assistant. Use this instead of the HA logger.

````python
Message("ovos.phal.sensor",
         {"state": sensor.value,
          "sensor_id": f"{name}_{unique_id}",
          "device_name": name,
          "name": unique_id,
          "attributes": sensor.attrs})

Message("ovos.phal.binary_sensor",
         {"state": sensor.value,
          "sensor_id": f"{name}_{unique_id}",
          "device_name": name,
          "name": unique_id,
          "attributes": sensor.attrs})
````

## Sensors

PulseAudio
```
PAHostnameSensor
PAVersionSensor
PAChannelCountSensor
PAPlaybackSensor
PABluezActiveSensor
PABluezConnectedSensor
PANowPlayingSensor
PADefaultSourceSensor
PADefaultSinkSensor
PAAudioPlayingSensor
```

OS Info
```
OSNameSensor
OSSystemSensor
BootTimeSensor
ReleaseSensor
MachineSensor
ArchitectureSensor
```

Running Applications
```
SystemdSensor
DBUSDaemonSensor
KDEConnectSensor
PipewireSensor
PlasmaShellSensor
PulseAudioSensor
FirefoxSensor
SpotifySensor
MiniDLNASensor
UPMPDCliSensor
```

Memory Usage
```
MemoryTotalSensor
MemoryUsageSensor
SwapUsageSensor
SwapTotalSensor
DiskUsageSensor
DiskPercentSensor
DiskTotalSensor
```

CPU Usage
```
CPUTemperatureSensor
CPUUsageSensor
CPUCountSensor
```

Network Sensors
```
LocalIPSensor
ExternalIPSensor
```

Screen Sensors
```
ScreenBrightnessSensor
```

Battery Sensors
```
BatterySensor
BatteryChargeSensor
BatteryCurrentSensor
BatteryStoredEnergySensor
BatteryPowerSensor
BatteryStatusSensor
BatteryVoltageSensor
```

Fan Sensors
```
CpuFanSensor
GpuFanSensor
```

BluetoothSensors
```
BluetoothDevicePresence
BluetoothDeviceName
BluetoothSpeakerConnected
```

## Related projects

- [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant): the Home Assistant integration this plugin can report readings to
- [OVOS-PHAL](https://github.com/OpenVoiceOS/ovos-PHAL): the platform abstraction layer this plugin runs under

## License

Apache-2.0
