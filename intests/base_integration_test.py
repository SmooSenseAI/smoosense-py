"""Base integration test class with server management."""

import socket
import threading
import time
import unittest
from pathlib import Path
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from smoosense.app import SenseTableApp


def find_free_port() -> int:
    """Find a free port to run the test server on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class ServerFixture:
    """Test server wrapper for SenseTableApp with proper lifecycle management."""

    def __init__(self, host: str = "localhost", port: Optional[int] = None):
        self.host = host
        self.port = port or find_free_port()
        self.app_instance: Optional[SenseTableApp] = None
        self.thread: Optional[threading.Thread] = None
        self.server_ready = threading.Event()
        self.shutdown_flag = threading.Event()

    def _run_server(self) -> None:
        """Run the server in a separate thread."""
        try:
            # Create SenseTableApp instance with minimal configuration
            self.app_instance = SenseTableApp()
            flask_app = self.app_instance.create_app()

            # Configure Flask app to be more suitable for testing
            flask_app.config['TESTING'] = True
            flask_app.config['DEBUG'] = False

            # Signal that server is ready
            self.server_ready.set()

            # Run the Flask app
            flask_app.run(
                host=self.host,
                port=self.port,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            print(f"Server failed to start: {e}")
            self.server_ready.set()  # Set anyway to unblock waiting thread

    def start(self) -> None:
        """Start the server in a background thread."""
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

        # Wait for server to be ready (with timeout)
        if not self.server_ready.wait(timeout=10):
            raise RuntimeError("Server failed to start within 10 seconds")

        # Give the server a moment to fully initialize
        time.sleep(1)

    def stop(self) -> None:
        """Stop the server."""
        self.shutdown_flag.set()
        if self.thread and self.thread.is_alive():
            # Flask's built-in server doesn't have a graceful shutdown,
            # but the daemon thread will be cleaned up when main thread exits
            pass

    @property
    def base_url(self) -> str:
        """Get the base URL for the server."""
        return f"http://{self.host}:{self.port}"


class BaseIntegrationTest(unittest.TestCase):
    """Base test class for integration tests with server and browser management."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up server and browser for all tests in the class."""
        # Start the test server
        cls.server = ServerFixture()
        cls.server.start()

        # Start Playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

        # Ensure screenshots directory exists
        cls.screenshots_dir = Path("intests/screenshots")
        cls.screenshots_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Clean up server and browser after all tests."""
        cls.browser.close()
        cls.playwright.stop()
        cls.server.stop()

    def setUp(self) -> None:
        """Set up a new browser context and page for each test."""
        self.context: BrowserContext = self.browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        self.page: Page = self.context.new_page()

    def tearDown(self) -> None:
        """Clean up browser context after each test."""
        self.context.close()

    def take_screenshot(self, filename: str) -> Path:
        """Take a screenshot and save it with the given filename."""
        screenshot_path = self.screenshots_dir / filename
        self.page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to: {screenshot_path}")
        return screenshot_path

    @property
    def base_url(self) -> str:
        """Get the base URL for the test server."""
        return self.server.base_url