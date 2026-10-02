"""Common behaviour shared by every page object.

Page objects own locators and low-level interactions. Step definitions only call
intention-revealing methods (login, add_to_cart, ...) and never touch locators.
"""

from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

Locator = tuple[str, str]


class BasePage:
    #: Path appended to the application base URL by open(). Override in subclasses.
    path: str = "/"

    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    # --- navigation -------------------------------------------------------
    def open(self) -> BasePage:
        self.driver.get(f"{self.base_url}{self.path}")
        return self

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    # --- element helpers (explicit waits only, no sleeps) ------------------
    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def click(self, locator: Locator) -> None:
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type(self, locator: Locator, text: str) -> None:
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text

    def is_visible(self, locator: Locator) -> bool:
        elements = self.driver.find_elements(*locator)
        return bool(elements) and elements[0].is_displayed()

    def wait_for_url_contains(self, fragment: str) -> None:
        self.wait.until(EC.url_contains(fragment))
