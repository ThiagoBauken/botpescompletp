#!/usr/bin/env python3
"""
Simular clique no botao Ativar Licenca
"""

import sys
import os

# Limpar TODOS os modulos
for mod in list(sys.modules.keys()):
    if any(x in mod for x in ['license', 'dialog', 'ui.', 'utils.']):
        try:
            del sys.modules[mod]
        except:
            pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("SIMULACAO: Clicar botao Ativar Licenca")
print("="*60)

from utils.license_manager import LicenseManager

# Mock para simular o dialog
class MockDialog:
    def __init__(self, license_manager):
        self.license_manager = license_manager

    def simulate_button_click(self, license_key):
        """Simula exatamente o que o botao faz"""
        print(f"\n[SIMULACAO] Usuario digitou: {license_key}")
        print("[SIMULACAO] Usuario clicou botao 'Ativar Licenca'")
        print()

        # CODIGO EXATO da linha 174 do license_dialog.py:
        success, message = self.license_manager.activate_license(license_key)

        print()
        print("[RESULTADO]")
        print(f"  Success: {success}")
        print(f"  Message: {message}")

        return success, message

# Teste
lm = LicenseManager()
dialog = MockDialog(lm)

# Simular clique
dialog.simulate_button_click("MONTH-4A42-AQ8N")

print()
print("="*60)
print("VERIFIQUE O LOG ACIMA:")
print("Deve mostrar: 'Enviando para: .../activate'")
print("NAO deve mostrar: 'Enviando dados para: .../validate'")
print("="*60)
