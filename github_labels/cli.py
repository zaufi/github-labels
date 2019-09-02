# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Alex Turbov <i.zaufi@gmail.com>
#

# Project specific imports
from .logger import setup_logger
from .version import __version__
from .term import color_print, color_text, fore_print, hex_to_rgb

# Standard imports
import click
import click_plugins
import collections
import functools
import pathlib
import ycfg.collections
import ycfg.config_file
import yaml
import github


def _select_fg_color(bg_color: str):
    rgb = hex_to_rgb(bg_color)
    return '#000000' if functools.reduce(lambda s,x: s + int(x > 128) , rgb, 0) >= 2 else '#ffffff'


class _DummyRepo:

    def __init__(self, name):
        self.name = name

    def get_labels(self):
        return []


class _DummySession:

    def get_repo(self, name):
        return _DummyRepo(name)


_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(context_settings=_CONTEXT_SETTINGS)
@click.option(
    '--config'
  , default=click.get_app_dir('') + 'github-labels.conf'
  , show_default=True
  , metavar='FILE'
  , help='File name of the user config.'
  )
@click.option(
    '--dry-run'
  , '-r'
  , default=False
  , is_flag=True
  , help='Do not perform real actions.'
  )
@click.option(
    '--verbose'
  , '-v'
  , default=False
  , is_flag=True
  , help='Be a little bit verbose.'
  )
@click.option(
    '--only-show-labels'
  , '-s'
  , default=False
  , is_flag=True
  , help='Only show configured labels. Do not do any network operations.'
  )
@click.argument('input-file')
def cli(config, input_file, dry_run, verbose, only_show_labels):
    """ Mass-setting labels to Github repositories """

    if only_show_labels:
        dry_run = True

    config_file = pathlib.Path(config)
    data = collections.OrderedDict()

    if config_file.exists():
        data = ycfg.config_file.config(config_file)

    input_file = pathlib.Path(input_file)
    input_data = ycfg.config_file.config(input_file)

    data.update(input_data)
    cfg = ycfg.collections.folded_keys_dict(
        data
      , node_factory=ycfg.collections.ordered_dict_node_factory()
      )

    session = _DummySession()
    if not only_show_labels:
        session = github.Github(cfg.credentials.user, cfg.credentials.password)

    for name in cfg.repositories:
        repo = session.get_repo(name)

        if not only_show_labels:
            click.echo(f'Current labels of {repo.name}')

        labels = repo.get_labels()
        desired_label_names = {l['name']: ycfg.config_file.items_as_attributes(l) for l in cfg.labels}
        for l in labels:
            color_str = color_text(l.name, _select_fg_color('#' + l.color), '#' + l.color)
            print(f'  [{l.color}] {color_str}: {l.description}')
            if l.name in desired_label_names \
              and desired_label_names[l.name].description == l.description \
              and desired_label_names[l.name].color == l.color:
                if verbose:
                    fore_print(f'  Keeping the label `{color_str}`', '#888888')
                del desired_label_names[l.name]
            else:
                if verbose:
                    fore_print(f'  Deleting the label `{color_str}`', '#888888')
                if not dry_run:
                    l.delete()

        if desired_label_names:
            if only_show_labels:
                click.echo(f'Configured labels from `{input_file}`')
            else:
                click.echo(f'Updating labels of {repo.name}')

            for l in desired_label_names.values():
                label = ycfg.config_file.items_as_attributes(l)
                color_str = color_text(l.name, _select_fg_color('#' + l.color), '#' + l.color)
                print(f'  [{l.color}] {color_str}: {l.description}')
                if not dry_run:
                    repo.create_label(label.name, label.color, description=label.description)
