# scripts/activate_env.ps1
# Run from repo root:  powershell -ExecutionPolicy Bypass -File .\scripts\activate_env.ps1

$ErrorActionPreference = "Stop"
$EnvName = "clickup-prototype"

# Note: 'conda activate' works if you've run 'conda init powershell' at least once.
conda activate $EnvName

Write-Host "Activated conda env: $EnvName"
Write-Host "Run: python .\src\clickup_python_setup.py"
