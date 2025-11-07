@echo off
chcp 65001 >nul 2>&1

REM Mudar para o diretorio do script
cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - NUITKA BUILD
echo   MSVC Manual Activation
echo ========================================
echo.

REM Ativar ambiente MSVC 2019 BuildTools
echo [1/6] Ativando MSVC 2019 BuildTools...
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel ativar MSVC!
    pause
    exit /b 1
)
echo.
echo OK: MSVC ativado!
echo.

REM Verificar cl.exe
echo [2/6] Verificando compilador...
where cl.exe
if %errorlevel% neq 0 (
    echo ERRO: cl.exe nao encontrado!
    pause
    exit /b 1
)
echo.
echo OK: Compilador encontrado!
echo.

REM Verificar Nuitka
echo [3/6] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Nuitka...
    pip install nuitka ordered-set
)
echo OK: Nuitka instalado!
echo.

REM Limpar builds
echo [4/6] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo OK!
echo.

echo [5/6] Compilando com Nuitka + MSVC...
echo IMPORTANTE: Janela do CMD ficara aberta ate terminar!
echo Tempo estimado: 15-25 minutos
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
    --output-filename=FishingMageBOT.exe ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    --jobs=1 ^
    --low-memory ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Compilacao falhou!
    echo.
    echo Veja o arquivo nuitka-crash-report.xml para detalhes
    pause
    exit /b 1
)

echo.
echo [6/6] Organizando arquivos...
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT
move FishingMageBOT.exe dist\FishingMageBOT\ >nul
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul
xcopy /E /I /Y config dist\FishingMageBOT\config\ >nul
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data

REM Limpar temporarios
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist

echo.
echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Executavel: dist\FishingMageBOT\FishingMageBOT.exe
echo.
echo Compilado com MSVC 2019 BuildTools (14.29)
echo.
pause
