@echo off
setlocal
chcp 65001 >nul
powershell.exe -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0PatchManager.ps1" -GameDirectory "%~1"
set "sr2PatchResult=%errorlevel%"
exit /b %sr2PatchResult%
