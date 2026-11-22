"""Sensor 'CREG-tarief'."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SOURCE_URL, TIMEZONE
from .coordinator import CregCoordinator
from .parser import ParseError, select

BRUSSELS = ZoneInfo(TIMEZONE)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, add: AddEntitiesCallback) -> None:
    add([CregTariefSensor(hass.data[DOMAIN][entry.entry_id], entry)])


class CregTariefSensor(CoordinatorEntity[CregCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "CREG-tarief"
    _attr_native_unit_of_measurement = "EUR/kWh"
    _attr_icon = "mdi:ev-station"
    _attr_state_class = None
    _attr_suggested_display_precision = 4

    def __init__(self, coordinator: CregCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_tarief"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="CREG",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Kwartaalwissel zonder te wachten op de volgende dagelijkse fetch
        self.async_on_remove(
            async_track_time_interval(self.hass, self._tick, timedelta(minutes=30))
        )

    @callback
    def _tick(self, _now: datetime) -> None:
        self.async_write_ha_state()

    def _selection(self) -> dict | None:
        if not self.coordinator.last_update_success or not self.coordinator.data:
            return None
        try:
            return select(self.coordinator.data, datetime.now(BRUSSELS).date())
        except ParseError:
            return None

    @property
    def available(self) -> bool:
        return self._selection() is not None

    @property
    def native_value(self):
        sel = self._selection()
        return sel["tarief"] if sel else None

    @property
    def extra_state_attributes(self):
        sel = self._selection()
        if not sel:
            return None
        fetched = self.coordinator.last_fetched
        return {
            "kwartaal": sel["kwartaal"],
            "volgend_kwartaal": sel["volgend_kwartaal"],
            "volgend_tarief": sel["volgend_tarief"],
            "volgend_tarief_vanaf": sel["volgend_tarief_vanaf"].isoformat(),
            "bron_url": SOURCE_URL,
            "laatst_opgehaald": fetched.isoformat() if fetched else None,
        }
