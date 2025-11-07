@echo off
echo ========================================
echo   LIMPEZA DE PRINTS E SCREENSHOTS
echo ========================================
echo.

echo Procurando por prints fora da pasta templates...
echo.

REM Procurar prints em pastas que nao deveriam ter
set FOUND=0

echo Verificando fishing_bot_v4...
if exist fishing_bot_v4\*.png (
    echo ❌ ENCONTRADO: Prints em fishing_bot_v4\
    dir /B fishing_bot_v4\*.png
    set FOUND=1
)
if exist fishing_bot_v4\*.jpg (
    dir /B fishing_bot_v4\*.jpg
    set FOUND=1
)

echo.
echo Verificando pasta raiz...
for %%f in (*.png *.jpg *.jpeg *.bmp) do (
    if exist "%%f" (
        echo ❌ ENCONTRADO: %%f
        set FOUND=1
    )
)

echo.
echo Verificando data\...
if exist data\*.png (
    echo ❌ ENCONTRADO: Prints em data\
    dir /B data\*.png
    set FOUND=1
)
if exist data\*.jpg (
    dir /B data\*.jpg
    set FOUND=1
)

echo.
echo Verificando core\, ui\, utils\...
for /R core %%f in (*.png *.jpg) do (
    echo ❌ ENCONTRADO: %%f
    set FOUND=1
)
for /R ui %%f in (*.png *.jpg) do (
    echo ❌ ENCONTRADO: %%f
    set FOUND=1
)
for /R utils %%f in (*.png *.jpg) do (
    echo ❌ ENCONTRADO: %%f
    set FOUND=1
)

echo.
echo ========================================
if %FOUND%==0 (
    echo ✅ Nenhum print desnecessario encontrado!
    echo.
    pause
    exit /b 0
)

echo.
echo ⚠️ Prints encontrados!
echo.
echo Deseja DELETAR todos os prints acima? (S/N)
choice /C SN /M "Confirmar"

if errorlevel 2 (
    echo.
    echo ❌ Cancelado pelo usuario.
    pause
    exit /b 0
)

echo.
echo 🗑️ Deletando prints...

REM Deletar prints
del /Q fishing_bot_v4\*.png 2>nul
del /Q fishing_bot_v4\*.jpg 2>nul
del /Q fishing_bot_v4\*.jpeg 2>nul
del /Q fishing_bot_v4\*.bmp 2>nul

del /Q *.png 2>nul
del /Q *.jpg 2>nul
del /Q *.jpeg 2>nul
del /Q *.bmp 2>nul

del /Q data\*.png 2>nul
del /Q data\*.jpg 2>nul

for /R core %%f in (*.png *.jpg) do del /Q "%%f" 2>nul
for /R ui %%f in (*.png *.jpg) do del /Q "%%f" 2>nul
for /R utils %%f in (*.png *.jpg) do del /Q "%%f" 2>nul

echo.
echo ✅ Prints deletados!
echo.
echo 📂 Templates preservados em: templates\
echo.
pause
