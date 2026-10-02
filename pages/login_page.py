from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/"

    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    @property
    def error_message(self) -> str:
        return self.text_of(self.ERROR)
