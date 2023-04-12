@echo off
color 02
set /p py_location=".py script full path: "
set /p icon_location=".ico file full path: "

nuitka --windows-icon-from-ico=%icon_location% %py_location%

pause