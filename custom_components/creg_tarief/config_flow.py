"""Config flow: keuze van het gewest."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_REGION, DEFAULT_REGION, DOMAIN, REGIONS


class CregConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_REGION])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"CREG-tarief {REGIONS[user_input[CONF_REGION]]}", data=user_input
            )
        schema = vol.Schema(
            {
                vol.Required(CONF_REGION, default=DEFAULT_REGION): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=list(REGIONS),
                        mode="dropdown",
                        translation_key="region",
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
