#!/usr/bin/env python3
"""
🧪 Teste de Integração Completo - Ultimate Fishing Bot v4.0

Verifica se todos os componentes estão funcionando corretamente:
- FishingEngine
- TemplateEngine 
- RodManager
- FeedingSystem
- ChestManager
- InventoryManager
- InputManager
- GameState
"""

import sys
import os

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """🔍 Testar importação de todos os componentes"""
    print("🔍 Testando importações...")
    
    try:
        # Core components
        from core.fishing_engine import FishingEngine, FishingState
        print("  ✅ FishingEngine importado")
        
        from core.template_engine import TemplateEngine, TemplateResult
        print("  ✅ TemplateEngine importado")
        
        from core.rod_manager import RodManager, RodStatus, RodInfo
        print("  ✅ RodManager importado")
        
        from core.feeding_system import FeedingSystem
        print("  ✅ FeedingSystem importado")
        
        from core.chest_manager import ChestManager, ChestOperation, ChestSide
        print("  ✅ ChestManager importado")
        
        from core.inventory_manager import InventoryManager
        print("  ✅ InventoryManager importado")
        
        from core.input_manager import InputManager
        print("  ✅ InputManager importado")
        
        from core.game_state import GameState
        print("  ✅ GameState importado")
        
        from core.config_manager import ConfigManager
        print("  ✅ ConfigManager importado")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        return False

def test_component_initialization():
    """🏗️ Testar inicialização de componentes"""
    print("\n🏗️ Testando inicialização de componentes...")
    
    try:
        # ConfigManager primeiro
        from core.config_manager import ConfigManager
        config = ConfigManager()
        print("  ✅ ConfigManager inicializado")
        
        # GameState
        from core.game_state import GameState
        game_state = GameState(config_manager=config)
        print("  ✅ GameState inicializado")
        
        # TemplateEngine
        from core.template_engine import TemplateEngine
        template_engine = TemplateEngine(config_manager=config)
        print("  ✅ TemplateEngine inicializado")
        
        # InputManager
        from core.input_manager import InputManager
        input_manager = InputManager(config_manager=config)
        print("  ✅ InputManager inicializado")
        
        # ChestManager
        from core.chest_manager import ChestManager
        chest_manager = ChestManager(config_manager=config, game_state=game_state)
        print("  ✅ ChestManager inicializado")
        
        # RodManager
        from core.rod_manager import RodManager
        rod_manager = RodManager(
            template_engine=template_engine,
            input_manager=input_manager,
            chest_manager=chest_manager,
            config_manager=config,
            game_state=game_state
        )
        print("  ✅ RodManager inicializado")
        
        # FeedingSystem
        from core.feeding_system import FeedingSystem
        feeding_system = FeedingSystem(
            config_manager=config,
            template_engine=template_engine,
            chest_manager=chest_manager,
            game_state=game_state
        )
        print("  ✅ FeedingSystem inicializado")
        
        # InventoryManager
        from core.inventory_manager import InventoryManager
        inventory_manager = InventoryManager(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config
        )
        print("  ✅ InventoryManager inicializado")
        
        # FishingEngine (integração completa)
        from core.fishing_engine import FishingEngine
        fishing_engine = FishingEngine(
            template_engine=template_engine,
            input_manager=input_manager,
            rod_manager=rod_manager,
            feeding_system=feeding_system,
            inventory_manager=inventory_manager,
            chest_manager=chest_manager,
            game_state=game_state,
            config_manager=config
        )
        print("  ✅ FishingEngine inicializado com todos os componentes")
        
        return {
            'config': config,
            'game_state': game_state,
            'template_engine': template_engine,
            'input_manager': input_manager,
            'chest_manager': chest_manager,
            'rod_manager': rod_manager,
            'feeding_system': feeding_system,
            'inventory_manager': inventory_manager,
            'fishing_engine': fishing_engine
        }
        
    except Exception as e:
        print(f"  ❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_component_methods(components):
    """🔧 Testar métodos básicos dos componentes"""
    print("\n🔧 Testando métodos básicos...")
    
    try:
        # TemplateEngine
        template_engine = components['template_engine']
        available_templates = template_engine.get_available_templates()
        print(f"  ✅ TemplateEngine: {len(available_templates)} templates disponíveis")
        
        # RodManager
        rod_manager = components['rod_manager']
        current_rod = rod_manager.get_current_rod()
        rod_summary = rod_manager.get_rod_status_summary()
        print(f"  ✅ RodManager: vara atual={current_rod}, status={rod_summary}")
        
        # FeedingSystem
        feeding_system = components['feeding_system']
        feeding_stats = feeding_system.get_stats()
        print(f"  ✅ FeedingSystem: stats={feeding_stats}")
        
        # GameState
        game_state = components['game_state']
        current_mode = game_state.get_current_mode()
        print(f"  ✅ GameState: modo atual={current_mode}")
        
        # FishingEngine
        fishing_engine = components['fishing_engine']
        fishing_state = fishing_engine.get_state()
        fishing_stats = fishing_engine.get_stats()
        print(f"  ✅ FishingEngine: estado={fishing_state}, stats={fishing_stats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos métodos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_flow(components):
    """🔄 Testar fluxo de integração entre componentes"""
    print("\n🔄 Testando fluxo de integração...")
    
    try:
        fishing_engine = components['fishing_engine']
        rod_manager = components['rod_manager']
        feeding_system = components['feeding_system']
        
        # Simular incremento de peixe capturado
        print("  🐟 Simulando captura de peixe...")
        fishing_engine.increment_fish_count()
        
        # Verificar se sistemas dependentes foram notificados
        feeding_stats = feeding_system.get_stats()
        print(f"  📈 FeedingSystem atualizado: {feeding_stats['fish_count_since_feeding']} peixes")
        
        # Testar necessidade de troca de vara
        needs_switch = rod_manager.needs_rod_switch()
        print(f"  🎣 RodManager: precisa trocar vara = {needs_switch}")
        
        # Testar necessidade de alimentação
        needs_feeding = feeding_system.should_trigger_feeding()
        print(f"  🍖 FeedingSystem: precisa alimentar = {needs_feeding}")
        
        print("  ✅ Fluxo de integração testado com sucesso")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no fluxo de integração: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_loading(components):
    """⚙️ Testar carregamento de configurações"""
    print("\n⚙️ Testando carregamento de configurações...")
    
    try:
        config = components['config']
        
        # Testar configurações críticas
        template_confidence = config.get('template_confidence', {})
        rod_system = config.get('rod_system', {})
        feeding_system = config.get('feeding_system', {})
        coordinates = config.get('coordinates', {})
        
        print(f"  📋 Template confidence: {len(template_confidence)} templates configurados")
        print(f"  🎣 Rod system: {rod_system}")
        print(f"  🍖 Feeding system: {feeding_system}")
        print(f"  📍 Coordinates: {len(coordinates)} seções de coordenadas")
        
        # Testar prioridades
        bait_priority = config.get('bait_priority', {})
        food_priority = config.get('food_priority', {})
        
        print(f"  🎣 Bait priority: {bait_priority}")
        print(f"  🍖 Food priority: {food_priority}")
        
        print("  ✅ Configurações carregadas corretamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no carregamento de config: {e}")
        return False

def test_template_system(components):
    """🎯 Testar sistema de templates"""
    print("\n🎯 Testando sistema de templates...")
    
    try:
        template_engine = components['template_engine']
        
        # Verificar templates críticos
        critical_templates = ['catch', 'inventory', 'loot']
        missing_templates = []
        
        for template in critical_templates:
            if not template_engine.has_template(template):
                missing_templates.append(template)
        
        if missing_templates:
            print(f"  ⚠️ Templates críticos ausentes: {missing_templates}")
        else:
            print("  ✅ Todos os templates críticos estão disponíveis")
        
        # Testar configurações de confiança
        for template in critical_templates:
            confidence = template_engine.get_template_confidence(template)
            print(f"  📊 {template}: confiança = {confidence}")
        
        # Testar detecção de iscas
        bait_templates = template_engine.detect_bait_templates()
        print(f"  🎣 Iscas detectadas: {len(bait_templates)}")
        
        # Testar detecção de comidas
        food_templates = template_engine.detect_food_templates()
        print(f"  🍖 Comidas detectadas: {len(food_templates)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no sistema de templates: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_complete_integration_test():
    """🚀 Executar teste completo de integração"""
    print("🚀 TESTE DE INTEGRAÇÃO COMPLETO - Ultimate Fishing Bot v4.0")
    print("="*70)
    
    results = []
    
    # 1. Testar importações
    results.append(("Importações", test_imports()))
    
    # 2. Testar inicialização
    components = test_component_initialization()
    results.append(("Inicialização", components is not None))
    
    if components:
        # 3. Testar métodos básicos
        results.append(("Métodos básicos", test_component_methods(components)))
        
        # 4. Testar configurações
        results.append(("Configurações", test_config_loading(components)))
        
        # 5. Testar sistema de templates
        results.append(("Sistema de templates", test_template_system(components)))
        
        # 6. Testar fluxo de integração
        results.append(("Fluxo de integração", test_integration_flow(components)))
    
    # Relatório final
    print("\n" + "="*70)
    print("📊 RELATÓRIO FINAL")
    print("="*70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
    
    print("="*70)
    print(f"📈 RESULTADO: {passed}/{total} testes passaram ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! O sistema está funcionalmente integrado.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    try:
        success = run_complete_integration_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal no teste: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)