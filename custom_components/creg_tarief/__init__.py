"""CREG-tarief voor terugbetaling thuisladen bedrijfswagens."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import CONF_REGION, DEFAULT_REGION, DOMAIN
from .coordinator import STORAGE_VERSION, CregCoordinator, storage_key

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = CregCoordinator(hass, entry, entry.data.get(CONF_REGION, DEFAULT_REGION))
    await coordinator.async_load_cache()
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Bewaarde tabel opruimen als de integratie verwijderd wordt."""
    await Store(hass, STORAGE_VERSION, storage_key(entry)).async_remove()
