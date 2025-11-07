@echo off
REM ===================================================================
REM   🔍 Fishing Bot - Modo Verbose (Debug Completo)
REM ===================================================================
REM
REM   Este script inicia o bot em modo VERBOSE
REM   TODOS os logs aparecem no console (útil para debug)
REM
REM ===================================================================

echo.
echo ================================================================
echo    🔍 Fishing Bot - VERBOSE MODE (Debug Completo)
echo ================================================================
echo.

REM Configurar nível de log
set CONSOLE_LOG_LEVEL=VERBOSE

echo ✅ Nível de log: %CONSOLE_LOG_LEVEL%
echo.
echo 📝 TODOS os logs serão exibidos:
echo    • Debug de posições do mouse
echo    • Validações intermediárias
echo    • Trace completo do fluxo
echo.
echo ⚠️ ATENÇÃO: Muitas linhas no console!
echo.
echo ================================================================
echo.

REM Iniciar bot
python main.py

pause
