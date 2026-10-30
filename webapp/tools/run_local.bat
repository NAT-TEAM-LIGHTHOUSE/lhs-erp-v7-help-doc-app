@echo off
rem Quick local preview of the Help Centre (needs Python 3). Close this window to stop.
cd /d "%~dp0.."
start "" http://localhost:8080/layout.html
python -m http.server 8080
