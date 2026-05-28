param(
    [string]$Python = "python",
    [string]$WheelDir = "wheels\py312-win_amd64"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$ResolvedWheelDir = if ([System.IO.Path]::IsPathRooted($WheelDir)) {
    $WheelDir
}
else {
    Join-Path $RepoRoot $WheelDir
}
if (-not (Test-Path $ResolvedWheelDir)) {
    $ReleaseWheelDir = Join-Path $RepoRoot "..\wheels\py312-win_amd64"
    if (Test-Path $ReleaseWheelDir) {
        $ResolvedWheelDir = $ReleaseWheelDir
    }
    else {
        throw "Wheelhouse not found: $WheelDir"
    }
}
$ResolvedWheelDir = (Resolve-Path $ResolvedWheelDir).Path
Push-Location $RepoRoot
try {
    & $Python -m pip install --no-index --find-links $ResolvedWheelDir -r requirements-dev.txt
    & $Python -m PyInstaller (Join-Path $RepoRoot "packaging\nn_qt.spec") --noconfirm
}
finally {
    Pop-Location
}
