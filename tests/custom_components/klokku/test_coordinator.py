"""Tests for the Klokku coordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_asyncio import fixture
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.klokku.coordinator import KlokkuDataUpdateCoordinator, KlokkuData


@fixture
def mock_hass():
    """Return a mocked HomeAssistant instance."""
    mock = MagicMock(spec=HomeAssistant)
    mock.data = {'network': {}}
    return mock


@fixture
def mock_config_entry():
    """Return a mocked ConfigEntry instance."""
    config_entry = MagicMock(spec=ConfigEntry)
    config_entry.data = {
        CONF_URL: "https://example.com",
        CONF_ID: "user123"
    }
    return config_entry


@fixture
def mock_klokku_api():
    """Return a mocked KlokkuApi instance."""
    with patch("custom_components.klokku.coordinator.KlokkuApi") as mock_api_class:
        mock_api = mock_api_class.return_value
        mock_api.get_current_event = AsyncMock()
        mock_api.get_current_week_plan = AsyncMock()
        yield mock_api


@fixture
async def mock_session():
    """Return a mocked ClientSession instance."""
    return MagicMock()

@fixture
async def coordinator(mock_hass, mock_config_entry, mock_klokku_api, mock_session):
    """Return a KlokkuDataUpdateCoordinator instance."""
    return KlokkuDataUpdateCoordinator(mock_hass, config_entry=mock_config_entry, session=mock_session)


@pytest.mark.asyncio
async def test_update_data_success(coordinator, mock_klokku_api):
    """Test successful data update."""
    # Mock the return values
    mock_event = MagicMock()
    mock_week_plan = MagicMock()
    mock_week_plan.items = [MagicMock(), MagicMock()]

    mock_klokku_api.get_current_event.return_value = mock_event
    mock_klokku_api.get_current_week_plan.return_value = mock_week_plan

    # Call the method
    result = await coordinator._async_update_data()

    # Verify the result
    assert isinstance(result, KlokkuData)
    assert result.current_event == mock_event
    assert result.weekly_items == mock_week_plan.items

    # Verify the API calls
    mock_klokku_api.get_current_event.assert_called_once()
    mock_klokku_api.get_current_week_plan.assert_called_once()


@pytest.mark.asyncio
async def test_update_data_event_exception(coordinator, mock_klokku_api):
    """Test handling of exception from get_current_event."""
    # Mock the return values
    mock_event_exception = Exception("Event error")
    mock_week_plan = MagicMock()
    mock_week_plan.items = [MagicMock(), MagicMock()]

    mock_klokku_api.get_current_event.return_value = mock_event_exception
    mock_klokku_api.get_current_week_plan.return_value = mock_week_plan

    # Call the method
    result = await coordinator._async_update_data()

    # Verify the result
    assert isinstance(result, KlokkuData)
    assert result.current_event is None
    assert result.weekly_items == mock_week_plan.items


@pytest.mark.asyncio
async def test_update_data_weekly_items_exception(coordinator, mock_klokku_api):
    """Test handling of exception from get_current_week_plan."""
    # Mock the return values
    mock_event = MagicMock()
    mock_weekly_plan_exception = Exception("Budgets error")

    mock_klokku_api.get_current_event.return_value = mock_event
    mock_klokku_api.get_current_week_plan.return_value = mock_weekly_plan_exception

    # Call the method and expect an exception
    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator._async_update_data()

    # Verify the exception message
    assert "Failed to fetch weekly plan" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_data_general_exception(coordinator, mock_klokku_api):
    """Test handling of general exceptions."""
    # Mock the API to raise an exception
    mock_klokku_api.get_current_event.side_effect = Exception("General error")
    mock_klokku_api.get_current_week_plan.side_effect = Exception("General error")

    # Call the method and expect an exception
    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator._async_update_data()

    # Verify the exception message
    assert "Error communicating with API" in str(excinfo.value)
