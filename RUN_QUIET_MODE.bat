@echo off
REM ===================================================================
REM   🎯 Fishing Bot - Modo Silencioso (Console Limpo)
REM ===================================================================
REM
REM   Este script inicia o bot em modo QUIET
REM   Apenas logs essenciais aparecem no console
REM
REM   Para mudar o nível de log, edite a linha abaixo:
REM   - QUIET   = Mínimo (recomendado)
REM   - NORMAL  = Padrão
REM   - VERBOSE = Debug completo
REM
REM ===================================================================

echo.
echo ================================================================
echo    🎯 Fishing Bot - QUIET MODE (Console Limpo)
echo ================================================================
echo.

REM Configurar nível de log
set CONSOLE_LOG_LEVEL=QUIET

echo ✅ Nível de log: %CONSOLE_LOG_LEVEL%
echo.
echo 📝 Apenas logs essenciais serão exibidos:
echo    • Peixes capturados
echo    • Comandos do servidor
echo    • Erros críticos
echo.
echo 💡 Para logs completos, veja: data/logs/
echo.
echo ================================================================
echo.

REM Iniciar bot
python main.py

pause
