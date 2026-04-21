param(
    [string]$ComfyUIDir = "",
    [string]$Listen = "127.0.0.1",
    [int]$Port = 8188,
    [switch]$AutoLaunch
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")

if ([string]::IsNullOrWhiteSpace($ComfyUIDir)) {
    $Candidate = Join-Path (Join-Path $RepoRoot "..\..") "main.py"
    if (Test-Path -LiteralPath $Candidate) {
        $ComfyUIDir = Resolve-Path (Join-Path $RepoRoot "..\..")
    }
    elseif (Test-Path -LiteralPath (Join-Path $RepoRoot "ComfyUI\main.py")) {
        $ComfyUIDir = Resolve-Path (Join-Path $RepoRoot "ComfyUI")
    }
    else {
        throw "Could not locate ComfyUI. Pass -ComfyUIDir explicitly."
    }
}

$Python = "python"

$ComfyArgs = @(
    "main.py",
    "--listen", $Listen,
    "--port", $Port,
    "--cpu"
)

if (-not $AutoLaunch) {
    $ComfyArgs += "--disable-auto-launch"
}

Write-Host "Starting ComfyUI for Intel AI PC / OpenVINO:"
Write-Host "$Python $($ComfyArgs -join ' ')"
Write-Host ""
Write-Host "OpenVINO device selection is still controlled inside the ERNIE-Image node, for example device=GPU."

Push-Location $ComfyUIDir
try {
    & $Python @ComfyArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
