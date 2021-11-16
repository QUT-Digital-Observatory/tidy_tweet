import nox


@nox.session
def tests(session):
    session.install("pytest")
    session.install(".")
    session.run("pytest")


@nox.session
def lint(session):
    session.install("flake8", "black")
    session.run("flake8")
    session.run("black", "--check", ".")
