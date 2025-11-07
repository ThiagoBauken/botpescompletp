@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   🧹 LIMPEZA DE SCREENSHOTS
echo ========================================
echo.
echo Este script limpa screenshots acumulados
echo mas PRESERVA templates necessários!
echo.

REM Contar screenshots antes
set /a count=0

echo 📊 Verificando screenshots...
echo.

REM Verificar pasta de manutenção
if exist "fishing_bot_v4\screenshots\maintenance\*.png" (
    echo [1] Pasta: fishing_bot_v4\screenshots\maintenance\
    for %%F in ("fishing_bot_v4\screenshots\maintenance\*.png") do (
        set /a count+=1
    )
    echo    Encontrados: !count! arquivos
    echo.
)

REM Verificar pasta data/screenshots
set /a count2=0
if exist "data\screenshots\*.png" (
    echo [2] Pasta: data\screenshots\
    for %%F in ("data\screenshots\*.png") do (
        set /a count2+=1
    )
    echo    Encontrados: !count2! arquivos
    echo.
)

REM Calcular total
set /a total=count+count2

if %total% equ 0 (
    echo ✅ Nenhum screenshot encontrado para limpar!
    echo.
    pause
    exit /b 0
)

echo ⚠️  TOTAL: %total% screenshots serão deletados
echo.
echo ❌ ISSO NÃO PODE SER DESFEITO!
echo.
echo ✅ PASTAS PRESERVADAS:
echo    - templates\ (NUNCA deletado)
echo    - Outros arquivos (apenas PNGs de screenshots)
echo.

choice /C SN /M "Deseja continuar com a limpeza"
if errorlevel 2 goto cancelar
if errorlevel 1 goto limpar

:limpar
echo.
echo 🧹 Limpando screenshots...
echo.

REM Limpar maintenance
if exist "fishing_bot_v4\screenshots\maintenance\*.png" (
    del /Q "fishing_bot_v4\screenshots\maintenance\*.png" 2>nul
    echo ✅ Pasta fishing_bot_v4\screenshots\maintenance\ limpa
)

REM Limpar data/screenshots
if exist "data\screenshots\*.png" (
    del /Q "data\screenshots\*.png" 2>nul
    echo ✅ Pasta data\screenshots\ limpa
)

echo.
echo ========================================
echo   ✅ LIMPEZA CONCLUÍDA!
echo ========================================
echo.
echo %total% screenshots deletados
echo Templates preservados ✅
echo.
pause
exit /b 0

:cancelar
echo.
echo ❌ Limpeza cancelada pelo usuário
echo.
pause
exit /b 1
