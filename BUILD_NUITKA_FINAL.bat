@echo off
chcp 65001 >nul 2>&1

cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - BUILD FINAL
echo   Python 3.13 + MSVC 14.29
echo ========================================
echo.

REM IMPORTANTE: Ativar MSVC ANTES de chamar Nuitka
echo [1/5] Ativando MSVC 2019 BuildTools...
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: MSVC nao encontrado!
    echo.
    echo Instale Visual Studio 2019 Build Tools:
    echo https://aka.ms/vs/16/release/vs_buildtools.exe
    pause
    exit /b 1
)
echo OK: MSVC 14.29 ativado
echo.

REM Verificar compilador
echo [2/5] Verificando compilador C...
cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    where cl.exe >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Compilador nao encontrado no PATH!
        pause
        exit /b 1
    )
)
echo OK: Compilador pronto
echo.

REM Limpar builds
echo [3/5] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build 2>nul
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist 2>nul
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe 2>nul
if exist main.build rmdir /S /Q main.build 2>nul
if exist main.dist rmdir /S /Q main.dist 2>nul
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT 2>nul
echo OK: Limpo
echo.

echo [4/5] Compilando (15-25 min)...
echo.
echo CONFIGURACAO:
echo - Python 3.13.7
echo - MSVC 14.29 (BuildTools 2019)
echo - Standalone + Onefile
echo - Todas as pastas incluidas
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
    echo Verifique nuitka-crash-report.xml
    echo.
    echo POSSIVEL SOLUCAO:
    echo 1. Feche programas para liberar RAM
    echo 2. Execute como Administrador
    echo 3. Desative antivirus temporariamente
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Organizando distribuicao...
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT
move FishingMageBOT.exe dist\FishingMageBOT\ >nul 2>&1
xcopy /E /I /Y /Q templates dist\FishingMageBOT\templates\ >nul 2>&1
xcopy /E /I /Y /Q locales dist\FishingMageBOT\locales\ >nul 2>&1
xcopy /E /I /Y /Q config dist\FishingMageBOT\config\ >nul 2>&1
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data

REM Criar README
echo Fishing MageBot v5.0 > dist\FishingMageBOT\README.txt
echo Compilado com Nuitka + MSVC >> dist\FishingMageBOT\README.txt
echo Python 3.13.7 >> dist\FishingMageBOT\README.txt

REM Limpar temporarios
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build 2>nul
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist 2>nul
if exist main.build rmdir /S /Q main.build 2>nul
if exist main.dist rmdir /S /Q main.dist 2>nul

echo.
echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Executavel: dist\FishingMageBOT\FishingMageBOT.exe
echo.
echo Teste executando:
echo   cd dist\FishingMageBOT
echo   FishingMageBOT.exe
echo.
pause
