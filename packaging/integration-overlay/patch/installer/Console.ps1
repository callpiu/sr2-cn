param([ValidateSet('Install','Verify','Uninstall')][string]$Action='Install',[string]$GameDirectory,[switch]$Quiet)
$ErrorActionPreference='Stop'
[Console]::OutputEncoding=New-Object Text.UTF8Encoding($false)
. (Join-Path $PSScriptRoot 'Core.ps1')
if ([string]::IsNullOrWhiteSpace($GameDirectory)) {
    $candidates=@(Get-Sr2Candidates)
    if ($candidates.Count -eq 1) { $GameDirectory=$candidates[0] }
    else {
        Add-Type -AssemblyName System.Windows.Forms
        $dialog=New-Object Windows.Forms.FolderBrowserDialog
        $dialog.Description='选择黑道圣徒2游戏目录（包含 SR2_pc.exe）'
        $dialog.ShowNewFolderButton=$false
        if ($dialog.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) { throw '已取消选择，未修改游戏。' }
        $GameDirectory=$dialog.SelectedPath
        $dialog.Dispose()
    }
}
$result=Invoke-Sr2Fix -Action $Action -GameDirectory $GameDirectory
if(-not $Quiet){
    Write-Host $result.Message
    Write-Host ('游戏目录：'+$result.GameDirectory)
    Write-Host ('SHA-256：'+$result.Sha256)
}
return $result
