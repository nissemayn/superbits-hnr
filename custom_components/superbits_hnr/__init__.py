"""Superbits Hit'n'Run integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_COOKIE, CONF_SCAN_INTERVAL, CONF_USER_ID, DEFAULT_SCAN_INTERVAL, DOMAIN, PLATFORMS
from .coordinator import SuperbitsHnrCoordinator


def _entry_cookie(entry: ConfigEntry) -> str:
    return str(entry.options.get(CONF_COOKIE) or entry.data[CONF_COOKIE])


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Superbits HNR config entry."""
    # A replaced cookie is stored in options. Remove any older copy from data
    # before setting up the coordinator so only the current cookie is retained.
    if CONF_COOKIE in entry.options and CONF_COOKIE in entry.data:
        data = dict(entry.data)
        data.pop(CONF_COOKIE)
        hass.config_entries.async_update_entry(entry, data=data)

    interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    coordinator = SuperbitsHnrCoordinator(
        hass,
        async_get_clientsession(hass),
        int(entry.data[CONF_USER_ID]),
        _entry_cookie(entry),
        interval,
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Superbits HNR config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
