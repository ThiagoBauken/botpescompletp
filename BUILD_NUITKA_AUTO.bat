@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - BUILD AUTO
echo   Detecta VS 2019 ou VS 2022
echo ========================================
echo.

REM Detectar qual Visual Studio esta instalado
set MSVC_FOUND=0
set MSVC_VERSION=

echo [1/6] Detectando Visual Studio...

REM Tentar VS 2022 primeiro (mais recente)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2022 Community
    set MSVC_FOUND=1
    goto :found_msvc
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2022 Professional
    set MSVC_FOUND=1
    goto :found_msvc
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2022 BuildTools
    set MSVC_FOUND=1
    goto :found_msvc
)

REM Tentar VS 2019
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2019 Community
    set MSVC_FOUND=1
    goto :found_msvc
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2019 Professional
    set MSVC_FOUND=1
    goto :found_msvc
)

if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=2019 BuildTools
    set MSVC_FOUND=1
    goto :found_msvc
)

:found_msvc
if %MSVC_FOUND%==0 (
    echo ERRO: Visual Studio nao encontrado!
    echo.
    echo Instale uma das opcoes:
    echo - Visual Studio 2022 Community (GRATIS)
    echo - Visual Studio 2019 BuildTools
    echo.
    echo Download: https://visualstudio.microsoft.com/downloads/
    echo.
    pause
    exit /b 1
)

echo OK: Encontrado Visual Studio %MSVC_VERSION%
echo Local: %MSVC_PATH%
echo.

REM Ativar MSVC
echo [2/6] Ativando ambiente MSVC...
call "%MSVC_PATH%" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar MSVC!
    pause
    exit /b 1
)
echo OK: MSVC ativado
echo.

REM Verificar compilador
echo [3/6] Verificando compilador C...
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: cl.exe nao encontrado no PATH!
    echo.
    echo Reinstale o Visual Studio com:
    echo - Desktop development with C++
    echo - MSVC v143 build tools
    pause
    exit /b 1
)
echo OK: Compilador encontrado
echo.

REM Verificar Nuitka
echo [4/6] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Nuitka...
    pip install nuitka ordered-set
)
echo OK: Nuitka instalado
echo.

REM Limpar builds anteriores
echo [5/6] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build 2>nul
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist 2>nul
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe 2>nul
if exist main.build rmdir /S /Q main.build 2>nul
if exist main.dist rmdir /S /Q main.dist 2>nul
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT 2>nul
echo OK: Limpo
echo.

echo [6/6] Compilando com Nuitka...
echo.
echo CONFIGURACAO:
echo - Visual Studio: %MSVC_VERSION%
echo - Python: 3.13.7
echo - Nuitka: 2.8.4
echo - Tempo estimado: 15-25 minutos
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --enable-plugin=tk-inter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=locales=locales ^
    --include-data-dir=config=config ^
    --include-data-dir=client=client ^
    --include-data-dir=ui=ui ^
    --include-data-dir=utils=utils ^
    --include-module=win32com ^
    --include-module=win32api ^
    --include-module=win32con ^
    --include-module=PIL._tkinter_finder ^
    --output-filename=FishingMageBOT.exe ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    --jobs=1 ^
    --low-memory ^
    --remove-output ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   ERRO NA COMPILACAO!
    echo ========================================
    echo.
    echo Veja nuitka-crash-report.xml para detalhes
    echo.
    echo DICAS:
    echo 1. Feche programas desnecessarios (Chrome, etc)
    echo 2. Execute como Administrador
    echo 3. Desative antivirus temporariamente
    echo 4. Verifique espaco em disco (minimo 5GB livre)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ORGANIZANDO DISTRIBUICAO
echo ========================================
echo.

REM Criar estrutura
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT

REM Mover executavel
move FishingMageBOT.exe dist\FishingMageBOT\ >nul 2>&1

REM Copiar recursos
echo Copiando templates...
xcopy /E /I /Y /Q templates dist\FishingMageBOT\templates\ >nul 2>&1
echo Copiando traducoes...
xcopy /E /I /Y /Q locales dist\FishingMageBOT\locales\ >nul 2>&1
echo Copiando configuracoes...
xcopy /E /I /Y /Q config dist\FishingMageBOT\config\ >nul 2>&1

REM Criar pasta data
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data

REM Criar README
(
echo ========================================
echo  FISHING MAGEBOT v5.0
echo ========================================
echo.
echo Compilado com:
echo - Visual Studio %MSVC_VERSION%
echo - Python 3.13.7
echo - Nuitka 2.8.4
echo.
echo COMO USAR:
echo 1. Execute FishingMageBOT.exe
echo 2. Configure nas abas
echo 3. Pressione F9 para iniciar
echo.
echo HOTKEYS:
echo F9  - Iniciar
echo F1  - Pausar
echo F2  - Parar
echo ESC - Emergencia
echo.
) > dist\FishingMageBOT\README.txt

echo OK: README criado
echo.

REM Limpar temporarios
echo Limpando temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build 2>nul
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist 2>nul
if exist main.build rmdir /S /Q main.build 2>nul
if exist main.dist rmdir /S /Q main.dist 2>nul
echo.

echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Visual Studio: %MSVC_VERSION%
echo Executavel: dist\FishingMageBOT\FishingMageBOT.exe
echo.
echo TESTAR:
echo   cd dist\FishingMageBOT
echo   FishingMageBOT.exe
echo.
echo DISTRIBUIR:
echo   Comprima a pasta dist\FishingMageBOT em ZIP
echo.
pause
