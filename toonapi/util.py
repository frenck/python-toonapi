"""Collection of small utility functions for ToonAPI."""
from datetime import datetime
from typing import Any, Optional


def convert_temperature(temperature: int) -> Optional[float]:
    """Convert a temperature value from the ToonAPI to a float value."""
    if temperature is None:
        return None
    return temperature / 100.0


def convert_boolean(value: Any) -> Optional[bool]:
    """Convert a value from the ToonAPI to a boolean."""
    if value is None:
        return None
    return bool(value)


def convert_datetime(timestamp: int) -> datetime:
    """Convert a java microseconds timestamp from the ToonAPI to a datetime."""
    return datetime.utcfromtimestamp(timestamp // 1000.0).replace(
        microsecond=timestamp % 1000 * 1000
    )


def convert_kwh(value: int) -> Optional[float]:
    """Convert a Wh value from the ToonAPI to a kWH value."""
    if value is None:
        return None
    return round(float(value) / 1000.0, 2)


def convert_cm3(value: int) -> Optional[float]:
    """Convert a value from the ToonAPI to a CM3 value."""
    if value is None:
        return None
    return round(float(value) / 1000.0, 2)


def convert_negative_none(value: int) -> Optional[int]:
    """Convert an negative int value from the ToonAPI to a NoneType."""
    return None if value < 0 else value


def convert_m3(value: int) -> Optional[float]:
    """Convert a value from the ToonAPI to a M3 value."""
    if value is None:
        return None
    return round(float(value) / 1000.0, 2)


def convert_lmin(value: int) -> Optional[float]:
    """Convert a value from the ToonAPI to a L/MINUTE value."""
    if value is None:
        return None
    return round(float(value) / 60.0, 1)
