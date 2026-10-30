@echo off
rem One-click manual update: run this after pasting new / changed PDFs into the V7 documentation folder.
rem   1) rebuilds the menu and copies the PDFs to docs\     2) converts new / changed PDFs to Reader (HTML) view
rem First time only on this PC:  pip install pymupdf pillow
rem Other source folder:  update_now.bat "D:\path\to\V7_MENU_HELP_DOC"
title Lighthouse Help Centre - update now
cd /d "%~dp0.."
echo.
echo === Step 1 of 2: menu and PDFs ===
python tools\build_v7.py %*
if errorlevel 1 goto failed
echo.
echo === Step 2 of 2: Reader view (only new / changed PDFs) ===
python tools\build_html.py
if errorlevel 1 goto failed
python tools\build_md.py
if errorlevel 1 goto failed
echo.
echo Done. Refresh the browser (F5) to see the changes.
pause
exit /b 0
:failed
echo.
echo Something went wrong - see the messages above.
pause
exit /b 1
