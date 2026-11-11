@echo off
title Cockpit GTI - SP-Aguas
echo ==============================================================================
echo  SP-AGUAS / SA-GTI -- INICIALIZADOR OFICIAL DO COCKPIT GTI (V11)
echo ==============================================================================
cd /d "%~dp0\.."

echo [*] Verificando dependencias Python...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo [*] Iniciando Backend Flask (:5000)...
if exist "main.py" (
    start /b python main.py
) else (
    start /b python backend/main.py
)

timeout /t 2 /nobreak >nul

echo [*] Abrindo Cockpit GTI em http://localhost:5000/...
start "" "http://localhost:5000/"

echo ==============================================================================
echo  Cockpit GTI em execucao via HTTP! Para encerrar o backend, feche esta janela.
echo ==============================================================================
pause
