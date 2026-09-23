<#
MANGO Employee first-time installer for Windows.
Run: powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
Does not install external AI runtimes or require administrator privileges.
#>
param([switch]$NoWizard)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (Get-Command py -ErrorAction SilentlyContinue) {
  & py -3 -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,14) else 1)"
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Se necesita Python 3.10–3.13. Consulta docs\PREREQUISITES.md."
    exit 1
  }
  if (!(Test-Path -LiteralPath ".venv")) { & py -3 -m venv .venv }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
  & python -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,14) else 1)"
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Se necesita Python 3.10–3.13. Consulta docs\PREREQUISITES.md."
    exit 1
  }
  if (!(Test-Path -LiteralPath ".venv")) { & python -m venv .venv }
} else {
  Write-Error "Instala Python 3.10–3.13 antes de continuar."
  exit 1
}
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$mango = Join-Path $PSScriptRoot ".venv\Scripts\mango.exe"
if (!(Test-Path -LiteralPath $python)) {
  Write-Error "La carpeta .venv ya existe pero no es un entorno Python válido; no se borró."
  exit 1
}
Write-Host "Instalando MANGO Employee y Word/PDF..."
& $python -m pip install -e ".[meeting,quote]"
if ($LASTEXITCODE -ne 0) {
  Write-Error "Falló pip. Revisa conectividad y docs\TROUBLESHOOTING.md."
  exit 1
}
& $mango guided check
if ($LASTEXITCODE -ne 0) { exit 1 }
Write-Host "Instalado. Para reabrir: .\.venv\Scripts\mango.exe guided"
if (!$NoWizard) { & $mango guided; exit $LASTEXITCODE }
