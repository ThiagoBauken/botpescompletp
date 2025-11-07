#!/usr/bin/env python3
"""
🧪 Teste de Hotkeys
Verifica se as hotkeys estão funcionando corretamente
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time

def test_hotkeys():
    """Testar hotkeys individualmente"""
    print("🧪 Testando sistema de hotkeys...")
    
    try:
        import keyboard
        print("✅ Biblioteca keyboard importada")
        
        # Contador de testes
        test_results = {
            'f9_calls': 0,
            'tab_calls': 0,
            'f1_calls': 0
        }
        
        def test_f9():
            test_results['f9_calls'] += 1
            print(f"🟢 F9 pressionado! Total: {test_results['f9_calls']}")
        
        def test_tab():
            test_results['tab_calls'] += 1
            print(f"🔵 TAB pressionado! Total: {test_results['tab_calls']}")
        
        def test_f1():
            test_results['f1_calls'] += 1
            print(f"🟡 F1 pressionado! Total: {test_results['f1_calls']}")
        
        def test_exit():
            print("🛑 ESC pressionado - saindo...")
            return False
        
        # Limpar hotkeys
        keyboard.clear_all_hotkeys()
        print("🧹 Hotkeys limpas")
        
        # Registrar hotkeys de teste
        keyboard.add_hotkey('f9', test_f9)
        keyboard.add_hotkey('tab', test_tab)
        keyboard.add_hotkey('f1', test_f1)
        keyboard.add_hotkey('esc', test_exit)
        
        print("✅ Hotkeys registradas:")
        print("  - F9: Teste de start_bot")
        print("  - TAB: Teste de rod_switch")
        print("  - F1: Teste de pause")
        print("  - ESC: Sair do teste")
        
        print("\n" + "="*50)
        print("🎮 TESTE DE HOTKEYS ATIVO")
        print("Pressione as teclas para testar:")
        print("F9, TAB, F1 ou ESC para sair")
        print("="*50)
        
        # Loop de teste
        start_time = time.time()
        while True:
            try:
                time.sleep(0.1)
                
                # Auto-sair após 30 segundos
                if time.time() - start_time > 30:
                    print("⏰ Timeout de 30s - saindo...")
                    break
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrompido pelo usuário")
                break
        
        # Resultados
        print("\n" + "="*50)
        print("📊 RESULTADOS DO TESTE:")
        print(f"F9 (start_bot): {test_results['f9_calls']} vezes")
        print(f"TAB (rod_switch): {test_results['tab_calls']} vezes") 
        print(f"F1 (pause): {test_results['f1_calls']} vezes")
        
        # Verificar problema
        if test_results['f9_calls'] == 0 and test_results['tab_calls'] > 0:
            print("❌ PROBLEMA: F9 não funciona mas TAB sim")
            print("   Possível conflito de teclas")
        elif test_results['f9_calls'] > 0:
            print("✅ F9 funcionando corretamente")
        
        keyboard.clear_all_hotkeys()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_hotkeys()