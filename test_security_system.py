#!/usr/bin/env python3
"""
🧪 Ultimate Fishing Bot v5.0 - Security System Test
Script para testar todos os componentes de segurança
"""

import sys
import os
from pathlib import Path

# Wrapper de print seguro
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


def test_crypto_manager():
    """Testar CryptoManager"""
    _safe_print("\n" + "="*60)
    _safe_print("🔐 Teste 1: CryptoManager (AES-256)")
    _safe_print("="*60)

    try:
        from utils.crypto_manager import CryptoManager, encrypt_string, decrypt_string

        # Teste 1: Criptografia básica
        _safe_print("\n📝 Teste 1.1: Criptografia/Descriptografia básica")
        crypto = CryptoManager()

        original = "https://private-keygen.pbzgje.easypanel.host"
        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)

        _safe_print(f"  Original:  {original}")
        _safe_print(f"  Encrypted: {encrypted[:50]}...")
        _safe_print(f"  Decrypted: {decrypted}")

        if original == decrypted:
            _safe_print("  ✅ PASSOU")
        else:
            _safe_print("  ❌ FALHOU")
            return False

        # Teste 2: Helper functions
        _safe_print("\n📝 Teste 1.2: Helper functions")
        encrypted2 = encrypt_string("test data")
        decrypted2 = decrypt_string(encrypted2)

        if decrypted2 == "test data":
            _safe_print("  ✅ PASSOU")
        else:
            _safe_print("  ❌ FALHOU")
            return False

        # Teste 3: Dicionário
        _safe_print("\n📝 Teste 1.3: Criptografia de dicionário")
        data = {
            'server': 'https://api.example.com',
            'key': '12345-67890'
        }
        encrypted_dict = crypto.encrypt_dict(data)
        decrypted_dict = crypto.decrypt_dict(encrypted_dict)

        if data == decrypted_dict:
            _safe_print("  ✅ PASSOU")
        else:
            _safe_print("  ❌ FALHOU")
            return False

        _safe_print("\n✅ CryptoManager: TODOS OS TESTES PASSARAM")
        return True

    except Exception as e:
        _safe_print(f"\n❌ CryptoManager: FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_string_obfuscator():
    """Testar StringObfuscator"""
    _safe_print("\n" + "="*60)
    _safe_print("🔒 Teste 2: StringObfuscator")
    _safe_print("="*60)

    try:
        from utils.string_obfuscator import obfuscate, deobfuscate, generate_obfuscated_code

        # Teste 1: Ofuscação básica
        _safe_print("\n📝 Teste 2.1: Ofuscação/Deofuscação básica")
        urls = [
            "https://private-keygen.pbzgje.easypanel.host",
            "wss://private-serverpesca.pbzgje.easypanel.host/ws",
            "67a4a76a-d71b-4d07-9ba8-f7e794ce0578"
        ]

        for url in urls:
            obfuscated = obfuscate(url)
            deobfuscated = deobfuscate(obfuscated)

            if url == deobfuscated:
                _safe_print(f"  ✅ {url[:40]}...")
            else:
                _safe_print(f"  ❌ {url[:40]}...")
                return False

        # Teste 2: Caracteres especiais
        _safe_print("\n📝 Teste 2.2: Caracteres especiais")
        special = ["Café com açúcar", "🔐🎣", "key=value&test=123"]

        for text in special:
            try:
                obf = obfuscate(text)
                dec = deobfuscate(obf)
                if text == dec:
                    _safe_print(f"  ✅ {text}")
                else:
                    _safe_print(f"  ❌ {text}")
                    return False
            except:
                _safe_print(f"  ❌ {text} (exception)")
                return False

        # Teste 3: Geração de código
        _safe_print("\n📝 Teste 2.3: Geração de código")
        code = generate_obfuscated_code("https://api.test.com", "API_URL")
        if "deobfuscate" in code and "API_URL" in code:
            _safe_print("  ✅ Código gerado corretamente")
        else:
            _safe_print("  ❌ Código inválido")
            return False

        _safe_print("\n✅ StringObfuscator: TODOS OS TESTES PASSARAM")
        return True

    except Exception as e:
        _safe_print(f"\n❌ StringObfuscator: FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_license_manager():
    """Testar LicenseManager com crypto"""
    _safe_print("\n" + "="*60)
    _safe_print("🔑 Teste 3: LicenseManager (com crypto)")
    _safe_print("="*60)

    try:
        from utils.license_manager import LicenseManager

        # Criar LicenseManager
        _safe_print("\n📝 Teste 3.1: Inicialização")
        lm = LicenseManager()

        if lm.crypto:
            _safe_print("  ✅ CryptoManager inicializado")
        else:
            _safe_print("  ⚠️ CryptoManager não disponível (continuando sem crypto)")

        # Teste 2: Salvar/Carregar licença
        _safe_print("\n📝 Teste 3.2: Salvar/Carregar licença criptografada")

        test_key = "TEST-LICENSE-KEY-12345-67890-ABCDEF"
        test_file = "test_license.key"

        # Temporariamente usar arquivo de teste
        lm.license_file = test_file

        # Salvar
        if lm.save_license(test_key):
            _safe_print("  ✅ Licença salva")
        else:
            _safe_print("  ❌ Erro ao salvar licença")
            return False

        # Verificar que foi criptografada
        if lm.crypto:
            with open(test_file, 'r') as f:
                stored = f.read()
            if test_key not in stored:
                _safe_print("  ✅ Licença está criptografada (não em plaintext)")
            else:
                _safe_print("  ⚠️ Licença em plaintext (crypto não funcionou)")

        # Carregar
        loaded_key = lm.load_license()
        if loaded_key == test_key:
            _safe_print("  ✅ Licença carregada corretamente")
        else:
            _safe_print(f"  ❌ Licença incorreta: {loaded_key}")
            return False

        # Limpar arquivo de teste
        if os.path.exists(test_file):
            os.remove(test_file)
            _safe_print("  🧹 Arquivo de teste removido")

        _safe_print("\n✅ LicenseManager: TODOS OS TESTES PASSARAM")
        return True

    except Exception as e:
        _safe_print(f"\n❌ LicenseManager: FALHOU - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_scripts():
    """Testar scripts de build existem e estão corretos"""
    _safe_print("\n" + "="*60)
    _safe_print("🔨 Teste 4: Scripts de Build")
    _safe_print("="*60)

    scripts = [
        "build_tools/obfuscate_secrets.py",
        "build_tools/build_nuitka.py",
    ]

    all_ok = True
    for script_path in scripts:
        path = Path(script_path)
        if path.exists():
            _safe_print(f"  ✅ {script_path}")
        else:
            _safe_print(f"  ❌ {script_path} NÃO ENCONTRADO")
            all_ok = False

    if all_ok:
        _safe_print("\n✅ Scripts de Build: TODOS PRESENTES")
    else:
        _safe_print("\n❌ Scripts de Build: FALTANDO ARQUIVOS")

    return all_ok


def test_gitignore():
    """Testar se .gitignore está protegendo secrets"""
    _safe_print("\n" + "="*60)
    _safe_print("🚫 Teste 5: .gitignore (proteção de secrets)")
    _safe_print("="*60)

    try:
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            _safe_print("  ⚠️ .gitignore não encontrado")
            return False

        with open(gitignore_path, 'r') as f:
            content = f.read()

        required_entries = [
            ".secrets.json",
            ".secrets.enc",
            "license.key",
        ]

        all_ok = True
        for entry in required_entries:
            if entry in content:
                _safe_print(f"  ✅ {entry}")
            else:
                _safe_print(f"  ❌ {entry} NÃO ESTÁ NO .gitignore")
                all_ok = False

        if all_ok:
            _safe_print("\n✅ .gitignore: CONFIGURADO CORRETAMENTE")
        else:
            _safe_print("\n❌ .gitignore: FALTANDO ENTRADAS")

        return all_ok

    except Exception as e:
        _safe_print(f"\n❌ .gitignore: ERRO - {e}")
        return False


def main():
    """Executar todos os testes"""
    _safe_print("\n" + "="*60)
    _safe_print("🧪 ULTIMATE FISHING BOT v5.0 - SECURITY SYSTEM TEST")
    _safe_print("="*60)

    results = {}

    # Executar testes
    results['CryptoManager'] = test_crypto_manager()
    results['StringObfuscator'] = test_string_obfuscator()
    results['LicenseManager'] = test_license_manager()
    results['BuildScripts'] = test_build_scripts()
    results['GitIgnore'] = test_gitignore()

    # Resumo
    _safe_print("\n" + "="*60)
    _safe_print("📊 RESUMO DOS TESTES")
    _safe_print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        _safe_print(f"  {test_name:20s} {status}")

    # Resultado final
    all_passed = all(results.values())

    _safe_print("\n" + "="*60)
    if all_passed:
        _safe_print("🎉 TODOS OS TESTES PASSARAM!")
        _safe_print("✅ Sistema de segurança está funcionando corretamente")
    else:
        _safe_print("❌ ALGUNS TESTES FALHARAM!")
        _safe_print("⚠️ Verifique os erros acima")
    _safe_print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _safe_print("\n\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        _safe_print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
