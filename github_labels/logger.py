# -*- coding: utf-8 -*-
#
# Copyright (c) 2019-2021 Alex Turbov <i.zaufi@gmail.com>
#

# Project specific imports

# Standard imports
import logging


def setup_logger(verbose: bool) -> logging.Logger:
    # Create logger
    logger = logging.getLogger('github-labels')

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Create console handler and set level to debug
    handler = logging.StreamHandler()                       # NOTE Write everything to `stderr`!
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(name)s[%(levelname)s]: %(message)s')
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
