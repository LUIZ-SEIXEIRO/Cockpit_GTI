@echo off
title Cockpit GTI - SP-Aguas
echo ==============================================================================
echo  SP-AGUAS / SA-GTI -- INICIALIZADOR OFICIAL DO COCKPIT GTI (V11)
echo ==============================================================================
cd /d "%~dp0\.."

echo [*] Verificando dependencias Python...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo [*] Iniciando Backend Flask (:5000) em segundo plano...
start /b python backend/main.py

timeout /t 2 /nobreak >nul

echo [*] Abrindo Cockpit GTI no navegador padrao...
start "" "painel.html"

echo ==============================================================================
echo  Cockpit GTI em execucao! Para encerrar o backend, feche esta janela.
echo ==============================================================================
pause
