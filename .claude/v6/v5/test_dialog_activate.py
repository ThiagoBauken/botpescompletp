#!/usr/bin/env python3
"""
Teste para verificar se o dialog chama activate ou validate
"""

import sys
import os

# Garantir caminho correto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Limpar modulos carregados
for mod in list(sys.modules.keys()):
    if mod.startswith('ui.') or mod.startswith('utils.'):
        del sys.modules[mod]

print("="*60)
print("TESTE: Verificar se dialog chama activate_license()")
print("="*60)

from utils.license_manager import LicenseManager
import inspect

lm = LicenseManager()

# Importar dialog DEPOIS de limpar cache
from ui.license_dialog import LicenseDialog

# Obter source do metodo activate_license
source = inspect.getsource(LicenseDialog.activate_license)

print("\nAnalisando metodo activate_license() do LicenseDialog...")
print()

# Verificar qual metodo esta sendo chamado
found_activate = False
found_validate = False

for i, line in enumerate(source.split('\n'), 1):
    if 'self.license_manager' in line:
        print(f"Linha {i}: {line.strip()}")
        if '.activate_license(' in line:
            found_activate = True
        if '.validate_license(' in line:
            found_validate = True

print()
print("="*60)
print("RESULTADO:")
if found_activate and not found_validate:
    print("CORRETO: Dialog chama activate_license()")
elif found_validate:
    print("ERRADO: Dialog chama validate_license()")
else:
    print("AVISO: Nenhum metodo encontrado")
print("="*60)
print()
print("Agora FECHE o bot completamente e execute novamente!")
print("Use: python main.py")
