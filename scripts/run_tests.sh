#!/usr/bin/env bash
# Creates/updates a virtualenv and runs the suite headless, writing Allure results.
# Used by Jenkins (inside the container). Extra arguments are passed through to pytest,
# e.g.  bash scripts/run_tests.sh -m smoke
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

rm -rf allure-results
pytest --headless --alluredir=allure-results "$@"
