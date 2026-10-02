"""Root pytest configuration: CLI options, WebDriver lifecycle, page fixtures, Allure hooks.

Configuration precedence: command-line option > environment variable > default.

  --browser      / BROWSER          chrome | firefox            (default: chrome)
  --headless     / HEADLESS=1       run without a visible window
  --app-url      / APP_URL          application under test      (default: https://www.saucedemo.com)
  --remote-url   / SELENIUM_REMOTE_URL  Selenium Grid / cloud hub; when set, a Remote driver is used

Container-only overrides (used by the Jenkins image, which ships Debian's Chromium):
  CHROME_BIN         path to the Chrome/Chromium binary
  CHROMEDRIVER_PATH  path to a matching chromedriver (otherwise Selenium Manager resolves one)
"""

from __future__ import annotations

import os
import platform
from pathlib import Path

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from pages import CartPage, InventoryPage, LoginPage

DEFAULT_APP_URL = "https://www.saucedemo.com"


# --------------------------------------------------------------------------- options
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ui", "UI test settings")
    group.addoption("--browser", default=os.getenv("BROWSER", "chrome"), choices=("chrome", "firefox"))
    group.addoption(
        "--headless",
        action="store_true",
        default=os.getenv("HEADLESS", "").lower() in ("1", "true", "yes"),
    )
    group.addoption("--app-url", default=os.getenv("APP_URL", DEFAULT_APP_URL))
    group.addoption("--remote-url", default=os.getenv("SELENIUM_REMOTE_URL", ""))


@pytest.fixture(scope="session")
def browser_name(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("--browser")


@pytest.fixture(scope="session")
def app_url(pytestconfig: pytest.Config) -> str:
    return pytestconfig.getoption("--app-url")


# --------------------------------------------------------------------------- driver
def _chrome_options(headless: bool) -> ChromeOptions:
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    # Needed inside Docker containers; harmless elsewhere.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Stop Chrome's password-manager / breached-password bubbles from appearing over the page.
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    if chrome_bin := os.getenv("CHROME_BIN"):
        options.binary_location = chrome_bin
    return options


def _firefox_options(headless: bool) -> FirefoxOptions:
    options = FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")
    return options


def _create_driver(browser: str, headless: bool, remote_url: str) -> webdriver.Remote:
    options = _chrome_options(headless) if browser == "chrome" else _firefox_options(headless)

    if remote_url:
        return webdriver.Remote(command_executor=remote_url, options=options)

    if browser == "chrome":
        driver_path = os.getenv("CHROMEDRIVER_PATH")
        service = ChromeService(executable_path=driver_path) if driver_path else ChromeService()
        return webdriver.Chrome(options=options, service=service)
    return webdriver.Firefox(options=options)


@pytest.fixture
def driver(pytestconfig: pytest.Config, browser_name: str):
    """One fresh browser per scenario: slower than sharing, but scenarios stay independent."""
    drv = _create_driver(
        browser=browser_name,
        headless=pytestconfig.getoption("--headless"),
        remote_url=pytestconfig.getoption("--remote-url"),
    )
    drv.implicitly_wait(0)  # explicit waits only (see BasePage)
    yield drv
    drv.quit()


# --------------------------------------------------------------------------- page objects
@pytest.fixture
def login_page(driver, app_url) -> LoginPage:
    return LoginPage(driver, app_url)


@pytest.fixture
def inventory_page(driver, app_url) -> InventoryPage:
    return InventoryPage(driver, app_url)


@pytest.fixture
def cart_page(driver, app_url) -> CartPage:
    return CartPage(driver, app_url)


# --------------------------------------------------------------------------- Allure hooks
def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    """pytest-bdd hook: attach a screenshot and the page URL to Allure when a step fails."""
    try:
        drv = request.getfixturevalue("driver")
        allure.attach(
            drv.get_screenshot_as_png(),
            name=f"screenshot - {step.text}",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(drv.current_url, name="url", attachment_type=allure.attachment_type.TEXT)
    except Exception as err:  # never let reporting hide the real failure
        print(f"[allure] could not attach screenshot: {err}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write environment.properties so the Allure report shows what the run was executed against."""
    results_dir = session.config.getoption("--alluredir", default=None)
    if not results_dir:
        return
    path = Path(results_dir)
    path.mkdir(parents=True, exist_ok=True)
    env = {
        "Browser": session.config.getoption("--browser"),
        "Headless": session.config.getoption("--headless"),
        "App.URL": session.config.getoption("--app-url"),
        "Remote.URL": session.config.getoption("--remote-url") or "local",
        "Python": platform.python_version(),
        "OS": platform.platform(),
    }
    (path / "environment.properties").write_text(
        "\n".join(f"{key}={value}" for key, value in env.items()) + "\n", encoding="utf-8"
    )
