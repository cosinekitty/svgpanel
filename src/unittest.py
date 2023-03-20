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


def FontTest() -> int:
    p = Panel(12)
    f = Font('../fonts/Quicksand-Light.ttf')
    p.addPath(f.render('quick brown fox', 3.0, 10.0, 10.0))
    p.addPath(f.render('STIF CURL MASS',  3.0, 20.0, 10.0))
    text = p.svg()
    with open('output/font01.svg', 'wt') as outfile:
        outfile.write(text)
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
