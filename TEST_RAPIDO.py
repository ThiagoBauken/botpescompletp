#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TESTE RAPIDO - Verificar integracao cliente e servidor"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 70)
    print("TESTE RAPIDO - INTEGRACAO CLIENTE/SERVIDOR")
    print("=" * 70)

    errors = []

    # TESTE 1: Imports
    print("\n[1/5] Testando imports...")
    try:
        from ui.unified_auth_dialog import UnifiedAuthDialog
        from utils.license_manager import LicenseManager
        from client.ws_client import WebSocketClient
        print("OK - Todos os imports funcionam")
    except Exception as e:
        errors.append(f"ERRO imports: {e}")
        print(f"FALHOU: {e}")

    # TESTE 2: UnifiedAuthDialog tem logica correta
    print("\n[2/5] Verificando UnifiedAuthDialog...")
    try:
        with open("ui/unified_auth_dialog.py", "r", encoding="utf-8") as f:
            content = f.read()

        checks = [
            ("saved_key = self.license_manager.load_license()", "Carrega license salva"),
            ("if saved_key == license_key:", "Compara keys"),
            ("validate_license(license_key)", "Chama validate"),
            ("activate_license(license_key)", "Chama activate")
        ]

        for code, desc in checks:
            if code in content:
                print(f"  OK - {desc}")
            else:
                errors.append(f"UnifiedAuthDialog: Falta {desc}")
                print(f"  FALHOU - {desc}")
    except Exception as e:
        errors.append(f"ERRO UnifiedAuthDialog: {e}")
        print(f"FALHOU: {e}")

    # TESTE 3: main.py usa UnifiedAuthDialog
    print("\n[3/5] Verificando main.py...")
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()

        if "from ui.unified_auth_dialog import UnifiedAuthDialog" in content:
            print("  OK - Importa UnifiedAuthDialog")
        else:
            errors.append("main.py: NAO importa UnifiedAuthDialog")
            print("  FALHOU - NAO importa UnifiedAuthDialog")

        if "UnifiedAuthDialog(license_manager)" in content:
            print("  OK - Usa UnifiedAuthDialog")
        else:
            errors.append("main.py: NAO usa UnifiedAuthDialog")
            print("  FALHOU - NAO usa UnifiedAuthDialog")
    except Exception as e:
        errors.append(f"ERRO main.py: {e}")
        print(f"FALHOU: {e}")

    # TESTE 4: WebSocketClient tem eventos
    print("\n[4/5] Verificando WebSocketClient...")
    try:
        with open("client/ws_client.py", "r", encoding="utf-8") as f:
            content = f.read()

        checks = [
            ("def send_fishing_stopped(self):", "Metodo send_fishing_stopped"),
            ("def send_fishing_paused(self):", "Metodo send_fishing_paused"),
        ]

        for code, desc in checks:
            if code in content:
                print(f"  OK - {desc}")
            else:
                print(f"  WARNING - {desc} nao encontrado (opcional)")
    except Exception as e:
        print(f"WARNING: {e}")

    # TESTE 5: Servidor tem endpoints
    print("\n[5/5] Verificando servidor...")
    try:
        with open("server_auth/server.py", "r", encoding="utf-8") as f:
            content = f.read()

        endpoints = [
            ("/auth/activate", "Ativacao"),
            ("/auth/reset-password", "Reset senha usuario"),
            ("/api/stats/", "Stats"),
            ("/api/ranking/monthly", "Ranking mensal"),
            ("/ws", "WebSocket"),
        ]

        for endpoint, desc in endpoints:
            if endpoint in content:
                print(f"  OK - {desc}")
            else:
                errors.append(f"Servidor: Falta endpoint {endpoint}")
                print(f"  FALHOU - {desc}")
    except Exception as e:
        errors.append(f"ERRO servidor: {e}")
        print(f"FALHOU: {e}")

    # RESUMO
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)

    if not errors:
        print("\nOK - TODOS OS TESTES PASSARAM!")
        print("PODE COMPILAR COM SEGURANCA!")
        print("\nCHECKLIST:")
        print("  [OK] UnifiedAuthDialog com logica ativar vs validar")
        print("  [OK] main.py usa UnifiedAuthDialog")
        print("  [OK] Servidor tem todos os endpoints")
        return 0
    else:
        print(f"\nFALHOU - {len(errors)} erro(s) encontrado(s):")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print("\nNAO COMPILE AINDA - Corrija os erros acima primeiro!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
