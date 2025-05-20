import nox


PYTHON_VERSIONS = [(3, 8), (3, 9), (3, 10), (3, 11)]
SQLALCHEMY_VERSIONS = ["1.0", "1.1", "1.2", "1.3"]
nox.options.default_venv_backend = "uv|venv"


@nox.session()
def lint(session):
    session.install("flake8")
    # stop the linter if there are Python syntax errors or undefined names
    session.run("flake8", ".", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics")
    # exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
    session.run("flake8", ".", "--count", "--exit-zero", "--max-complexity=10", "--max-line-length=127", "--statistics")


@nox.session()
@nox.parametrize("python,sqlalchemy",
                 [(f"{interpreter}{python_major}.{python_minor}", sqlalchemy_version)
                  for interpreter in ("", "pypy-")
                  for (python_major, python_minor) in PYTHON_VERSIONS
                  for sqlalchemy_version in SQLALCHEMY_VERSIONS
                  if sqlalchemy_version >= "1.2" or (python_major, python_minor) <= (3, 9)])
def test(session, sqlalchemy):
    session.install("-r", "requirements-test.txt")
    session.install(f"sqlalchemy~={sqlalchemy}.0")
    if "--coverage" in session.posargs:
        session.run("coverage", "run", "--source=sqlalchemy_mptt", "-m", "pytest", "sqlalchemy_mptt/")
        session.run("coverage", "xml")
    else:
        session.run("pytest", "sqlalchemy_mptt/")
