#!/usr/bin/env bash
# MANGO Employee installer for macOS/Linux. Run: bash install.sh
# No external AI runtimes or accounts are installed or authenticated.
set -euo pipefail
cd "$(dirname "$0")"
PYTHON=""
for cmd in python3 python; do
  if command -v "$cmd" >/dev/null 2>&1 && "$cmd" -c \
      'import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] < (3,14) else 1)' >/dev/null 2>&1; then
    PYTHON="$cmd"
    break
  fi
done
if [[ -z "$PYTHON" ]]; then
  echo "Necesitas Python 3.10–3.13. Lee docs/PREREQUISITES.md."
  exit 1
fi
if [[ ! -e .venv ]]; then
  "$PYTHON" -m venv .venv
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "La carpeta .venv existe pero no tiene un Python válido; no se borró ningún dato."
  exit 1
fi
echo "Instalando MANGO Employee y las dependencias Word/PDF..."
.venv/bin/python -m pip install -e ".[meeting,quote]"
.venv/bin/mango guided check
echo
echo "Instalado. Para reabrir: .venv/bin/mango guided"
if ! env | grep -q '^MANGO_NO_WIZARD=1$'; then
  exec .venv/bin/mango guided
fi
