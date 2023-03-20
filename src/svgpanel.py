#!/usr/bin/env python3
"""Classes for generating VCV Rack panel designs.

For more information, see:
https://github.com/cosinekitty/svgpanel
"""
from typing import Any, List, Tuple, Optional, Union, Callable, Dict
from fontTools.ttLib import TTFont                          # type: ignore
from fontTools.pens.svgPathPen import SVGPathPen            # type: ignore
from fontTools.pens.transformPen import TransformPen        # type: ignore
from fontTools.misc.transform import DecomposedTransform    # type: ignore

class Error(Exception):
    """Indicates an error in an svgpanel function."""
    def __init__(self, message: str) -> None:
        Exception.__init__(self, message)


class Font:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.ttfont = TTFont(filename)
        self.glyphs = self.ttfont.getGlyphSet()

    def render(self, text: str, xpos: float, ypos: float, points: float) -> str:
        # Calculate how many millimeters there are per font unit in this point size.
        mmPerEm = (25.4 / 72)*points
        mmPerUnit = mmPerEm / self.ttfont['head'].unitsPerEm
        x = xpos
        y = ypos
        spen = SVGPathPen(self.glyphs)
        for ch in text:
            if glyph := self.glyphs.get(ch):
                tran = DecomposedTransform(translateX = x, translateY = y, scaleX = mmPerUnit, scaleY = -mmPerUnit).toTransform()
                pen = TransformPen(spen, tran)
                glyph.draw(pen)
                x += mmPerUnit * glyph.width
            else:
                # Use a "3-em space", which confusingly is one-third of an em wide.
                x += mmPerEm / 3
        return str(spen.getCommands())


class Panel:
    def __init__(self, hpWidth: int) -> None:
        if hpWidth <= 0:
            raise Error('Invalid hpWidth={}'.format(hpWidth))
        self.mmWidth = 5.08 * hpWidth
        self.mmHeight = 128.5
        self.pathlist: List[str] = []

    def addPath(self, pathText:str) -> None:
        self.pathlist.append(pathText)

    def svg(self) -> str:
        '''Generate the SVG for the panel design.'''
        text = '<?xml version="1.0" encoding="utf-8"?>\n'
        text += '<svg xmlns="http://www.w3.org/2000/svg" width="{0:0.2f}mm" height="{1:0.2f}mm" viewBox="0 0 {0:0.2f} {1:0.2f}">\n'.format(self.mmWidth, self.mmHeight)
        if len(self.pathlist) > 0:
            text += '<g style="stroke:#000000;stroke-width:0.25;stroke-linecap:round;stroke-linejoin:bevel">\n'
            for pt in self.pathlist:
                text += '<path d="{}"/>\n'.format(pt)
            text += '</g>\n'
        text += '</svg>\n'
        return text

