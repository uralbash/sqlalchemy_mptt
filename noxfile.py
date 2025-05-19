import nox


PYTHON_VERSIONS = ["3.7", "3.8", "3.9"]
# uv pip still works with Python 3.7
nox.options.default_venv_backend = "uv"


# Fails for pypy-3.7. See: https://github.com/astral-sh/uv/issues/9490
@nox.session(python=[python_version for python_version in PYTHON_VERSIONS] +
             [f"pypy-{python_version}" for python_version in PYTHON_VERSIONS])
@nox.parametrize("sqlalchemy", [0, 1, 2, 3])
def test(session, sqlalchemy):
    session.install("pip==24.0")
    session.install("-r", "requirements-test.txt")
    session.install(f"sqlalchemy~=1.{sqlalchemy}.0")
    session.run("pytest", "sqlalchemy_mptt/")
