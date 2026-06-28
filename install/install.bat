@echo off
rem install.bat - Windows double-click shim for the guided EADOS installer (M9 9.3).
rem A bare .ps1 opens in an editor on double-click; this runs it through PowerShell instead.
rem All the install logic lives in install.ps1 (next to this file); this only launches it.
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
set RC=%ERRORLEVEL%
echo.
pause
exit /b %RC%
