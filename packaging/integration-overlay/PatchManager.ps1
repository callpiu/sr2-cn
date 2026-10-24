param([string]$GameDirectory,[switch]$SmokeTest,[ValidateSet('None','Install','Verify','Uninstall')][string]$SmokeAction='None',[string]$SmokeReport)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'patch/installer/Manager.ps1') @PSBoundParameters
