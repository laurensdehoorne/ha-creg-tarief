"""CREG-tarief voor terugbetaling thuisladen bedrijfswagens."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import CONF_REGION, DEFAULT_REGION, DOMAIN
from .coordinator import STORAGE_VERSION, CregCoordinator, storage_key

PLATFORMS = ["sensor"]

type CregConfigEntry = ConfigEntry[CregCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: CregConfigEntry) -> bool:
    coordinator = CregCoordinator(hass, entry, entry.data.get(CONF_REGION, DEFAULT_REGION))
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: CregConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: CregConfigEntry) -> None:
    """Bewaarde tabel opruimen als de integratie verwijderd wordt."""
    await Store(hass, STORAGE_VERSION, storage_key(entry)).async_remove()
