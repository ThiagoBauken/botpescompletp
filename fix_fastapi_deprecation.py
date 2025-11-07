#!/usr/bin/env python3
"""
🔧 Script de Correção Automática: FastAPI DeprecationWarning

Este script corrige automaticamente os warnings de @app.on_event()
migrando para o padrão lifespan do FastAPI.

Uso:
    python fix_fastapi_deprecation.py server/server.py

Ou se o arquivo estiver em outro local:
    python fix_fastapi_deprecation.py /caminho/para/server.py
"""

import re
import sys
import os
from pathlib import Path

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def backup_file(file_path):
    """Criar backup do arquivo original"""
    backup_path = f"{file_path}.backup"

    if os.path.exists(backup_path):
        _safe_print(f"⚠️ Backup já existe: {backup_path}")
        response = input("Sobrescrever? (s/N): ").strip().lower()
        if response != 's':
            _safe_print("❌ Operação cancelada")
            return None

    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        _safe_print(f"✅ Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        _safe_print(f"❌ Erro ao criar backup: {e}")
        return None

def extract_startup_shutdown(content):
    """Extrair código dos eventos startup e shutdown"""

    # Padrão para @app.on_event("startup")
    startup_pattern = r'@app\.on_event\(["\']startup["\']\)\s*\n\s*async\s+def\s+\w+\([^)]*\):\s*\n((?:.*\n)*?)(?=\n@|\napp\s*=|\n\nclass|\n\ndef\s+\w+|\Z)'

    # Padrão para @app.on_event("shutdown")
    shutdown_pattern = r'@app\.on_event\(["\']shutdown["\']\)\s*\n\s*async\s+def\s+\w+\([^)]*\):\s*\n((?:.*\n)*?)(?=\n@|\napp\s*=|\n\nclass|\n\ndef\s+\w+|\Z)'

    startup_match = re.search(startup_pattern, content)
    shutdown_match = re.search(shutdown_pattern, content)

    startup_code = ""
    shutdown_code = ""

    if startup_match:
        startup_code = startup_match.group(1).rstrip()
        _safe_print("✅ Código de startup encontrado")
    else:
        _safe_print("⚠️ Código de startup não encontrado")

    if shutdown_match:
        shutdown_code = shutdown_match.group(1).rstrip()
        _safe_print("✅ Código de shutdown encontrado")
    else:
        _safe_print("⚠️ Código de shutdown não encontrado")

    return startup_code, shutdown_code

def create_lifespan_function(startup_code, shutdown_code):
    """Criar função lifespan com o código extraído"""

    # Remover indentação extra se houver
    def dedent_code(code):
        if not code:
            return ""
        lines = code.split('\n')
        # Encontrar indentação mínima (ignorando linhas vazias)
        min_indent = min((len(line) - len(line.lstrip())
                         for line in lines if line.strip()), default=0)
        # Remover indentação comum
        dedented = '\n'.join(line[min_indent:] if line.strip() else line
                            for line in lines)
        return dedented

    startup_code = dedent_code(startup_code)
    shutdown_code = dedent_code(shutdown_code)

    # Adicionar indentação correta (4 espaços)
    def indent_code(code, spaces=4):
        if not code:
            return ""
        indent = ' ' * spaces
        return '\n'.join(indent + line if line.strip() else line
                        for line in code.split('\n'))

    startup_indented = indent_code(startup_code, 4)
    shutdown_indented = indent_code(shutdown_code, 4)

    lifespan_code = f'''@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do servidor

    Substitui @app.on_event("startup") e @app.on_event("shutdown")
    para eliminar DeprecationWarnings do FastAPI.
    """

    # ═══════════════════════════════════════════════════════
    # STARTUP - Executado quando servidor inicia
    # ═══════════════════════════════════════════════════════

{startup_indented}

    yield  # Servidor roda aqui

    # ═══════════════════════════════════════════════════════
    # SHUTDOWN - Executado quando servidor desliga
    # ═══════════════════════════════════════════════════════

{shutdown_indented}
'''

    return lifespan_code

def check_imports(content):
    """Verificar se imports necessários existem"""
    has_asynccontextmanager = 'from contextlib import asynccontextmanager' in content
    has_fastapi_import = 'from fastapi import FastAPI' in content or 'import fastapi' in content

    return has_asynccontextmanager, has_fastapi_import

def add_import(content):
    """Adicionar import do asynccontextmanager se necessário"""

    # Procurar onde adicionar o import
    # Tentativa 1: Depois de outras importações do contextlib
    if 'from contextlib import' in content:
        content = re.sub(
            r'(from contextlib import [^\n]+)',
            r'\1, asynccontextmanager',
            content,
            count=1
        )
        _safe_print("✅ Adicionado asynccontextmanager ao import existente")

    # Tentativa 2: Adicionar nova linha após imports do FastAPI
    elif 'from fastapi import' in content:
        content = re.sub(
            r'(from fastapi import [^\n]+\n)',
            r'\1from contextlib import asynccontextmanager\n',
            content,
            count=1
        )
        _safe_print("✅ Adicionado import de asynccontextmanager")

    # Tentativa 3: Adicionar no início dos imports
    else:
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_pos = i + 1
                break

        if insert_pos > 0:
            lines.insert(insert_pos, 'from contextlib import asynccontextmanager')
            content = '\n'.join(lines)
            _safe_print("✅ Adicionado import de asynccontextmanager")

    return content

def remove_old_event_handlers(content):
    """Remover decoradores @app.on_event antigos"""

    # Remover @app.on_event("startup") e sua função
    content = re.sub(
        r'@app\.on_event\(["\']startup["\']\)\s*\n\s*async\s+def\s+\w+\([^)]*\):\s*\n(?:.*\n)*?(?=\n@|\napp\s*=|\n\nclass|\n\ndef\s+\w+)',
        '',
        content
    )

    # Remover @app.on_event("shutdown") e sua função
    content = re.sub(
        r'@app\.on_event\(["\']shutdown["\']\)\s*\n\s*async\s+def\s+\w+\([^)]*\):\s*\n(?:.*\n)*?(?=\n@|\napp\s*=|\n\nclass|\n\ndef\s+\w+)',
        '',
        content
    )

    _safe_print("✅ Decoradores @app.on_event() removidos")

    return content

def modify_fastapi_init(content, has_lifespan_already=False):
    """Modificar inicialização do FastAPI para usar lifespan"""

    if has_lifespan_already:
        _safe_print("ℹ️ FastAPI já usa lifespan, pulando modificação")
        return content

    # Padrão 1: app = FastAPI()
    if re.search(r'app\s*=\s*FastAPI\(\s*\)', content):
        content = re.sub(
            r'app\s*=\s*FastAPI\(\s*\)',
            'app = FastAPI(lifespan=lifespan)',
            content
        )
        _safe_print("✅ Modificado: app = FastAPI(lifespan=lifespan)")

    # Padrão 2: app = FastAPI(title=..., version=...)
    elif re.search(r'app\s*=\s*FastAPI\([^)]+\)', content):
        content = re.sub(
            r'(app\s*=\s*FastAPI\()([^)]+)(\))',
            r'\1\2, lifespan=lifespan\3',
            content
        )
        _safe_print("✅ Adicionado lifespan=lifespan ao FastAPI()")

    else:
        _safe_print("⚠️ Não encontrado padrão de inicialização do FastAPI")

    return content

def fix_fastapi_deprecation(file_path):
    """Função principal para corrigir o arquivo"""

    _safe_print("\n" + "="*60)
    _safe_print("🔧 Correção Automática: FastAPI DeprecationWarning")
    _safe_print("="*60)

    # Verificar se arquivo existe
    if not os.path.exists(file_path):
        _safe_print(f"❌ Arquivo não encontrado: {file_path}")
        return False

    _safe_print(f"\n📂 Arquivo: {file_path}")

    # Criar backup
    _safe_print("\n1️⃣ Criando backup...")
    if not backup_file(file_path):
        return False

    # Ler arquivo
    _safe_print("\n2️⃣ Lendo arquivo...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        _safe_print(f"✅ Arquivo lido: {len(content)} caracteres")
    except Exception as e:
        _safe_print(f"❌ Erro ao ler arquivo: {e}")
        return False

    # Verificar se já foi corrigido
    if 'lifespan=lifespan' in content and '@asynccontextmanager' in content:
        _safe_print("\n✅ Arquivo já foi corrigido! (contém lifespan)")
        return True

    # Extrair código de startup e shutdown
    _safe_print("\n3️⃣ Extraindo código de startup e shutdown...")
    startup_code, shutdown_code = extract_startup_shutdown(content)

    if not startup_code and not shutdown_code:
        _safe_print("⚠️ Nenhum código de evento encontrado, arquivo pode já estar correto")
        return False

    # Criar função lifespan
    _safe_print("\n4️⃣ Criando função lifespan...")
    lifespan_func = create_lifespan_function(startup_code, shutdown_code)
    _safe_print("✅ Função lifespan criada")

    # Verificar imports
    _safe_print("\n5️⃣ Verificando imports...")
    has_async, has_fastapi = check_imports(content)

    if not has_async:
        _safe_print("⚠️ Import de asynccontextmanager não encontrado, adicionando...")
        content = add_import(content)
    else:
        _safe_print("✅ Import de asynccontextmanager já existe")

    # Encontrar onde inserir lifespan (antes da criação do app)
    _safe_print("\n6️⃣ Inserindo função lifespan...")

    # Procurar por "app = FastAPI"
    app_match = re.search(r'(app\s*=\s*FastAPI\()', content)

    if app_match:
        insert_pos = app_match.start()

        # Inserir lifespan antes de app = FastAPI()
        content = content[:insert_pos] + lifespan_func + '\n\n' + content[insert_pos:]
        _safe_print("✅ Função lifespan inserida")
    else:
        _safe_print("⚠️ Não encontrado 'app = FastAPI()', adicionando no final dos imports")
        # Adicionar após todos os imports
        lines = content.split('\n')
        last_import = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import = i + 1

        lines.insert(last_import + 2, lifespan_func)
        content = '\n'.join(lines)
        _safe_print("✅ Função lifespan adicionada")

    # Remover decoradores antigos
    _safe_print("\n7️⃣ Removendo decoradores @app.on_event()...")
    content = remove_old_event_handlers(content)

    # Modificar inicialização do FastAPI
    _safe_print("\n8️⃣ Modificando FastAPI() para usar lifespan...")
    has_lifespan = 'lifespan=lifespan' in content
    content = modify_fastapi_init(content, has_lifespan)

    # Salvar arquivo modificado
    _safe_print("\n9️⃣ Salvando arquivo modificado...")
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        _safe_print(f"✅ Arquivo salvo: {file_path}")
    except Exception as e:
        _safe_print(f"❌ Erro ao salvar arquivo: {e}")
        return False

    _safe_print("\n" + "="*60)
    _safe_print("✅ Correção concluída com sucesso!")
    _safe_print("="*60)

    _safe_print("\n📋 Próximos passos:")
    _safe_print("   1. Reinicie o servidor")
    _safe_print("   2. Verifique que não há mais warnings")
    _safe_print("   3. Teste que tudo funciona corretamente")
    _safe_print(f"   4. Se houver problemas, restaure: {file_path}.backup")

    return True

def main():
    """Função principal"""

    if len(sys.argv) < 2:
        _safe_print("❌ Uso: python fix_fastapi_deprecation.py <caminho-para-server.py>")
        _safe_print("\nExemplos:")
        _safe_print("   python fix_fastapi_deprecation.py server/server.py")
        _safe_print("   python fix_fastapi_deprecation.py /app/server.py")
        sys.exit(1)

    file_path = sys.argv[1]

    success = fix_fastapi_deprecation(file_path)

    if success:
        _safe_print("\n🎉 Sucesso! Arquivo corrigido.")
        sys.exit(0)
    else:
        _safe_print("\n❌ Falha ao corrigir arquivo.")
        sys.exit(1)

if __name__ == "__main__":
    main()
