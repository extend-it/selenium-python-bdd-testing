# selenium-pytest

A UI test automation scaffold using **Python, pytest-bdd (Gherkin), Selenium 4 and the Page Object Model**, with **Allure** reporting. The tests run locally, in a local **Jenkins in Docker** that has the Allure plugin, and in **GitHub Actions**.

The application under test is the public demo shop [saucedemo.com](https://www.saucedemo.com).

## Project layout

```
selenium-pytest/
├── features/                  # Gherkin scenarios (business-readable)
│   ├── login.feature
│   └── cart.feature
├── pages/                     # Page Object Model: locators + actions, no assertions
│   ├── base_page.py           # explicit-wait helpers shared by all pages
│   ├── login_page.py
│   ├── inventory_page.py
│   └── cart_page.py
├── tests/step_defs/           # step definitions: glue between Gherkin and page objects
│   ├── conftest.py            # steps shared across features
│   ├── test_login.py
│   └── test_cart.py
├── conftest.py                # CLI options, WebDriver fixture, page fixtures, Allure hooks
├── pytest.ini
├── scripts/run_tests.sh       # used by Jenkins
├── Jenkinsfile                # for a Pipeline-from-SCM job
├── jenkins/                   # local Jenkins: Dockerfile, plugins, JCasC, compose file
└── .github/workflows/         # lint + UI tests (Chrome/Firefox) + Allure report → GitHub Pages
```

## 1. Run locally (Windows / PowerShell)

Requirements: Python 3.10+ and Chrome or Firefox. You don't need to download a driver: Selenium Manager resolves one automatically.

```powershell
cd C:\Auto\selenium-pytest
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

pytest                                  # all scenarios, Chrome, visible browser
pytest -m smoke --headless              # smoke subset, headless
pytest --browser firefox                # Firefox
pytest --app-url https://www.saucedemo.com -k login
```

Every run writes raw Allure results to `allure-results/` (configured in `pytest.ini`).

### View the Allure report without Jenkins

The Allure CLI needs Java 8+ on the PATH. Install it with one of:

- `scoop install allure`
- `npm install -g allure-commandline`

```powershell
allure serve allure-results             # builds a temporary report and opens the browser
# or
allure generate allure-results --clean -o allure-report
allure open allure-report
```

## 2. Run in a local Jenkins (Docker Desktop)

```powershell
cd C:\Auto\selenium-pytest
docker compose -f jenkins/docker-compose.yml up -d --build
```

The first build of the image takes a few minutes. Then:

1. Open http://localhost:8080 and log in as **admin / admin** (this login is set in `jenkins/docker-compose.yml`; local use only).
2. Open the job **selenium-pytest-local** (created by Configuration-as-Code), click **Build with Parameters** and choose a marker or leave it empty.
3. When the build finishes, click **Allure Report** on the build page.

How it works:

- The project folder is mounted read-only at `/project`. Each build copies it into the job workspace, so you don't need Git or a commit. Your edits are picked up on the next build.
- The image contains Python, Debian Chromium with chromedriver, and the Allure CLI in `/opt/allure`. `conftest.py` picks up the browser and driver through the `CHROME_BIN` and `CHROMEDRIVER_PATH` environment variables.
- `jenkins/init.groovy.d/allure-tool.groovy` registers the CLI as the Jenkins tool `allure`. If the report step fails with a message about a missing Allure commandline, add the tool by hand:
  - Go to **Manage Jenkins → Tools → Allure Commandline → Add**.
  - Set Name to `allure`, untick "Install automatically", and set the directory to `/opt/allure`.

Stop Jenkins with `docker compose -f jenkins/docker-compose.yml down`. Add `-v` to also delete the Jenkins data volume.

> If you edit `scripts/run_tests.sh` on Windows, keep **LF** line endings. With CRLF endings, bash in the container fails with `$'\r': command not found`. `.gitattributes` enforces LF for files checked out from Git.

Instead of the local job, you can create a *Pipeline from SCM* job that checks out this repository and uses the root `Jenkinsfile`.

## 3. GitHub Actions

| Workflow | Trigger | What it does |
|---|---|---|
| `lint.yml` | push to `main`, PRs | `ruff check` and `ruff format --check` |
| `ui-tests.yml` | push to `main`, PRs, weekdays 05:00 UTC, manual (optional marker input) | Headless tests on Chrome and Firefox in parallel. It uploads the `allure-results-*` artifacts and builds one Allure report per browser (`allure-report` artifact). On `main` it publishes the report to GitHub Pages. |

To publish to Pages, go to **Settings → Pages → Build and deployment → Source** and select **GitHub Actions**. Until you do that, the `deploy-pages` job fails, but the tests and the report artifact are unaffected.

## Configuration

| Option | Env variable | Default |
|---|---|---|
| `--browser chrome\|firefox` | `BROWSER` | `chrome` |
| `--headless` | `HEADLESS=1` | off |
| `--app-url URL` | `APP_URL` | `https://www.saucedemo.com` |
| `--remote-url URL` | `SELENIUM_REMOTE_URL` | empty (local browser) |

`--remote-url` switches to `webdriver.Remote`. That is the hook for a Selenium Grid or a cloud provider such as BrowserStack. BrowserStack also needs provider-specific capabilities (`bstack:options`) and credentials. Check BrowserStack's current Selenium/Python documentation before adding them.

## Adding a test

1. Write the scenario in a `.feature` file under `features/`.
2. Add any missing locators and actions to a page object in `pages/`. Keep assertions out of page objects.
3. Implement the steps in `tests/step_defs/`. Put steps used by several features in `tests/step_defs/conftest.py`. New modules need `scenarios("<file>.feature")`.
4. Tag scenarios (`@smoke`, ...) and register any new tag under `markers` in `pytest.ini`, because `--strict-markers` is on.

## Dependency updates

Dependabot (`.github/dependabot.yml`) checks weekly for new versions of the Python packages and GitHub Actions and opens pull requests for them; each PR runs the lint and UI test workflows. The Jenkins base image is covered too once its tag in `jenkins/Dockerfile` is pinned to a version. Update `jenkins/plugins.txt` and `ALLURE_VERSION` (in `jenkins/Dockerfile` and `ui-tests.yml`) by hand.

## License

[MIT](LICENSE)
