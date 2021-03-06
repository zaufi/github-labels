# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Alex Turbov <i.zaufi@gmail.com>
#

# Project specific imports

# Standard imports


# NOTE This code is from `truecolor` Python package
# ATTENTION The original code (1.0b2) is buggy and won't work for me
#
#    In [6]: truecolor.fore_print('Test', '#aabbcc')
#    Test
#
#    In [7]: truecolor.color_print('Test', '#aabbcc', '#ff00bb')
#    ;a;am;f;fmTest
#
# That is why I took it and hack...
# https://github.com/simplegadget512/Truecolor/issues/2
#

_Z_FORE = 38
_Z_BACK = 48


def _e(red_component, green_component, blue_component, z_level=_Z_FORE):
    """Return escaped color sequence"""
    return '\x1b[{};2;{};{};{}m'.format(
        z_level, red_component, green_component, blue_component)


def _f(red_component, green_component, blue_component):
    """Return escaped foreground color sequence"""
    return _e(red_component, green_component, blue_component, _Z_FORE)


def _b(red_component, green_component, blue_component):
    """Return escaped background color sequence"""
    return _e(red_component, green_component, blue_component, _Z_BACK)


def _r():
    """Return reset sequence"""
    return '\x1b[0m'


def _gamut(component):
    """keeps color components in the proper range"""
    return min(max(int(component), 0), 254)


def hex_to_rgb(hex_string):
    """Return a tuple of red, green and blue components for the color
    given as #rrggbb.
    """
    return tuple(int(hex_string[i:i + 2], 16) for i in range(1, len(hex_string), 2))


def rgb_to_hex(red_component=None, green_component=None, blue_component=None):
    """Return color as #rrggbb for the given color tuple or component
    values. Can be called as

    TUPLE VERSION:
        rgb_to_hex(COLORS['white']) or rgb_to_hex((128, 63, 96))

    COMPONENT VERSION
        rgb_to_hex(64, 183, 22)

    """
    if isinstance(red_component, tuple):
        red_component, green_component, blue_component = red_component
    return '#{:02X}{:02X}{:02X}'.format(
        red_component, green_component, blue_component)


def fore_text(txt, foreground):
    """Return text string with foreground only set."""
    if isinstance(foreground, str) and foreground.startswith('#'):
        foreground = hex_to_rgb(foreground)
    return '{}{}{}'.format(_f(*foreground), txt, _r())


def color_text(txt, foreground, background):
    """Return text string with foreground and background set."""
    if isinstance(foreground, str) and foreground.startswith('#'):
        foreground = hex_to_rgb(foreground)
    if isinstance(background, str) and background.startswith('#'):
        background = hex_to_rgb(background)
    return '{}{}{}{}'.format(_f(*foreground), _b(*background), txt, _r())


def fore_print(txt, foreground):
    """Print text string with foreground only set."""
    print(fore_text(txt, foreground))


def color_print(txt, foreground, background):
    """Print text string with foreground and background set."""
    print(color_text(txt, foreground, background))
