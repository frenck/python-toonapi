"""Models for the Quby ToonAPI."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from .const import (
    ACTIVE_STATE_HOLIDAY,
    BURNER_STATE_ON,
    BURNER_STATE_PREHEATING,
    BURNER_STATE_TAP_WATER,
    PROGRAM_STATE_ON,
    PROGRAM_STATE_OVERRIDE,
)
from .util import (
    convert_boolean,
    convert_cm3,
    convert_datetime,
    convert_kwh,
    convert_lmin,
    convert_m3,
    convert_negative_none,
    convert_temperature,
)


def process_data(
    data: Dict[str, Any],
    key: str,
    current_value: Any,
    conversion: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """test."""
    if key not in data:
        return current_value

    if data[key] is None:
        return current_value

    if conversion is None:
        return data[key]

    return conversion(data[key])


@dataclass
class Agreement:
    """Object holding a Toon customer utility Agreement."""

    agreement_id_checksum: Optional[str] = None
    agreement_id: Optional[str] = None
    city: Optional[str] = None
    display_common_name: Optional[str] = None
    display_hardware_version: Optional[str] = None
    display_software_version: Optional[str] = None
    heating_type: Optional[str] = None
    house_number: Optional[str] = None
    is_toon_solar: Optional[bool] = None
    is_toonly: Optional[bool] = None
    postal_code: Optional[str] = None
    street: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Agreement:
        """Return an Agreement object from a data dictionary."""
        return Agreement(
            agreement_id_checksum=data.get("agreementIdChecksum"),
            agreement_id=data.get("agreementId"),
            city=data.get("city"),
            display_common_name=data.get("displayCommonName"),
            display_hardware_version=data.get("displayHardwareVersion"),
            display_software_version=data.get("displaySoftwareVersion"),
            heating_type=data.get("heatingType"),
            house_number=data.get("houseNumber"),
            is_toon_solar=data.get("isToonSolar"),
            is_toonly=data.get("isToonly"),
            postal_code=data.get("postalCode"),
            street=data.get("street"),
        )


@dataclass
class ThermostatInfo:
    """Object holding Toon thermostat information."""

    active_state: Optional[int] = None
    boiler_module_connected: Optional[bool] = None
    burner_state: Optional[int] = None
    current_display_temperature: Optional[float] = None
    current_humidity: Optional[int] = None
    current_modulation_level: Optional[int] = None
    current_setpoint: Optional[float] = None
    error_found: Optional[bool] = None
    has_boiler_fault: Optional[bool] = None
    have_opentherm_boiler: Optional[bool] = None
    holiday_mode: Optional[bool] = None
    next_program: Optional[int] = None
    next_setpoint: Optional[float] = None
    next_state: Optional[int] = None
    next_time: Optional[datetime] = None
    opentherm_communication_error: Optional[bool] = None
    program_state: Optional[int] = None
    real_setpoint: Optional[float] = None
    set_by_load_shifthing: Optional[int] = None

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()

    @property
    def burner(self) -> Optional[bool]:
        """Return if burner is on based on its state."""
        if self.burner_state is None:
            return None
        return bool(self.burner_state)

    @property
    def hot_tapwater(self) -> Optional[bool]:
        """Return if burner is on based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_TAP_WATER

    @property
    def heating(self) -> Optional[bool]:
        """Return if burner is pre heating based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_ON

    @property
    def pre_heating(self) -> Optional[bool]:
        """Return if burner is pre heating based on its state."""
        if self.burner_state is None:
            return None
        return self.burner_state == BURNER_STATE_PREHEATING

    @property
    def program(self) -> Optional[bool]:
        """Return if program mode is turned on."""
        if self.program_state is None:
            return None
        return self.program_state in [PROGRAM_STATE_ON, PROGRAM_STATE_OVERRIDE]

    @property
    def program_overridden(self) -> Optional[bool]:
        """Return if program mode is overriden."""
        if self.program_state is None:
            return None
        return self.program_state == PROGRAM_STATE_OVERRIDE

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this ThermostatInfo object with data from a dictionary."""
        self.active_state = process_data(
            data, "activeState", self.active_state, convert_negative_none
        )
        self.boiler_module_connected = process_data(
            data, "boilerModuleConnected", self.boiler_module_connected, convert_boolean
        )
        self.burner_state = process_data(data, "burnerInfo", self.burner_state, int)
        self.current_display_temperature = process_data(
            data,
            "currentDisplayTemp",
            self.current_display_temperature,
            convert_temperature,
        )
        self.current_humidity = process_data(
            data, "currentHumidity", self.current_humidity
        )
        self.current_modulation_level = process_data(
            data, "currentModulationLevel", self.current_modulation_level
        )
        self.current_setpoint = process_data(
            data, "currentSetpoint", self.current_setpoint, convert_temperature
        )
        self.error_found = process_data(
            data, "errorFound", self.error_found, lambda x: x != 255
        )
        self.has_boiler_fault = process_data(
            data, "hasBoilerFault", self.has_boiler_fault, convert_boolean
        )
        self.have_opentherm_boiler = process_data(
            data, "haveOTBoiler", self.have_opentherm_boiler, convert_boolean
        )
        self.holiday_mode = process_data(
            data, "activeState", self.holiday_mode, lambda x: x == ACTIVE_STATE_HOLIDAY
        )
        self.next_program = process_data(
            data, "nextProgram", self.next_program, convert_negative_none
        )
        self.next_setpoint = process_data(
            data, "nextSetpoint", self.next_setpoint, convert_temperature
        )
        self.next_state = process_data(
            data, "nextState", self.next_state, convert_negative_none
        )
        self.next_time = process_data(
            data, "nextTime", self.next_state, convert_datetime
        )
        self.opentherm_communication_error = process_data(
            data, "otCommError", self.opentherm_communication_error, convert_boolean
        )
        self.program_state = process_data(data, "programState", self.program_state)
        self.real_setpoint = process_data(
            data, "realSetpoint", self.real_setpoint, convert_temperature
        )
        self.set_by_load_shifthing = process_data(
            data, "setByLoadShifting", self.set_by_load_shifthing, convert_boolean
        )

        self.last_updated_from_display = process_data(
            data,
            "lastUpdatedFromDisplay",
            self.last_updated_from_display,
            convert_datetime,
        )
        self.last_updated = datetime.utcnow()


@dataclass
class PowerUsage:
    """Object holding Toon power usage information."""

    average_produced: Optional[float] = None
    average_solar: Optional[float] = None
    average: Optional[float] = None
    current_produced: Optional[int] = None
    current_solar: Optional[int] = None
    current: Optional[int] = None
    day_average: Optional[float] = None
    day_cost: Optional[float] = None
    day_high_usage: Optional[float] = None
    day_low_usage: Optional[float] = None
    day_max_solar: Optional[int] = None
    day_produced_solar: Optional[float] = None
    is_smart: Optional[bool] = None
    meter_high: Optional[float] = None
    meter_low: Optional[float] = None
    meter_produced_high: Optional[float] = None
    meter_produced_low: Optional[float] = None

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()

    @property
    def day_usage(self) -> Optional[float]:
        """Calculate day total usage."""
        if self.day_high_usage is None or self.day_low_usage is None:
            return None
        return round(self.day_high_usage + self.day_low_usage, 2)

    @property
    def day_to_grid_usage(self) -> Optional[float]:
        """Calculate day total to grid."""
        if self.day_usage is None or self.day_produced_solar is None:
            return None
        return abs(min(0.0, round(self.day_usage - self.day_produced_solar, 2)))

    @property
    def day_from_grid_usage(self) -> Optional[float]:
        """Calculate day total to grid."""
        if self.day_produced_solar is None or self.day_usage is None:
            return None
        return abs(min(0.0, round(self.day_produced_solar - self.day_usage, 2)))

    @property
    def current_covered_by_solar(self) -> Optional[int]:
        """Calculate current solar covering current usage."""
        if self.current_solar is None or self.current is None:
            return None
        return min(100, round((self.current_solar / self.current) * 100))

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this PowerUsage object with data from a dictionary."""
        self.average = process_data(data, "avgValue", self.average)
        self.average_produced = process_data(
            data, "avgProduValue", self.average_produced
        )
        self.average_solar = process_data(data, "avgSolarValue", self.average_solar)
        self.current = process_data(data, "value", self.current, round)
        self.current_produced = process_data(
            data, "valueProduced", self.current_produced, round
        )
        self.current_solar = process_data(data, "valueSolar", self.current_solar, round)
        self.day_average = process_data(
            data, "avgDayValue", self.day_average, convert_kwh
        )
        self.day_cost = process_data(data, "dayCost", self.day_cost)
        self.day_high_usage = process_data(
            data, "dayUsage", self.day_high_usage, convert_kwh
        )
        self.day_low_usage = process_data(
            data, "dayLowUsage", self.day_low_usage, convert_kwh
        )
        self.day_max_solar = process_data(data, "maxSolar", self.day_max_solar)
        self.day_produced_solar = process_data(
            data, "solarProducedToday", self.day_produced_solar, convert_kwh
        )
        self.is_smart = process_data(data, "isSmart", self.is_smart, convert_boolean)
        self.meter_high = process_data(
            data, "meterReading", self.meter_high, convert_kwh
        )
        self.meter_low = process_data(
            data, "meterReadingLow", self.meter_low, convert_kwh
        )
        self.meter_produced_high = process_data(
            data, "meterReadingProdu", self.meter_high, convert_kwh
        )
        self.meter_produced_low = process_data(
            data, "meterReadingLowProdu", self.meter_produced_low, convert_kwh
        )

        self.last_updated_from_display = process_data(
            data,
            "lastUpdatedFromDisplay",
            self.last_updated_from_display,
            convert_datetime,
        )
        self.last_updated = datetime.utcnow()


@dataclass
class GasUsage:
    """Object holding Toon gas usage information."""

    average: Optional[float] = None
    current: Optional[float] = None
    day_average: Optional[float] = None
    day_cost: Optional[float] = None
    day_usage: Optional[float] = None
    is_smart: Optional[bool] = None
    meter: Optional[float] = None

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this GasUsage object with data from a dictionary."""
        self.average = process_data(data, "avgValue", self.average, convert_cm3)
        self.current = process_data(data, "value", self.current, convert_cm3)
        self.day_average = process_data(
            data, "avgDayValue", self.day_average, convert_cm3
        )
        self.day_cost = process_data(data, "dayCost", self.day_cost)
        self.day_usage = process_data(data, "dayUsage", self.day_usage, convert_cm3)
        self.is_smart = process_data(data, "isSmart", self.is_smart, convert_boolean)
        self.meter = process_data(data, "meterReading", self.meter, convert_cm3)

        self.last_updated_from_display = process_data(
            data,
            "lastUpdatedFromDisplay",
            self.last_updated_from_display,
            convert_datetime,
        )
        self.last_update = datetime.utcnow()


@dataclass
class WaterUsage:
    """Object holding Toon water usage information."""

    average: Optional[float] = None
    current: Optional[float] = None
    day_average: Optional[float] = None
    day_cost: Optional[float] = None
    day_usage: Optional[float] = None
    installed: Optional[bool] = None
    is_smart: Optional[bool] = None
    meter: Optional[float] = None

    last_updated_from_display: Optional[datetime] = None
    last_updated = datetime.utcnow()

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update this WaterUsage object with data from a dictionary."""
        self.average = process_data(data, "avgValue", self.average, convert_lmin)
        self.current = process_data(data, "value", self.current, convert_lmin)
        self.day_average = process_data(
            data, "avgDayValue", self.day_average, convert_m3
        )
        self.day_cost = process_data(data, "dayCost", self.day_cost)
        self.day_usage = process_data(data, "dayUsage", self.day_usage, convert_m3)
        self.installed = process_data(
            data, "installed", self.installed, convert_boolean
        )
        self.is_smart = process_data(data, "isSmart", self.is_smart, convert_boolean)
        self.meter = process_data(data, "meterReading", self.meter, convert_m3)
        self.last_updated_from_display = process_data(
            data,
            "lastUpdatedFromDisplay",
            self.last_updated_from_display,
            convert_datetime,
        )
        self.last_update = datetime.utcnow()


class Status:
    """Object holding all status information for this ToonAPI instance."""

    agreement: Agreement
    thermostat: ThermostatInfo = ThermostatInfo()
    power_usage: PowerUsage = PowerUsage()
    gas_usage: GasUsage = GasUsage()
    water_usage: WaterUsage = WaterUsage()

    last_updated_from_display: Optional[datetime] = None
    last_updated: datetime = datetime.utcnow()
    server_time: Optional[datetime] = None

    def __init__(self, agreement: Agreement):
        """Initialize an empty ToonAPI Status class."""
        self.agreement = agreement

    def update_from_dict(self, data: Dict[str, Any]) -> Status:
        """Update the status object with data received from the ToonAPI."""
        if "thermostatInfo" in data:
            self.thermostat.update_from_dict(data["thermostatInfo"])
        if "powerUsage" in data:
            self.power_usage.update_from_dict(data["powerUsage"])
        if "gasUsage" in data:
            self.gas_usage.update_from_dict(data["gasUsage"])
        if "waterUsage" in data:
            self.water_usage.update_from_dict(data["waterUsage"])
        if "lastUpdateFromDisplay" in data:
            self.last_updated_from_display = convert_datetime(
                data["lastUpdateFromDisplay"]
            )
        if "serverTime" in data:
            self.server_time = convert_datetime(data["serverTime"])
        self.last_updated = datetime.utcnow()

        return self
