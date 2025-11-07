@echo off
echo ========================================
echo   O QUE VAI NO .EXE vs O QUE FICA FORA
echo ========================================
echo.

echo ✅ COMPILADO DENTRO DO .EXE (automatico):
echo    - main.py
echo    - core\*.py
echo    - ui\*.py
echo    - utils\*.py
echo    - client\*.py (se usado)
echo.

echo 📦 DEVE ESTAR AO LADO DO .EXE:
echo    - templates\ (40+ imagens PNG)
echo    - locales\ (traducoes PT/EN/RU)
echo    - config\ (default_config.json)
echo.

echo ❌ NAO INCLUIR NA DISTRIBUICAO:
echo    - server\ (servidor separado)
echo    - fishing_bot_v4\ (backup/antigo)
echo    - arduino_hid_controller_BOOTKEYBOARD\ (hardware)
echo    - .claude\ (docs internas)
echo    - data\ (criada em runtime)
echo    - build\ (cache PyInstaller)
echo    - dist\ (output PyInstaller)
echo    - __pycache__\ (cache Python)
echo    - venv\ (ambiente virtual)
echo    - .git\ (controle de versao)
echo.

echo ========================================
echo   ESTRUTURA FINAL DE DISTRIBUICAO
echo ========================================
echo.
echo FishingBot_Release\
echo ├── FishingBot.exe       (50-80 MB)
echo ├── templates\           (5-10 MB)
echo ├── locales\             (50 KB)
echo ├── config\              (10 KB)
echo └── README.md
echo.
echo (data\ sera criada automaticamente na primeira execucao)
echo.

pause
