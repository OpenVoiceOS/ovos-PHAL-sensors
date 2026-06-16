# AGENTS.md — ovos-PHAL-sensors

PHAL plugin that reads host-device sensors (CPU, memory, battery, network, fan, OS, running apps, PulseAudio, screen brightness, Bluetooth) and publishes them to Home Assistant (HTTP or MQTT discovery), the OVOS messagebus, and/or a local file log.

## Setup
```
pip install .
```
Optional sensor backends are not installed by default:
- `pip install pulsectl` — PulseAudio sensors
- `pip install screen-brightness-control` — screen brightness sensor
- `pip install pybluez2` — Bluetooth sensors
- `pip install ha-mqtt-discoverable` — MQTT logger

Core deps: `ovos-plugin-manager~=2.1`, `psutil`, `requests`, `anyascii`. Each optional backend is probed at import; if missing, that sensor group self-disables.

## Test
No test suite exists. There is no `test`/`tests` directory and no test runner configured. `build_tests.yml` only builds the wheel and `pip install .` — it does not run tests.

## Lint/Typecheck
None configured.

## Layout
- `ovos_PHAL_sensors/__init__.py` — `PHALSensors` (the `PHALPlugin` entry point) and `OVOSDevice` (builds the sensor list from config flags).
- `ovos_PHAL_sensors/device.py` — `BaseDevice`: `bind()` wires up loggers; `update()` reads sensors in a thread pool, honouring `_thread_safe`, `_once`, `_slow` flags.
- `ovos_PHAL_sensors/sensors/` — sensor implementations: `cpu.py`, `memory.py`, `battery.py`, `fan.py`, `network.py`, `os_system.py`, `procs.py` (running apps), `base.py` (`Sensor`/`BusSensor`).
- `ovos_PHAL_sensors/sensors/extra/` — optional backends: `pulse.py`, `screen.py`, `blue.py` (Bluetooth scanner thread), `wifiscan.py`.
- `ovos_PHAL_sensors/loggers/` — `MessageBusLogger`, `FileSensorLogger`, `ha_http.HomeAssistantUpdater`, `ha_mqtt.MQTTUpdater`.
- `ovos_PHAL_sensors/__main__.py` — `standalone_launch()` console-script entry (`ovos-sensors`) using a `FakeBus`.

Entry-point group: `ovos.plugin.phal` → `ovos-PHAL-sensors=ovos_PHAL_sensors:PHALSensors`. Also a `console_scripts` entry `ovos-sensors`.

Sensors get IDs of the form `sensor.ovos_{name}_{sensor_id}`. Config lives under `PHAL` → `ovos-PHAL-sensors` in OVOS config; HA host/token fall back to `ovos-PHAL-plugin-homeassistant` config if unset.

## Conventions (Org hard rules)
- Branches: `dev` (work) / `master` (stable). NEVER `main`.
- Never edit `version.py` — gh-automations bumps semver from conventional-commit prefixes (`feat:`/`fix:`/`feat!:`).
- New repos private by default.
- Commit identity: JarbasAi <jarbasai@mailfence.com>.
- Reference `OpenVoiceOS/gh-automations` reusable workflows at `@dev`.
- No Neon / `neon-*` references.
- No meta-commentary (no history, no dates) in docs/commits/PRs/code.
- CI is provided by `OpenVoiceOS/gh-automations`.

## Gotchas
- The current `.github/workflows/` are legacy inline workflows (`actions/checkout@v2`, `setup.py sdist/bdist_wheel`, `publish_*.yml`, `dev2master.yml`) — NOT the gh-automations reusable workflows. Migrating to gh-automations is the main CI gap.
- `ovos_PHAL_sensors.egg-info/` is committed and should not be.
- `disable_ha` and `disable_filelog` default to `True` in `bind()`; loggers must be explicitly enabled.
- `OVOSDevice.__init__` reads the bluetooth flag as `blue=` but `PHALSensors.initialize` passes `apps=config["app_sensors"]` while the README documents `apps_sensors` — note the singular/plural key mismatch when editing config handling.
- Bluetooth runs a background `BlueScanner` daemon thread started in `OVOSDevice.__init__`.
- WiFi scan needs root (`wifiscan.py`), so `wifi` defaults off.
- Optional backends (`pulse`, `sbc`, `bluetooth`) are `None` when their package is absent, which silently disables those sensors.
