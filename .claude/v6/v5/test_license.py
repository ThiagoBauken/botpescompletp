#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do sistema de licencas
"""

import sys
import os

# Configurar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.license_manager import LicenseManager

def test_license():
    print("\n" + "="*60)
    print("TESTE DO SISTEMA DE LICENCAS")
    print("="*60)

    # Criar license manager
    lm = LicenseManager()

    print(f"\nHardware ID: {lm.hardware_id}")
    print(f"Project ID: {lm.project_id}")
    print(f"Server URL: {lm.server_url}")

    # Remover licenca existente para teste limpo
    if os.path.exists("license.key"):
        os.remove("license.key")
        print("\nLicenca existente removida para teste limpo")

    print("\n" + "="*60)
    print("Insira a chave de licenca para testar:")
    license_key = input("Chave: ").strip()

    if not license_key:
        print("Nenhuma chave fornecida")
        return

    print("\n" + "="*60)
    print("TESTANDO ATIVACAO")
    print("="*60)

    # Testar ativacao
    valid, data = lm.activate_license(license_key)

    print(f"\nResultado da ativacao: {'SUCESSO' if valid else 'FALHOU'}")
    print(f"Resposta: {data}")

    if not valid:
        print("\n" + "="*60)
        print("TESTANDO VALIDACAO DIRETA")
        print("="*60)

        # Se ativacao falhou, tentar validacao direta
        valid, data = lm.validate_license(license_key)

        print(f"\nResultado da validacao: {'SUCESSO' if valid else 'FALHOU'}")
        print(f"Resposta: {data}")

    if valid:
        print("\n" + "="*60)
        print("LICENCA VALIDA!")
        print("="*60)
        print(f"Expira em: {data.get('expires_at', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        print(f"Plano: {data.get('plan_name', 'N/A')}")
        print(f"Dias restantes: {data.get('days_remaining', 'N/A')}")
    else:
        print("\n" + "="*60)
        print("LICENCA INVALIDA")
        print("="*60)
        print(f"Erro: {data.get('message', data.get('error', 'Desconhecido'))}")

if __name__ == "__main__":
    test_license()
    input("\nPressione Enter para sair...")