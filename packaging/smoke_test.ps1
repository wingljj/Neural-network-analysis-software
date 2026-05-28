param(
    [string]$ExePath = "dist\nn_qt\nn_qt.exe"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
if (-not [System.IO.Path]::IsPathRooted($ExePath)) {
    $ExePath = Join-Path $RepoRoot $ExePath
}
if (-not (Test-Path $ExePath)) {
    throw "Executable not found: $ExePath"
}
$process = Start-Process -FilePath $ExePath -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 5
if (-not $process.HasExited) {
    Stop-Process -Id $process.Id
    exit 0
}
exit $process.ExitCode
