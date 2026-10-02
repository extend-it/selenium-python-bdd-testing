from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


def _slug(product_name: str) -> str:
    """'Sauce Labs Backpack' -> 'sauce-labs-backpack' (the app builds its button ids this way)."""
    return product_name.strip().lower().replace(" ", "-")


class InventoryPage(BasePage):
    path = "/inventory.html"

    TITLE = (By.CLASS_NAME, "title")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")

    def is_loaded(self) -> bool:
        self.wait_for_url_contains("inventory.html")
        return self.text_of(self.TITLE) == "Products"

    def add_to_cart(self, product_name: str) -> None:
        self.click((By.ID, f"add-to-cart-{_slug(product_name)}"))

    @property
    def cart_count(self) -> int:
        if not self.is_visible(self.CART_BADGE):
            return 0
        return int(self.text_of(self.CART_BADGE))

    def open_cart(self) -> None:
        self.click(self.CART_LINK)
