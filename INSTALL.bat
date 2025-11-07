@echo off
echo ============================================================
echo Ultimate Fishing Bot v5.0 - Instalador
echo ============================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Python detectado!
echo.

REM Criar ambiente virtual
echo [2/3] Criando ambiente virtual...
python -m venv venv
call venv\Scripts\activate.bat

REM Instalar dependências
echo [3/3] Instalando dependencias...
pip install -r requirements.txt

echo.
echo ============================================================
echo Instalacao concluida!
echo.
echo Para iniciar o bot, execute: RUN.bat
echo ============================================================
pause
