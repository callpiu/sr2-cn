param([string]$GameDirectory,[switch]$SmokeTest,[ValidateSet('None','Install','Verify','Uninstall')][string]$SmokeAction='None',[string]$SmokeReport)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'Core.ps1')
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
$form=New-Object Windows.Forms.Form
$form.Text='黑道圣徒2 · 直升机护卫字幕修复 v1.0'
$form.ClientSize=New-Object Drawing.Size(700,400)
$form.StartPosition='CenterScreen';$form.FormBorderStyle='FixedDialog';$form.MaximizeBox=$false
$label=New-Object Windows.Forms.Label
$label.Text="修复2～6级的两句活动提示。适用：已验证的简中 v546 环境。`r`n安装和卸载前请先退出游戏。"
$label.Location=New-Object Drawing.Point(20,16);$label.Size=New-Object Drawing.Size(660,46);$form.Controls.Add($label)
$path=New-Object Windows.Forms.TextBox
$path.Location=New-Object Drawing.Point(20,76);$path.Size=New-Object Drawing.Size(555,25);$form.Controls.Add($path)
if ($GameDirectory) {$path.Text=$GameDirectory} else {$candidates=@(Get-Sr2Candidates);if($candidates.Count -ge 1){$path.Text=$candidates[0]}}
$browse=New-Object Windows.Forms.Button
$browse.Text='选择目录';$browse.Location=New-Object Drawing.Point(585,74);$browse.Size=New-Object Drawing.Size(95,28);$form.Controls.Add($browse)
$status=New-Object Windows.Forms.TextBox
$status.Multiline=$true;$status.ReadOnly=$true;$status.ScrollBars='Vertical';$status.Location=New-Object Drawing.Point(20,164);$status.Size=New-Object Drawing.Size(660,175);$form.Controls.Add($status)
$status.Text='请选择游戏目录，再点击“检查状态”。'
$buttons=@{}
$names=@{Install='安装 / 更新';Verify='检查状态';Uninstall='卸载 / 恢复'}
$script:Sr2ManagerRoot=(Get-Item -LiteralPath $PSScriptRoot).Parent.Parent.FullName
function Invoke-Sr2ManagerAction([string]$Action) {
    foreach($b in $buttons.Values){$b.Enabled=$false}
    try {
        $wrapper=Join-Path $script:Sr2ManagerRoot (@{Install='Install.ps1';Verify='Test-Patch.ps1';Uninstall='Uninstall.ps1'}[$Action])
        $result=& $wrapper -GameDirectory $path.Text -Quiet
        $status.Text=$result.Message+"`r`n`r`n目录："+$result.GameDirectory+"`r`nSHA-256："+$result.Sha256
        if($SmokeTest -and $SmokeReport){Write-Sr2Json $SmokeReport ([ordered]@{success=$true;action=$Action;result=$result;uiTitle=$form.Text})}
    } catch {
        $status.Text='操作停止：'+$_.Exception.Message
        if($SmokeTest -and $SmokeReport){Write-Sr2Json $SmokeReport ([ordered]@{success=$false;action=$Action;error=$_.Exception.Message})}
    } finally {foreach($b in $buttons.Values){$b.Enabled=$true}}
}
$x=20
foreach($action in @('Install','Verify','Uninstall')) {
    $button=New-Object Windows.Forms.Button
    $button.Text=$names[$action];$button.Tag=$action;$button.Location=New-Object Drawing.Point($x,117);$button.Size=New-Object Drawing.Size(150,32)
    $button.Add_Click({Invoke-Sr2ManagerAction ([string]$this.Tag)})
    $form.Controls.Add($button);$buttons[$action]=$button;$x+=165
}
$open=New-Object Windows.Forms.Button
$open.Text='打开备份目录';$open.Location=New-Object Drawing.Point(20,353);$open.Size=New-Object Drawing.Size(150,30);$form.Controls.Add($open)
$open.Add_Click({try {$root=Get-Sr2Root $path.Text;$target=Join-Path $root $script:Sr2Config.stateFolder;if(-not(Test-Path -LiteralPath $target)){$target=$root};Start-Process -FilePath 'explorer.exe' -ArgumentList ('"'+$target+'"')}catch{$status.Text=$_.Exception.Message}})
$close=New-Object Windows.Forms.Button
$close.Text='关闭';$close.Location=New-Object Drawing.Point(580,353);$close.Size=New-Object Drawing.Size(100,30);$close.Add_Click({$form.Close()});$form.Controls.Add($close)
$browse.Add_Click({$d=New-Object Windows.Forms.FolderBrowserDialog;$d.Description='选择包含 SR2_pc.exe 的游戏目录';$d.ShowNewFolderButton=$false;if($d.ShowDialog() -eq 'OK'){$path.Text=$d.SelectedPath};$d.Dispose()})
if($SmokeTest){
    $timer=New-Object Windows.Forms.Timer;$timer.Interval=800
    $timer.Add_Tick({$timer.Stop();if($SmokeAction -ne 'None'){$buttons[$SmokeAction].PerformClick()}elseif($SmokeReport){Write-Sr2Json $SmokeReport ([ordered]@{success=$true;action='Launch';uiTitle=$form.Text})};$form.Close()})
    $form.Add_Shown({$timer.Start()})
}
try {[void]$form.ShowDialog()} finally {if($SmokeTest){$timer.Dispose()};$form.Dispose()}
