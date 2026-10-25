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
    interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    coordinator = SuperbitsHnrCoordinator(
        hass,
        async_get_clientsession(hass),
        int(entry.data[CONF_USER_ID]),
        _entry_cookie(entry),
        interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Superbits HNR config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload integration after options or cookie changes."""
    await hass.config_entries.async_reload(entry.entry_id)
