from ovos_PHAL_sensors import PHALSensors
from ovos_config import Configuration


def standalone_launch():
    from ovos_bus_client import MessageBusClient
    from ovos_utils import wait_for_exit_signal
    from ovos_utils.log import LOG

    conf = Configuration().get("PHAL", {}).get("ovos-PHAL-sensors", {})
    # Connect to the real messagebus so readings actually reach the bus as
    # ovos.phal.sensor — a FakeBus here emits into the void, which makes the
    # standalone launcher useless on a real device.
    bus = MessageBusClient()
    bus.run_in_thread()
    bus.connected_event.wait()
    LOG.info("ovos-PHAL-sensors connected to the messagebus")
    sensor = PHALSensors(bus=bus, config=conf)
    try:
        wait_for_exit_signal()
    finally:
        sensor.shutdown()


if __name__ == "__main__":

    standalone_launch()
