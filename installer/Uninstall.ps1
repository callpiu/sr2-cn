param([string]$GameDirectory,[switch]$Quiet)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'patch/installer/Console.ps1') -Action Uninstall -GameDirectory $GameDirectory -Quiet:$Quiet
