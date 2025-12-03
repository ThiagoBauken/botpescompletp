@echo off
chcp 65001 >nul
echo ============================================================
echo 🔍 VERIFICAÇÃO DE DEPENDÊNCIAS - FishingMageBot
echo ============================================================
echo.

echo 📋 1. Verificando Visual C++ Redistributable...
echo.

echo [x64 DLLs]:
dir "C:\Windows\System32\vcruntime*.dll" 2>nul
if errorlevel 1 (
    echo ❌ Não encontrado!
) else (
    echo ✅ Encontrado
)

echo.
echo [x86 DLLs]:
dir "C:\Windows\SysWOW64\vcruntime*.dll" 2>nul
if errorlevel 1 (
    echo ⚠️  Não encontrado ou sistema 32-bit
) else (
    echo ✅ Encontrado
)

echo.
echo [msvcp DLLs]:
dir "C:\Windows\System32\msvcp*.dll" 2>nul
if errorlevel 1 (
    echo ❌ Não encontrado!
) else (
    echo ✅ Encontrado
)

echo.
echo ============================================================
echo 📋 2. Verificando Resolução de Tela...
echo ============================================================
wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution
echo.

echo ============================================================
echo 📋 3. Verificando Templates de Peixes...
echo ============================================================
if exist "templates\SALMONN.png" (
    echo ✅ SALMONN.png
) else (
    echo ❌ SALMONN.png FALTANDO
)

if exist "templates\TROUTT.png" (
    echo ✅ TROUTT.png
) else (
    echo ❌ TROUTT.png FALTANDO
)

if exist "templates\shark.png" (
    echo ✅ shark.png
) else (
    echo ❌ shark.png FALTANDO
)

if exist "templates\sardine.png" (
    echo ✅ sardine.png
) else (
    echo ❌ sardine.png FALTANDO
)

if exist "templates\anchovy.png" (
    echo ✅ anchovy.png
) else (
    echo ❌ anchovy.png FALTANDO
)

if exist "templates\yellowperch.png" (
    echo ✅ yellowperch.png
) else (
    echo ❌ yellowperch.png FALTANDO
)

if exist "templates\herring.png" (
    echo ✅ herring.png
) else (
    echo ❌ herring.png FALTANDO
)

if exist "templates\catfish.png" (
    echo ✅ catfish.png
) else (
    echo ❌ catfish.png FALTANDO
)

if exist "templates\roughy.png" (
    echo ✅ roughy.png
) else (
    echo ❌ roughy.png FALTANDO
)

echo.
echo ============================================================
echo 📋 4. Testando Imports Python...
echo ============================================================
python -c "import cv2; print('✅ OpenCV (cv2) OK')" 2>nul
if errorlevel 1 (
    echo ❌ OpenCV (cv2) FALHOU - INSTALAR VISUAL C++!
)

python -c "import numpy; print('✅ NumPy OK')" 2>nul
if errorlevel 1 (
    echo ❌ NumPy FALHOU - INSTALAR VISUAL C++!
)

python -c "import pyautogui; print('✅ PyAutoGUI OK')" 2>nul
if errorlevel 1 (
    echo ❌ PyAutoGUI FALHOU
)

python -c "import serial; print('✅ PySerial OK')" 2>nul
if errorlevel 1 (
    echo ⚠️  PySerial não instalado (necessário apenas para Arduino)
)

echo.
echo ============================================================
echo 📊 RESUMO
echo ============================================================
echo.
echo Se todas as verificações acima passaram:
echo ✅ Sistema está pronto para rodar o bot!
echo.
echo Se alguma FALHOU:
echo 1. Instalar Visual C++ 2015-2022 (x64 E x86)
echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
echo    https://aka.ms/vs/17/release/vc_redist.x86.exe
echo.
echo 2. Instalar Visual C++ 2013 (x64 E x86)
echo    https://aka.ms/highdpimfc2013x64enu
echo    https://aka.ms/highdpimfc2013x86enu
echo.
echo 3. Reiniciar o PC após instalar
echo.
echo ============================================================
pause
