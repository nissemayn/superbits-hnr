"""Config and options flows for Superbits Hit'n'Run."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    SuperbitsAuthError,
    SuperbitsConnectionError,
    SuperbitsRateLimitError,
    async_get_hnr_data,
)
from .const import (
    CONF_COOKIE,
    CONF_SCAN_INTERVAL,
    CONF_USER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


def _interval_selector() -> NumberSelector:
    return NumberSelector(
        NumberSelectorConfig(
            min=MIN_SCAN_INTERVAL,
            max=MAX_SCAN_INTERVAL,
            step=5,
            mode=NumberSelectorMode.BOX,
            unit_of_measurement="min",
        )
    )


def _cookie_selector() -> TextSelector:
    return TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD, multiline=True))


class SuperbitsHnrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle setup from Home Assistant's UI."""

    VERSION = 1

    async def async_step_reauth(self, entry_data: dict[str, Any]):
        """Start reauthentication for an existing entry."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        """Validate and store a replacement Superbits cookie."""
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()

        if user_input is not None:
            cookie = str(user_input.get(CONF_COOKIE, "")).strip()
            try:
                if not cookie:
                    raise ValueError
                await async_get_hnr_data(
                    async_get_clientsession(self.hass),
                    int(entry.data[CONF_USER_ID]),
                    cookie,
                )
            except ValueError:
                errors["base"] = "invalid_input"
            except SuperbitsAuthError:
                errors["base"] = "invalid_auth"
            except (SuperbitsConnectionError, SuperbitsRateLimitError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(str(entry.data[CONF_USER_ID]))
                self._abort_if_unique_id_mismatch()
                # Reauthentication moves the active credential back into data
                # and removes any previous options-flow copy.
                options = {
                    key: value
                    for key, value in entry.options.items()
                    if key != CONF_COOKIE
                }
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={CONF_COOKIE: cookie},
                    options=options,
                )

        schema = vol.Schema({vol.Required(CONF_COOKIE): _cookie_selector()})
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=schema, errors=errors
        )

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                user_id = int(str(user_input[CONF_USER_ID]).strip())
                cookie = str(user_input[CONF_COOKIE]).strip()
                if user_id <= 0 or not cookie:
                    raise ValueError
            except (KeyError, TypeError, ValueError):
                errors["base"] = "invalid_input"
            else:
                try:
                    await async_get_hnr_data(
                        async_get_clientsession(self.hass), user_id, cookie
                    )
                except SuperbitsAuthError:
                    errors["base"] = "invalid_auth"
                except (SuperbitsConnectionError, SuperbitsRateLimitError):
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(str(user_id))
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Superbits HNR ({user_id})",
                        data={CONF_USER_ID: user_id, CONF_COOKIE: cookie},
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_USER_ID): TextSelector(),
                vol.Required(CONF_COOKIE): _cookie_selector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return SuperbitsHnrOptionsFlow()


class SuperbitsHnrOptionsFlow(config_entries.OptionsFlowWithReload):
    """Allow changing the polling interval and refreshing the cookie."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            interval = int(user_input[CONF_SCAN_INTERVAL])
            new_cookie = str(user_input.get(CONF_COOKIE, "")).strip()
            if new_cookie:
                try:
                    await async_get_hnr_data(
                        async_get_clientsession(self.hass),
                        int(self.config_entry.data[CONF_USER_ID]),
                        new_cookie,
                    )
                except SuperbitsAuthError:
                    errors["base"] = "invalid_auth"
                except (SuperbitsConnectionError, SuperbitsRateLimitError):
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_create_entry(
                        title="",
                        data={CONF_SCAN_INTERVAL: interval, CONF_COOKIE: new_cookie},
                    )
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_SCAN_INTERVAL: interval,
                        **(
                            {CONF_COOKIE: self.config_entry.options[CONF_COOKIE]}
                            if self.config_entry.options.get(CONF_COOKIE)
                            else {}
                        ),
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): _interval_selector(),
                vol.Optional(CONF_COOKIE): _cookie_selector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
