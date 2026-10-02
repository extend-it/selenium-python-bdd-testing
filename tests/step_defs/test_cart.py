from pytest_bdd import parsers, scenarios, then, when

from pages import CartPage, InventoryPage

scenarios("cart.feature")


@when(parsers.parse('I add "{product}" to the cart'))
def add_product(inventory_page: InventoryPage, product: str) -> None:
    inventory_page.add_to_cart(product)


@then(parsers.parse("the cart badge shows {count:d}"))
def cart_badge_count(inventory_page: InventoryPage, count: int) -> None:
    assert inventory_page.cart_count == count


@when("I open the cart")
def open_cart(inventory_page: InventoryPage, cart_page: CartPage) -> None:
    inventory_page.open_cart()
    cart_page.is_loaded()


@then(parsers.parse('the cart contains "{product}"'))
def cart_contains(cart_page: CartPage, product: str) -> None:
    assert product in cart_page.item_names
