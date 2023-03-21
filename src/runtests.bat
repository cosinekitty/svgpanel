@echo off
setlocal EnableDelayedExpansion

echo.Type-checking svgpanel.py
mypy --strict --module svgpanel || exit /b 1

echo.Type-checking unittest.py
mypy --strict unittest.py || exit /b 1

if exist output/*.svg (
    del output/*.svg
)

py unittest.py all || exit /b 1

for %%n in (empty font01) do (
    echo.runtests.bat: checking %%n.svg
    fc correct\%%n.svg output\%%n.svg || exit /b 1
)

type pass.txt
exit /b 0
