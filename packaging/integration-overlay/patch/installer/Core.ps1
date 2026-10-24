Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'
$script:Sr2ImplementationRoot = $PSScriptRoot
$script:Sr2Config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'fix.json') -Raw -Encoding UTF8 | ConvertFrom-Json

function Get-Sr2Hash([string]$Path) {
    $stream=[IO.File]::OpenRead($Path);$sha=[Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose();$stream.Dispose() }
}
function Get-Sr2ByteHash([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
function Convert-Sr2Hex([string]$Hex) {
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i=0; $i -lt $bytes.Length; $i++) { $bytes[$i] = [Convert]::ToByte($Hex.Substring(2*$i,2),16) }
    return ,$bytes
}
function Write-Sr2Json([string]$Path, $Value) {
    $temp = $Path + '.writing'
    [IO.File]::WriteAllText($temp, ($Value | ConvertTo-Json -Depth 10), (New-Object Text.UTF8Encoding($false)))
    if ([IO.File]::Exists($Path)) { [IO.File]::Replace($temp,$Path,[NullString]::Value) }
    else { [IO.File]::Move($temp,$Path) }
}
function Assert-Sr2PlainPath([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    while ($null -ne $item) {
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw '目录含符号链接或联接点，请选择真实游戏目录。' }
        $item = if ($item -is [IO.DirectoryInfo]) { $item.Parent } else { $item.Directory }
    }
}
function Get-Sr2Root([string]$GameDirectory) {
    if ([string]::IsNullOrWhiteSpace($GameDirectory)) { throw '请选择包含 SR2_pc.exe 的游戏目录。' }
    $item = Get-Item -LiteralPath $GameDirectory -Force
    if (-not $item.PSIsContainer) { throw '请选择游戏文件夹，不要选择 EXE 文件。' }
    Assert-Sr2PlainPath $item.FullName
    return $item.FullName.TrimEnd('\')
}
function Get-Sr2Candidates {
    $roots = New-Object 'System.Collections.Generic.List[string]'
    $libraries = New-Object 'System.Collections.Generic.List[string]'
    foreach ($reg in @('HKCU:\Software\Valve\Steam','HKLM:\SOFTWARE\WOW6432Node\Valve\Steam','HKLM:\SOFTWARE\Valve\Steam')) {
        $r = Get-ItemProperty -LiteralPath $reg -ErrorAction SilentlyContinue
        if ($null -ne $r) {
            foreach ($name in @('SteamPath','InstallPath')) {
                if ($r.PSObject.Properties[$name] -and $r.$name) { $libraries.Add([string]$r.$name) }
            }
        }
    }
    foreach ($steam in @($libraries.ToArray())) {
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdf) {
            $text = Get-Content -LiteralPath $vdf -Raw
            foreach ($m in [regex]::Matches($text,'"path"\s+"([^"]+)"')) { $libraries.Add($m.Groups[1].Value.Replace('\\','\')) }
        }
    }
    foreach ($lib in $libraries) {
        $candidate = Join-Path $lib 'steamapps\common\Saints Row 2'
        if (Test-Path -LiteralPath (Join-Path $candidate 'SR2_pc.exe')) { $roots.Add($candidate) }
        $acf = Join-Path $lib 'steamapps\appmanifest_9480.acf'
        if (Test-Path -LiteralPath $acf) {
            $m = [regex]::Match((Get-Content -LiteralPath $acf -Raw),'"installdir"\s+"([^"]+)"')
            if ($m.Success) {
                $candidate = Join-Path (Join-Path $lib 'steamapps\common') $m.Groups[1].Value
                if (Test-Path -LiteralPath (Join-Path $candidate 'SR2_pc.exe')) { $roots.Add($candidate) }
            }
        }
    }
    $ancestor = Get-Item -LiteralPath $script:Sr2ImplementationRoot
    for ($i=0; $i -lt 5 -and $null -ne $ancestor; $i++) {
        if (Test-Path -LiteralPath (Join-Path $ancestor.FullName 'SR2_pc.exe')) { $roots.Add($ancestor.FullName) }
        $ancestor=$ancestor.Parent
    }
    return @($roots | Sort-Object -Unique)
}
function Assert-Sr2Assets([string]$Root) {
    $cfg=$script:Sr2Config
    foreach ($name in @($cfg.exe,$cfg.textAsset,'common.vpp_pc')) {
        $path=Join-Path $Root $name
        if (-not [IO.File]::Exists($path)) { throw ('缺少游戏文件：' + $name) }
        Assert-Sr2PlainPath $path
    }
    $path=Join-Path $Root $cfg.exe
    if ((Get-Item -LiteralPath $path).Length -ne $cfg.size) { throw '主程序大小不匹配，本补丁不支持此版本。' }
    $hash=Get-Sr2Hash $path
    if ($hash -notin @($cfg.originalSha256,$cfg.patchedSha256)) { throw ('主程序版本不匹配，未作任何修改。SHA-256：' + $hash) }
    if ((Get-Sr2Hash (Join-Path $Root $cfg.textAsset)) -ne $cfg.textSha256) { throw '汉化资源版本不匹配。此包仅支持已验证的简中 v546 文本资源，不支持原繁中或未知汉化版。' }
    $f=[IO.File]::OpenRead((Join-Path $Root 'common.vpp_pc'))
    try { $header=New-Object byte[] 5; if ($f.Read($header,0,5) -ne 5 -or [BitConverter]::ToString($header) -ne 'CE-0A-89-51-04') { throw 'common.vpp_pc 不是可识别的 SR2 资源包。' } }
    finally { $f.Dispose() }
    return $hash
}
function Assert-Sr2Stopped([string]$Root) {
    $exe=Join-Path $Root $script:Sr2Config.exe
    foreach ($p in @([Diagnostics.Process]::GetProcessesByName('SR2_pc'))) {
        try { $processPath=$p.MainModule.FileName }
        catch { throw '检测到同名游戏进程但无法核对路径，请先退出游戏。' }
        finally { $p.Dispose() }
        if (-not $processPath) { throw '检测到同名游戏进程但无法核对路径，请先退出游戏。' }
        if ([string]::Equals($processPath,$exe,[StringComparison]::OrdinalIgnoreCase)) { throw '请先正常退出这份《黑道圣徒2》，再安装或卸载补丁。' }
    }
}
function Get-Sr2PatchedBytes([byte[]]$Bytes) {
    $cfg=$script:Sr2Config
    if ((Get-Sr2ByteHash $Bytes) -ne $cfg.originalSha256) { throw '构建输入不是受支持的原始程序。' }
    $result=[byte[]]$Bytes.Clone()
    foreach ($patch in $cfg.patches) {
        $before=Convert-Sr2Hex $patch.before; $after=Convert-Sr2Hex $patch.after
        for ($i=0; $i -lt $before.Length; $i++) {
            if ($result[$patch.offset+$i] -ne $before[$i]) { throw '补丁位置校验失败。' }
            $result[$patch.offset+$i]=$after[$i]
        }
    }
    if ((Get-Sr2ByteHash $result) -ne $cfg.patchedSha256) { throw '修复后程序校验失败。' }
    return ,$result
}
function Get-Sr2Status([string]$Root,[string]$Hash) {
    $cfg=$script:Sr2Config
    $folder=Join-Path $Root $cfg.stateFolder; $backup=Join-Path $folder 'original.exe'
    $canRestore=[IO.File]::Exists($backup) -and (Get-Sr2Hash $backup) -eq $cfg.originalSha256
    $fixed=$Hash -eq $cfg.patchedSha256
    $message=if ($fixed) { '修复已安装，主程序及汉化资源校验通过。' } else { '版本匹配，可以安装修复。' }
    if ($fixed -and -not $canRestore) { $message+=' 未发现本安装器保存的原程序备份。' }
    [pscustomobject]@{Status=$(if($fixed){'Installed'}else{'NotInstalled'});Message=$message;GameDirectory=$Root;Sha256=$Hash;CanRestore=$canRestore;Version=$cfg.version;RuntimeVerified=$null}
}
function Invoke-Sr2Fix {
    param([ValidateSet('Install','Verify','Uninstall')][string]$Action,[string]$GameDirectory)
    $cfg=$script:Sr2Config; $root=Get-Sr2Root $GameDirectory; $hash=Assert-Sr2Assets $root
    $folder=Join-Path $root $cfg.stateFolder; $exe=Join-Path $root $cfg.exe
    if ($Action -ne 'Verify') { Assert-Sr2Stopped $root }
    if (Test-Path -LiteralPath $folder) { Assert-Sr2PlainPath $folder }
    if ($Action -eq 'Verify' -and -not [IO.Directory]::Exists($folder)) { return Get-Sr2Status $root $hash }
    [IO.Directory]::CreateDirectory($folder) | Out-Null
    $lock=$null; $stage=Join-Path $folder 'staged.exe'; $pending=Join-Path $folder 'pending.json'
    $backup=Join-Path $folder 'original.exe'; $receipt=Join-Path $folder 'installed.json'
    foreach ($file in @('lock','staged.exe','pending.json','original.exe','installed.json','rollback.exe','installed.json.writing','pending.json.writing')) {
        $path=Join-Path $folder $file
        if (Test-Path -LiteralPath $path) { Assert-Sr2PlainPath $path }
    }
    try {
        try { $lock=[IO.File]::Open((Join-Path $folder 'lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None) }
        catch { throw '此游戏目录有另一项补丁操作正在进行，请稍后重试。' }
        $hash=Assert-Sr2Assets $root
        if ([IO.File]::Exists($pending)) {
            # Known executable hashes plus the verified backup make both sides recoverable.
            if (-not [IO.File]::Exists($backup) -or (Get-Sr2Hash $backup) -ne $cfg.originalSha256) { throw '检测到未完成事务且备份缺失或损坏，请保留现场，不要覆盖游戏文件。' }
            foreach ($p in @($stage,$pending+'.writing')) { if ([IO.File]::Exists($p)) { [IO.File]::Delete($p) } }
            Write-Sr2Json $receipt ([ordered]@{version=$cfg.version;transactionId=[Guid]::NewGuid().ToString();recovered=$true;installed=($hash -eq $cfg.patchedSha256);installedSha256=$hash;gameRoot=$root;runtimeRoot=$root;virtualRoot='game executable';backup='original.exe';backupSha256=$cfg.originalSha256;recipe='patch/installer/fix.json';recipeSha256=(Get-Sr2Hash (Join-Path $script:Sr2ImplementationRoot 'fix.json'));files=@([ordered]@{relative='SR2_pc.exe';targetRelative='SR2_pc.exe';size=$cfg.size;sha256=$hash});runtimeVerified=$null})
            [IO.File]::Delete($pending)
        }
        if ($Action -eq 'Verify') { return Get-Sr2Status $root $hash }
        if ($Action -eq 'Install' -and $hash -eq $cfg.patchedSha256) { return Get-Sr2Status $root $hash }
        if ($Action -eq 'Uninstall' -and $hash -eq $cfg.originalSha256) {
            $result=Get-Sr2Status $root $hash; $result.Message='原程序状态，未重复卸载。'; return $result
        }
        $previous=[IO.File]::ReadAllBytes($exe)
        if ($Action -eq 'Install') {
            if ([IO.File]::Exists($backup)) {
                if ((Get-Sr2Hash $backup) -ne $cfg.originalSha256) { throw '已有备份校验失败，为保护原文件已停止安装。' }
            } else {
                $stream=[IO.File]::Open($backup,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
                try { $stream.Write($previous,0,$previous.Length);$stream.Flush($true) } finally { $stream.Dispose() }
            }
            $next=Get-Sr2PatchedBytes $previous; $expected=$cfg.patchedSha256
        } else {
            if (-not [IO.File]::Exists($backup) -or (Get-Sr2Hash $backup) -ne $cfg.originalSha256) { throw '没有可核验的原程序备份，无法自动卸载。' }
            $next=[IO.File]::ReadAllBytes($backup); $expected=$cfg.originalSha256
        }
        $activated=$false
        try {
            if ([IO.File]::Exists($stage)) { [IO.File]::Delete($stage) }
            $stream=[IO.File]::Open($stage,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
            try { $stream.Write($next,0,$next.Length);$stream.Flush($true) } finally { $stream.Dispose() }
            if ((Get-Sr2Hash $stage) -ne $expected) { throw '暂存文件校验失败。' }
            Write-Sr2Json $pending ([ordered]@{version=$cfg.version;action=$Action;before=$hash;after=$expected;backupSha256=$cfg.originalSha256})
            [IO.File]::Replace($stage,$exe,[NullString]::Value);$activated=$true
            if ((Get-Sr2Hash $exe) -ne $expected) { throw '安装文件校验失败。' }
            Write-Sr2Json $receipt ([ordered]@{version=$cfg.version;transactionId=[Guid]::NewGuid().ToString();action=$Action;installed=($Action -eq 'Install');installedAt=[DateTime]::UtcNow.ToString('o');gameRoot=$root;runtimeRoot=$root;virtualRoot='game executable';backup='original.exe';backupSha256=$cfg.originalSha256;recipe='patch/installer/fix.json';recipeSha256=(Get-Sr2Hash (Join-Path $script:Sr2ImplementationRoot 'fix.json'));files=@([ordered]@{relative='SR2_pc.exe';targetRelative='SR2_pc.exe';size=$next.Length;sha256=$expected});runtimeVerified=$null})
            [IO.File]::Delete($pending)
        } catch {
            if ($activated) {
                $rollback=Join-Path $folder 'rollback.exe'
                [IO.File]::WriteAllBytes($rollback,$previous)
                if ((Get-Sr2Hash $rollback) -ne $hash) { throw '自动回退暂存校验失败，请保留备份。' }
                [IO.File]::Replace($rollback,$exe,[NullString]::Value)
            }
            throw
        }
        $result=Get-Sr2Status $root $expected
        $result.Message=if ($Action -eq 'Install') { '修复安装成功。请重新启动游戏。原程序已自动备份。' } else { '已恢复原程序。备份仍保留在游戏目录。' }
        return $result
    } finally { if ($null -ne $lock) { $lock.Dispose() } }
}
