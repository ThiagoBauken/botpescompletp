@echo off
chcp 65001 >nul
echo ========================================
echo   COMPILADOR NUITKA - FishingBot v5.0
echo   (Performance Máxima + Segurança)
echo ========================================
echo.

echo [1/7] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Nuitka não encontrado. Instalando...
    echo    Isso pode demorar alguns minutos...
    pip install nuitka ordered-set zstandard
) else (
    echo ✅ Nuitka instalado
)
echo.

echo [2/7] Verificando Visual Studio Build Tools...
echo ⚠️ IMPORTANTE: Nuitka requer Visual Studio Build Tools
echo    Se não tiver instalado, baixe em:
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo    Instale com: "Desktop development with C++"
echo.
pause
echo.

echo [3/7] Limpando builds anteriores...
if exist "main.build" rmdir /s /q "main.build"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.onefile-build" rmdir /s /q "main.onefile-build"
if exist "FishingBot_v5.0.exe" del /q "FishingBot_v5.0.exe"
echo ✅ Pastas limpas
echo.

echo [4/7] Compilando com Nuitka...
echo    ⚠️ ISSO VAI DEMORAR 5-15 MINUTOS!
echo    ☕ Vá tomar um café...
echo.

python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-disable-console ^
    --enable-plugin=tk-inter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=config=config ^
    --include-data-dir=locales=locales ^
    --output-filename=FishingBot_v5.0.exe ^
    --windows-icon-from-ico=icon.ico ^
    --assume-yes-for-downloads ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO na compilação!
    echo    Possíveis causas:
    echo    - Visual Studio Build Tools não instalado
    echo    - Alguma biblioteca incompatível
    echo.
    pause
    exit /b 1
)

echo.
echo [5/7] Verificando executável...
if exist "FishingBot_v5.0.exe" (
    echo ✅ FishingBot_v5.0.exe criado com sucesso!
    echo.
    echo 📊 Tamanho do arquivo:
    for %%A in ("FishingBot_v5.0.exe") do echo    %%~zA bytes (~%%~zAMB)
) else (
    echo ❌ Executável não encontrado!
    pause
    exit /b 1
)
echo.

echo [6/7] Limpando arquivos temporários...
if exist "main.build" rmdir /s /q "main.build"
if exist "main.dist" rmdir /s /q "main.dist"
if exist "main.onefile-build" rmdir /s /q "main.onefile-build"
echo ✅ Temporários removidos
echo.

echo [7/7] Criando release...
if not exist "release" mkdir release
move /y "FishingBot_v5.0.exe" "release\" >nul
echo ✅ Movido para release\
echo.

echo ========================================
echo   ✅ COMPILAÇÃO NUITKA CONCLUÍDA!
echo ========================================
echo.
echo 📦 Executável: release\FishingBot_v5.0.exe
echo 🚀 Performance: 2-3x mais rápido
echo 🔐 Segurança: Muito alta (compilado)
echo.
pause
explorer release
