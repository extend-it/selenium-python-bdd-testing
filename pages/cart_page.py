from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    path = "/cart.html"

    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")

    def is_loaded(self) -> bool:
        self.wait_for_url_contains("cart.html")
        return True

    @property
    def item_names(self) -> list[str]:
        return [element.text for element in self.find_all(self.ITEM_NAMES)]
