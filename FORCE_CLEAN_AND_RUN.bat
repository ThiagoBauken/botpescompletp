@echo off
echo ========================================
echo LIMPEZA FORCADA DE CACHE PYTHON
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Removendo __pycache__...
if exist "__pycache__" rd /s /q "__pycache__"
if exist "ui\__pycache__" rd /s /q "ui\__pycache__"
if exist "utils\__pycache__" rd /s /q "utils\__pycache__"
if exist "core\__pycache__" rd /s /q "core\__pycache__"
echo OK

echo [2/4] Removendo arquivos .pyc...
del /s /q *.pyc 2>nul
echo OK

echo [3/4] Removendo license.key antigo...
if exist "license.key" del /q "license.key"
if exist "data\license.key" del /q "data\license.key"
echo OK

echo [4/4] Verificando codigo do dialog...
python -c "import sys; sys.path.insert(0, '.'); from ui.license_dialog import LicenseDialog; import inspect; src = inspect.getsource(LicenseDialog.activate_license); print('CORRETO' if 'activate_license(license_key)' in src else 'ERRADO')"

echo.
echo ========================================
echo INICIANDO BOT...
echo ========================================
echo.

python main.py

pause
