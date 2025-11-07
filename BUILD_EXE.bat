@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo   🎣 FISHING MAGEBOT v5.0 - BUILDER
echo ========================================
echo.

REM Limpa builds anteriores
echo [1/5] 🧹 Limpando builds anteriores...
if exist build rmdir /S /Q build
if exist dist rmdir /S /Q dist
if exist *.spec del /Q *.spec
echo ✅ Limpeza concluída!
echo.

echo [2/5] 📦 Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PyInstaller não encontrado. Instalando...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller já instalado!
)
echo.

echo [3/5] ⚙️  Compilando com PyInstaller...
echo ⏳ Isso pode levar alguns minutos...
echo.

pyinstaller --noconfirm ^
    --onedir ^
    --windowed ^
    --name "FishingMageBOT" ^
    --add-data "templates;templates" ^
    --add-data "locales;locales" ^
    --add-data "config;config" ^
    --add-data "templates\motion.gif;templates" ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=mss ^
    --hidden-import=keyboard ^
    --hidden-import=pyautogui ^
    --hidden-import=serial ^
    --hidden-import=websocket ^
    --hidden-import=cryptography ^
    --collect-all cv2 ^
    --collect-all numpy ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERRO: Compilação falhou!
    pause
    exit /b 1
)

echo.
echo [4/5] 📂 Copiando arquivos de dados...
xcopy /E /I /Y templates dist\FishingMageBOT\templates\ >nul
xcopy /E /I /Y locales dist\FishingMageBOT\locales\ >nul
xcopy /E /I /Y config dist\FishingMageBOT\config\ >nul

REM Criar pasta data
if not exist dist\FishingMageBOT\data mkdir dist\FishingMageBOT\data
echo ✅ Arquivos copiados (GIF incluído em templates/)!
echo.

echo [5/5] 📝 Criando README...
(
echo ========================================
echo  🎣 FISHING MAGEBOT v5.0
echo ========================================
echo.
echo 🚀 COMO USAR:
echo 1. Execute "FishingMageBOT.exe"
echo 2. Configure as opções nas abas
echo 3. Pressione F9 para iniciar o bot
echo.
echo ⚙️  REQUISITOS:
echo - Windows 10/11
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
echo   ├── config.json      Suas configurações
echo   ├── license.key      Sua licença
echo   └── logs/            Logs do sistema
echo.
echo 🌍 IDIOMAS DISPONÍVEIS:
echo - Português ^(PT^)
echo - English ^(EN^)
echo - Русский ^(RU^)
echo - Español ^(ES^)
echo.
echo ⚠️  IMPORTANTE:
echo - NÃO delete as pastas templates, locales e config
echo - Seus dados ficam salvos na pasta data/
echo - Logs são criados automaticamente em data/logs/
echo.
echo 💬 SUPORTE:
echo Discord: [Seu Discord]
echo GitHub: [Seu GitHub]
echo ========================================
) > dist\FishingMageBOT\README.txt

echo ✅ README criado!
echo.

echo ========================================
echo   ✅ BUILD CONCLUÍDO COM SUCESSO!
echo ========================================
echo.
echo 📦 Pacote pronto em: dist\FishingMageBOT\
echo.
echo 📁 ESTRUTURA DO PACOTE:
echo   FishingMageBOT\
echo   ├── 🎯 FishingMageBOT.exe    ^(EXECUTÁVEL PRINCIPAL^)
echo   ├── 📂 templates\             ^(Detecção de imagens^)
echo   ├── 🌍 locales\               ^(4 idiomas^)
echo   ├── ⚙️  config\                ^(Configurações^)
echo   ├── 💾 data\                  ^(Dados do usuário^)
echo   ├── 📚 _internal\             ^(Bibliotecas Python^)
echo   └── 📝 README.txt             ^(Instruções^)
echo.
echo 💡 COMO DISTRIBUIR:
echo    1. Comprima a pasta "FishingMageBOT" em ZIP
echo    2. Envie o arquivo ZIP para os usuários
echo    3. Usuários extraem e executam FishingMageBOT.exe
echo.
echo ⚠️  O .exe NÃO funciona sozinho - precisa das pastas!
echo.
pause
