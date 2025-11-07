"""
Patch para adicionar calibração automática do MouseTo no chest_manager.py

Este script adiciona automaticamente a chamada para calibrate_mouseto()
após detectar que o baú foi aberto.
"""

import os
import re


def patch_chest_manager():
    """Adiciona calibração automática no ChestManager"""

    file_path = "core/chest_manager.py"

    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        print("   Certifique-se de executar no diretório v5/")
        return False

    # Ler arquivo
    print(f"📖 Lendo {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Verificar se já tem o patch
    if 'calibrate_mouseto' in content:
        print("⚠️ Patch já foi aplicado anteriormente!")
        print("   O código de calibração já está no arquivo.")
        return True

    # Padrão para encontrar onde adicionar (após detectar baú aberto)
    pattern = r"(self\.chest_open = True\s*\n\s*_safe_print\(.*?ba[uú] aberto.*?\"\))"

    # Substituição com código de calibração
    replacement = r'''\1

        # ✅ PATCH: Calibrar MouseTo após abrir baú (Arduino)
        if hasattr(self.input_manager, 'calibrate_mouseto'):
            _safe_print("🎯 Calibrando MouseTo após abrir baú...")
            try:
                self.input_manager.calibrate_mouseto(959, 539)
                _safe_print("✅ MouseTo calibrado!")
            except Exception as e:
                _safe_print(f"⚠️ Erro ao calibrar MouseTo: {e}")'''

    # Aplicar patch
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content == content:
        print("❌ Não foi possível encontrar o local para adicionar o patch")
        print("   Vou tentar um método alternativo...")

        # Método alternativo: buscar apenas "self.chest_open = True"
        pattern2 = r"(self\.chest_open = True)"
        replacement2 = r'''\1

        # ✅ PATCH: Calibrar MouseTo após abrir baú (Arduino)
        if hasattr(self.input_manager, 'calibrate_mouseto'):
            _safe_print("🎯 Calibrando MouseTo após abrir baú...")
            try:
                self.input_manager.calibrate_mouseto(959, 539)
                _safe_print("✅ MouseTo calibrado!")
            except Exception as e:
                _safe_print(f"⚠️ Erro ao calibrar MouseTo: {e}")'''

        new_content = re.sub(pattern2, replacement2, content)

        if new_content == content:
            print("❌ Falha ao aplicar patch automaticamente")
            print()
            print("📋 Adicione manualmente no arquivo core/chest_manager.py")
            print("   Após a linha 'self.chest_open = True', adicione:")
            print()
            print('''
        # Calibrar MouseTo após abrir baú
        if hasattr(self.input_manager, 'calibrate_mouseto'):
            _safe_print("🎯 Calibrando MouseTo após abrir baú...")
            self.input_manager.calibrate_mouseto(959, 539)
            ''')
            return False

    # Fazer backup
    backup_path = file_path + ".backup"
    print(f"💾 Criando backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Salvar arquivo modificado
    print(f"✍️ Aplicando patch em {file_path}...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print()
    print("="*70)
    print("✅ PATCH APLICADO COM SUCESSO!")
    print("="*70)
    print()
    print("Mudanças:")
    print("  ✅ Calibração automática adicionada ao ChestManager")
    print("  ✅ Backup criado em core/chest_manager.py.backup")
    print()
    print("Agora quando o baú abrir, o MouseTo será calibrado automaticamente!")
    print()
    print("Próximos passos:")
    print("  1. Verificar resolução: python -c \"import pyautogui; print(pyautogui.size())\"")
    print("  2. Testar posicionamento: python test_arduino_manual_positioning.py")
    print("  3. Testar Page Down no jogo")
    print()

    return True


if __name__ == "__main__":
    print("="*70)
    print("🔧 PATCH: Adicionar Calibração Automática do MouseTo")
    print("="*70)
    print()

    success = patch_chest_manager()

    if not success:
        print()
        print("="*70)
        print("❌ PATCH FALHOU")
        print("="*70)
        print()
        print("Consulte SOLUCAO_MOUSETO_POSICIONAMENTO.md para instruções manuais")
    else:
        print("="*70)
        print("✅ PATCH CONCLUÍDO")
        print("="*70)
