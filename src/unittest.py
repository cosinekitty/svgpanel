#!/usr/bin/env python3
import sys
from typing import Any, List, Tuple, Optional, Union, Callable, Dict
from svgpanel import *

Verbose = False

def Info(message: str) -> None:
    print('unittest.py | {}'.format(message))

def Debug(message: str) -> None:
    if Verbose:
        Info(message)

def Fail(message: str) -> int:
    Info('FAIL: {}'.format(message))
    return 1


def EmptyPanel() -> int:
    p = Panel(3)
    if p.mmWidth != 15.24:
        return Fail('Incorrect panel width = {} mm.'.format(p.mmWidth))
    text = p.svg()
    with open('output/empty.svg', 'wt') as outfile:
        outfile.write(text)
    return 0


def TextBoundingBox(t:TextItem, x:float, y:float) -> Element:
    (w, h) = t.measure()
    rect = Element('rect')
    rect.setAttribFloat('x', x)
    rect.setAttribFloat('y', y)
    rect.setAttribFloat('width', w)
    rect.setAttribFloat('height', h)
    rect.setAttrib('style', 'fill:none;stroke:blue;stroke-width:0.1')
    return rect

def FontTest() -> int:
    panel = Panel(12)
    group = Element('g').setAttrib('style', 'stroke:#000000;stroke-width:0.25;stroke-linecap:round;stroke-linejoin:bevel')
    with Font('../fonts/Quicksand-Light.ttf') as font:

        t1 = TextItem('quick brown fox', font, 10.0)
        (x1, y1) = (3.0, 10.0)
        group.append(TextPath(t1, x1, y1))
        group.append(TextBoundingBox(t1, x1, y1))

        t2 = TextItem('STIF CURL MASS', font, 10.0)
        (x2, y2) = (3.0, 20.0)
        group.append(TextPath(t2, x2, y2))
        group.append(TextBoundingBox(t2, x2, y2))

    panel.append(group)
    with open('output/font01.svg', 'wt') as outfile:
        outfile.write(panel.svg())
    return 0


UnitTests: Dict[str, Callable[[], int]] = {
    'empty_panel' : EmptyPanel,
    'font': FontTest,
}


def RunTest(args: List[str]) -> int:
    if len(args) > 0:
        if args[0] == '-v':
            global Verbose
            Verbose = True
            args = args[1:]
    if len(args) == 1:
        name = args[0]
        if name == 'all':
            for (name, func) in UnitTests.items():
                if func() == 0:
                    Info('PASS: {}'.format(name))
                else:
                    Info('FAIL: {}'.format(name))
                    return 1
            Info('SUCCESS')
            return 0
        checkfunc = UnitTests.get(name)
        if not checkfunc:
            Info('ERROR: unknown test name [{}]'.format(name))
            return 1
        if checkfunc() == 0:
            Info('PASS: {}'.format(name))
            return 0
        else:
            Info('FAIL: {}'.format(name))
            return 1
    print('unittest.py : ERROR: invalid command line.')
    return 1


if __name__ == '__main__':
    sys.exit(RunTest(sys.argv[1:]))
