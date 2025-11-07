@echo off
chcp 65001 >nul 2>&1

REM Mudar para o diretorio do script
cd /d "%~dp0"

cls
echo ========================================
echo   FISHING MAGEBOT v5.0 - NUITKA BUILD
echo   Python 3.13 + MSVC (CORRIGIDO)
echo ========================================
echo.
echo Diretorio de trabalho: %CD%
echo.

REM Ativar ambiente MSVC 2019
echo [1/8] Ativando ambiente Visual Studio 2019...
call "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Nao foi possivel ativar ambiente MSVC
    pause
    exit /b 1
)
echo OK: Ambiente MSVC ativado!
echo.

REM Verificar se Nuitka esta instalado
echo [2/8] Verificando Nuitka...
pip show nuitka >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Nuitka...
    pip install nuitka
    pip install ordered-set
) else (
    echo OK: Nuitka ja instalado!
)
echo.

REM Verificar compilador
echo [3/8] Verificando compilador C...
where cl.exe >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: MSVC nao encontrado no PATH
    pause
    exit /b 1
)
echo OK: MSVC encontrado!
echo.

REM Verificar pastas necessarias
echo [4/8] Verificando recursos...
set MISSING_DIRS=0

if not exist "templates" (
    echo ERRO: Pasta templates nao encontrada!
    set MISSING_DIRS=1
)
if not exist "locales" (
    echo ERRO: Pasta locales nao encontrada!
    set MISSING_DIRS=1
)
if not exist "config" (
    echo ERRO: Pasta config nao encontrada!
    set MISSING_DIRS=1
)
if not exist "utils" (
    echo ERRO: Pasta utils nao encontrada!
    set MISSING_DIRS=1
)
if not exist "icon.ico" (
    echo ERRO: Arquivo icon.ico nao encontrado!
    set MISSING_DIRS=1
)

if %MISSING_DIRS%==1 (
    echo.
    echo ERRO: Recursos necessarios nao encontrados!
    pause
    exit /b 1
)

echo OK: Todos os recursos encontrados!
echo.

REM Limpar builds anteriores
echo [5/8] Limpando builds anteriores...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist FishingMageBOT.exe del /Q FishingMageBOT.exe
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist
if exist dist\FishingMageBOT rmdir /S /Q dist\FishingMageBOT
echo OK: Limpeza concluida!
echo.

echo [6/8] Compilando com Nuitka...
echo.
echo IMPORTANTE: Usando MSVC (NAO MinGW64) para Python 3.13
echo Primeira compilacao pode levar 10-20 minutos...
echo.

nuitka ^
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
    --msvc=latest ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    --jobs=2 ^
    --low-memory ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ERRO: Compilacao Nuitka falhou!
    echo.
    echo Verifique os erros acima.
    echo.
    echo DICA: Se houver erro de memoria, tente:
    echo   - Fechar programas desnecessarios
    echo   - Usar --jobs=1 ao inves de --jobs=2
    echo.
    pause
    exit /b 1
)

echo.
echo [7/8] Organizando arquivos...

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

echo OK: Arquivos organizados!
echo.

echo [8/8] Criando README...
(
echo ========================================
echo  FISHING MAGEBOT v5.0 - NUITKA BUILD
echo ========================================
echo.
echo COMPILADO COM NUITKA + MSVC 2019
echo    Codigo nativo C - Muito mais rapido!
echo.
echo COMO USAR:
echo 1. Execute "FishingMageBOT.exe"
echo 2. Configure as opcoes nas abas
echo 3. Pressione F9 para iniciar o bot
echo.
echo REQUISITOS:
echo - Windows 10/11 ^(64-bit^)
echo - Arduino Leonardo conectado ^(opcional^)
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
echo - templates/      Imagens para deteccao + motion.gif
echo - locales/        Traducoes ^(PT/EN/RU/ES^)
echo - config/         Configuracoes padrao
echo - data/           Seus dados e configuracoes
echo.
echo IDIOMAS DISPONIVEIS:
echo - Portugues ^(PT^)
echo - English ^(EN^)
echo - Russkiy ^(RU^)
echo - Espanol ^(ES^)
echo.
echo VANTAGENS DA VERSAO NUITKA:
echo - 3-5x mais rapido que PyInstaller
echo - Deteccao de templates otimizada
echo - Menor uso de memoria RAM
echo - Startup mais rapido
echo - Codigo otimizado nativamente em C
echo.
echo IMPORTANTE:
echo - NAO delete as pastas templates, locales, config
echo - Seus dados ficam salvos na pasta data/
echo - Logs sao criados automaticamente em data/logs/
echo.
echo COMPILADO COM:
echo - Python 3.13.7
echo - Nuitka 2.8.4
echo - MSVC 2019
echo - Otimizacoes de performance ativadas
echo.
echo ========================================
) > dist\FishingMageBOT\README.txt

echo OK: README criado!
echo.

REM Limpar arquivos temporarios
echo Limpando arquivos temporarios...
if exist FishingMageBOT.build rmdir /S /Q FishingMageBOT.build
if exist FishingMageBOT.dist rmdir /S /Q FishingMageBOT.dist
if exist main.build rmdir /S /Q main.build
if exist main.dist rmdir /S /Q main.dist
echo.

echo ========================================
echo   BUILD CONCLUIDO COM SUCESSO!
echo ========================================
echo.
echo Pacote pronto em: dist\FishingMageBOT\
echo.
echo ESTRUTURA DO PACOTE:
echo   FishingMageBOT\
echo   - FishingMageBOT.exe    ^(EXECUTAVEL^)
echo   - templates\            ^(imagens + GIF^)
echo   - locales\              ^(traducoes^)
echo   - config\               ^(configuracoes^)
echo   - data\                 ^(dados do usuario^)
echo   - README.txt
echo.
echo COMO DISTRIBUIR:
echo 1. Comprima a pasta "FishingMageBOT" em ZIP
echo 2. Envie para os usuarios
echo 3. Usuarios extraem e executam FishingMageBOT.exe
echo.
echo DIFERENCA DO BUILD ANTERIOR:
echo - Compilado com MSVC ao inves de MinGW64
echo - Compativel com Python 3.13
echo - Todas as pastas de dados incluidas
echo - Otimizado para uso de memoria
echo.
pause
