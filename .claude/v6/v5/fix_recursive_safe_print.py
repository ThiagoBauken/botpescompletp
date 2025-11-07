#!/usr/bin/env python3
"""
Script para corrigir as funcoes _safe_print recursivas
Substitui _safe_print(text) por print(text) DENTRO da funcao _safe_print
"""

import os
import re
from pathlib import Path

def fix_recursive_safe_print(filepath):
    """Corrigir funcao _safe_print recursiva em um arquivo"""
    print(f"Processando: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar se tem a funcao _safe_print
        if 'def _safe_print(text):' not in content:
            print(f"  [SKIP] Arquivo nao possui _safe_print")
            return False

        # Padrao correto da funcao
        correct_pattern = """def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\\x00-\\x7F]+', '?', str(text))
        print(clean)"""

        # Padrao errado (recursivo) - variacoes
        wrong_patterns = [
            # Variacao 1: com import re as _re
            r'def _safe_print\(text\):\s+try:\s+_safe_print\(text\)\s+except \(UnicodeEncodeError, UnicodeDecodeError\):\s+import re as _re\s+clean = _re\.sub\(r\'\[\^\\\\x00-\\\\x7F\]\+\', \'\?\', str\(text\)\)\s+_safe_print\(clean\)',
            # Variacao 2: com import re
            r'def _safe_print\(text\):\s+try:\s+_safe_print\(text\)\s+except \(UnicodeEncodeError, UnicodeDecodeError\):\s+import re\s+clean = re\.sub\(r\'\[\^\\\\x00-\\\\x7F\]\+\', \'\?\', str\(text\)\)\s+_safe_print\(clean\)',
        ]

        # Verificar se esta recursivo
        is_recursive = '_safe_print(text)' in content and 'def _safe_print(text):' in content

        if not is_recursive:
            print(f"  [SKIP] Funcao _safe_print nao esta recursiva")
            return False

        # Substituir usando abordagem mais direta
        # Encontrar o bloco da funcao _safe_print e substituir
        lines = content.split('\n')
        new_lines = []
        in_safe_print = False
        skip_until_blank = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Detectar inicio da funcao _safe_print
            if 'def _safe_print(text):' in line:
                in_safe_print = True
                # Adicionar a funcao correta
                new_lines.append('def _safe_print(text):')
                new_lines.append('    try:')
                new_lines.append('        print(text)')
                new_lines.append('    except (UnicodeEncodeError, UnicodeDecodeError):')
                new_lines.append('        import re as _re')
                new_lines.append('        clean = _re.sub(r\'[^\\x00-\\x7F]+\', \'?\', str(text))')
                new_lines.append('        print(clean)')
                skip_until_blank = True
                i += 1
                continue

            # Pular linhas da funcao errada ate encontrar linha em branco
            if skip_until_blank:
                if line.strip() == '':
                    skip_until_blank = False
                    in_safe_print = False
                    new_lines.append(line)
                i += 1
                continue

            # Linha normal
            new_lines.append(line)
            i += 1

        new_content = '\n'.join(new_lines)

        # Salvar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"  [OK] Funcao _safe_print corrigida")
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

        if fix_recursive_safe_print(py_file):
            fixed_count += 1

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {fixed_count} arquivos corrigidos")
    print(f"{'='*60}")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
