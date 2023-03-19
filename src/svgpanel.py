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

    def render(self, text: str, xpos: float, ypos: float, xscale: float, yscale: float) -> str:
        x = xpos
        y = ypos
        spen = SVGPathPen(self.glyphs)
        space = self.glyphs['r']
        xshift = 0.96 * xscale
        for ch in text:
            tran = DecomposedTransform(translateX = x, translateY = y, scaleX = xscale, scaleY = -yscale).toTransform()
            pen = TransformPen(spen, tran)
            glyph = self.glyphs.get(ch)
            if glyph:
                glyph.draw(pen)
                x += glyph.width * xshift
            else:
                x += space.width * xshift
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
        for pt in self.pathlist:
            text += '<path d="{}"/>\n'.format(pt)
        text += '</svg>\n'
        return text

