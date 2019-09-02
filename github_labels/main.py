# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Alex Turbov <i.zaufi@gmail.com>
#

# Project specific imports
from .cli import cli

# Standard imports
import click
import sys


def main():
    try:
        cli.main(sys.argv[1:], standalone_mode=False)

    except (click.exceptions.MissingParameter, click.exceptions.UsageError) as ex:
        click.secho('CLI Error: {}'.format(ex.format_message()), fg='red', err=True)

    except (RuntimeError) as ex:
        click.secho('Error: {}'.format(ex.format_message()), fg='red', err=True)
