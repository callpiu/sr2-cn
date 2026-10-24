@echo off
setlocal
chcp 65001 >nul
powershell.exe -NoLogo -NoProfile -STA -ExecutionPolicy Bypass -File "%~dp0Test-Patch.ps1" -GameDirectory "%~1"
set "sr2PatchResult=%errorlevel%"
if not defined SR2_PATCH_NO_PAUSE pause
exit /b %sr2PatchResult%
