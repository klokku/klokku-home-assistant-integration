"""Config flow for the Klokku integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_URL, CONF_ID, CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from klokku_python_client import KlokkuApi

from . import KlokkuDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_URL): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_ACCESS_TOKEN): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # Validate that the URL is properly formatted
    try:
        cv.url(data[CONF_URL])
    except vol.Invalid:
        raise CannotConnect

    api = KlokkuApi(data[CONF_URL])
    api.session = async_get_clientsession(hass)
    authentication_type_key = CONF_ACCESS_TOKEN if data.get(CONF_ACCESS_TOKEN) else CONF_USERNAME
    _LOGGER.warning(f"Authenticating with {authentication_type_key}: {data[authentication_type_key]}")
    authenticated = await api.authenticate(data[authentication_type_key])
    if not authenticated:
        raise InvalidAuth

    return {
        "title": f"Klokku - {data[CONF_USERNAME]}",
        CONF_URL: data[CONF_URL],
        CONF_ID: api.authenticated_user_uid,
        CONF_USERNAME: data[CONF_USERNAME],
        CONF_ACCESS_TOKEN: data.get(CONF_ACCESS_TOKEN)
    }


class KlokkuConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Klokku."""

    VERSION = 1
    MINOR_VERSION = 2

    async def async_migrate_entry(hass, config_entry: ConfigEntry[KlokkuDataUpdateCoordinator]):
        """Migrate old entry."""
        _LOGGER.debug("Migrating configuration from version %s.%s", config_entry.version, config_entry.minor_version)

        if config_entry.version > 1 or config_entry.minor_version > 2:
            # This means the user has downgraded from a future version
            return False

        if config_entry.version == 1:

            new_data = {**config_entry.data}
            if config_entry.minor_version < 2:
                new_data[CONF_ACCESS_TOKEN] = ""
                pass


            hass.config_entries.async_update_entry(config_entry, data=new_data, minor_version=2, version=1)

        _LOGGER.debug("Migration to configuration version %s.%s successful", config_entry.version, config_entry.minor_version)

        return True

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Validate that either username or access token is provided
            if not user_input.get(CONF_USERNAME) and not user_input.get(CONF_ACCESS_TOKEN):
                errors["base"] = "missing_credentials"
            elif not errors:
                try:
                    info = await validate_input(self.hass, user_input)
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(title=info["title"], data=info)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
