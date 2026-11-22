"""DataUpdateCoordinator: de CREG-pagina ophalen en de laatste tabel bewaren.

De CREG publiceert het tarief van het volgende kwartaal weken op voorhand. Staat
dat er al, dan volstaat een wekelijkse controle; anders wordt dagelijks gekeken.
Is de pagina even niet bereikbaar, dan blijft de laatst opgehaalde tabel gelden
(ook na een herstart). Alleen een onleesbare pagina maakt de sensor onbeschikbaar.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SOURCE_URL, TIMEZONE
from .parser import ParseError, Quarter, next_quarter, parse_page, quarter_of

_LOGGER = logging.getLogger(__name__)

INTERVAL_NEXT_KNOWN = timedelta(days=7)  # volgend kwartaal staat er al
INTERVAL_NEXT_UNKNOWN = timedelta(days=1)  # wachten op publicatie volgend kwartaal
INTERVAL_RETRY = timedelta(hours=1)  # pagina niet bereikbaar
STORAGE_VERSION = 1


def storage_key(entry: ConfigEntry) -> str:
    return f"{DOMAIN}.{entry.entry_id}"


class CregCoordinator(DataUpdateCoordinator[dict[Quarter, float]]):
    last_fetched: datetime | None = None

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, region: str) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=entry, name=DOMAIN, update_interval=INTERVAL_NEXT_UNKNOWN
        )
        self.region = region
        self._store: Store[dict] = Store(hass, STORAGE_VERSION, storage_key(entry))
        self._cached: dict[Quarter, float] | None = None

    async def async_load_cache(self) -> None:
        """Laatst opgehaalde tabel van schijf lezen (vóór de eerste refresh)."""
        raw = await self._store.async_load()
        if not raw or raw.get("region") != self.region:
            return
        try:
            table: dict[Quarter, float] = {}
            for key, value in raw["tabel"].items():
                year, quarter = key.split("-")
                table[(int(year), int(quarter))] = float(value)
            self.last_fetched = dt_util.parse_datetime(raw["laatst_opgehaald"])
            self._cached = table
        except (KeyError, ValueError, TypeError, AttributeError):
            _LOGGER.warning("Bewaarde CREG-tabel is ongeldig en wordt genegeerd")

    def _interval_for(self, table: dict[Quarter, float]) -> timedelta:
        today = dt_util.now(dt_util.get_time_zone(TIMEZONE)).date()
        if next_quarter(quarter_of(today)) in table:
            return INTERVAL_NEXT_KNOWN
        return INTERVAL_NEXT_UNKNOWN

    async def _async_update_data(self) -> dict[Quarter, float]:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(SOURCE_URL, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except Exception as err:  # noqa: BLE001
            previous = self.data or self._cached
            self.update_interval = INTERVAL_RETRY
            if previous is None:
                raise UpdateFailed(f"CREG-pagina niet bereikbaar: {err}") from err
            _LOGGER.warning(
                "CREG-pagina niet bereikbaar (%s); laatst opgehaalde tabel blijft gelden", err
            )
            return previous
        try:
            table = parse_page(html, self.region)
        except ParseError as err:
            self.update_interval = INTERVAL_NEXT_UNKNOWN
            raise UpdateFailed(f"CREG-pagina niet te lezen: {err}") from err
        self.last_fetched = dt_util.utcnow()
        self.update_interval = self._interval_for(table)
        self._cached = table
        await self._store.async_save(
            {
                "region": self.region,
                "laatst_opgehaald": self.last_fetched.isoformat(),
                "tabel": {f"{y}-{q}": v for (y, q), v in table.items()},
            }
        )
        return table
