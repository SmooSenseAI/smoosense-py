"""Homepage integration tests."""

import sys
import time
from pathlib import Path

# Add the intests directory to sys.path for imports
sys.path.insert(0, str(Path(__file__).parent))

from base_integration_test import BaseIntegrationTest


class TestHomepage(BaseIntegrationTest):
    """Test cases for the homepage functionality."""

    def test_homepage_loads_successfully(self) -> None:
        """Test that the homepage loads successfully and contains expected content."""
        # Navigate to the homepage
        response = self.page.goto(self.base_url)

        # Check that the response was successful
        self.assertIsNotNone(response)
        self.assertEqual(response.status, 200)

        # Wait for the page to load completely
        self.page.wait_for_load_state("networkidle")

        # Check that the page has loaded some content (not just a blank page)
        body_content = self.page.locator("body").text_content()
        self.assertIsNotNone(body_content)
        self.assertGreater(len(body_content.strip()), 0, "Page appears to be blank")

        # Check that the page title is accessible (optional check)
        title = self.page.title()
        print(f"Page title: '{title}'")

        # Take a screenshot for debugging/verification
        self.take_screenshot("homepage_loaded.png")

    def test_settings_icon_button_and_popover(self) -> None:
        """Test that the settings icon button exists and shows a popover when clicked."""
        # Navigate to the homepage
        response = self.page.goto(self.base_url)
        self.assertEqual(response.status, 200)

        # Wait for the page to load completely
        self.page.wait_for_load_state("networkidle")

        # Find the settings button using the exact selector from the UI code
        # IconPopover with Settings icon creates a PopoverTrigger with title="Settings"
        settings_button = self.page.locator('[data-slot="popover-trigger"][title="Settings"]')

        # Assert that the settings button exists
        self.assertEqual(settings_button.count(), 1, "Settings button not found on the page")

        # Click the settings button
        settings_button.click()

        # Wait for the popover to appear and find it using the exact selector
        # PopoverContent creates an element with data-slot="popover-content"
        popover = self.page.locator('[data-slot="popover-content"]')

        # Wait for the popover to be visible
        popover.wait_for(state="visible", timeout=5000)

        # Assert that the popover is visible
        self.assertTrue(popover.is_visible(), "Settings popover did not appear")

        # Take a screenshot of the popover state
        self.take_screenshot("settings_popover.png")

