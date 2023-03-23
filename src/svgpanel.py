#!/usr/bin/env python3
"""Classes for generating VCV Rack panel designs.

For more information, see:
https://github.com/cosinekitty/svgpanel
"""
from typing import Any, List, Tuple, Optional, Union, Callable, Dict
from enum import Enum, unique
import xml.etree.ElementTree as et
from fontTools.ttLib import TTFont                          # type: ignore
from fontTools.pens.svgPathPen import SVGPathPen            # type: ignore
from fontTools.pens.transformPen import TransformPen        # type: ignore
from fontTools.misc.transform import DecomposedTransform    # type: ignore

# Prevent seeing lots of "ns0:" everywhere when we re-serialized the XML.
et.register_namespace('', 'http://www.w3.org/2000/svg')


class Error(Exception):
    """Indicates an error in an svgpanel function."""
    def __init__(self, message:str) -> None:
        Exception.__init__(self, message)


@unique
class HorizontalAlignment(Enum):
    Left = 0
    Center = 1
    Right = 2


@unique
class VerticalAlignment(Enum):
    Top = 0
    Middle = 1
    Bottom = 2


def Move(x:float, y:float) -> str:
    return 'M {:0.2f},{:0.2f} '.format(x, y)


def Line(x:float, y:float) -> str:
    return 'L {:0.2f},{:0.2f} '.format(x, y)


def _FormatMillimeters(x: float) -> str:
    return '{:0.6g}'.format(x)


class Font:
    def __init__(self, filename:str) -> None:
        self.filename = filename
        self.ttfont = TTFont(filename)
        self.glyphs = self.ttfont.getGlyphSet()

    def __enter__(self) -> 'Font':
        self.ttfont.__enter__()
        return self

    def __exit__(self, exc_type:Any, exc_val:Any, exc_tb:Any) -> Any:
        return self.ttfont.__exit__(exc_type, exc_val, exc_tb)

    def render(self, text:str, xpos:float, ypos:float, points:float) -> str:
        # Calculate how many millimeters there are per font unit in this point size.
        mmPerEm = (25.4 / 72)*points
        mmPerUnit = mmPerEm / self.ttfont['head'].unitsPerEm
        x = xpos
        y = ypos + mmPerUnit * (self.ttfont['head'].yMax + self.ttfont['head'].yMin/2)
        spen = SVGPathPen(self.glyphs, _FormatMillimeters)
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

    def measure(self, text:str, points:float) -> Tuple[float,float]:
        mmPerEm = (25.4 / 72)*points
        mmPerUnit = mmPerEm / self.ttfont['head'].unitsPerEm
        x = 0.0
        y = mmPerUnit * (self.ttfont['head'].yMax - self.ttfont['head'].yMin)
        for ch in text:
            if glyph := self.glyphs.get(ch):
                x += mmPerUnit * glyph.width
            else:
                # Use a "3-em space", which confusingly is one-third of an em wide.
                x += mmPerEm / 3
        return (x, y)


class TextItem:
    def __init__(self, text:str, font:Font, points:float):
        self.text = text
        self.font = font
        self.points = points

    def render(self, x:float, y:float) -> str:
        return self.font.render(self.text, x, y, self.points)

    def measure(self) -> Tuple[float,float]:
        return self.font.measure(self.text, self.points)

    def toPath(
            self,
            xpos: float,
            ypos: float,
            horizontal: HorizontalAlignment,
            vertical: VerticalAlignment,
            style: str = '',
            id: str = '') -> 'TextPath':

        (dx, dy) = self.measure()

        if horizontal == HorizontalAlignment.Left:
            x = xpos
        elif horizontal == HorizontalAlignment.Right:
            x = xpos - dx
        elif horizontal == HorizontalAlignment.Center:
            x = xpos - (dx/2)
        else:
            raise Error('Invalid horizontal alignment: {}'.format(horizontal))

        if vertical == VerticalAlignment.Top:
            y = ypos
        elif vertical == VerticalAlignment.Bottom:
            y = ypos - dy
        elif vertical == VerticalAlignment.Middle:
            y = ypos - (dy/2)
        else:
            raise Error('Invalid vertical alignment: {}'.format(vertical))

        tp = TextPath(self, x, y, id)
        tp.setAttrib('style', style)
        return tp


class Element:
    def __init__(self, tag:str, id:str = '') -> None:
        self.tag = tag
        self.attrib: Dict[str, str] = {}
        self.children: List[Element] = []
        self.setAttrib('id', id)

    def setAttrib(self, key:str, value:str) -> 'Element':
        if value:
            self.attrib[key] = value
        return self

    def setAttribFloat(self, key:str, value:float) -> 'Element':
        return self.setAttrib(key, '{:0.6g}'.format(value))

    def append(self, elem:'Element') -> 'Element':
        self.children.append(elem)
        return self

    def xml(self) -> et.Element:
        elem = et.Element(self.tag, self.attrib)
        for child in self.children:
            elem.append(child.xml())
        return elem


class TextPath(Element):
    def __init__(self, textItem:TextItem, x:float, y:float, id:str = '') -> None:
        super().__init__('path', id)
        self.setAttrib('d', textItem.render(x, y))


class BorderRect(Element):
    def __init__(self, hpWidth:int, fillColor:str, borderColor:str) -> None:
        super().__init__('rect', 'border_rect')
        if hpWidth <= 0:
            raise Error('Invalid hpWidth={}'.format(hpWidth))
        self.setAttribFloat('width', 5.08 * hpWidth)
        self.setAttribFloat('height', 128.5)
        self.setAttrib('x', '0')
        self.setAttrib('y', '0')
        self.setAttrib('style', 'display:inline;fill:{};fill-opacity:1;fill-rule:nonzero;stroke:{};stroke-width:0.7;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:none;stroke-opacity:1;image-rendering:auto'.format(fillColor, borderColor))


class LinearGradient(Element):
    def __init__(self, id:str, x1:float, y1:float, x2:float, y2:float, color1:str, color2:str) -> None:
        super().__init__('linearGradient', id)
        self.setAttribFloat('x1', x1)
        self.setAttribFloat('y1', y1)
        self.setAttribFloat('x2', x2)
        self.setAttribFloat('y2', y2)
        self.setAttrib('gradientUnits', 'userSpaceOnUse')
        self.append(Element('stop').setAttrib('offset', '0').setAttrib('style', 'stop-color:{};stop-opacity:1;'.format(color1)))
        self.append(Element('stop').setAttrib('offset', '1').setAttrib('style', 'stop-color:{};stop-opacity:1;'.format(color2)))


class Panel(Element):
    def __init__(self, hpWidth:int) -> None:
        super().__init__('svg')
        if hpWidth <= 0:
            raise Error('Invalid hpWidth={}'.format(hpWidth))
        self.mmWidth = 5.08 * hpWidth
        self.mmHeight = 128.5
        self.setAttrib('xmlns', 'http://www.w3.org/2000/svg')
        self.setAttrib('width', '{:0.2f}mm'.format(self.mmWidth))
        self.setAttrib('height', '{:0.2f}mm'.format(self.mmHeight))
        self.setAttrib('viewBox', '0 0 {:0.2f} {:0.2f}'.format(self.mmWidth, self.mmHeight))

    def svg(self, indent:str = '    ') -> str:
        root = self.xml()
        et.indent(root, indent)
        rootBytes = et.tostring(root, encoding='utf-8')
        # Just being picky, but I prefer generating my own <?xml ... ?> declaration,
        # just so I can use double-quotes for consistency.
        # See: https://bugs.python.org/issue36233
        return '<?xml version="1.0" encoding="utf-8"?>\n' + rootBytes.decode('utf8') + '\n'    # type: ignore

    def save(self, outFileName:str, indent:str = '    ') -> None:
        with open(outFileName, 'wt') as outfile:
            outfile.write(self.svg(indent))
