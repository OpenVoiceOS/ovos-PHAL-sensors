from ovos_PHAL_sensors import PHALSensors
from ovos_config import Configuration


def standalone_launch():

    from ovos_utils.messagebus import FakeBus
    from ovos_utils import wait_for_exit_signal

    conf = Configuration().get("PHAL", {}).get("ovos-PHAL-sensors", {})
    sensor = PHALSensors(bus=FakeBus(), config=conf)
    wait_for_exit_signal()


if __name__ == "__main__":

    standalone_launch()
