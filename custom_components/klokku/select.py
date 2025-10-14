from klokku_python_client import Budget

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

    if coordinator.data.budgets is not None:
        async_add_entities([
            BudgetSelect(coordinator, coordinator.data.budgets, coordinator.data.current_event.budget)
        ])


class BudgetSelect(CoordinatorEntity[KlokkuDataUpdateCoordinator], SelectEntity):

    def __init__(
            self,
            coordinator: KlokkuDataUpdateCoordinator,
            budgets: list[Budget],
            current_budget: Budget,
    ) -> None:
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "budget"
        self._attr_unique_id = f"{DOMAIN}_budget_select_{coordinator.api.user_id}"
        self._attr_current_option = current_budget.name
        self._attr_options = [budget.name for budget in budgets]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("Updating select")
        self._attr_current_option = self.coordinator.data.current_event.budget.name
        self._attr_options = [budget.name for budget in self.coordinator.data.budgets]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        _LOGGER.debug("Changing budget to: %s", option)

        budget_id = next((budget.id for budget in self.coordinator.data.budgets if budget.name == option), None)

        if budget_id is None:
            _LOGGER.error("No matching budget found for option: %s", option)
            return

        _LOGGER.debug("Budget ID: %s", budget_id)
        await self.coordinator.api.set_current_budget(budget_id)
        await self.coordinator.async_request_refresh()
