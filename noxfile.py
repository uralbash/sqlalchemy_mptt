# -*- coding: utf-8 -*-
#
# Copyright (c) 2025 Fayaz Yusuf Khan <fayaz.yusuf.khan@gmail.com>
#
# Distributed under terms of the MIT license.
#
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "nox",
#     "nox-uv",
#     "requests",
# ]
# ///
""" Entry point script for testing, linting, and development of the package.

    This project uses Nox to create isolated environments.

    Requirements:
    - uv

    Usage:

      Run all tests and linting:
        $ uv run noxfile.py
      Run tests for a specific SQLAlchemy version:
        $ uv run noxfile.py -t sqla12
      Run tests for a specific Python version:
        $ uv run noxfile.py -s test -p 3.X

      Set up a development environment with the default Python version (3.8):
        $ uv run noxfile.py -s dev
      Set up a development environment with a specific Python version:
        $ uv run noxfile.py -s dev -P 3.X
"""
from itertools import groupby

import nox
from packaging.requirements import Requirement
from packaging.version import Version
import requests


# Python versions supported and tested against: 3.8, 3.9, 3.10, 3.11
PYTHON_MINOR_VERSION_MIN = 8
PYTHON_MINOR_VERSION_MAX = 11

nox.options.default_venv_backend = "uv"


@nox.session()
def lint(session):
    """Run flake8."""
    session.install("flake8")
    # stop the linter if there are Python syntax errors or undefined names
    session.run("flake8", "--select=E9,F63,F7,F82", "--show-source")
    # exit-zero treats all errors as warnings
    session.run("flake8", "--exit-zero", "--max-complexity=10")


def parametrize_test_versions():
    """Parametrize the session with all supported Python & SQLAlchemy versions."""
    response = requests.get("https://pypi.org/pypi/SQLAlchemy/json")
    response.raise_for_status()
    data = response.json()
    all_major_and_minor_sqlalchemy_versions = [
        Version(f"{major}.{minor}")
        for (major, minor), _ in groupby(
            sorted(Version(version) for version in data["releases"].keys()),
            key=lambda v: (v.major, v.minor)
        )
    ]

    with open("requirements.txt", "r") as f:
        requirement = Requirement(f.read().strip())
    filtered_sqlalchemy_versions = [
        version for version in all_major_and_minor_sqlalchemy_versions
        if version in requirement.specifier
    ]

    return [
        nox.param(
            f"3.{python_minor}", str(sqlalchemy_version),
            tags=[f"sqla{sqlalchemy_version.major}{sqlalchemy_version.minor}"]
        )
        for python_minor in range(PYTHON_MINOR_VERSION_MIN, PYTHON_MINOR_VERSION_MAX + 1)
        for sqlalchemy_version in filtered_sqlalchemy_versions
        # SQLA 1.1 or below doesn't seem to support Python 3.10+
        if sqlalchemy_version >= Version("1.2") or python_minor <= 9]


@nox.session()
@nox.parametrize("python,sqlalchemy", parametrize_test_versions())
def test(session, sqlalchemy):
    """Run tests with pytest.

    You can pass arguments to pytest using the `--` option.

        $ uv run noxfile.py -s test -- sqlalchemy_mptt/tests/test_events.py

    If no arguments are provided, it defaults to running all tests in the package.

    For running tests for a specific SQLAlchemy version, use the tags option:

        $ uv run noxfile.py -s test -t sqla12

    For fine-grained control over running the tests, refer the nox documentation: https://nox.thea.codes/en/stable/usage.html
    """
    session.install("-r", "requirements-test.txt")
    session.install(f"sqlalchemy~={sqlalchemy}.0")
    session.install("-e", ".")
    pytest_args = session.posargs or ["--pyargs", "sqlalchemy_mptt"]
    session.run("pytest", *pytest_args)


@nox.session(default=False)
def dev(session):
    """Set up a development environment.
    This will create a virtual environment and install the package in editable mode in .venv.

    To use a specific Python version, use the -P option:
    $ uv run noxfile.py -s dev -P 3.X
    """
    session.run("uv", "venv", "--python", session.python or f"3.{PYTHON_MINOR_VERSION_MIN}", "--seed")
    session.run(".venv/bin/pip", "install", "-r", "requirements-test.txt", external=True)
    session.run(".venv/bin/pip", "install", "-e", ".", external=True)


@nox.session(default=False)
def build(session):
    """Build the package."""
    session.install("build")
    session.run("python", "-m", "build")


if __name__ == "__main__":
    nox.main()
