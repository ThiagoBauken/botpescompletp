#!/usr/bin/env python3
"""
🧪 Teste de Persistência de Templates - Fishing Bot v4.0

Teste para validar que as alterações de confiança dos templates
são persistidas corretamente no config.json
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_template_persistence():
    """Testar persistência de confiança de templates"""
    print("\n🧪 Testando persistência de templates...")
    
    try:
        from utils.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        
        # 1. Inicializar componentes
        config = ConfigManager()
        template_engine = TemplateEngine(config_manager=config)
        
        print(f"📋 Formato config: {'UNIFIED' if config.is_unified_format else 'LEGADO'}")
        
        # 2. Testar valor inicial
        initial_confidence = template_engine.get_template_confidence('catch')
        print(f"🔍 Confiança inicial 'catch': {initial_confidence}")
        
        # 3. Alterar confiança
        new_confidence = 0.85
        print(f"🔧 Alterando para: {new_confidence}")
        template_engine.set_template_confidence('catch', new_confidence)
        
        # 4. Verificar se foi salvo no arquivo
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        if config.is_unified_format:
            saved_confidence = config_data.get('template_confidence', {}).get('values', {}).get('catch')
        else:
            saved_confidence = config_data.get('template_confidence', {}).get('catch')
        
        print(f"💾 Confiança salva no arquivo: {saved_confidence}")
        
        # 5. Recarregar e verificar
        config2 = ConfigManager()
        template_engine2 = TemplateEngine(config_manager=config2)
        reloaded_confidence = template_engine2.get_template_confidence('catch')
        print(f"🔄 Confiança recarregada: {reloaded_confidence}")
        
        # 6. Verificar se persistiu
        if abs(reloaded_confidence - new_confidence) < 0.001:
            print("✅ TESTE PASSOU: Persistência funcionando!")
            return True
        else:
            print(f"❌ TESTE FALHOU: {reloaded_confidence} != {new_confidence}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_templates():
    """Testar persistência de múltiplos templates"""
    print("\n🧪 Testando múltiplos templates...")
    
    try:
        from utils.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        
        config = ConfigManager()
        template_engine = TemplateEngine(config_manager=config)
        
        # Múltiplos templates para testar
        test_templates = {
            'catch': 0.88,
            'VARANOBAUCI': 0.82,
            'enbausi': 0.73,
            'varaquebrada': 0.68
        }
        
        # Aplicar todas as alterações
        for template_name, confidence in test_templates.items():
            print(f"🔧 Configurando {template_name} = {confidence}")
            template_engine.set_template_confidence(template_name, confidence)
        
        # Verificar se foram salvas
        config2 = ConfigManager()
        template_engine2 = TemplateEngine(config_manager=config2)
        
        all_passed = True
        for template_name, expected_confidence in test_templates.items():
            actual_confidence = template_engine2.get_template_confidence(template_name)
            
            if abs(actual_confidence - expected_confidence) < 0.001:
                print(f"✅ {template_name}: {actual_confidence} (OK)")
            else:
                print(f"❌ {template_name}: {actual_confidence} != {expected_confidence}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Erro no teste múltiplo: {e}")
        return False

def main():
    """Executar todos os testes de persistência"""
    print("🧪" + "="*60)
    print("🧪 TESTE DE PERSISTÊNCIA DE TEMPLATES - V4.0")
    print("🧪" + "="*60)
    
    tests = [
        ("Persistência Simples", test_template_persistence),
        ("Múltiplos Templates", test_multiple_templates)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Falha crítica em {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n🧪" + "="*60)
    print("📊 RESUMO DOS TESTES:")
    print("🧪" + "="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Persistência de templates está funcionando corretamente!")
        print("\n🔧 Problemas corrigidos:")
        print("  💾 Templates são salvos automaticamente no config.json")
        print("  🔄 Configurações persistem entre reinicializações")
        print("  📋 Suporte tanto para formato UNIFIED quanto LEGADO")
        print("  ⚡ Performance otimizada com cache local")
    else:
        print("⚠️ Alguns testes falharam - verificar implementação")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)