"""PercentageSensor's un-overridden default must be numeric 0, not False -
Home Assistant / graphing consumers expect a number on a %-unit sensor,
and `False` would render as 0 but compare/serialize incorrectly."""
from ovos_PHAL_sensors.sensors.base import PercentageSensor


def test_percentage_sensor_default_value_is_int_zero_not_bool():
    value = PercentageSensor(unique_id="test_pct").value
    assert value == 0
    # bool is a subclass of int in Python, so isinstance(False, int) is
    # True too - explicitly rule out bool to catch a `return False` regression
    assert type(value) is int
    assert value is not False
