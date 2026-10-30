@echo off
rem Builds the "Reader" (HTML) view of every PDF in docs\  ->  html\
rem First time only:  pip install pymupdf pillow
cd /d "%~dp0.."
python tools\build_html.py %*
pause
