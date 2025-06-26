# Klokku Home Assistant integration

This is a Home Assistant integration for Klokku, allowing you to read and control your current budget from Home Assistant.

## Installation

### Using HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2. Click on HACS in the sidebar.
3. Click on "Integrations".
4. Click on the three dots in the top right corner and select "Custom repositories".
5. Enter `klokku/klokku-home-assistant-integration` in the repository field, select "Integration" as the category, and click "Add".
6. Click on the "+ Explore & Download Repositories" button in the bottom right.
7. Search for "Klokku" and click on it.
8. Click on "Download" in the bottom right corner.
9. Restart Home Assistant.

### Manual Installation

If you don't use HACS, you can install the integration manually:

1. Download the latest release from the [GitHub repository](https://github.com/klokku/klokku-home-assistant-integration).
2. Extract the contents.
3. Copy the `custom_components/klokku` directory to your Home Assistant's `custom_components` directory.
4. Restart Home Assistant.

## Configuration

After installation, you need to configure the integration:

1. Go to your Home Assistant instance.
2. Navigate to **Settings** > **Devices & Services**.
3. Click on the **+ Add Integration** button in the bottom right corner.
4. Search for "Klokku" and select it.
5. You will be prompted to enter the following information:
   - **URL**: The URL of your Klokku service (e.g., http://localhost:8080/)
   - **Username**: Your Klokku username for authentication
6. Click **Submit** to add the integration.

Once configured, the integration will fetch your current and other active budgets from Klokku and make them available in Home Assistant as a select entity

## Development

## Setup

1. Clone the repository
2. Install dependencies with Poetry:

```bash
poetry install
```

### Testing

To run the tests, you need to install the test dependencies:

```bash
poetry install --with test
```

Then you can run the tests using pytest:

```bash
# Run all tests
poetry run pytest -v

# Run specific tests
poetry run pytest tests/custom_components/klokku/test_coordinator.py 
```
