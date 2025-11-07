#!/usr/bin/env python3
"""
🔧 Script para migrar licença plaintext para criptografada

Este script:
1. Lê a licença atual (plaintext)
2. Re-salva usando o novo sistema de criptografia
3. Valida que a nova licença funciona
"""

import os
import sys

def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


def main():
    _safe_print("\n" + "="*60)
    _safe_print("🔧 Migração de Licença: Plaintext → Criptografada")
    _safe_print("="*60)

    try:
        from utils.license_manager import LicenseManager

        # Criar gerenciador
        _safe_print("\n1️⃣ Carregando LicenseManager...")
        lm = LicenseManager()

        if not lm.crypto:
            _safe_print("⚠️ Sistema de criptografia não disponível!")
            _safe_print("Execute: pip install cryptography")
            return 1

        # Verificar se existe licença
        license_file = lm.license_file
        if not os.path.exists(license_file):
            _safe_print(f"\n⚠️ Arquivo de licença não encontrado: {license_file}")
            _safe_print("Execute o bot normalmente para ativar uma licença primeiro.")
            return 0

        # Carregar licença atual
        _safe_print("\n2️⃣ Carregando licença atual...")
        license_key = lm.load_license()

        if not license_key:
            _safe_print("❌ Não foi possível carregar a licença!")
            return 1

        _safe_print(f"✅ Licença carregada: {license_key[:10]}...")

        # Verificar se já está criptografada
        with open(license_file, 'r') as f:
            stored = f.read().strip()

        import re
        is_base64_like = (
            len(stored) % 4 == 0 and
            re.match(r'^[A-Za-z0-9+/]*={0,2}$', stored) is not None and
            len(stored) > 50  # Licenças criptografadas são longas
        )

        if is_base64_like:
            _safe_print("\n✅ Licença já está criptografada!")
            _safe_print("Nenhuma ação necessária.")
            return 0

        # Migrar para formato criptografado
        _safe_print("\n3️⃣ Migrando para formato criptografado...")

        # Fazer backup
        backup_file = license_file + ".backup"
        with open(license_file, 'r') as f:
            backup_data = f.read()
        with open(backup_file, 'w') as f:
            f.write(backup_data)
        _safe_print(f"💾 Backup criado: {backup_file}")

        # Re-salvar com criptografia
        success = lm.save_license(license_key)

        if not success:
            _safe_print("❌ Erro ao salvar licença criptografada!")
            _safe_print("Restaurando backup...")
            with open(backup_file, 'r') as f:
                backup_data = f.read()
            with open(license_file, 'w') as f:
                f.write(backup_data)
            return 1

        _safe_print("✅ Licença salva com criptografia AES-256!")

        # Validar que pode ser lida
        _safe_print("\n4️⃣ Validando nova licença...")
        loaded_key = lm.load_license()

        if loaded_key == license_key:
            _safe_print("✅ Validação bem-sucedida!")
            _safe_print(f"✅ Licença criptografada: {license_key[:10]}...")

            # Remover backup
            try:
                os.remove(backup_file)
                _safe_print("🧹 Backup removido")
            except:
                pass

            _safe_print("\n" + "="*60)
            _safe_print("🎉 Migração concluída com sucesso!")
            _safe_print("="*60)
            _safe_print("\nSua licença agora está protegida com AES-256.")
            _safe_print("O bot funcionará normalmente.")

            return 0
        else:
            _safe_print("❌ Falha na validação!")
            _safe_print("Restaurando backup...")
            with open(backup_file, 'r') as f:
                backup_data = f.read()
            with open(license_file, 'w') as f:
                f.write(backup_data)
            return 1

    except Exception as e:
        _safe_print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
