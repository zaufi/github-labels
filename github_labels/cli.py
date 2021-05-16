# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2021 Alex Turbov <i.zaufi@gmail.com>
#

# Standard imports
import collections
import functools
import pathlib

# Third party packages
import click
import exitstatus
import github
import ycfg.collections
import ycfg.config_file

# Local imports
from .term import color_text, fore_print, hex_to_rgb


def _select_fg_color(bg_color: str):
    rgb = hex_to_rgb(bg_color)
    return '#000000' if functools.reduce(lambda s, x: s + int(x > 128), rgb, 0) >= 2 else '#ffffff'


class _DummyRepo:

    def __init__(self, name):
        self.name = name

    def get_labels(self):
        return []


class _DummySession:

    def get_repo(self, name):
        return _DummyRepo(name)


@click.command()
@click.help_option(
    '--help'
  , '-h'
  )
@click.version_option(
    package_name='github_labels'
  )
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
        desired_label_names = {label['name']: ycfg.config_file.items_as_attributes(label) for label in cfg.labels}
        for label in labels:
            color_str = color_text(label.name, _select_fg_color('#' + label.color), '#' + label.color)
            print(f'  [{label.color}] {color_str}: {label.description}')
            if label.name in desired_label_names \
              and desired_label_names[label.name].description == label.description \
              and desired_label_names[label.name].color == label.color:
                if verbose:
                    fore_print(f'  Keeping the label `{color_str}`', '#888888')
                del desired_label_names[label.name]
            else:
                if verbose:
                    fore_print(f'  Deleting the label `{color_str}`', '#888888')
                if not dry_run:
                    label.delete()

        if desired_label_names:
            if only_show_labels:
                click.echo(f'Configured labels from `{input_file}`')
            else:
                click.echo(f'Updating labels of {repo.name}')

            for lbl in desired_label_names.values():
                label = ycfg.config_file.items_as_attributes(lbl)
                color_str = color_text(lbl.name, _select_fg_color('#' + lbl.color), '#' + lbl.color)
                print(f'  [{lbl.color}] {color_str}: {lbl.description}')
                if not dry_run:
                    repo.create_label(label.name, label.color, description=label.description)

    return exitstatus.ExitStatus.success
