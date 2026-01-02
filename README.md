# ClickUp Prototype

This is a lightweight scaffold for running your **unchanged** ClickUp setup script.

## Layout
- \src/clickup_python_setup.py\ (your original code, unchanged)
- \config.yaml\, \.env.example\ are placeholders for later (not used by the current script)

## Setup (Windows / PowerShell)
1) Create env:
\\\powershell
conda env create -f environment.yml
\\\

2) Activate:
\\\powershell
conda activate clickup-prototype
\\\

3) Run:
\\\powershell
python .\src\clickup_python_setup.py
\\\
