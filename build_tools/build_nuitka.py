#!/usr/bin/env python3
"""
🔨 Ultimate Fishing Bot v5.0 - Nuitka Build Script
Script automatizado para compilar com Nuitka + ofuscação de strings
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Wrapper de print seguro
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


# ═══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DO BUILD
# ═══════════════════════════════════════════════════════════════════

ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
MAIN_FILE = ROOT_DIR / "main.py"

BUILD_CONFIG = {
    # Informações do produto
    "product_name": "UltimateFishingBot",
    "company_name": "Ultimate Fishing Bot",
    "file_version": "5.0.0.0",
    "product_version": "5.0.0",
    "file_description": "Advanced Fishing Automation System",
    "copyright": f"Copyright {datetime.now().year}",

    # Opções de compilação
    "standalone": True,
    "onefile": True,
    "windows_disable_console": False,  # False = mostra console (True para release final)
    "remove_output": True,  # Limpar arquivos temporários

    # Plugins
    "plugins": [
        "tk-inter",  # Para tkinter UI
        # "numpy" se usar numpy
    ],

    # Diretórios de dados para incluir
    "include_data_dirs": [
        ("templates", "templates"),
        ("locales", "locales"),
        ("config", "config"),
    ],

    # Arquivos de dados para incluir
    "include_data_files": [
        ("README.md", "README.md"),
    ],

    # Otimizações
    "lto": "yes",  # Link Time Optimization (yes/no/auto)
    "jobs": 4,     # Número de threads de compilação

    # Ícone (opcional)
    "icon_path": None,  # ROOT_DIR / "assets" / "icon.ico"
}


# ═══════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════════════════

def check_nuitka_installed() -> bool:
    """Verificar se Nuitka está instalado"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            _safe_print(f"✅ Nuitka encontrado: {version}")
            return True
        return False
    except Exception:
        return False


def install_nuitka():
    """Instalar Nuitka via pip"""
    _safe_print("\n📦 Instalando Nuitka...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "nuitka"],
            check=True
        )
        _safe_print("✅ Nuitka instalado com sucesso!")
        return True
    except Exception as e:
        _safe_print(f"❌ Erro ao instalar Nuitka: {e}")
        return False


def clean_build_dirs():
    """Limpar diretórios de build antigos"""
    _safe_print("\n🧹 Limpando diretórios de build...")

    dirs_to_clean = [BUILD_DIR, DIST_DIR]

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                _safe_print(f"  ✅ Removido: {dir_path.name}")
            except Exception as e:
                _safe_print(f"  ⚠️ Erro ao remover {dir_path.name}: {e}")

    # Remover cache do Nuitka
    nuitka_cache = ROOT_DIR / "main.build"
    if nuitka_cache.exists():
        try:
            shutil.rmtree(nuitka_cache)
            _safe_print(f"  ✅ Removido: main.build (cache)")
        except Exception as e:
            _safe_print(f"  ⚠️ Erro ao remover cache: {e}")


def build_nuitka_command() -> list:
    """Construir comando Nuitka"""

    cmd = [
        sys.executable,
        "-m", "nuitka",
        str(MAIN_FILE),
    ]

    # Modo standalone
    if BUILD_CONFIG["standalone"]:
        cmd.append("--standalone")

    # Onefile
    if BUILD_CONFIG["onefile"]:
        cmd.append("--onefile")

    # Desabilitar console (Windows)
    if BUILD_CONFIG["windows_disable_console"] and sys.platform == "win32":
        cmd.append("--windows-disable-console")

    # Remover output
    if BUILD_CONFIG["remove_output"]:
        cmd.append("--remove-output")

    # Plugins
    for plugin in BUILD_CONFIG["plugins"]:
        cmd.append(f"--enable-plugin={plugin}")

    # Incluir diretórios de dados
    for src, dst in BUILD_CONFIG["include_data_dirs"]:
        src_path = ROOT_DIR / src
        if src_path.exists():
            cmd.append(f"--include-data-dir={src}={dst}")

    # Incluir arquivos de dados
    for src, dst in BUILD_CONFIG["include_data_files"]:
        src_path = ROOT_DIR / src
        if src_path.exists():
            cmd.append(f"--include-data-file={src}={dst}")

    # Otimizações
    if BUILD_CONFIG["lto"]:
        cmd.append(f"--lto={BUILD_CONFIG['lto']}")

    if BUILD_CONFIG["jobs"]:
        cmd.append(f"--jobs={BUILD_CONFIG['jobs']}")

    # Ícone (Windows)
    if BUILD_CONFIG["icon_path"] and sys.platform == "win32":
        icon_path = BUILD_CONFIG["icon_path"]
        if icon_path and icon_path.exists():
            cmd.append(f"--windows-icon-from-ico={icon_path}")

    # Informações de versão (Windows)
    if sys.platform == "win32":
        cmd.extend([
            f"--windows-company-name={BUILD_CONFIG['company_name']}",
            f"--windows-product-name={BUILD_CONFIG['product_name']}",
            f"--windows-file-version={BUILD_CONFIG['file_version']}",
            f"--windows-product-version={BUILD_CONFIG['product_version']}",
            f"--windows-file-description={BUILD_CONFIG['file_description']}",
        ])

    # Output directory
    cmd.append(f"--output-dir={DIST_DIR}")

    return cmd


def run_nuitka_build() -> bool:
    """Executar build do Nuitka"""
    _safe_print("\n🔨 Iniciando compilação com Nuitka...")
    _safe_print("=" * 60)

    cmd = build_nuitka_command()

    # Mostrar comando
    _safe_print("\n📋 Comando Nuitka:")
    _safe_print(" ".join(cmd))
    _safe_print("\n" + "=" * 60)

    try:
        # Executar Nuitka
        result = subprocess.run(cmd, cwd=ROOT_DIR)

        if result.returncode == 0:
            _safe_print("\n" + "=" * 60)
            _safe_print("✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
            _safe_print("=" * 60)
            return True
        else:
            _safe_print("\n" + "=" * 60)
            _safe_print("❌ COMPILAÇÃO FALHOU!")
            _safe_print("=" * 60)
            return False

    except Exception as e:
        _safe_print(f"\n❌ Erro durante compilação: {e}")
        return False


def find_executable() -> Path:
    """Encontrar executável gerado"""
    if BUILD_CONFIG["onefile"]:
        # Onefile: executável único
        exe_name = "main.exe" if sys.platform == "win32" else "main.bin"
        exe_path = DIST_DIR / exe_name
        if exe_path.exists():
            return exe_path

    # Standalone: procurar em dist/main.dist/
    dist_folder = DIST_DIR / "main.dist"
    if dist_folder.exists():
        for file in dist_folder.iterdir():
            if file.name.endswith((".exe", ".bin")):
                return file

    return None


def show_build_summary(success: bool, exe_path: Path = None):
    """Mostrar resumo do build"""
    _safe_print("\n" + "=" * 60)
    _safe_print("📊 RESUMO DO BUILD")
    _safe_print("=" * 60)

    if success and exe_path:
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        _safe_print(f"\n✅ Executável gerado:")
        _safe_print(f"   📍 Local: {exe_path}")
        _safe_print(f"   📦 Tamanho: {file_size:.2f} MB")

        _safe_print(f"\n📝 Informações:")
        _safe_print(f"   Nome: {BUILD_CONFIG['product_name']}")
        _safe_print(f"   Versão: {BUILD_CONFIG['product_version']}")
        _safe_print(f"   Descrição: {BUILD_CONFIG['file_description']}")

        _safe_print(f"\n🔒 Proteções aplicadas:")
        _safe_print(f"   ✅ Código compilado para C")
        _safe_print(f"   ✅ Strings ofuscadas (se executou obfuscate_secrets.py)")
        _safe_print(f"   ✅ Licenças criptografadas com AES-256")

        _safe_print(f"\n🚀 Próximos passos:")
        _safe_print(f"   1. Teste o executável: {exe_path}")
        _safe_print(f"   2. Verifique se todas as funcionalidades funcionam")
        _safe_print(f"   3. (Opcional) Assine digitalmente com certificado")
        _safe_print(f"   4. Distribua o executável")

    else:
        _safe_print("\n❌ Build falhou! Verifique os erros acima.")
        _safe_print("\n💡 Dicas de troubleshooting:")
        _safe_print("   - Verifique se todas as dependências estão instaladas")
        _safe_print("   - Execute: pip install -r requirements.txt")
        _safe_print("   - Verifique se os caminhos de templates/locales existem")

    _safe_print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════
# MAIN - Fluxo de build
# ═══════════════════════════════════════════════════════════════════

def main():
    """Função principal de build"""
    _safe_print("\n" + "=" * 60)
    _safe_print("🔨 ULTIMATE FISHING BOT v5.0 - BUILD SCRIPT")
    _safe_print("=" * 60)

    # 1. Verificar se está no diretório correto
    if not MAIN_FILE.exists():
        _safe_print(f"\n❌ Erro: main.py não encontrado em {ROOT_DIR}")
        return 1

    # 2. Verificar Nuitka
    _safe_print("\n📦 Verificando Nuitka...")
    if not check_nuitka_installed():
        _safe_print("⚠️ Nuitka não encontrado!")

        choice = input("\nDeseja instalar Nuitka agora? (s/n): ").strip().lower()
        if choice == 's':
            if not install_nuitka():
                return 1
        else:
            _safe_print("❌ Build cancelado. Instale Nuitka com: pip install nuitka")
            return 1

    # 3. Ofuscação de strings (opcional)
    _safe_print("\n🔒 Ofuscação de strings")
    _safe_print("⚠️ IMPORTANTE: Execute build_tools/obfuscate_secrets.py ANTES de compilar!")
    _safe_print("   Isso protegerá URLs e chaves sensíveis no binário.")

    choice = input("\nJá executou obfuscate_secrets.py? (s/n): ").strip().lower()
    if choice != 's':
        _safe_print("\n💡 Execute primeiro:")
        _safe_print("   python build_tools/obfuscate_secrets.py")
        _safe_print("\nDepois execute este script novamente.")
        return 0

    # 4. Limpar builds antigos
    choice = input("\nLimpar builds antigos? (s/n): ").strip().lower()
    if choice == 's':
        clean_build_dirs()

    # 5. Configurar modo
    _safe_print("\n⚙️ Configuração do build:")
    _safe_print(f"   Standalone: {BUILD_CONFIG['standalone']}")
    _safe_print(f"   Onefile: {BUILD_CONFIG['onefile']}")
    _safe_print(f"   Console: {'Habilitado' if not BUILD_CONFIG['windows_disable_console'] else 'Desabilitado'}")

    choice = input("\nContinuar com esta configuração? (s/n): ").strip().lower()
    if choice != 's':
        _safe_print("\n💡 Edite BUILD_CONFIG em build_nuitka.py para alterar")
        return 0

    # 6. Executar build
    success = run_nuitka_build()

    # 7. Encontrar executável
    exe_path = None
    if success:
        exe_path = find_executable()
        if not exe_path:
            _safe_print("\n⚠️ Executável não encontrado em dist/")

    # 8. Mostrar resumo
    show_build_summary(success, exe_path)

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _safe_print("\n\n⚠️ Build interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        _safe_print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
