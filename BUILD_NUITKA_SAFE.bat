@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo Compilando com Nuitka (codigo nativo C)
echo Muito mais rapido que PyInstaller!
echo.

REM Verificar se Nuitka esta instalado
echo [1/6] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Nuitka nao encontrado. Instalando...
    pip install nuitka
    pip install ordered-set
) else (
    echo OK: Nuitka ja instalado!
)
echo.

REM Verificar compilador C (MSVC ou MinGW)
echo [2/6] Verificando compilador C...
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo MSVC nao encontrado. Tentando MinGW...
    where gcc.exe >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERRO: Nenhum compilador C encontrado!
        echo.
        echo SOLUCOES:
        echo 1. Instale Visual Studio Build Tools
        echo    https://visualstudio.microsoft.com/downloads/
        echo    (Selecione "Build Tools for Visual Studio")
        echo.
        echo 2. OU instale MinGW-w64
        echo    https://www.mingw-w64.org/
        echo.
        pause
        exit /b 1
    ) else (
        echo OK: MinGW encontrado!
        set COMPILER=--mingw64
    )
) else (
    echo OK: MSVC encontrado!
    set COMPILER=--msvc=latest
)
echo.

REM Limpar builds anteriores
echo [3/6] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo OK: Limpeza concluida!
echo.

echo [4/6] Compilando com Nuitka...
echo Primeira compilacao pode levar 10-15 minutos...
echo (compilacoes seguintes serao muito mais rapidas)
echo.

nuitka --standalone --onefile --windows-disable-console --windows-icon-from-ico=icon.ico --enable-plugin=tk-inter --include-data-dir=client=client --include-data-dir=ui=ui --include-package=PIL --include-package=cv2 --include-package=numpy --include-package=mss --include-package=keyboard --include-package=pyautogui --include-package=serial --include-package=websocket --include-package=cryptography --output-filename=FishingMageBOT.exe %COMPILER% --assume-yes-for-downloads --show-progress --show-memory main.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Compilacao Nuitka falhou!
    pause
    exit /b 1
)

echo.
echo [5/6] Organizando arquivos...

REM Criar pasta de distribuicao
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT

REM Mover executavel
move FishingMageBOT.exe dist\FishingMageBOT\ >nul

REM Copiar pastas necessarias
echo Copiando templates...
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
echo Copiando traducoes...
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul
echo Copiando configuracoes...
xcopy /E /I /Y config dist\FishingMageBOT\config\ >nul

REM Criar pasta data
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data

echo OK: Arquivos organizados (GIF incluido em templates/)!
echo.

echo [6/6] Criando README...
(
echo ========================================
echo  FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo COMPILADO COM NUITKA (CODIGO NATIVO C)
echo    Muito mais rapido que versoes Python!
echo.
echo COMO USAR:
echo 1. Execute "FishingMageBOT.exe"
echo 2. Configure as opcoes nas abas
echo 3. Pressione F9 para iniciar o bot
echo.
echo REQUISITOS:
echo - Windows 10/11 (64-bit)
echo - Arduino Leonardo conectado
echo - Licenca valida
echo.
echo HOTKEYS PRINCIPAIS:
echo F9  - Iniciar bot
echo F1  - Pausar/Continuar
echo F2  - Parar bot
echo ESC - Parada de emergencia
echo F4  - Mostrar/Ocultar interface
echo.
echo ESTRUTURA DE PASTAS:
echo - templates/      Imagens para deteccao
echo - locales/        Traducoes (PT/EN/RU/ES)
echo - config/         Configuracoes padrao
echo - data/           Seus dados e configuracoes
echo.
echo IDIOMAS DISPONIVEIS:
echo - Portugues (PT)
echo - English (EN)
echo - Russkiy (RU)
echo - Espanol (ES)
echo.
echo VANTAGENS DA VERSAO NUITKA:
echo - 3-5x mais rapido que PyInstaller
echo - Deteccao de templates mais rapida
echo - Menor uso de memoria RAM
echo - Startup mais rapido
echo - Codigo otimizado nativamente
echo.
echo IMPORTANTE:
echo - NAO delete as pastas templates, locales, config, client e ui
echo - Seus dados ficam salvos na pasta data/
echo - Logs sao criados automaticamente em data/logs/
echo - Screenshots acumulam em data/screenshots/
echo - Use LIMPAR_SCREENSHOTS.bat para limpar screenshots antigos
echo.
echo ========================================
) > dist\FishingMageBOT\README.txt

echo OK: README criado!
echo.

REM Limpar arquivos temporarios de build
echo Limpando arquivos temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
echo.

echo ========================================
echo   BUILD NUITKA CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Pacote pronto em: dist\FishingMageBOT\
echo.
echo ESTRUTURA DO PACOTE:
echo   FishingMageBOT\
echo   - FishingMageBOT.exe    (EXECUTAVEL NATIVO C)
echo   - templates\            (Deteccao de imagens)
echo   - locales\              (4 idiomas)
echo   - config\               (Configuracoes)
echo   - data\                 (Dados do usuario)
echo   - README.txt            (Instrucoes)
echo.
echo VANTAGENS NUITKA vs PyInstaller:
echo    - 3-5x mais rapido
echo    - Menor tamanho do .exe (arquivo unico)
echo    - Sem pasta _internal
echo    - Codigo nativo C otimizado
echo.
echo COMO DISTRIBUIR:
echo    1. Comprima a pasta "FishingMageBOT" em ZIP
echo    2. Envie o arquivo ZIP para os usuarios
echo    3. Usuarios extraem e executam FishingMageBOT.exe
echo.
pause
