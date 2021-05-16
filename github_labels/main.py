# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2021 Alex Turbov <i.zaufi@gmail.com>
#

# Third party packages
import click
import exitstatus

# Local imports
from .cli import cli


def main():
    try:
        return cli()

    except (RuntimeError) as ex:
        click.secho(f'Error: {ex!s}', fg='red', err=True)

    return exitstatus.ExitStatus.failure
