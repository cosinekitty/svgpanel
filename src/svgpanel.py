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
        self._parse(self.xml.getroot())

    def render(self, text: str) -> PathList:
        return PathList()

    def _parse(self, elem: et.Element) -> None:
        # Search recursively for all <g> elements that have aria-label attributes.
        # The aria-label gives the list of characters that appears as paths.
        if (elem.tag == '{http://www.w3.org/2000/svg}g') and (charlist := elem.attrib.get('aria-label')):
            # Stop recursing and capture child elements
            pathlist = [child for child in elem if child.tag == '{http://www.w3.org/2000/svg}path']
            if len(pathlist) != len(charlist):
                raise Exception('aria-label contains {} characters [{}], but there are {} child paths.'.format(len(charlist), charlist, len(pathlist)))
        else:
            # Keep searching recursively
            for child in elem:
                self._parse(child)


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

