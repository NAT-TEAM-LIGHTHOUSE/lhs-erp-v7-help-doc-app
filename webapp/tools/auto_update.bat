@echo off
rem Watches the V7 documentation folder and updates menu + Reader view automatically.
rem Leave this window open (minimise it). To start with Windows: put a shortcut to this file in
rem   shell:startup
rem Other source folder:  auto_update.bat "D:\path\to\V7_MENU_HELP_DOC"
title Lighthouse Help Centre - auto update
cd /d "%~dp0.."
python tools\auto_update.py %*
pause
