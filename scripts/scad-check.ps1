param(
    [string]$File = "src\Plug_Puller_Parametric.scad",
    [string[]]$Defines = @()   # e.g. -Defines 'grip_width=25' or -Defines 'size=Measure my hand'
)
$exe = $env:OPENSCAD_EXE
if (-not $exe) { $exe = 'C:\Program Files\OpenSCAD (Nightly)\openscad.com' }
if (-not (Test-Path $exe)) { Write-Output "CHECK FAILED: OpenSCAD not found at $exe"; exit 1 }
if (-not (Test-Path build)) { New-Item -ItemType Directory build | Out-Null }
if (Test-Path build\check.stl) { Remove-Item build\check.stl -Force }

# A text value can arrive with its quotes or without them (Windows PowerShell
# strips them when it starts a script with -File), so a value that is not a
# number, true/false, a [list] or already quoted gets its quotes here.
function Format-Define([string]$define) {
    $i = $define.IndexOf('=')
    if ($i -lt 1) { return $define }
    $name = $define.Substring(0, $i).Trim()
    $value = $define.Substring($i + 1).Trim()
    $isNumber = $value -match '^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$'
    if ($isNumber -or $value -ceq 'true' -or $value -ceq 'false' -or $value -match '^\[.*\]$' -or $value -match '^".*"$') {
        return "$name=$value"
    }
    return $name + '="' + $value.Replace('"', '\"') + '"'
}

# Windows PowerShell 5.1 drops the quotes inside an argument it hands to a
# program, so the command line is built here by the rules programs split it
# by: an argument with a space or a quote is quoted, a quote becomes \", and
# backslashes before a quote are doubled.
function ConvertTo-Argument([string]$arg) {
    if ($arg.Length -gt 0 -and $arg -notmatch '[\s"]') { return $arg }
    $escaped = [regex]::Replace($arg, '(\\*)"', { param($m) $m.Groups[1].Value + $m.Groups[1].Value + '\"' })
    $escaped = [regex]::Replace($escaped, '(\\+)$', { param($m) $m.Groups[1].Value + $m.Groups[1].Value })
    return '"' + $escaped + '"'
}

# OpenSCAD does not test a text value against the setting's dropdown list,
# so a misspelled choice would quietly check the default shape; it is
# reported here as a warning, which fails the check.
function Test-DropdownValue([string]$define, [string]$scadText) {
    $i = $define.IndexOf('=')
    $value = $define.Substring($i + 1)
    if ($i -lt 1 -or $value -notmatch '^"(.*)"$') { return $null }
    $value = $Matches[1].Replace('\"', '"')
    $name = $define.Substring(0, $i)
    $pattern = '(?m)^\s*' + [regex]::Escape($name) + '\s*=\s*"[^"]*"\s*;\s*//\s*\[([^\]]*)\]'
    $list = [regex]::Match($scadText, $pattern)
    if (-not $list.Success) { return $null }
    $choices = @($list.Groups[1].Value.Split(',') | ForEach-Object { $_.Trim() })
    if ($choices -ccontains $value) { return $null }
    return "WARNING: scad-check: $name=""$value"" is not one of its dropdown choices: $($choices -join ', ')"
}

$scadText = if (Test-Path -LiteralPath $File) { Get-Content -Raw -Encoding UTF8 -LiteralPath $File } else { '' }
$argList = @('--hardwarnings', '--check-parameter-ranges=true')
$notices = @()
foreach ($d in $Defines) {
    $define = Format-Define $d
    $argList += @('-D', $define)
    $notice = Test-DropdownValue $define $scadText
    if ($notice) { $notices += $notice }
}
$argList += @('-o', 'build\check.stl', $File)

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $exe
$psi.Arguments = ($argList | ForEach-Object { ConvertTo-Argument $_ }) -join ' '
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.WorkingDirectory = (Get-Location).Path
$proc = [System.Diagnostics.Process]::Start($psi)
$stdout = $proc.StandardOutput.ReadToEndAsync()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
$out = @($notices) + @(($stdout.Result + "`n" + $stderr) -split "`r?`n" | Where-Object { $_ -ne '' })
$out | Write-Output
$bad = [bool]($out | Where-Object { $_ -cmatch 'WARNING:|ERROR:' })
$stl = Test-Path build\check.stl
if ($bad -or -not $stl) { Write-Output "CHECK FAILED (warnings/errors above, or STL exists=$stl)"; exit 1 }
Write-Output "CHECK PASSED: build\check.stl written by $exe"
