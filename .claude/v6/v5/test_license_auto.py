#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste automatico do sistema de licencas
"""

import sys
import os
import json

# Configurar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.license_manager import LicenseManager

def test_license_auto():
    print("\n" + "="*60)
    print("TESTE AUTOMATICO DO SISTEMA DE LICENCAS")
    print("="*60)

    # Criar license manager
    lm = LicenseManager()

    print(f"\nHardware ID: {lm.hardware_id}")
    print(f"Project ID: {lm.project_id}")
    print(f"Server URL: {lm.server_url}")

    # Testar com uma chave de teste
    # NOTA: Substitua por uma chave valida para teste
    test_keys = [
        "TEST-KEY-HERE",  # Adicione sua chave aqui
    ]

    # Verificar se tem licenca salva
    saved_key = lm.load_license()
    if saved_key:
        print(f"\nLicenca encontrada no arquivo: {saved_key[:10]}...")
        test_keys.insert(0, saved_key)

    for i, license_key in enumerate(test_keys):
        if license_key == "TEST-KEY-HERE":
            print("\n[!] Adicione uma chave valida no arquivo test_license_auto.py")
            continue

        print(f"\n" + "="*60)
        print(f"TESTE {i+1}: {license_key[:10]}...")
        print("="*60)

        # Primeiro tentar ativar
        print("\n1. Tentando ATIVAR a chave...")
        valid, data = lm.activate_license(license_key)

        if valid:
            print("   SUCESSO na ativacao!")
            print(f"   Resposta: {json.dumps(data, indent=2)}")
        else:
            print("   Falhou na ativacao")
            print(f"   Erro: {data.get('message', 'Desconhecido')}")

            # Se falhou ativacao, tentar validar
            print("\n2. Tentando VALIDAR a chave...")
            valid, data = lm.validate_license(license_key)

            if valid:
                print("   SUCESSO na validacao!")
                print(f"   Resposta: {json.dumps(data, indent=2)}")
            else:
                print("   Falhou na validacao")
                print(f"   Erro: {data.get('message', 'Desconhecido')}")

        if valid:
            print("\n" + "-"*40)
            print("LICENCA VALIDA!")
            print("-"*40)
            print(f"Expira em: {data.get('expires_at', 'N/A')}")
            print(f"Status: {data.get('status', 'N/A')}")
            print(f"Plano: {data.get('plan_name', 'N/A')}")
            print(f"Dias restantes: {data.get('days_remaining', 'N/A')}")
            break
        else:
            print("\n" + "-"*40)
            print("LICENCA INVALIDA")
            print("-"*40)

    print("\n" + "="*60)
    print("TESTE FINALIZADO")
    print("="*60)

if __name__ == "__main__":
    test_license_auto()