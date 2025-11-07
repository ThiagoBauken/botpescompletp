@echo off
REM ============================================
REM 🎣 Fishing MageBOT v5.0 - Silent Launcher
REM ============================================
REM Inicia o bot sem mostrar janela de comando
REM ============================================

REM Método 1: Se o .exe compilado existe
if exist "dist\FishingMageBOT\FishingMageBOT.exe" (
    start /B "" "dist\FishingMageBOT\FishingMageBOT.exe"
    exit
)

REM Método 2: Se está em desenvolvimento (Python)
if exist "main.py" (
    start /B pythonw.exe main.py
    exit
)

REM Se nenhum dos dois existe, mostra erro
echo ❌ ERRO: Não foi possível encontrar o executável ou main.py
pause
