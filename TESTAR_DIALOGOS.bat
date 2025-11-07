@echo off
echo ========================================
echo   TESTAR DIALOGOS DE AUTENTICACAO
echo ========================================
echo.

echo Existem 2 dialogos diferentes no projeto:
echo.
echo 1. LicenseDialog (ui\license_dialog.py)
echo    - Apenas LICENSE KEY
echo    - Obrigatorio (sempre aparece)
echo    - Valida licenca local
echo.
echo 2. ActivationDialog (client\activation_dialog.py)
echo    - Login + Senha + License Key
echo    - Opcional (servidor multi-usuario)
echo    - Conecta ao servidor WebSocket
echo.

:menu
echo ========================================
echo   Escolha qual dialogo testar:
echo ========================================
echo.
echo [1] LicenseDialog (apenas KEY)
echo [2] ActivationDialog (Login/Senha/Key)
echo [3] Ambos em sequencia
echo [4] Sair
echo.

choice /C 1234 /M "Opcao"

if errorlevel 4 goto :end
if errorlevel 3 goto :both
if errorlevel 2 goto :activation
if errorlevel 1 goto :license

:license
echo.
echo Testando LicenseDialog...
python -c "from ui.license_dialog import LicenseDialog; from utils.license_manager import LicenseManager; lm = LicenseManager(); ld = LicenseDialog(lm); key = ld.show(); print('\nResultado:', key if key else 'Cancelado')"
echo.
pause
goto menu

:activation
echo.
echo Testando ActivationDialog...
python -c "from client.activation_dialog import ActivationDialog; ad = ActivationDialog(); result = ad.show(); print('\nResultado:', result if result else 'Cancelado')"
echo.
pause
goto menu

:both
echo.
echo Testando LicenseDialog primeiro...
python -c "from ui.license_dialog import LicenseDialog; from utils.license_manager import LicenseManager; lm = LicenseManager(); ld = LicenseDialog(lm); key = ld.show(); print('\n[1/2] LicenseDialog:', key if key else 'Cancelado')"

echo.
echo Agora testando ActivationDialog...
python -c "from client.activation_dialog import ActivationDialog; ad = ActivationDialog(); result = ad.show(); print('\n[2/2] ActivationDialog:', result if result else 'Cancelado')"
echo.
pause
goto menu

:end
echo.
echo Encerrando...
