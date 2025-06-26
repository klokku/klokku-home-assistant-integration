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
    return MagicMock(spec=HomeAssistant)


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
        mock_api.get_all_budgets = AsyncMock()
        yield mock_api


@fixture
async def coordinator(mock_hass, mock_config_entry, mock_klokku_api):
    """Return a KlokkuDataUpdateCoordinator instance."""
    return KlokkuDataUpdateCoordinator(mock_hass, config_entry=mock_config_entry)


@pytest.mark.asyncio
async def test_coordinator_init(coordinator, mock_klokku_api):
    """Test coordinator initialization."""
    assert coordinator.api.user_id == "user123"
    assert coordinator.last_update_success is False


@pytest.mark.asyncio
async def test_update_data_success(coordinator, mock_klokku_api):
    """Test successful data update."""
    # Mock the return values
    mock_event = MagicMock()
    mock_budgets = [MagicMock(), MagicMock()]

    mock_klokku_api.get_current_event.return_value = mock_event
    mock_klokku_api.get_all_budgets.return_value = mock_budgets

    # Call the method
    result = await coordinator._async_update_data()

    # Verify the result
    assert isinstance(result, KlokkuData)
    assert result.current_event == mock_event
    assert result.budgets == mock_budgets

    # Verify the API calls
    mock_klokku_api.get_current_event.assert_called_once()
    mock_klokku_api.get_all_budgets.assert_called_once()


@pytest.mark.asyncio
async def test_update_data_event_exception(coordinator, mock_klokku_api):
    """Test handling of exception from get_current_event."""
    # Mock the return values
    mock_event_exception = Exception("Event error")
    mock_budgets = [MagicMock(), MagicMock()]

    mock_klokku_api.get_current_event.return_value = mock_event_exception
    mock_klokku_api.get_all_budgets.return_value = mock_budgets

    # Call the method
    result = await coordinator._async_update_data()

    # Verify the result
    assert isinstance(result, KlokkuData)
    assert result.current_event is None
    assert result.budgets == mock_budgets


@pytest.mark.asyncio
async def test_update_data_budgets_exception(coordinator, mock_klokku_api):
    """Test handling of exception from get_all_budgets."""
    # Mock the return values
    mock_event = MagicMock()
    mock_budgets_exception = Exception("Budgets error")

    mock_klokku_api.get_current_event.return_value = mock_event
    mock_klokku_api.get_all_budgets.return_value = mock_budgets_exception

    # Call the method and expect an exception
    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator._async_update_data()

    # Verify the exception message
    assert "Failed to fetch budgets" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_data_general_exception(coordinator, mock_klokku_api):
    """Test handling of general exceptions."""
    # Mock the API to raise an exception
    mock_klokku_api.get_current_event.side_effect = Exception("General error")
    mock_klokku_api.get_all_budgets.side_effect = Exception("General error")

    # Call the method and expect an exception
    with pytest.raises(UpdateFailed) as excinfo:
        await coordinator._async_update_data()

    # Verify the exception message
    assert "Error communicating with API" in str(excinfo.value)
