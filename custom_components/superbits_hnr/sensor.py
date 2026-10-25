"""Sensors for Superbits Hit'n'Run."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import CONF_USER_ID, DOMAIN
from .coordinator import SuperbitsHnrCoordinator

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="total",
        name="Total antal",
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="hitrun",
        name="Hit'n'Run",
        icon="mdi:alert-circle-outline",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    coordinator: SuperbitsHnrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        SuperbitsHnrSensor(coordinator, entry, description)
        for description in SENSORS
    )


class SuperbitsHnrSensor(CoordinatorEntity[SuperbitsHnrCoordinator], SensorEntity):
    """Expose one value from the Superbits HNR coordinator."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        coordinator: SuperbitsHnrCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        user_id = str(entry.data[CONF_USER_ID])
        self._attr_unique_id = f"{user_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, user_id)},
            name=f"Superbits HNR {user_id}",
            manufacturer="Superbits",
            model="Hit'n'Run status",
        )

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        key = self.entity_description.key
        return int(self.coordinator.data["total" if key == "total" else "hitrun"])

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.coordinator.data is None or self.entity_description.key != "hitrun":
            return None
        return {
            "active_torrents": [
                {"name": item["name"], "torrent_id": item["torrent_id"], "seedtime": item["seedtime"]}
                for item in self.coordinator.data["active_hnr"]
            ],
            "last_checked": self.coordinator.data.get("last_checked"),
        }
