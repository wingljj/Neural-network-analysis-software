param(
    [string]$Python = "python",
    [string]$WheelDir = "wheels\py312-win_amd64"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $RepoRoot
try {
    New-Item -ItemType Directory -Force -Path $WheelDir | Out-Null
    & $Python -m pip download -r requirements-dev.txt -d $WheelDir --only-binary=:all:
}
finally {
    Pop-Location
}
