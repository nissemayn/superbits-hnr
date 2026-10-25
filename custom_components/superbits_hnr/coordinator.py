"""Data update coordinator for Superbits Hit'n'Run."""

from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientSession
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import (
    ConfigEntryAuthFailed,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    SuperbitsAuthError,
    SuperbitsConnectionError,
    SuperbitsRateLimitError,
    async_get_hnr_data,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SuperbitsHnrCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch Superbits HNR data on a configurable interval."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        user_id: int,
        cookie: str,
        interval_minutes: int,
    ) -> None:
        self.session = session
        self.user_id = user_id
        self.cookie = cookie
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval_minutes),
            always_update=False,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await async_get_hnr_data(self.session, self.user_id, self.cookie)
            data["last_checked"] = dt_util.utcnow().isoformat()
            return data
        except SuperbitsAuthError as err:
            raise ConfigEntryAuthFailed(
                "Superbits rejected the cookie. Update it in the integration options."
            ) from err
        except (SuperbitsConnectionError, SuperbitsRateLimitError) as err:
            raise UpdateFailed(str(err)) from err
