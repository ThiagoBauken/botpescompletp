#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testando import...")
    from core.config_manager import ConfigManager
    print("✅ ConfigManager importado com sucesso")
    
    print("Criando instância...")
    config = ConfigManager()
    print("✅ ConfigManager criado")
    
    print("Testando get...")
    bait = config.get('bait_priority')
    print(f"✅ Bait priority: {bait}")
    
    print("Testando set...")
    config.set('test_key', 'test_value')
    print("✅ Set realizado")
    
    print("Testando save...")
    result = config.save_user_config()
    print(f"✅ Save result: {result}")
    
    print("Verificando se foi salvo...")
    config2 = ConfigManager()
    test_value = config2.get('test_key')
    print(f"✅ Valor recuperado: {test_value}")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()