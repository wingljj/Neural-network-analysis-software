param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $RepoRoot
try {
    & $Python -m pip install -r requirements-dev.txt
    & $Python -m PyInstaller (Join-Path $RepoRoot "packaging\nn_qt.spec") --noconfirm
}
finally {
    Pop-Location
}
