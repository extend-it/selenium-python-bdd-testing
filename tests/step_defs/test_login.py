from pytest_bdd import parsers, scenarios, then, when

from pages import LoginPage

# Binds every scenario in the feature file to a generated pytest test.
scenarios("login.feature")


@when(parsers.parse('I log in as "{username}" with password "{password}"'))
def log_in(login_page: LoginPage, username: str, password: str) -> None:
    login_page.login(username, password)


# parsers.re instead of parsers.parse: the GherkinLens extension rejects
# parse-style matches when a long Examples value outweighs the pattern's words.
@then(parsers.re(r'I see the login error "(?P<message>.+)"'))
def login_error_is_shown(login_page: LoginPage, message: str) -> None:
    assert login_page.error_message == message
