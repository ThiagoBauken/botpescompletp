#!/usr/bin/env python3
"""
🧪 Verificação Rápida dos Botões de Salvar
Testa se ConfigManager salva dados corretamente
"""

import sys
import os
import json

# Adicionar ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_manager():
    """Teste básico do ConfigManager"""
    print("🧪 Testando ConfigManager...")
    
    try:
        from core.config_manager import ConfigManager
        
        # Criar instância
        config = ConfigManager()
        print(f"  ✅ ConfigManager criado")
        
        # Verificar dados atuais
        current_bait = config.get('bait_priority')
        print(f"  📋 Bait priority atual: {current_bait}")
        
        # Testar set e save
        config.set('test_timestamp', '123456')
        config.set('bait_priority.carne de crocodilo', 1)
        
        # Salvar
        config.save_user_config()
        print(f"  ✅ Dados salvos com save_user_config()")
        
        # Verificar se foi salvo
        config2 = ConfigManager()
        saved_timestamp = config2.get('test_timestamp')
        saved_crocodilo = config2.get('bait_priority.carne de crocodilo')
        
        if saved_timestamp == '123456':
            print(f"  ✅ Timestamp salvo corretamente")
        else:
            print(f"  ❌ Timestamp não salvo: {saved_timestamp}")
            
        if saved_crocodilo == 1:
            print(f"  ✅ Carne de crocodilo salva como prioridade 1")
        else:
            print(f"  ❌ Carne de crocodilo incorreta: {saved_crocodilo}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_confidence():
    """Teste das configurações de template"""
    print("\n🧪 Testando Template Confidence...")
    
    try:
        from core.config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Testar configurações de template atuais
        catch_conf = config.get('template_confidence.catch')
        varano_conf = config.get('template_confidence.VARANOBAUCI')
        
        print(f"  📊 Catch confidence: {catch_conf}")
        print(f"  📊 VARANOBAUCI confidence: {varano_conf}")
        
        # Testar modificação
        config.set('template_confidence.catch', 0.85)
        config.save_user_config()
        
        # Verificar
        config2 = ConfigManager()
        new_catch = config2.get('template_confidence.catch')
        
        if new_catch == 0.85:
            print(f"  ✅ Template confidence salva corretamente: {new_catch}")
            return True
        else:
            print(f"  ❌ Template confidence não salva: {new_catch}")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 VERIFICAÇÃO DOS BOTÕES DE SALVAR")
    print("=" * 60)
    
    test1 = test_config_manager()
    test2 = test_template_confidence()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("=" * 60)
    
    if test1 and test2:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("💾 ConfigManager está salvando corretamente!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Verificar implementação dos save_* methods")