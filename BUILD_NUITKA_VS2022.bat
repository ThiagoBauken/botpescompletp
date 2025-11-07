@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - BUILD
echo   Visual Studio 2022 + Python 3.13
echo ========================================
echo.

REM Detectar Visual Studio 2022
set MSVC_PATH=
set MSVC_VERSION=

echo [1/7] Procurando Visual Studio 2022...

if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=Community
    echo OK: Visual Studio 2022 Community encontrado
    goto :msvc_found
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=Professional
    echo OK: Visual Studio 2022 Professional encontrado
    goto :msvc_found
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=BuildTools
    echo OK: Visual Studio 2022 BuildTools encontrado
    goto :msvc_found
)

if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat" (
    set MSVC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat
    set MSVC_VERSION=Enterprise
    echo OK: Visual Studio 2022 Enterprise encontrado
    goto :msvc_found
)

REM VS 2022 não encontrado
echo.
echo ERRO: Visual Studio 2022 nao encontrado!
echo.
echo Por favor, instale Visual Studio 2022:
echo https://visualstudio.microsoft.com/downloads/
echo.
echo Componentes necessarios:
echo - Desktop development with C++
echo - MSVC v143 build tools
echo - Windows 10/11 SDK
echo.
pause
exit /b 1

:msvc_found
echo Versao: %MSVC_VERSION%
echo.

REM Ativar ambiente MSVC 2022
echo [2/7] Ativando ambiente Visual Studio 2022...
call "%MSVC_PATH%"
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar MSVC!
    pause
    exit /b 1
)
echo OK: Ambiente MSVC ativado
echo.

REM Verificar compilador
echo [3/7] Verificando compilador C (cl.exe)...
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Compilador cl.exe nao encontrado!
    echo.
    echo Reinstale VS 2022 com componentes C++
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('where cl.exe') do set CL_PATH=%%i
echo OK: %CL_PATH%
echo.

REM Verificar Python
echo [4/7] Verificando Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do set PY_VER=%%v
echo OK: Python %PY_VER%
echo.

REM Verificar/Instalar Nuitka
echo [5/7] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Nuitka + ordered-set...
    pip install nuitka ordered-set
) else (
    echo OK: Nuitka ja instalado
)
echo.

REM Limpar builds anteriores
echo [6/7] Limpando builds anteriores...
if exist FishingMageBOT.build (
    echo Removendo FishingMageBOT.build...
    rmdir /S /Q FishingMageBOT.build 2>nul
)
if exist FishingMageBOT.dist (
    echo Removendo FishingMageBOT.dist...
    rmdir /S /Q FishingMageBOT.dist 2>nul
)
if exist FishingMageBOT.exe (
    echo Removendo FishingMageBOT.exe...
    del /Q FishingMageBOT.exe 2>nul
)
if exist main.build (
    echo Removendo main.build...
    rmdir /S /Q main.build 2>nul
)
if exist main.dist (
    echo Removendo main.dist...
    rmdir /S /Q main.dist 2>nul
)
if exist dist\FishingMageBOT (
    echo Removendo dist\FishingMageBOT...
    rmdir /S /Q dist\FishingMageBOT 2>nul
)
echo OK: Limpo
echo.

echo [7/7] Compilando com Nuitka + MSVC 2022...
echo.
echo ========================================
echo   CONFIGURACAO DA COMPILACAO
echo ========================================
echo Visual Studio: 2022 %MSVC_VERSION%
echo Python: %PY_VER%
echo Compilador: MSVC v143
echo Modo: Standalone + Onefile
echo Otimizacao: Low Memory (jobs=1)
echo Tempo estimado: 15-25 minutos
echo ========================================
echo.
echo ATENCAO: Nao feche esta janela!
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
    echo Codigo de erro: %errorlevel%
    echo.
    echo Veja o arquivo: nuitka-crash-report.xml
    echo.
    echo SOLUCOES POSSIVEIS:
    echo 1. Feche navegadores e programas pesados
    echo 2. Execute este script como Administrador
    echo 3. Desative antivirus temporariamente
    echo 4. Verifique espaco em disco (min 5GB)
    echo 5. Aumente memoria virtual do Windows
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ORGANIZANDO DISTRIBUICAO
echo ========================================
echo.

REM Criar estrutura de distribuicao
if not exist dist mkdir dist
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT

REM Mover executavel
echo Movendo executavel...
if exist FishingMageBOT.exe (
    move /Y FishingMageBOT.exe dist\FishingMageBOT\ >nul
    echo OK: FishingMageBOT.exe
) else (
    echo ERRO: FishingMageBOT.exe nao foi criado!
    pause
    exit /b 1
)

REM Copiar recursos
echo Copiando recursos...
xcopy /E /I /Y /Q templates dist\FishingMageBOT\templates\ >nul 2>&1
echo - templates\ [OK]
xcopy /E /I /Y /Q locales dist\FishingMageBOT\locales\ >nul 2>&1
echo - locales\ [OK]
xcopy /E /I /Y /Q config dist\FishingMageBOT\config\ >nul 2>&1
echo - config\ [OK]

REM Criar pasta data
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data
echo - data\ [OK]

REM Criar README detalhado
(
echo ========================================
echo  FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo INFORMACOES DE COMPILACAO:
echo - Visual Studio: 2022 %MSVC_VERSION%
echo - Python: %PY_VER%
echo - Compilador: MSVC v143 ^(C++^)
echo - Nuitka: 2.8.4
echo - Data: %date% %time%
echo.
echo ========================================
echo  COMO USAR
echo ========================================
echo.
echo 1. Execute FishingMageBOT.exe
echo 2. Configure nas abas da interface
echo 3. Pressione F9 para iniciar o bot
echo.
echo ========================================
echo  HOTKEYS
echo ========================================
echo.
echo F9  - Iniciar bot
echo F1  - Pausar/Retomar
echo F2  - Parar bot
echo ESC - Parada de emergencia
echo F4  - Mostrar/Ocultar interface
echo F6  - Alimentacao manual
echo F5  - Limpeza manual
echo.
echo ========================================
echo  ESTRUTURA DE PASTAS
echo ========================================
echo.
echo FishingMageBOT\
echo - FishingMageBOT.exe   ^(executavel principal^)
echo - templates\           ^(imagens para deteccao^)
echo - locales\             ^(traducoes PT/EN/RU/ES^)
echo - config\              ^(configuracoes padrao^)
echo - data\                ^(seus dados e logs^)
echo.
echo ========================================
echo  REQUISITOS DO SISTEMA
echo ========================================
echo.
echo - Windows 10/11 ^(64-bit^)
echo - 4GB RAM ^(minimo^)
echo - 500MB espaco em disco
echo - Resolucao: 1920x1080
echo.
echo ========================================
echo  VANTAGENS NUITKA
echo ========================================
echo.
echo - 3-5x mais rapido que PyInstaller
echo - Codigo compilado em C nativo
echo - Deteccao de templates otimizada
echo - Menor uso de memoria
echo - Startup instantaneo
echo.
echo ========================================
) > dist\FishingMageBOT\README.txt

echo - README.txt [OK]
echo.

REM Limpar arquivos temporarios
echo Limpando temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build 2>nul
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist 2>nul
if exist main.build rmdir /S /Q main.build 2>nul
if exist main.dist rmdir /S /Q main.dist 2>nul
echo OK: Limpo
echo.

echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Visual Studio: 2022 %MSVC_VERSION%
echo Python: %PY_VER%
echo.
echo EXECUTAVEL:
echo   dist\FishingMageBOT\FishingMageBOT.exe
echo.
echo TESTAR AGORA:
echo   cd dist\FishingMageBOT
echo   FishingMageBOT.exe
echo.
echo PARA DISTRIBUIR:
echo   1. Comprima a pasta "dist\FishingMageBOT" em ZIP
echo   2. Envie o arquivo ZIP para usuarios
echo   3. Usuarios extraem e executam FishingMageBOT.exe
echo.
echo TAMANHO DO PACOTE:
for /f "tokens=3" %%a in ('dir "dist\FishingMageBOT" ^| find "File(s)"') do echo   %%a bytes
echo.
pause
