@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   🎣 FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo 🚀 Compilando com Nuitka (código nativo C)
echo ⚡ Muito mais rápido que PyInstaller!
echo.

REM Verificar se Nuitka está instalado
echo [1/6] 📦 Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Nuitka não encontrado. Instalando...
    pip install nuitka
    pip install ordered-set
) else (
    echo ✅ Nuitka já instalado!
)
echo.

REM Verificar compilador C (MSVC ou MinGW)
echo [2/6] 🔧 Verificando compilador C...
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  MSVC não encontrado. Tentando MinGW...
    where gcc.exe >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ❌ ERRO: Nenhum compilador C encontrado!
        echo.
        echo 📋 SOLUÇÕES:
        echo 1. Instale Visual Studio Build Tools
        echo    https://visualstudio.microsoft.com/downloads/
        echo    ^(Selecione "Build Tools for Visual Studio"^)
        echo.
        echo 2. OU instale MinGW-w64
        echo    https://www.mingw-w64.org/
        echo.
        pause
        exit /b 1
    ) else (
        echo ✅ MinGW encontrado!
        set COMPILER=--mingw64
    )
) else (
    echo ✅ MSVC encontrado!
    set COMPILER=--msvc=latest
)
echo.

REM Limpar builds anteriores
echo [3/6] 🧹 Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo ✅ Limpeza concluída!
echo.

echo [4/6] ⚙️  Compilando com Nuitka...
echo ⏳ Primeira compilação pode levar 10-15 minutos...
echo    (compilações seguintes serão muito mais rápidas)
echo.

nuitka ^
    --onefile ^
    --windows-disable-console ^
    --windows-icon-from-ico=magoicon.ico ^
    --company-name="FishingMageBOT" ^
    --product-name="FishingMageBOT v5.0" ^
    --file-version=5.0.0.0 ^
    --product-version=5.0.0.0 ^
    --file-description="Ultimate Fishing Bot - Protected Edition" ^
    --copyright="Copyright 2025" ^
    --enable-plugin=tk-inter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=locales=locales ^
    --include-data-dir=config=config ^
    --include-data-dir=client=client ^
    --include-data-dir=ui=ui ^
    --include-data-dir=core=core ^
    --include-data-dir=utils=utils ^
    --include-data-file=templates/motion.gif=templates/motion.gif ^
    --include-data-file=magoicon.ico=magoicon.ico ^
    --include-package=PIL ^
    --include-package=cv2 ^
    --include-package=numpy ^
    --include-package=mss ^
    --include-package=keyboard ^
    --include-package=pyautogui ^
    --include-package=serial ^
    --include-package=websockets ^
    --include-package=asyncio ^
    --include-package=requests ^
    --include-package=cryptography ^
    --include-package=certifi ^
    --follow-imports ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=pandas ^
    --nofollow-import-to=scipy ^
    --nofollow-import-to=IPython ^
    --lto=yes ^
    --output-filename=FishingMageBOT.exe ^
    %COMPILER% ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --remove-output ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Compilação Nuitka falhou!
    pause
    exit /b 1
)

echo.
echo [5/6] 📂 Organizando arquivos...

REM Criar pasta de distribuição
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT

REM Mover executável
move FishingMageBOT.exe dist\FishingMageBOT\ >nul

REM Copiar pastas necessárias
echo Copiando templates...
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
echo Copiando traduções...
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul
echo Copiando configurações...
xcopy /E /I /Y config dist\FishingMageBOT\config\ >nul

REM Criar pasta data
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data

echo ✅ Arquivos organizados (GIF incluído em templates/)!
echo.

echo [6/6] 📝 Criando README...
(
echo ========================================
echo  🎣 FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo ⚡ COMPILADO COM NUITKA ^(CÓDIGO NATIVO C^)
echo    Muito mais rápido que versões Python!
echo.
echo 🚀 COMO USAR:
echo 1. Execute "FishingMageBOT.exe"
echo 2. Configure as opções nas abas
echo 3. Pressione F9 para iniciar o bot
echo.
echo ⚙️  REQUISITOS:
echo - Windows 10/11 ^(64-bit^)
echo - Arduino Leonardo conectado
echo - Licença válida
echo.
echo ⌨️  HOTKEYS PRINCIPAIS:
echo F9  - Iniciar bot
echo F1  - Pausar/Continuar
echo F2  - Parar bot
echo ESC - Parada de emergência
echo F4  - Mostrar/Ocultar interface
echo.
echo 📁 ESTRUTURA DE PASTAS:
echo - templates/      Imagens para detecção
echo - locales/        Traduções ^(PT/EN/RU/ES^)
echo - config/         Configurações padrão
echo - data/           Seus dados e configurações
echo.
echo 🌍 IDIOMAS DISPONÍVEIS:
echo - Português ^(PT^)
echo - English ^(EN^)
echo - Русский ^(RU^)
echo - Español ^(ES^)
echo.
echo ⚡ VANTAGENS DA VERSÃO NUITKA:
echo ✅ 3-5x mais rápido que PyInstaller
echo ✅ Detecção de templates mais rápida
echo ✅ Menor uso de memória RAM
echo ✅ Startup mais rápido
echo ✅ Código otimizado nativamente
echo.
echo ⚠️  IMPORTANTE:
echo - NÃO delete as pastas templates, locales, config, client e ui
echo - Seus dados ficam salvos na pasta data/
echo - Logs são criados automaticamente em data/logs/
echo - Screenshots acumulam em data/screenshots/ e fishing_bot_v4/screenshots/
echo - Use LIMPAR_SCREENSHOTS.bat para limpar screenshots antigos
echo.
echo 💬 SUPORTE:
echo Discord: [Seu Discord]
echo GitHub: [Seu GitHub]
echo ========================================
) > dist\FishingMageBOT\README.txt

echo ✅ README criado!
echo.

REM Limpar arquivos temporários de build
echo 🧹 Limpando arquivos temporários...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
echo.

echo ========================================
echo   ✅ BUILD NUITKA CONCLUÍDO COM SUCESSO!
echo ========================================
echo.
echo 📦 Pacote pronto em: dist\FishingMageBOT\
echo.
echo 📊 TAMANHO DO EXECUTÁVEL:
for %%A in (dist\FishingMageBOT\FishingMageBOT.exe) do echo    %%~zA bytes ^(~%%~zA KB^)
echo.
echo 📁 ESTRUTURA DO PACOTE:
echo   FishingMageBOT\
echo   ├── ⚡ FishingMageBOT.exe    ^(EXECUTÁVEL NATIVO C^)
echo   ├── 📂 templates\             ^(Detecção de imagens^)
echo   ├── 🌍 locales\               ^(4 idiomas^)
echo   ├── ⚙️  config\                ^(Configurações^)
echo   ├── 💾 data\                  ^(Dados do usuário^)
echo   └── 📝 README.txt             ^(Instruções^)
echo.
echo ⚡ VANTAGENS NUITKA vs PyInstaller:
echo    ✅ 3-5x mais rápido
echo    ✅ Menor tamanho do .exe ^(arquivo único^)
echo    ✅ Sem pasta _internal
echo    ✅ Código nativo C otimizado
echo.
echo 💡 COMO DISTRIBUIR:
echo    1. Comprima a pasta "FishingMageBOT" em ZIP
echo    2. Envie o arquivo ZIP para os usuários
echo    3. Usuários extraem e executam FishingMageBOT.exe
echo.
pause
