import os
import tempfile
from typing import Any

import nox
import nox_poetry
from nox import Session

places = ["src", "tests", "noxfile.py"]

nox.options.stop_on_first_error = True

nox.options.sessions = ["black", "isort", "lint", "mypy", "tests", "audit"]


def install_poetry_group(session: Session, poetry_group="", *args: str, **kwargs: Any) -> None:
    req_path = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    session.run(
        "poetry",
        "export",
        f"--with={poetry_group}",
        "--format=requirements.txt",
        f"--output={req_path}",
        external=True,
    )
    session.install("-r", req_path, "--no-deps", *args, **kwargs)
    os.unlink(req_path)


@nox_poetry.session
def black(session):
    session.install("black")
    args = ["black"]
    if "check" in session.posargs:
        args.append("--check")
        args.append("--diff")
    args.extend(places)
    session.run(*args)


@nox_poetry.session
def isort(session):
    session.install("isort")
    args = ["isort"]
    if "check" in session.posargs:
        args.append("--check")
    args.extend(places)
    session.run(*args)


@nox_poetry.session
def lint(session):
    session.install("flake8")
    args = ["flake8"]
    args.extend(places)
    session.run(*args)


@nox_poetry.session
def mypy(session):
    install_poetry_group(session, "test")
    args = ["mypy"]
    args.extend(places)
    session.run(*args)


@nox_poetry.session
def tests(session):
    install_poetry_group(session, "test")
    sqlite_env = {"DATABASE__ENGINE": "sqlite"}
    session.run("pytest", "tests/unit", env=sqlite_env)
    session.run("pytest", "tests/component", env=sqlite_env)
    session.run("pytest", "tests/integration", env=sqlite_env)


@nox_poetry.session
def audit(session):
    install_poetry_group(session, "audit")
    session.run("pip-audit")
