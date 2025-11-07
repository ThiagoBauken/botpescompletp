@echo off
chcp 65001 >nul 2>&1

cls
echo ========================================
echo   FISHING MAGEBOT - VALIDACAO PRE-BUILD
echo ========================================
echo.

cd /d "%~dp0"

set ERRORS=0

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    set ERRORS=1
) else (
    for /f "tokens=2" %%i in ('python --version') do set PYTHON_VER=%%i
    echo OK: Python %PYTHON_VER% encontrado
)
echo.

echo [2/6] Verificando dependencias...
echo Verificando opencv-python...
pip show opencv-python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: opencv-python nao instalado!
    set ERRORS=1
) else (
    echo OK: opencv-python instalado
)

echo Verificando numpy...
pip show numpy >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: numpy nao instalado!
    set ERRORS=1
) else (
    echo OK: numpy instalado
)

echo Verificando pyautogui...
pip show pyautogui >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pyautogui nao instalado!
    set ERRORS=1
) else (
    echo OK: pyautogui instalado
)

echo Verificando mss...
pip show mss >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: mss nao instalado!
    set ERRORS=1
) else (
    echo OK: mss instalado
)

echo Verificando keyboard...
pip show keyboard >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: keyboard nao instalado!
    set ERRORS=1
) else (
    echo OK: keyboard instalado
)

echo Verificando pywin32...
pip show pywin32 >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: pywin32 nao instalado!
    set ERRORS=1
) else (
    echo OK: pywin32 instalado
)

echo Verificando nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: nuitka nao instalado!
    set ERRORS=1
) else (
    echo OK: nuitka instalado
)
echo.

echo [3/6] Verificando estrutura de pastas...
if not exist "templates\" (
    echo ERRO: Pasta templates\ nao encontrada!
    set ERRORS=1
) else (
    for /f %%a in ('dir /b templates\*.png 2^>nul ^| find /c /v ""') do set TEMPLATE_COUNT=%%a
    if !TEMPLATE_COUNT! GTR 0 (
        echo OK: Pasta templates\ encontrada ^(!TEMPLATE_COUNT! arquivos PNG^)
    ) else (
        echo AVISO: Pasta templates\ vazia!
        set ERRORS=1
    )
)

if not exist "locales\" (
    echo ERRO: Pasta locales\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta locales\ encontrada
)

if not exist "config\" (
    echo ERRO: Pasta config\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta config\ encontrada
)

if not exist "core\" (
    echo ERRO: Pasta core\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta core\ encontrada
)

if not exist "ui\" (
    echo ERRO: Pasta ui\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta ui\ encontrada
)

if not exist "utils\" (
    echo ERRO: Pasta utils\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta utils\ encontrada
)

if not exist "client\" (
    echo ERRO: Pasta client\ nao encontrada!
    set ERRORS=1
) else (
    echo OK: Pasta client\ encontrada
)
echo.

echo [4/6] Verificando arquivos essenciais...
if not exist "main.py" (
    echo ERRO: main.py nao encontrado!
    set ERRORS=1
) else (
    echo OK: main.py encontrado
)

if not exist "icon.ico" (
    echo ERRO: icon.ico nao encontrado!
    set ERRORS=1
) else (
    echo OK: icon.ico encontrado
)

if not exist "config\default_config.json" (
    echo ERRO: config\default_config.json nao encontrado!
    set ERRORS=1
) else (
    echo OK: default_config.json encontrado
)
echo.

echo [5/6] Verificando MSVC...
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: MSVC 2019 nao encontrado!
    echo Instale Visual Studio Build Tools 2019
    set ERRORS=1
) else (
    where cl.exe >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Compilador MSVC nao encontrado no PATH!
        set ERRORS=1
    ) else (
        echo OK: MSVC 2019 configurado corretamente
    )
)
echo.

echo [6/6] Verificando espaco em disco...
for /f "tokens=3" %%a in ('dir /-c ^| find "bytes free"') do set FREE_SPACE=%%a
echo OK: Verificacao de espaco concluida
echo.

echo ========================================
echo   RESULTADO DA VALIDACAO
echo ========================================
echo.

if %ERRORS%==0 (
    echo STATUS: TUDO OK! ^✓^
    echo.
    echo Voce pode executar BUILD_NUITKA_FIXED.bat com seguranca.
    echo.
    echo PROXIMOS PASSOS:
    echo 1. Execute BUILD_NUITKA_FIXED.bat
    echo 2. Aguarde a compilacao ^(10-20 minutos^)
    echo 3. Teste o executavel em dist\FishingMageBOT\
    echo.
) else (
    echo STATUS: ERROS ENCONTRADOS! ^✗^
    echo.
    echo Corrija os erros acima antes de compilar.
    echo.
    echo DICAS:
    echo - Para instalar dependencias: pip install -r requirements.txt
    echo - Para instalar MSVC: Baixe Visual Studio Build Tools 2019
    echo.
)

echo ========================================
pause
