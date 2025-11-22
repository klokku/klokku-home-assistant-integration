"""Coordinator for Klokku."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_ID, CONF_ACCESS_TOKEN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from klokku_python_client import KlokkuApi, Budget, Event

from .const import (
    DOMAIN as KLOKKU_DOMAIN, SCAN_INTERVAL_SEC,
)

_LOGGER = logging.getLogger(__name__)


type KlokkuConfigEntry = ConfigEntry[KlokkuDataUpdateCoordinator]

@dataclass
class KlokkuData:
    """Data for Klokku integration."""
    current_event: Event | None
    budgets: list[Budget]

class KlokkuDataUpdateCoordinator(DataUpdateCoordinator[KlokkuData]):
    """Class to manage fetching Klokku data."""

    config_entry: KlokkuConfigEntry

    def __init__(self, hass: HomeAssistant, *, config_entry: KlokkuConfigEntry, session=None) -> None:
        """Initialize Klokku data updater."""

        self.api = KlokkuApi(config_entry.data[CONF_URL])
        # Authenticate with the API
        self.api.session = session or async_get_clientsession(hass)
        self._auth_failed = False

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{KLOKKU_DOMAIN}-{config_entry.data[CONF_ID]}",
            update_interval=timedelta(seconds=SCAN_INTERVAL_SEC),
            always_update=True,
        )

        # Default to false on init so _async_update_data logic works
        self.last_update_success = False

    async def async_initialize(self) -> None:
        """Initialize authentication asynchronously."""
        _LOGGER.debug("KlokkuDataUpdateCoordinator.async_initialize called")
        auth_string = self.config_entry.data.get(CONF_ACCESS_TOKEN) or self.config_entry.data.get(CONF_USERNAME)
        _LOGGER.debug(f"Auth string: '{auth_string}'")
        _LOGGER.debug(f"Config entry data: {self.config_entry.data}")
        authenticated = await self.api.authenticate(auth_string)
        if not authenticated:
            self._auth_failed = True
            raise ConfigEntryAuthFailed("Failed to authenticate with Klokku API")

    async def _async_update_data(self) -> KlokkuData:
        """Fetch data from Klokku."""
        _LOGGER.debug("KlokkuDataUpdateCoordinator._async_update_data called")

        if self._auth_failed:
            raise UpdateFailed("Authentication failed during initialization")

        try:
            current_event, budgets = await asyncio.gather(
                self.api.get_current_event(),
                self.api.get_all_budgets(),
                return_exceptions=True
            )

            # Handle exceptions from individual API calls
            if isinstance(current_event, Exception):
                _LOGGER.warning("Failed to fetch current event: %s", current_event)
                current_event = None

            if isinstance(budgets, Exception):
                _LOGGER.error("Failed to fetch budgets: %s", budgets)
                raise UpdateFailed(f"Failed to fetch budgets: {budgets}")

            _LOGGER.debug("Current event: %s", current_event)
            _LOGGER.debug("Budgets: %s", budgets)

            return KlokkuData(current_event, budgets)

        except Exception as err:
            _LOGGER.error("Error communicating with Klokku API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
