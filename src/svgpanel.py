#!/usr/bin/env python3
"""Classes for generating VCV Rack panel designs.
"""

import xml.etree.ElementTree as et


class Error(Exception):
    """Indicates an error in an svgpanel function."""
    def __init__(self, message: str) -> None:
        Exception.__init__(self, message)


class PathList:
    def __init__(self) -> None:
        pass

    def svg(self, xmm: float, ymm: float) -> str:
        return ''


class Font:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.xml = et.parse(filename)

    def render(self, text: str) -> PathList:
        return PathList()


class Panel:
    def __init__(self, hpWidth: int) -> None:
        if hpWidth <= 0:
            raise Error('Invalid hpWidth={}'.format(hpWidth))
        self.mmWidth = 5.08 * hpWidth
        self.mmHeight = 128.5

    def svg(self) -> str:
        '''Generate the SVG for the panel design.'''
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        text += '<svg xmlns="http://www.w3.org/2000/svg" width="{0:0.2f}mm" height="{1:0.2f}mm" viewBox="0 0 {0:0.2f} {1:0.2f}">\n'.format(self.mmWidth, self.mmHeight)
        text += '</svg>\n'
        return text

