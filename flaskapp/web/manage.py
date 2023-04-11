# SPDX-License-Identifier: GPL-3.0-or-later
import click
from flask.cli import FlaskGroup

from iib.web.app import create_app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli() -> None:
    """Manage the IIB Flask application."""


if __name__ == "__main__":
    cli()
