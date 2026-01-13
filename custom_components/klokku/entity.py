"""Base for all Klokku entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from klokku_python_client import WeeklyItem

from .const import DOMAIN
from .coordinator import KlokkuDataUpdateCoordinator


class KlokkuBaseEntity(CoordinatorEntity[KlokkuDataUpdateCoordinator]):
    """Common base for Klokku entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KlokkuDataUpdateCoordinator,
        weekly_items: list[WeeklyItem],
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)

        self.weekly_items = weekly_items

        self._attr_device_info = DeviceInfo(
            identifiers={DOMAIN},
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()