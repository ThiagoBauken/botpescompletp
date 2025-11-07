#!/usr/bin/env python3
"""
Script para testar ativacao de uma nova licenca
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.license_manager import LicenseManager

def test_license_key(key):
    """Testar ativacao de uma chave"""
    print("="*60)
    print("TESTE DE ATIVACAO DE LICENCA")
    print("="*60)

    lm = LicenseManager()

    print(f"\nHardware ID: {lm.hardware_id}")
    print(f"Chave: {key}")
    print(f"\nTentando ativar...\n")

    # Tentar ativar
    valid, data = lm.activate_license(key)

    print("\n" + "="*60)
    if valid:
        print("SUCESSO! Licenca ativada!")
        print(f"Expira em: {data.get('expires_at', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        print(f"Tempo restante: {data.get('time_remaining', 'N/A')} segundos")
    else:
        print("FALHA! Licenca NAO foi ativada")
        print(f"Erro: {data.get('message', 'Erro desconhecido')}")
    print("="*60)

    return valid

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python test_new_license.py <CHAVE>")
        print("\nExemplo:")
        print("  python test_new_license.py PROD-XXXX-YYYY-ZZZZ")
        sys.exit(1)

    key = sys.argv[1]
    test_license_key(key)
