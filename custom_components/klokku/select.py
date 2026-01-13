from klokku_python_client import CurrentEventPlanItem, WeeklyItem

from . import KlokkuDataUpdateCoordinator
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import KlokkuConfigEntry
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: KlokkuConfigEntry,
        async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Klokku from config entry."""
    coordinator = config_entry.runtime_data

    if coordinator.data.weekly_items is not None:
        async_add_entities([
            WeeklyItemSelect(coordinator, coordinator.data.weekly_items, coordinator.data.current_event.planItem)
        ])


class WeeklyItemSelect(CoordinatorEntity[KlokkuDataUpdateCoordinator], SelectEntity):

    def __init__(
            self,
            coordinator: KlokkuDataUpdateCoordinator,
            budget_items: list[WeeklyItem],
            current_budget: CurrentEventPlanItem,
    ) -> None:
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "budget"
        self._attr_unique_id = f"{DOMAIN}_budget_item_select_{coordinator.api.authenticated_user_uid}"
        self._attr_current_option = current_budget.name
        self._attr_options = [item.name for item in budget_items]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updating select")
        self._attr_current_option = self.coordinator.data.current_event.planItem.name
        self._attr_options = [item.name for item in self.coordinator.data.weekly_items]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        _LOGGER.debug("Changing current weekly item to: %s", option)

        budget_item_id = next((item.budget_item_id for item in self.coordinator.data.weekly_items if item.name == option), None)

        if budget_item_id is None:
            _LOGGER.error("No matching weekly item found for option: %s", option)
            return

        _LOGGER.debug("Budget Item ID: %s", budget_item_id)
        await self.coordinator.api.set_current_event(budget_item_id)
        await self.coordinator.async_request_refresh()
