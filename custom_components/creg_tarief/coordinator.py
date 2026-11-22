"""DataUpdateCoordinator: dagelijks de CREG-pagina ophalen."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SCAN_INTERVAL, SOURCE_URL
from .parser import ParseError, Quarter, parse_page

_LOGGER = logging.getLogger(__name__)


class CregCoordinator(DataUpdateCoordinator[dict[Quarter, float]]):
    last_fetched: datetime | None = None

    def __init__(self, hass: HomeAssistant, region: str) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.region = region

    async def _async_update_data(self) -> dict[Quarter, float]:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(SOURCE_URL, timeout=30) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"CREG-pagina niet bereikbaar: {err}") from err
        try:
            table = parse_page(html, self.region)
        except ParseError as err:
            raise UpdateFailed(f"CREG-pagina niet te lezen: {err}") from err
        self.last_fetched = dt_util.utcnow()
        return table
