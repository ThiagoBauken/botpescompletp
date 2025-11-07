#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples de Hotkeys - Diagnosticar Problemas
"""

import sys
import time

# Configurar encoding para Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

def safe_print(text):
    """Print seguro com fallback para Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)

safe_print("=" * 60)
safe_print("TESTE DE HOTKEYS - Ultimate Fishing Bot v4.0")
safe_print("=" * 60)

# Teste 1: Importar biblioteca keyboard
safe_print("\nTeste 1: Importando biblioteca keyboard...")
try:
    import keyboard
    safe_print("OK - Biblioteca keyboard importada com sucesso")
    safe_print(f"   Localizacao: {keyboard.__file__}")
except ImportError as e:
    safe_print(f"ERRO: Nao foi possivel importar keyboard: {e}")
    safe_print("\nSolucao:")
    safe_print("   pip install keyboard")
    sys.exit(1)

# Teste 2: Verificar permissoes de administrador (Windows)
safe_print("\nTeste 2: Verificando permissoes...")
try:
    import ctypes
    import os

    if os.name == 'nt':  # Windows
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            safe_print("OK - Executando com permissoes de administrador")
        else:
            safe_print("AVISO - NAO esta executando como administrador")
            safe_print("   ISSO PODE IMPEDIR AS HOTKEYS DE FUNCIONAREM!")
            safe_print("\nSolucao:")
            safe_print("   1. Feche este programa")
            safe_print("   2. Clique com botao direito no CMD/PowerShell")
            safe_print("   3. Selecione 'Executar como administrador'")
            safe_print("   4. Execute este teste novamente")
            safe_print("\n   OU continue para testar mesmo assim...")
except Exception as e:
    safe_print(f"AVISO - Nao foi possivel verificar permissoes: {e}")

# Teste 3: Testar registro de hotkeys básicas
print("\n⌨️ Teste 3: Registrando hotkeys de teste...")

hotkey_triggered = {
    'f9': False,
    'f6': False,
    'f1': False,
    'esc': False
}

def make_callback(key_name):
    def callback():
        hotkey_triggered[key_name] = True
        print(f"\n🎯 HOTKEY DETECTADA: {key_name.upper()}")
        print(f"   Timestamp: {time.time()}")
    return callback

try:
    # Limpar hotkeys anteriores
    try:
        keyboard.unhook_all()
    except:
        pass

    # Registrar hotkeys de teste
    test_hotkeys = ['f9', 'f6', 'f1', 'esc']

    for key in test_hotkeys:
        try:
            keyboard.add_hotkey(key, make_callback(key))
            print(f"  ✅ {key.upper()} registrado com sucesso")
        except Exception as e:
            print(f"  ❌ {key.upper()} falhou ao registrar: {e}")

    print("\n" + "=" * 60)
    print("🎮 TESTE INTERATIVO - Pressione as teclas:")
    print("=" * 60)
    print("  F9  - Testar F9 (Iniciar bot)")
    print("  F6  - Testar F6 (Alimentação)")
    print("  F1  - Testar F1 (Pausar)")
    print("  ESC - Sair do teste")
    print("=" * 60)
    print("\n⏳ Aguardando pressionamento de teclas...")
    print("   (Pressione ESC para sair)")

    # Loop de espera
    start_time = time.time()
    esc_pressed = False

    while not esc_pressed and (time.time() - start_time) < 60:
        if hotkey_triggered['esc']:
            esc_pressed = True
            print("\n🛑 ESC detectado - Encerrando teste...")
            break

        time.sleep(0.1)

    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DO TESTE")
    print("=" * 60)

    any_triggered = False
    for key, triggered in hotkey_triggered.items():
        status = "✅ FUNCIONOU" if triggered else "❌ NÃO DETECTADO"
        print(f"  {key.upper()}: {status}")
        if triggered:
            any_triggered = True

    print("\n" + "=" * 60)
    if any_triggered:
        print("✅ RESULTADO: Hotkeys estão funcionando!")
        print("   O problema pode estar na integração com o bot.")
    else:
        print("❌ RESULTADO: Nenhuma hotkey foi detectada!")
        print("\n🔧 POSSÍVEIS CAUSAS:")
        print("   1. Não está executando como administrador (Windows)")
        print("   2. Outro programa está bloqueando as hotkeys")
        print("   3. Problema com a biblioteca keyboard")
        print("   4. Antivírus ou software de segurança bloqueando")
        print("\n🔧 SOLUÇÕES:")
        print("   1. Execute como administrador")
        print("   2. Feche outros programas que usam hotkeys globais")
        print("   3. Reinstale keyboard: pip uninstall keyboard && pip install keyboard")
        print("   4. Desabilite temporariamente o antivírus para testar")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERRO durante o teste: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Limpar hotkeys
    try:
        keyboard.unhook_all()
        print("\n🧹 Hotkeys removidas")
    except:
        pass

print("\n✅ Teste finalizado!")
