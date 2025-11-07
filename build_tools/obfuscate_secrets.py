#!/usr/bin/env python3
"""
🔒 Ultimate Fishing Bot v5.0 - Secret Obfuscation Tool
Script para ofuscar strings sensíveis antes da compilação com Nuitka
"""

import os
import sys
import re
from pathlib import Path

# Adicionar pasta raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.string_obfuscator import obfuscate

# Wrapper de print seguro
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO: Strings para ofuscar
# ═══════════════════════════════════════════════════════════════════

SECRETS_TO_OBFUSCATE = {
    # URLs de API
    'https://private-keygen.pbzgje.easypanel.host': 'LICENSE_SERVER_URL',
    'wss://private-serverpesca.pbzgje.easypanel.host/ws': 'WS_SERVER_URL',

    # Project ID
    '67a4a76a-d71b-4d07-9ba8-f7e794ce0578': 'PROJECT_ID',

    # User-Agent (opcional)
    'UltimateFishingBot/4.0': 'USER_AGENT',
}


# ═══════════════════════════════════════════════════════════════════
# FUNÇÕES DE OFUSCAÇÃO
# ═══════════════════════════════════════════════════════════════════

def obfuscate_string_in_code(code: str, plaintext: str, var_name: str) -> str:
    """
    Substituir string literal por versão ofuscada no código

    Antes:
        self.server_url = "https://private-keygen.pbzgje.easypanel.host"

    Depois:
        from utils.string_obfuscator import deobfuscate as _d
        self.server_url = _d("eJwrSS0u...")

    Args:
        code: Código-fonte
        plaintext: String a substituir
        var_name: Nome da variável (para comentários)

    Returns:
        Código modificado
    """
    obfuscated = obfuscate(plaintext)

    # Padrões para encontrar a string (com aspas simples ou duplas)
    patterns = [
        f'"{plaintext}"',
        f"'{plaintext}'",
    ]

    # String de substituição
    replacement = f'_d("{obfuscated}")  # {var_name}'

    modified = code
    for pattern in patterns:
        if pattern in modified:
            modified = modified.replace(pattern, replacement)
            _safe_print(f"  ✅ Ofuscado: {var_name}")

    return modified


def add_deobfuscate_import(code: str) -> str:
    """
    Adicionar import do deobfuscate no topo do arquivo

    Args:
        code: Código-fonte

    Returns:
        Código com import adicionado
    """
    # Verificar se já tem o import
    if 'from utils.string_obfuscator import deobfuscate' in code:
        return code

    # Encontrar onde adicionar (após outros imports)
    lines = code.split('\n')

    # Encontrar última linha de import
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('import ') or line.strip().startswith('from '):
            last_import_idx = i

    # Adicionar import após última linha de import
    import_line = 'from utils.string_obfuscator import deobfuscate as _d  # Auto-added for obfuscation'
    lines.insert(last_import_idx + 1, import_line)

    return '\n'.join(lines)


def obfuscate_file(file_path: Path, backup: bool = True) -> bool:
    """
    Ofuscar secrets em um arquivo

    Args:
        file_path: Caminho do arquivo
        backup: Se True, cria backup .bak

    Returns:
        True se modificações foram feitas
    """
    _safe_print(f"\n📄 Processando: {file_path.name}")

    try:
        # Ler código original
        with open(file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        modified_code = original_code
        modifications_made = False

        # Ofuscar cada secret
        for plaintext, var_name in SECRETS_TO_OBFUSCATE.items():
            if plaintext in modified_code:
                modified_code = obfuscate_string_in_code(modified_code, plaintext, var_name)
                modifications_made = True

        # Se houve modificações, adicionar import
        if modifications_made:
            modified_code = add_deobfuscate_import(modified_code)

            # Criar backup se solicitado
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_code)
                _safe_print(f"  💾 Backup criado: {backup_path.name}")

            # Salvar arquivo modificado
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_code)

            _safe_print(f"  ✅ Arquivo ofuscado com sucesso!")
            return True
        else:
            _safe_print(f"  ⏭️  Nenhum secret encontrado")
            return False

    except Exception as e:
        _safe_print(f"  ❌ Erro: {e}")
        return False


def restore_backup(file_path: Path) -> bool:
    """
    Restaurar arquivo do backup

    Args:
        file_path: Caminho do arquivo

    Returns:
        True se restaurado com sucesso
    """
    backup_path = file_path.with_suffix(file_path.suffix + '.bak')

    if not backup_path.exists():
        _safe_print(f"❌ Backup não encontrado: {backup_path}")
        return False

    try:
        with open(backup_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(original_code)

        _safe_print(f"✅ Restaurado: {file_path.name}")
        return True

    except Exception as e:
        _safe_print(f"❌ Erro ao restaurar: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
# MAIN - Processamento de arquivos
# ═══════════════════════════════════════════════════════════════════

def main():
    """Função principal"""
    _safe_print("\n" + "="*60)
    _safe_print("🔒 Secret Obfuscation Tool - Ultimate Fishing Bot v5.0")
    _safe_print("="*60)

    # Arquivos que contêm secrets
    files_to_process = [
        ROOT_DIR / 'utils' / 'license_manager.py',
        ROOT_DIR / 'main.py',
    ]

    # Verificar se arquivos existem
    missing_files = [f for f in files_to_process if not f.exists()]
    if missing_files:
        _safe_print("\n⚠️ Arquivos não encontrados:")
        for f in missing_files:
            _safe_print(f"  - {f}")
        return 1

    # Menu de opções
    _safe_print("\nOpções:")
    _safe_print("  1. Ofuscar secrets (criar backups .bak)")
    _safe_print("  2. Restaurar backups")
    _safe_print("  3. Sair")

    choice = input("\nEscolha uma opção (1-3): ").strip()

    if choice == '1':
        # Ofuscar arquivos
        _safe_print("\n🔒 Ofuscando secrets...")

        modified_count = 0
        for file_path in files_to_process:
            if obfuscate_file(file_path, backup=True):
                modified_count += 1

        _safe_print("\n" + "="*60)
        _safe_print(f"✅ Ofuscação concluída! ({modified_count} arquivo(s) modificado(s))")
        _safe_print("="*60)
        _safe_print("\n⚠️ IMPORTANTE:")
        _safe_print("  - Backups .bak foram criados")
        _safe_print("  - Teste o código antes de compilar")
        _safe_print("  - Use 'python main.py' para verificar funcionamento")
        _safe_print("  - Se tudo OK, compile com build_nuitka.py")
        _safe_print("\n💡 Para reverter: execute este script e escolha opção 2")

    elif choice == '2':
        # Restaurar backups
        _safe_print("\n🔄 Restaurando backups...")

        restored_count = 0
        for file_path in files_to_process:
            if restore_backup(file_path):
                restored_count += 1

        _safe_print("\n" + "="*60)
        _safe_print(f"✅ Restauração concluída! ({restored_count} arquivo(s) restaurado(s))")
        _safe_print("="*60)

    else:
        _safe_print("\n👋 Saindo...")
        return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _safe_print("\n\n⚠️ Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        _safe_print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
