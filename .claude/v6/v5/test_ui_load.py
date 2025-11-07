#!/usr/bin/env python3
"""
🧪 Teste de Carregamento da UI
Verifica se a interface pode ser inicializada sem erros
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ui_initialization():
    """Testar se a UI pode ser inicializada sem erros"""
    print("🧪 Testando inicialização da UI...")
    
    try:
        print("  📦 Importando ConfigManager...")
        from core.config_manager import ConfigManager
        
        print("  ⚙️ Criando ConfigManager...")
        config_manager = ConfigManager()
        
        print("  🖥️ Importando FishingBotUI...")
        from ui.main_window import FishingBotUI
        
        print("  🚀 Testando construtor da UI...")
        # Criar UI com ConfigManager
        ui = FishingBotUI(config_manager=config_manager)
        
        print("  ✅ UI inicializada sem erros!")
        
        # Testar se as variáveis problemáticas existem
        required_vars = [
            'feeding_mode_var',
            'feeding_interval_var', 
            'feeding_fish_count_var',
            'feeding_eat_x_var',
            'feeding_eat_y_var'
        ]
        
        missing_vars = []
        for var_name in required_vars:
            if not hasattr(ui, var_name):
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"  ⚠️ Variáveis faltando: {missing_vars}")
            return False
        else:
            print(f"  ✅ Todas as {len(required_vars)} variáveis necessárias estão presentes")
        
        # Testar carregamento de configurações
        print("  🔧 Testando load_config_values...")
        ui.load_config_values()
        print("  ✅ Configurações carregadas sem erro!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager_integration():
    """Testar integração do ConfigManager com templates"""
    print("\n🧪 Testando integração ConfigManager...")
    
    try:
        from core.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        
        config = ConfigManager()
        
        print("  ⚙️ Testando template engine com config...")
        template_engine = TemplateEngine(config_manager=config)
        
        print("  🎯 Testando confidence de templates...")
        catch_conf = template_engine.get_template_confidence('catch')
        crocodilo_conf = template_engine.get_template_confidence('carnecrocodilo')
        
        print(f"    catch: {catch_conf}")
        print(f"    carnecrocodilo: {crocodilo_conf}")
        
        # Testar bait priority
        print("  🎣 Testando prioridade de iscas...")
        bait_priority = config.get('bait_priority', {})
        print(f"    bait_priority: {bait_priority}")
        
        # Verificar se carne de crocodilo está como prioridade 1
        if bait_priority.get('carne de crocodilo') == 1:
            print("  ✅ Carne de crocodilo está como prioridade 1!")
        else:
            print(f"  ⚠️ Carne de crocodilo prioridade: {bait_priority.get('carne de crocodilo')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na integração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE FUNCIONAMENTO DA UI V4.0")
    print("=" * 60)
    
    test1 = test_ui_initialization()
    test2 = test_config_manager_integration()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if test1 and test2:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 Interface está funcional e configurações OK!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        if not test1:
            print("  - Problema na inicialização da UI")
        if not test2:
            print("  - Problema na integração do ConfigManager")