#!/usr/bin/env python3
"""Classes for generating VCV Rack panel designs.
"""

class Error(Exception):
    """Indicates an error in an svgpanel function."""
    def __init__(self, message: str) -> None:
        Exception.__init__(self, message)


class Panel:
    def __init__(self, hpWidth: int) -> None:
        if hpWidth <= 0:
            raise Error('Invalid hpWidth={}'.format(hpWidth))
        self.mmWidth = 5.08 * hpWidth
        self.mmHeight = 128.5
