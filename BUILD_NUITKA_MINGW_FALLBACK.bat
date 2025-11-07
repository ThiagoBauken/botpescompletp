@echo off
chcp 65001 >nul 2>&1

REM Mudar para o diretorio do script
cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - NUITKA BUILD
echo   MinGW64 Fallback (Python 3.13)
echo ========================================
echo.
echo AVISO: Usando MinGW64 como fallback
echo Nuitka pode ter limitacoes com Python 3.13
echo.

REM Verificar se Nuitka esta instalado
echo [1/5] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Nuitka...
    pip install nuitka
    pip install ordered-set
) else (
    echo OK: Nuitka ja instalado!
)
echo.

REM Limpar builds anteriores
echo [2/5] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo OK: Limpeza concluida!
echo.

echo [3/5] Compilando com Nuitka (MinGW64 auto-download)...
echo Primeira compilacao pode levar 15-25 minutos...
echo.

nuitka ^
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
    --output-filename=FishingMageBOT.exe ^
    --mingw64 ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    --jobs=1 ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Compilacao falhou!
    echo.
    echo Tente a Opcao 2: BUILD_NUITKA_MSVC_MANUAL.bat
    pause
    exit /b 1
)

echo.
echo [4/5] Organizando arquivos...
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT
move FishingMageBOT.exe dist\FishingMageBOT\ >nul
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul
xcopy /E /I /Y config dist\FishingMageBOT\config\ >nul
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data
echo OK!
echo.

echo [5/5] Limpando temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist
echo.

echo ========================================
echo   BUILD CONCLUIDO!
echo ========================================
echo.
echo Executavel em: dist\FishingMageBOT\FishingMageBOT.exe
echo.
pause
