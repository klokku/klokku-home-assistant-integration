"""The Klokku integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .coordinator import KlokkuConfigEntry, KlokkuDataUpdateCoordinator

_PLATFORMS: list[Platform] = [Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: KlokkuConfigEntry) -> bool:
    """Set up Klokku from a config entry."""

    # Set up one data coordinator per account/config entry
    coordinator = KlokkuDataUpdateCoordinator(
        hass,
        config_entry=entry,
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: KlokkuConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
