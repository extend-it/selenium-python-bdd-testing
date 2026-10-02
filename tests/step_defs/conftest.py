"""Step definitions shared by more than one feature.

pytest-bdd discovers steps through pytest fixtures, so steps defined in a conftest.py
are visible to every test module in this folder.
"""

from pytest_bdd import given, parsers, then

from pages import InventoryPage, LoginPage


@given("I am on the login page")
def open_login_page(login_page: LoginPage) -> None:
    login_page.open()


@given(parsers.parse('I am logged in as "{username}"'))
def logged_in_as(login_page: LoginPage, inventory_page: InventoryPage, username: str) -> None:
    # All demo users on saucedemo.com share this public password.
    login_page.open()
    login_page.login(username, "secret_sauce")
    assert inventory_page.is_loaded(), "Login did not reach the products page"


@then("I see the products page")
def products_page_is_shown(inventory_page: InventoryPage) -> None:
    assert inventory_page.is_loaded()
