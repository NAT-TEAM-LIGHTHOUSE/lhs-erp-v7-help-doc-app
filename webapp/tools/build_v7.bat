@echo off
rem Rebuilds docs\ and menu\v7-menu.json from the V7 documentation folder.
rem Usage: build_v7.bat            (uses the default source folder)
rem        build_v7.bat "D:\path\to\V7_MENU_HELP_DOC"
python "%~dp0build_v7.py" %*
pause
