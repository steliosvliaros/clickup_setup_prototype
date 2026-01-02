# scripts/init_project.ps1
# Run from repo root:  powershell -ExecutionPolicy Bypass -File .\scripts\init_project.ps1

$ErrorActionPreference = "Stop"

# ---- Settings ----
$EnvName = "clickup-prototype"
$OriginalScriptName = "clickup_python_setup.py"  # your existing script file name
$Root = (Get-Location).Path

function Ensure-Dir($p) {
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p | Out-Null }
}

function Ensure-File($p, $content) {
  if (-not (Test-Path $p)) {
    $content | Out-File -FilePath $p -Encoding UTF8
  }
}

Write-Host "==> Creating folders"
Ensure-Dir (Join-Path $Root "src")
Ensure-Dir (Join-Path $Root "docs")
Ensure-Dir (Join-Path $Root "scripts")
Ensure-Dir (Join-Path $Root "notebooks")

Write-Host "==> Creating files (if missing)"

# config.yaml (placeholder - not used by your original code yet)
Ensure-File (Join-Path $Root "config.yaml") @"
# Prototype config placeholder.
# Your current script does NOT read this file.
# Keep it for later if you decide to externalize structure/settings.
workspace:
  name: "ClickUp Workspace Setup Prototype"
"@

# .env.example (placeholder - original code does NOT read env vars yet)
Ensure-File (Join-Path $Root ".env.example") @"
# Example only (DO NOT commit real secrets)
CLICKUP_API_TOKEN=your_token_here
CLICKUP_TEAM_ID=your_team_id_here
"@

# .gitignore
Ensure-File (Join-Path $Root ".gitignore") @"
# env/secrets
.env

# python
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/

# notebooks
.ipynb_checkpoints/

# builds
dist/
build/
*.egg-info/

# conda/venv
.venv/
venv/
.conda/
"@

# environment.yml
Ensure-File (Join-Path $Root "environment.yml") @"
name: $EnvName
channels:
  - conda-forge
dependencies:
  - python=3.12
  - requests
  - pip
"@

# README.md
Ensure-File (Join-Path $Root "README.md") @"
# ClickUp Prototype

This is a lightweight scaffold for running your **unchanged** ClickUp setup script.

## Layout
- \`src/$OriginalScriptName\` (your original code, unchanged)
- \`config.yaml\`, \`.env.example\` are placeholders for later (not used by the current script)

## Setup (Windows / PowerShell)
1) Create env:
\`\`\`powershell
conda env create -f environment.yml
\`\`\`

2) Activate:
\`\`\`powershell
conda activate $EnvName
\`\`\`

3) Run:
\`\`\`powershell
python .\src\$OriginalScriptName
\`\`\`
"@

# Put original script into src/ WITHOUT MODIFYING it:
# - If the script exists in repo root, copy it to src/
# - Otherwise, create a placeholder and tell user where to paste it
$RootScript = Join-Path $Root $OriginalScriptName
$SrcScript  = Join-Path $Root "src\$OriginalScriptName"

if (Test-Path $RootScript) {
  if (-not (Test-Path $SrcScript)) {
    Copy-Item $RootScript $SrcScript
    Write-Host "==> Copied $OriginalScriptName to src/"
  } else {
    Write-Host "==> src/$OriginalScriptName already exists (leaving as-is)"
  }
} else {
  if (-not (Test-Path $SrcScript)) {
    Ensure-File $SrcScript @"
# Paste your existing $OriginalScriptName content here (UNCHANGED).
# This placeholder is created only because the script wasn't found in repo root.
"@
    Write-Host "==> Created placeholder src/$OriginalScriptName (paste your original code unchanged)"
  }
}

Write-Host "==> Creating conda environment '$EnvName' (if it doesn't exist)"
# If env exists, conda will error; we catch and try update instead.
try {
  conda env create -f (Join-Path $Root "environment.yml")
} catch {
  Write-Host "==> Env may already exist. Attempting update instead..."
  conda env update -f (Join-Path $Root "environment.yml") --prune
}

Write-Host "Done."
Write-Host "Next: run .\scripts\activate_env.ps1 (or 'conda activate $EnvName')"
