@echo off
chcp 65001 >nul
echo ========================================
echo   COMPILADOR - FishingBot v5.0
echo ========================================
echo.

echo [1/5] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo   PyInstaller não encontrado. Instalando...
    pip install pyinstaller
) else (
    echo  PyInstaller instalado
)
echo.

echo [2/5] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo  Pastas limpas
echo.

echo [3/5] Compilando com PyInstaller...
echo    Aguarde, isso pode levar alguns minutos...
echo.
pyinstaller FishingBot.spec
echo.

if %errorlevel% neq 0 (
    echo L ERRO na compilação!
    echo    Verifique os erros acima.
    pause
    exit /b 1
)

echo [4/5] Verificando executável...
if exist "dist\FishingBot_v5.0.exe" (
    echo  FishingBot_v5.0.exe criado com sucesso!
    echo    Tamanho:
    dir "dist\FishingBot_v5.0.exe" | findstr "FishingBot"
) else (
    echo L Executável não encontrado!
    pause
    exit /b 1
)
echo.

echo [5/5] Criando pasta de release...
if not exist "release" mkdir release
copy "dist\FishingBot_v5.0.exe" "release\" >nul
echo  Copiado para pasta release\
echo.

echo ========================================
echo    COMPILAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Executável: release\FishingBot_v5.0.exe
echo.
echo Pressione qualquer tecla para abrir pasta...
pause >nul
explorer release
