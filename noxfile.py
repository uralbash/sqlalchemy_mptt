import nox


PYTHON_VERSIONS = [(3, 8), (3, 9), (3, 10), (3, 11)]
SQLALCHEMY_VERSIONS = ["1.0", "1.1", "1.2", "1.3"]
nox.options.default_venv_backend = "uv"


@nox.session()
@nox.parametrize("python,sqlalchemy",
                 [(f"{interpreter}-{python_major}.{python_minor}", sqlalchemy_version)
                  for interpreter in ("cpython", "pypy")
                  for (python_major, python_minor) in PYTHON_VERSIONS
                  for sqlalchemy_version in SQLALCHEMY_VERSIONS
                  if sqlalchemy_version >= "1.2" or (python_major, python_minor) <= (3, 9)])
def test(session, sqlalchemy):
    session.install("pip==24.0")
    session.install("-r", "requirements-test.txt")
    session.install(f"sqlalchemy~={sqlalchemy}.0")
    session.run("pytest", "sqlalchemy_mptt/")
