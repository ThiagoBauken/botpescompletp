#!/usr/bin/env python3
"""
Script para corrigir encoding em todos os arquivos core
Adiciona wrapper _safe_print em todos os arquivos
"""

import os
import re
from pathlib import Path

SAFE_PRINT_HEADER = """
# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\\x00-\\x7F]+', '?', str(text))
        print(clean)
"""

def fix_file(filepath):
    """Corrigir um arquivo"""
    print(f"Processando: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar se já tem o wrapper
        if '_safe_print' in content:
            print(f"  [SKIP] Arquivo ja possui _safe_print")
            return False

        # Adicionar import re se não tiver
        if 'import re' not in content and 'from re import' not in content:
            # Adicionar após os imports
            lines = content.split('\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_end = i + 1

            lines.insert(import_end, 'import re')
            content = '\n'.join(lines)

        # Adicionar o wrapper após os imports
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_end = i + 1

        lines.insert(import_end, SAFE_PRINT_HEADER)
        content = '\n'.join(lines)

        # Substituir print( por _safe_print(
        content = re.sub(r'(\s+)print\(', r'\1_safe_print(', content)

        # Salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  [OK] Arquivo corrigido")
        return True

    except Exception as e:
        print(f"  [ERRO] {e}")
        return False

def main():
    core_dir = Path(__file__).parent / 'core'

    if not core_dir.exists():
        print(f"ERRO: Pasta core nao encontrada: {core_dir}")
        return 1

    py_files = list(core_dir.glob('*.py'))

    print(f"\nEncontrados {len(py_files)} arquivos Python em core/\n")

    fixed_count = 0
    for py_file in py_files:
        if py_file.name == '__init__.py':
            continue

        if fix_file(py_file):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {fixed_count} arquivos corrigidos")
    print(f"{'='*60}")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
