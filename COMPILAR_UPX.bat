@echo off
chcp 65001 >nul
echo ========================================
echo   COMPILADOR UPX - FishingBot v5.0
echo   (Tamanho Reduzido ~40-50%)
echo ========================================
echo.

echo [1/6] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ PyInstaller não encontrado. Instalando...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller instalado
)
echo.

echo [2/6] Baixando UPX (se necessário)...
if not exist "upx.exe" (
    echo ⚠️ UPX não encontrado. Baixando...
    echo    Visite: https://github.com/upx/upx/releases/latest
    echo    Baixe: upx-X.XX-win64.zip
    echo    Extraia upx.exe para esta pasta
    echo.
    echo ❌ Por favor, baixe UPX manualmente e execute novamente
    pause
    exit /b 1
) else (
    echo ✅ UPX encontrado
    upx --version
)
echo.

echo [3/6] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo ✅ Pastas limpas
echo.

echo [4/6] Compilando com PyInstaller + UPX...
echo    Aguarde, isso pode levar 3-5 minutos...
echo.
pyinstaller FishingBot.spec
echo.

if %errorlevel% neq 0 (
    echo ❌ ERRO na compilação!
    pause
    exit /b 1
)

echo [5/6] Verificando resultado...
if exist "dist\FishingBot_v5.0.exe" (
    echo ✅ FishingBot_v5.0.exe criado com sucesso!
    echo.
    echo 📊 Tamanho do arquivo:
    for %%A in ("dist\FishingBot_v5.0.exe") do echo    %%~zA bytes (%%~zAKB)
) else (
    echo ❌ Executável não encontrado!
    pause
    exit /b 1
)
echo.

echo [6/6] Criando release...
if not exist "release" mkdir release
copy "dist\FishingBot_v5.0.exe" "release\" >nul
echo ✅ Copiado para release\
echo.

echo ========================================
echo   ✅ COMPILAÇÃO UPX CONCLUÍDA!
echo ========================================
echo.
echo 📦 Executável: release\FishingBot_v5.0.exe
echo 📉 Tamanho reduzido em ~40-50%
echo.
pause
explorer release
