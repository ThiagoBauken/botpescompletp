@echo off
cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - NUITKA BUILD
echo   COMPATIVEL COM PYTHON 3.13+
echo ========================================
echo.
echo Compilando com Nuitka (codigo nativo C)
echo Muito mais rapido que PyInstaller!
echo.

REM Verificar se Nuitka esta instalado
echo [1/6] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Nuitka nao encontrado. Instalando versao mais recente...
    pip install --upgrade nuitka
    pip install ordered-set
) else (
    echo OK - Nuitka ja instalado!
    echo Atualizando para versao mais recente...
    pip install --upgrade nuitka
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
        echo.
        echo 2. OU instale MinGW-w64
        echo    https://www.mingw-w64.org/
        echo.
        pause
        exit /b 1
    ) else (
        echo OK - MinGW encontrado!
        set COMPILER=--mingw64
    )
) else (
    echo OK - MSVC encontrado!
    set COMPILER=--msvc=latest
)
echo.

REM Limpar cache Python primeiro (CRITICO para evitar erros!)
echo [3/8] Limpando cache Python (__pycache__, .pyc)...
if exist "__pycache__" rmdir /S /Q "__pycache__"
if exist "ui\__pycache__" rmdir /S /Q "ui\__pycache__"
if exist "utils\__pycache__" rmdir /S /Q "utils\__pycache__"
if exist "core\__pycache__" rmdir /S /Q "core\__pycache__"
if exist "client\__pycache__" rmdir /S /Q "client\__pycache__"
del /s /q *.pyc 2>nul
echo OK - Cache Python limpo!
echo.

REM Limpar builds anteriores
echo [4/8] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo OK - Limpeza concluida!
echo.

echo [5/8] Compilando com Nuitka (modo Python 3.13+)...
echo Primeira compilacao pode levar 10-15 minutos...
echo (compilacoes seguintes serao muito mais rapidas)
echo.

REM ===================================================================
REM VERSAO COMPATIVEL PYTHON 3.13+
REM Removido: --lto=yes (problematico em Python 3.13+)
REM Removido: --jobs (deixar Nuitka decidir)
REM Adicionado: --python-flag=-OO (otimizacao)
REM ===================================================================

nuitka ^
    --onefile ^
    --standalone ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=magoicon.ico ^
    --company-name="FishingMageBOT" ^
    --product-name="FishingMageBOT v5.0" ^
    --file-version=5.0.5.0 ^
    --product-version=5.0.5.0 ^
    --file-description="Ultimate Fishing Bot - Protected Edition" ^
    --copyright="Copyright 2025" ^
    --enable-plugin=tk-inter ^
    --include-data-dir=templates=templates ^
    --include-data-dir=locales=locales ^
    --include-data-file=config/default_config.json=config/default_config.json ^
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
    --include-package=psutil ^
    --include-package=win32gui ^
    --follow-imports ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=pandas ^
    --nofollow-import-to=scipy ^
    --nofollow-import-to=IPython ^
    --python-flag=-OO ^
    --output-filename=FishingMageBOT.exe ^
    %COMPILER% ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --remove-output ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Compilacao Nuitka falhou!
    echo.
    echo SE O ERRO FOI RELACIONADO A PYTHON 3.13:
    echo Considere fazer downgrade para Python 3.11 ou 3.12
    echo   py -3.11 -m pip install -r requirements.txt
    echo   py -3.11 -m nuitka ...
    echo.
    pause
    exit /b 1
)

echo.
echo [6/8] Organizando arquivos...

REM Criar pasta de distribuicao
if not exist dist\FishingMageBOT mkdir dist\FishingMageBOT

REM Mover executavel
move FishingMageBOT.exe dist\FishingMageBOT\ >nul

REM Copiar pastas necessarias
echo Copiando templates...
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
echo Copiando traducoes...
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul

REM Criar pasta config e copiar APENAS default_config.json
echo Copiando configuracoes padrao...
if not exist dist\FishingMageBOT\config mkdir dist\FishingMageBOT\config
copy /Y config\default_config.json dist\FishingMageBOT\config\ >nul

REM Criar pasta data (para configuracoes do usuario)
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data
echo Pasta data/ criada (para configuracoes do usuario)

echo OK - Arquivos organizados!
echo.

echo [7/8] Criando README...
(
echo ========================================
echo  FISHING MAGEBOT v5.0.5 - NUITKA BUILD
echo  COMPILADO COM PYTHON 3.13+
echo ========================================
echo.
echo COMPILADO COM NUITKA
echo Muito mais rapido que versoes Python!
echo.
echo COMO USAR:
echo 1. Execute FishingMageBOT.exe
echo 2. Configure as opcoes nas abas
echo 3. Pressione F9 para iniciar o bot
echo.
echo HOTKEYS PRINCIPAIS:
echo F9  - Iniciar bot
echo F1  - Pausar/Continuar
echo F2  - Parar bot
echo ESC - Parada de emergencia
echo.
echo ESTRUTURA DE PASTAS:
echo - templates/      Imagens para deteccao
echo - locales/        Traducoes
echo - config/         Configuracoes padrao
echo - data/           Seus dados e configuracoes
echo.
echo VANTAGENS DA VERSAO NUITKA:
echo - 3-5x mais rapido que PyInstaller
echo - Deteccao de templates mais rapida
echo - Codigo nativo C otimizado
echo.
echo IMPORTANTE:
echo - NAO delete as pastas templates e locales
echo - Seus dados ficam salvos na pasta data/
echo.
) > dist\FishingMageBOT\README.txt

echo OK - README criado!
echo.

REM Limpar arquivos temporarios de build
echo [8/8] Limpando arquivos temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
echo.

echo ========================================
echo BUILD NUITKA CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Pacote pronto em: dist\FishingMageBOT
echo.
for %%A in (dist\FishingMageBOT\FishingMageBOT.exe) do echo TAMANHO: %%~zA bytes
echo.
echo COMO DISTRIBUIR:
echo 1. Comprima a pasta FishingMageBOT em ZIP
echo 2. Envie o arquivo ZIP para os usuarios
echo 3. Usuarios extraem e executam FishingMageBOT.exe
echo.
pause
