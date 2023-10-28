# PHAL Sensors

Expose sensor data from your OVOS device to various systems

- Messagebus events
- Home Assistant (http sensors)

![imagem](https://github.com/OpenVoiceOS/ovos-PHAL-sensors/assets/33701864/57ed6731-f6ec-4b23-8dc6-8d49fae7203f)

## Config

TODO - finish defining this

```json
{
  "name": "phal_device",
  "time_between_checks": 5,
  "screen_sensors": true,
  "battery_sensors": true,
  "cpu_sensors": true,
  "memory_sensors": true,
  "network_sensors": true,
  "fan_sensors": true,
  "os_sensors": true,
  "apps_sensors": true,
  "pulseaudio_sensors": true,
  "host": "",
  "token": ""
}
```

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
CPUUsageSenso
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
