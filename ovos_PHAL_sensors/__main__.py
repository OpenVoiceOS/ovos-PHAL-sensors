from ovos_PHAL_sensors import PHALSensors
from ovos_config import Configuration


def _standalone_bus(conf):
    """Return a bus for the standalone daemon.

    Two supported modes, chosen automatically:

    - **With OVOS**: connect to the real messagebus so readings also reach the
      bus as ``ovos.phal.sensor`` (on top of any HA/MQTT logger).
    - **Without OVOS**: if no messagebus is reachable — or the operator sets
      ``standalone``/``disable_bus`` in config — fall back to a FakeBus so the
      daemon still runs and pushes to MQTT / Home Assistant with no OVOS
      install at all.
    """
    from ovos_utils.fakebus import FakeBus
    from ovos_utils.log import LOG

    if conf.get("standalone") or conf.get("disable_bus"):
        LOG.info("ovos-PHAL-sensors: standalone mode, no OVOS bus (HA/MQTT only)")
        return FakeBus()
    try:
        from ovos_bus_client import MessageBusClient
        bus = MessageBusClient()
        bus.run_in_thread()
        if bus.connected_event.wait(5):
            LOG.info("ovos-PHAL-sensors connected to the OVOS messagebus")
            return bus
        LOG.warning("ovos-PHAL-sensors: no OVOS messagebus reachable; "
                    "running standalone (HA/MQTT only)")
        try:
            bus.close()  # stop the background reconnect thread before falling back
        except Exception:  # noqa: BLE001
            pass
    except Exception as err:  # noqa: BLE001 - no OVOS installed / bus unreachable
        LOG.warning(f"ovos-PHAL-sensors: could not reach the OVOS messagebus "
                    f"({err}); running standalone (HA/MQTT only)")
    return FakeBus()


def standalone_launch():
    from ovos_utils import wait_for_exit_signal

    conf = Configuration().get("PHAL", {}).get("ovos-PHAL-sensors", {})
    sensor = PHALSensors(bus=_standalone_bus(conf), config=conf)
    try:
        wait_for_exit_signal()
    finally:
        sensor.shutdown()


if __name__ == "__main__":

    standalone_launch()
