@echo off
echo ============================================================
echo Ultimate Fishing Bot v5.0
echo ============================================================
echo.

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Ambiente virtual ativado
) else (
    echo Aviso: Ambiente virtual nao encontrado
    echo Execute INSTALL.bat primeiro
    echo.
)

REM Executar bot
python main.py

pause
