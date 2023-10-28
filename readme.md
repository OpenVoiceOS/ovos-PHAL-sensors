# PHAL Sensors

Expose sensor data from your OVOS device to various systems

- Messagebus events
- Home Assistant (http sensors)

sensors will have a unique identifier of the format `sensor.ovos_{name}_{sensor_id}`

![imagem](https://github.com/OpenVoiceOS/ovos-PHAL-sensors/assets/33701864/57ed6731-f6ec-4b23-8dc6-8d49fae7203f)

## Dependencies

to enable pulseaudio sensors `pip install pulsectl`

to enable screen sensors `pip install screen-brightness-control `

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
      "disable_bus": false,
      "disable_ha": false,
      "ha_host": "http://192.168.1.8:8123",
      "ha_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2NGZmODYxY2M3ZDE0ZDZmODQ5..."
    }
  }
}
```

- name - the device name the sensors belong to
- time_between_checks - time to wait between reading sensors
- disable_bus - do not emit sensors readings to bus
- disable_ha - do not emit sensor readings to HA
- ha_host (optional) - home assistant url (default to [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant) if previously configured)
- ha_token (optional) - home assistant long lived access token (default to [ovos-PHAL-plugin-homeassistant](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-homeassistant) if previously configured)

## Sensors Loggers

Currently 2 sensor data loggers are provided

- HomeAssistant - if host and token are set the sensors will show up in home assistant
- Messagebus - sensor readings are emitted as bus messages


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
ExternalIPSensor
```

Screen Sensors
```
ScreenBrightnessSensor
```

Battery Sensors
```
BatterySensor
```

Fan Sensors
```
CpuFanSensor
GpuFanSensor
```