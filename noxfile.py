from __future__ import annotations

import nox

nox.options.sessions = ["lint", "typecheck", "tests"]


@nox.session()
def lint(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")


@nox.session()
def typecheck(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("mypy", ".")


@nox.session()
def tests(session: nox.Session) -> None:
    session.install(".[dev]")
    session.run("pytest")
