#!/usr/bin/env python3
"""
🔍 Debug: Testar conexão com servidor e identificar problema HTTP 400

Este script testa:
1. Conectividade básica com o servidor
2. Endpoint /health
3. Endpoint /auth/activate com credenciais reais
4. Endpoints alternativos
"""

import requests
import json
import sys
import os
from pathlib import Path

# Adicionar pasta raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def test_server_connection():
    """Testar conexão com servidor e endpoints"""

    server_url = "https://private-serverpesca.pbzgje.easypanel.host"

    _safe_print("\n" + "="*60)
    _safe_print("🔍 DEBUG: Testando conexão com servidor")
    _safe_print("="*60)

    # 1. Testar se servidor está acessível
    _safe_print("\n1️⃣ Testando conectividade básica...")
    try:
        response = requests.get(server_url, timeout=5)
        _safe_print(f"   ✅ Servidor acessível (HTTP {response.status_code})")
    except requests.exceptions.ConnectionError:
        _safe_print(f"   ❌ Servidor inacessível (Connection Error)")
        _safe_print(f"   💡 Servidor pode estar offline ou URL incorreta")
        return
    except requests.exceptions.Timeout:
        _safe_print(f"   ❌ Servidor não respondeu (Timeout)")
        _safe_print(f"   💡 Servidor pode estar sobrecarregado")
        return
    except Exception as e:
        _safe_print(f"   ❌ Erro: {e}")
        return

    # 2. Testar endpoint de health
    _safe_print("\n2️⃣ Testando endpoint /health...")
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        _safe_print(f"   HTTP {response.status_code}")
        if response.status_code == 200:
            try:
                health_data = response.json()
                _safe_print(f"   ✅ Health check OK: {health_data}")
            except:
                _safe_print(f"   ✅ Health check OK (response: {response.text[:100]})")
        else:
            _safe_print(f"   ⚠️ Health check retornou: {response.text[:200]}")
    except requests.exceptions.ConnectionError:
        _safe_print(f"   ❌ Endpoint /health não acessível")
    except Exception as e:
        _safe_print(f"   ❌ Erro: {e}")

    # 3. Testar endpoint /auth/activate
    _safe_print("\n3️⃣ Testando endpoint /auth/activate...")

    # Carregar credenciais reais
    try:
        from client.credential_manager import CredentialManager
        from utils.license_manager import LicenseManager

        cred_mgr = CredentialManager()
        credentials = cred_mgr.load_credentials()

        license_mgr = LicenseManager()
        hwid = license_mgr.get_hardware_id()

        if not credentials:
            _safe_print("   ⚠️ Credenciais não encontradas, usando valores de teste")
            login = "test@test.com"
            password = "test123"
            license_key = "TEST-KEY-1234"
        else:
            login = credentials['login']
            password = credentials['password']
            license_key = credentials['license_key']
            _safe_print("   ✅ Credenciais carregadas do arquivo")

        import platform
        pc_name = platform.node()

    except Exception as e:
        _safe_print(f"   ⚠️ Erro ao carregar credenciais: {e}")
        _safe_print("   Usando valores de teste...")
        login = "test@test.com"
        password = "test123"
        license_key = "TEST-KEY-1234"
        hwid = "test-hwid-123"
        pc_name = "TEST-PC"

    payload = {
        "login": login,
        "password": password,
        "license_key": license_key,
        "hwid": hwid,
        "pc_name": pc_name
    }

    _safe_print(f"\n   📤 Enviando payload:")
    _safe_print(f"      login: {login}")
    _safe_print(f"      password: {'*' * len(password)}")
    _safe_print(f"      license_key: {license_key[:10]}...")
    _safe_print(f"      hwid: {hwid[:16]}...")
    _safe_print(f"      pc_name: {pc_name}")

    try:
        _safe_print(f"\n   🔌 Conectando a {server_url}/auth/activate...")
        response = requests.post(
            f"{server_url}/auth/activate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        _safe_print(f"\n   📥 Resposta do servidor:")
        _safe_print(f"      HTTP Status: {response.status_code}")
        _safe_print(f"      Content-Type: {response.headers.get('content-type', 'N/A')}")

        # Tentar parsear JSON
        try:
            data = response.json()
            _safe_print(f"\n      Response Body (JSON):")
            _safe_print(json.dumps(data, indent=6))

            # Análise da resposta
            if response.status_code == 200:
                _safe_print("\n   ✅ SUCESSO! Autenticação funcionou")
                _safe_print(f"      Token: {data.get('token', 'N/A')[:20]}...")
                _safe_print(f"      Message: {data.get('message', 'N/A')}")

                if 'rules' in data:
                    _safe_print(f"\n      📋 Regras recebidas:")
                    for key, value in data['rules'].items():
                        _safe_print(f"         {key}: {value}")

            elif response.status_code == 400:
                _safe_print("\n   ❌ HTTP 400 - Bad Request")
                _safe_print(f"      Mensagem: {data.get('message', 'N/A')}")
                _safe_print(f"      Detalhes: {data.get('detail', 'N/A')}")

                # Sugestões de correção
                _safe_print("\n   💡 Possíveis causas:")
                if 'message' in data:
                    msg = str(data['message']).lower()
                    if 'license' in msg or 'key' in msg:
                        _safe_print("      • License key inválida ou expirada")
                        _safe_print("      • Verificar no Keymaster se a chave está ativa")
                        _safe_print(f"      • URL Keymaster: https://private-keygen.pbzgje.easypanel.host")
                    elif 'hwid' in msg or 'hardware' in msg:
                        _safe_print("      • HWID binding - licença vinculada a outro PC")
                        _safe_print("      • Desvincular no Keymaster ou usar PC original")
                    elif 'field' in msg or 'required' in msg or 'validation' in msg:
                        _safe_print("      • Campos obrigatórios faltando no payload")
                        _safe_print("      • Servidor esperando formato diferente")
                        _safe_print("      • Verificar logs do servidor para detalhes")
                    elif 'keymaster' in msg:
                        _safe_print("      • Problema ao conectar com Keymaster")
                        _safe_print("      • Keymaster pode estar offline")
                    else:
                        _safe_print("      • Erro genérico - ver logs do servidor")
                else:
                    _safe_print("      • Validação de campos falhando")
                    _safe_print("      • Keymaster offline ou inacessível")
                    _safe_print("      • Versão incompatível da API")
                    _safe_print("      • Verificar logs do servidor para mais detalhes")

            elif response.status_code == 401:
                _safe_print("\n   ❌ HTTP 401 - Unauthorized")
                _safe_print("      • Credenciais inválidas")
                _safe_print("      • Verificar login/senha/license_key")

            elif response.status_code == 404:
                _safe_print("\n   ❌ HTTP 404 - Not Found")
                _safe_print("      • Endpoint /auth/activate não existe no servidor")
                _safe_print("      • Verificar rota correta na documentação")

            elif response.status_code == 500:
                _safe_print("\n   ❌ HTTP 500 - Internal Server Error")
                _safe_print("      • Erro interno do servidor")
                _safe_print("      • Verificar logs do servidor")
                _safe_print("      • Pode ser erro no Keymaster ou banco de dados")

            else:
                _safe_print(f"\n   ⚠️ HTTP {response.status_code} - Status inesperado")

        except json.JSONDecodeError:
            _safe_print(f"\n      Response Body (Text):")
            _safe_print(f"      {response.text[:500]}")
            _safe_print("\n   ⚠️ Resposta não é JSON válido")
            _safe_print("   💡 Servidor pode não estar retornando JSON corretamente")

    except requests.exceptions.ConnectionError:
        _safe_print(f"   ❌ Não foi possível conectar ao endpoint")
        _safe_print(f"   💡 Servidor pode estar offline ou endpoint não existe")
    except requests.exceptions.Timeout:
        _safe_print(f"   ❌ Timeout ao conectar (10s)")
        _safe_print(f"   💡 Servidor pode estar processando muito lentamente")
        _safe_print(f"   💡 Keymaster pode estar demorando para responder")
    except Exception as e:
        _safe_print(f"   ❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

    # 4. Testar alternativas de endpoint
    _safe_print("\n4️⃣ Testando endpoints alternativos...")
    alternative_endpoints = [
        "/api/auth/activate",
        "/auth/login",
        "/api/auth/login",
        "/activate",
        "/api/activate"
    ]

    found_alternatives = []
    for endpoint in alternative_endpoints:
        try:
            response = requests.post(
                f"{server_url}{endpoint}",
                json=payload,
                timeout=3
            )
            if response.status_code != 404:
                _safe_print(f"   ✅ {endpoint} existe (HTTP {response.status_code})")
                found_alternatives.append(endpoint)
        except:
            pass

    if not found_alternatives:
        _safe_print("   ℹ️ Nenhum endpoint alternativo encontrado")
    else:
        _safe_print(f"\n   💡 Considere usar um destes endpoints alternativos:")
        for alt in found_alternatives:
            _safe_print(f"      • {alt}")

    # 5. Teste de Keymaster direto
    _safe_print("\n5️⃣ Testando Keymaster diretamente...")
    keymaster_url = "https://private-keygen.pbzgje.easypanel.host"
    try:
        keymaster_payload = {
            "license_key": license_key,
            "hwid": hwid
        }

        response = requests.post(
            f"{keymaster_url}/validate",
            json=keymaster_payload,
            timeout=5
        )

        _safe_print(f"   HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('valid'):
                _safe_print(f"   ✅ Keymaster validou a license key!")
                _safe_print(f"      Status: {data.get('status', 'N/A')}")
                _safe_print(f"      Expira: {data.get('expires_at', 'N/A')}")
            else:
                _safe_print(f"   ❌ Keymaster rejeitou a license key")
                _safe_print(f"      Mensagem: {data.get('message', 'N/A')}")
        else:
            _safe_print(f"   ⚠️ Keymaster retornou HTTP {response.status_code}")

    except Exception as e:
        _safe_print(f"   ❌ Erro ao testar Keymaster: {e}")
        _safe_print(f"   💡 Keymaster pode estar offline ou inacessível")

    _safe_print("\n" + "="*60)
    _safe_print("🏁 Teste concluído")
    _safe_print("="*60)
    _safe_print("\n📋 Próximos passos:")
    _safe_print("   1. Analise a saída acima")
    _safe_print("   2. Se HTTP 400, verifique os logs do servidor")
    _safe_print("   3. Se HTTP 404, endpoint pode estar incorreto")
    _safe_print("   4. Se Keymaster falhou, verifique a license key")
    _safe_print("   5. Consulte ANALISE_E_CORRECAO_SERVIDOR.md para mais detalhes")

if __name__ == "__main__":
    test_server_connection()
