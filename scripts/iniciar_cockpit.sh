#!/usr/bin/env bash
# ==============================================================================
# SP-ÁGUAS / SA-GTI -- INICIALIZADOR LINUX/MACOS DO COCKPIT GTI (V11)
# ==============================================================================
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=============================================================================="
echo " SP-AGUAS / SA-GTI -- INICIALIZADOR DO COCKPIT GTI V11"
echo "=============================================================================="

pip3 install -r requirements.txt --quiet

echo "[*] Iniciando Backend Flask (:5000)..."
python3 backend/main.py &

sleep 2

echo "[*] Abrindo painel.html..."
if which xdg-open > /dev/null; then
    xdg-open painel.html
elif which open > /dev/null; then
    open painel.html
fi
