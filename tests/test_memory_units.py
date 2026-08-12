"""Sensors report MB, not raw bytes - this was a real unit bug."""
import shutil

import psutil

from ovos_PHAL_sensors.sensors.memory import MemoryTotalSensor, DiskTotalSensor


def test_memory_total_sensor_reports_mb_not_bytes(monkeypatch):
    eight_gib_bytes = 8 * 1024 ** 3

    class _FakeVM:
        def __getitem__(self, idx):
            assert idx == 0
            return eight_gib_bytes

    monkeypatch.setattr(psutil, "virtual_memory", lambda: _FakeVM())

    expected_mb = round(eight_gib_bytes / 1024 ** 2, 3)
    assert expected_mb == 8 * 1024  # sanity check on the math itself
    assert MemoryTotalSensor().value == expected_mb


def test_disk_total_sensor_reports_mb_not_bytes(monkeypatch):
    hundred_gib_bytes = 100 * 1024 ** 3

    monkeypatch.setattr(
        shutil, "disk_usage",
        lambda path: (hundred_gib_bytes, 0, 0),
    )

    expected_mb = round(hundred_gib_bytes / 1024 ** 2, 3)
    assert expected_mb == 100 * 1024
    assert DiskTotalSensor().value == expected_mb
