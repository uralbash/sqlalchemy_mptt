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
# ]
# ///
""" Entry point script for testing, linting, and development of the package.

    This project uses Nox to create isolated environments.

    Requirements:
    - uv

    Usage:

      Run all tests and linting:
        $ uv run noxfile.py
      Run all tests with coverage and linting:
        $ uv run noxfile.py -- --coverage

      Set up a development environment with the default Python version (3.8):
        $ uv run noxfile.py -s dev
      Set up a development environment with a specific Python version:
        $ uv run noxfile.py -s dev -P 3.X
        $ uv run noxfile.py -s dev -P pypy-3.X    # For PyPy
"""
import nox


# Python versions supported and tested against: 3.8, 3.9, 3.10, 3.11
PYTHON_MINOR_VERSION_MIN = 8
PYTHON_MINOR_VERSION_MAX = 11
# SQLAlchemy versions supported and tested against: 1.0, 1.1, 1.2, 1.3
SQLALCHEMY_VERSIONS = ["1.0", "1.1", "1.2", "1.3"]

nox.options.default_venv_backend = "uv"


@nox.session()
def lint(session):
    """Run flake8."""
    session.install("flake8")
    # stop the linter if there are Python syntax errors or undefined names
    session.run(
        "flake8", ".", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics", "--extend-exclude", ".venv")
    # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
    session.run(
        "flake8", ".", "--count", "--exit-zero", "--max-complexity=10",
        "--max-line-length=127", "--statistics", "--extend-exclude", ".venv")


@nox.session()
@nox.parametrize("python,sqlalchemy",
                 [(f"{interpreter}3.{python_minor}", sqlalchemy_version)
                  for interpreter in ("", "pypy-")
                  for python_minor in range(PYTHON_MINOR_VERSION_MIN, PYTHON_MINOR_VERSION_MAX + 1)
                  for sqlalchemy_version in SQLALCHEMY_VERSIONS
                  # SQLA 1.1 or below doesn't seem to support Python 3.10+
                  if sqlalchemy_version >= "1.2" or python_minor <= 9])
def test(session, sqlalchemy):
    """Run tests with pytest.

    Use the --coverage option to run tests with coverage.
    For fine-grained control over running the tests, refer the nox documentation: https://nox.thea.codes/en/stable/usage.html
    """
    session.install("-r", "requirements-test.txt")
    session.install(f"sqlalchemy~={sqlalchemy}.0")
    if "--coverage" in session.posargs:
        session.run("coverage", "run", "--source=sqlalchemy_mptt", "-m", "pytest", "sqlalchemy_mptt/")
        session.run("coverage", "xml")
    else:
        session.run("pytest", "sqlalchemy_mptt/")


@nox.session(default=False)
def dev(session):
    """Set up a development environment.
    This will create a virtual environment and install the package in editable mode in .venv.

    To use a specific Python version, use the -P option:
    $ uv run noxfile.py -s dev -P 3.X
    $ uv run noxfile.py -s dev -P pypy-3.X    # For PyPy
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
