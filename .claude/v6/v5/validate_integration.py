#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validacao de Integracao - Ultimate Fishing Bot v4.0

Valida que TODOS os componentes estao conectados e funcionando.
"""

import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def safe_print(text):
    """Print com fallback para encoding"""
    try:
        print(text)
    except UnicodeEncodeError:
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '?', text)
        print(clean_text)

def print_section(title):
    """Print section header"""
    safe_print("\n" + "="*70)
    safe_print(f"  {title}")
    safe_print("="*70)

def validate_imports():
    """Validar que todos os modulos podem ser importados"""
    print_section("VALIDANDO IMPORTS")

    imports_to_test = [
        ('core.config_manager', 'ConfigManager'),
        ('core.template_engine', 'TemplateEngine'),
        ('core.input_manager', 'InputManager'),
        ('core.chest_manager', 'ChestManager'),
        ('core.rod_manager', 'RodManager'),
        ('core.feeding_system', 'FeedingSystem'),
        ('core.inventory_manager', 'InventoryManager'),
        ('core.fishing_engine', 'FishingEngine'),
        ('core.chest_operation_coordinator', 'ChestOperationCoordinator'),
        ('core.game_state', 'GameState'),
        ('ui.main_window', 'FishingBotUI'),
        ('utils.i18n', 'i18n'),
    ]

    results = {'success': 0, 'failed': 0, 'errors': []}

    for module_path, class_name in imports_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {module_path}.{class_name}")
            results['success'] += 1
        except Exception as e:
            print(f"  ❌ {module_path}.{class_name}: {e}")
            results['failed'] += 1
            results['errors'].append((module_path, class_name, str(e)))

    print(f"\n📊 Imports: {results['success']} ✅ | {results['failed']} ❌")
    return results

def validate_component_initialization():
    """Validar que componentes podem ser inicializados"""
    print_section("🔧 VALIDANDO INICIALIZAÇÃO DE COMPONENTES")

    results = {'success': 0, 'failed': 0, 'components': {}}

    try:
        # 1. ConfigManager
        print("  🔧 Inicializando ConfigManager...")
        from core.config_manager import ConfigManager
        config = ConfigManager()
        results['components']['ConfigManager'] = config
        print("    ✅ ConfigManager inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ ConfigManager falhou: {e}")
        results['failed'] += 1
        return results  # Sem config, não dá pra continuar

    try:
        # 2. TemplateEngine
        print("  🔧 Inicializando TemplateEngine...")
        from core.template_engine import TemplateEngine
        template_engine = TemplateEngine(config_manager=config)
        results['components']['TemplateEngine'] = template_engine
        print(f"    ✅ TemplateEngine inicializado ({len(template_engine.template_cache)} templates)")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ TemplateEngine falhou: {e}")
        results['failed'] += 1

    try:
        # 3. InputManager
        print("  🔧 Inicializando InputManager...")
        from core.input_manager import InputManager
        input_manager = InputManager(config_manager=config)
        results['components']['InputManager'] = input_manager
        print("    ✅ InputManager inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ InputManager falhou: {e}")
        results['failed'] += 1
        input_manager = None

    try:
        # 4. GameState
        print("  🔧 Inicializando GameState...")
        from core.game_state import GameState
        game_state = GameState()
        results['components']['GameState'] = game_state
        print("    ✅ GameState inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ GameState falhou: {e}")
        results['failed'] += 1
        game_state = None

    try:
        # 5. ChestManager
        print("  🔧 Inicializando ChestManager...")
        from core.chest_manager import ChestManager
        chest_manager = ChestManager(
            config_manager=config,
            input_manager=input_manager,
            game_state=game_state
        )
        results['components']['ChestManager'] = chest_manager
        print("    ✅ ChestManager inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ ChestManager falhou: {e}")
        results['failed'] += 1
        chest_manager = None

    try:
        # 6. RodManager
        print("  🔧 Inicializando RodManager...")
        from core.rod_manager import RodManager
        rod_manager = RodManager(
            template_engine=template_engine if 'TemplateEngine' in results['components'] else None,
            input_manager=input_manager,
            config_manager=config,
            chest_manager=chest_manager
        )
        results['components']['RodManager'] = rod_manager
        print("    ✅ RodManager inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ RodManager falhou: {e}")
        results['failed'] += 1
        rod_manager = None

    try:
        # 7. FeedingSystem
        print("  🔧 Inicializando FeedingSystem...")
        from core.feeding_system import FeedingSystem
        feeding_system = FeedingSystem(
            config_manager=config,
            template_engine=template_engine if 'TemplateEngine' in results['components'] else None,
            chest_manager=chest_manager
        )
        results['components']['FeedingSystem'] = feeding_system
        print("    ✅ FeedingSystem inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ FeedingSystem falhou: {e}")
        results['failed'] += 1
        feeding_system = None

    try:
        # 8. InventoryManager
        print("  🔧 Inicializando InventoryManager...")
        from core.inventory_manager import InventoryManager
        inventory_manager = InventoryManager(
            template_engine=template_engine if 'TemplateEngine' in results['components'] else None,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config
        )
        results['components']['InventoryManager'] = inventory_manager
        print("    ✅ InventoryManager inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ InventoryManager falhou: {e}")
        results['failed'] += 1
        inventory_manager = None

    try:
        # 9. ChestOperationCoordinator
        print("  🔧 Inicializando ChestOperationCoordinator...")
        from core.chest_operation_coordinator import ChestOperationCoordinator
        chest_coordinator = ChestOperationCoordinator(
            config_manager=config,
            feeding_system=feeding_system,
            rod_maintenance_system=rod_manager.maintenance_system if rod_manager else None,
            inventory_manager=inventory_manager
        )
        results['components']['ChestOperationCoordinator'] = chest_coordinator
        print("    ✅ ChestOperationCoordinator inicializado")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ ChestOperationCoordinator falhou: {e}")
        results['failed'] += 1

    try:
        # 10. FishingEngine (O CORAÇÃO!)
        print("  🔧 Inicializando FishingEngine...")
        from core.fishing_engine import FishingEngine
        fishing_engine = FishingEngine(
            template_engine=template_engine if 'TemplateEngine' in results['components'] else None,
            input_manager=input_manager,
            rod_manager=rod_manager,
            feeding_system=feeding_system,
            inventory_manager=inventory_manager,
            chest_manager=chest_manager,
            game_state=game_state,
            config_manager=config
        )
        results['components']['FishingEngine'] = fishing_engine
        print("    ✅ FishingEngine inicializado com TODOS os componentes!")
        results['success'] += 1
    except Exception as e:
        print(f"    ❌ FishingEngine falhou: {e}")
        results['failed'] += 1
        import traceback
        traceback.print_exc()

    print(f"\n📊 Componentes: {results['success']} ✅ | {results['failed']} ❌")
    return results

def validate_fishing_engine_integration():
    """Validar integração completa do FishingEngine"""
    print_section("🎣 VALIDANDO INTEGRAÇÃO DO FISHING ENGINE")

    try:
        # Inicializar todos os componentes
        from core.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        from core.input_manager import InputManager
        from core.chest_manager import ChestManager
        from core.rod_manager import RodManager
        from core.feeding_system import FeedingSystem
        from core.inventory_manager import InventoryManager
        from core.fishing_engine import FishingEngine
        from core.game_state import GameState

        config = ConfigManager()
        template_engine = TemplateEngine(config_manager=config)
        input_manager = InputManager(config_manager=config)
        game_state = GameState()
        chest_manager = ChestManager(
            config_manager=config,
            input_manager=input_manager,
            game_state=game_state
        )
        rod_manager = RodManager(
            template_engine=template_engine,
            input_manager=input_manager,
            config_manager=config,
            chest_manager=chest_manager
        )
        feeding_system = FeedingSystem(
            config_manager=config,
            template_engine=template_engine,
            chest_manager=chest_manager
        )
        inventory_manager = InventoryManager(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config
        )

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

        # Validar componentes internos
        print("  🔍 Validando componentes do FishingEngine:")
        print(f"    📋 TemplateEngine: {'✅' if fishing_engine.template_engine else '❌'}")
        print(f"    🖱️ InputManager: {'✅' if fishing_engine.input_manager else '❌'}")
        print(f"    🎣 RodManager: {'✅' if fishing_engine.rod_manager else '❌'}")
        print(f"    🍖 FeedingSystem: {'✅' if fishing_engine.feeding_system else '❌'}")
        print(f"    📦 InventoryManager: {'✅' if fishing_engine.inventory_manager else '❌'}")
        print(f"    🎁 ChestManager: {'✅' if fishing_engine.chest_manager else '❌'}")
        print(f"    🏪 ChestCoordinator: {'✅' if fishing_engine.chest_coordinator else '❌'}")

        # Validar métodos críticos
        print("\n  🔍 Validando métodos do FishingEngine:")
        methods_to_check = [
            'start', 'stop', 'pause',
            'trigger_feeding', 'trigger_cleaning', 'trigger_rod_switch',
            'process_priority_tasks', 'increment_fish_count',
            '_execute_complete_fishing_cycle'
        ]

        all_methods_exist = True
        for method_name in methods_to_check:
            has_method = hasattr(fishing_engine, method_name)
            print(f"    {'✅' if has_method else '❌'} {method_name}")
            if not has_method:
                all_methods_exist = False

        if all_methods_exist:
            print("\n  ✅ TODOS os métodos críticos estão presentes!")
        else:
            print("\n  ⚠️ Alguns métodos estão faltando")

        # Validar que callbacks podem ser configurados
        print("\n  🔍 Validando sistema de callbacks:")
        callback_test = {'called': False}

        def test_callback(*args, **kwargs):
            callback_test['called'] = True

        fishing_engine.set_callbacks(
            on_state_change=test_callback,
            on_fish_caught=test_callback,
            on_error=test_callback,
            on_stats_update=test_callback
        )

        print("    ✅ Callbacks configurados com sucesso")

        print("\n  ✅ FISHING ENGINE TOTALMENTE INTEGRADO!")
        return True

    except Exception as e:
        print(f"\n  ❌ Erro na validação: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_ui_integration():
    """Validar que UI pode inicializar com os componentes"""
    print_section("🎨 VALIDANDO INTEGRAÇÃO DA UI")

    try:
        print("  🔧 Tentando importar FishingBotUI...")
        from ui.main_window import FishingBotUI
        print("    ✅ FishingBotUI importada com sucesso")

        print("\n  ℹ️ NOTA: Não vamos inicializar a UI aqui para evitar abrir janela")
        print("    Para testar a UI completa, execute: python main.py")

        return True
    except Exception as e:
        print(f"    ❌ Erro ao importar UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executar todas as validações"""
    print("\n" + "="*70)
    print("  🧪 VALIDAÇÃO DE INTEGRAÇÃO - ULTIMATE FISHING BOT V4.0")
    print("="*70)

    results = {
        'imports': None,
        'initialization': None,
        'fishing_engine': None,
        'ui': None
    }

    # 1. Validar imports
    results['imports'] = validate_imports()

    # 2. Validar inicialização
    results['initialization'] = validate_component_initialization()

    # 3. Validar FishingEngine
    results['fishing_engine'] = validate_fishing_engine_integration()

    # 4. Validar UI
    results['ui'] = validate_ui_integration()

    # Resumo final
    print_section("📊 RESUMO FINAL")

    import_success = results['imports']['success']
    import_total = results['imports']['success'] + results['imports']['failed']
    init_success = results['initialization']['success']
    init_total = results['initialization']['success'] + results['initialization']['failed']

    print(f"  📦 Imports: {import_success}/{import_total} ✅")
    print(f"  🔧 Inicializações: {init_success}/{init_total} ✅")
    print(f"  🎣 FishingEngine: {'✅ Integrado' if results['fishing_engine'] else '❌ Falhou'}")
    print(f"  🎨 UI: {'✅ Disponível' if results['ui'] else '❌ Falhou'}")

    if (results['imports']['failed'] == 0 and
        results['initialization']['failed'] == 0 and
        results['fishing_engine'] and
        results['ui']):
        print("\n" + "="*70)
        print("  ✅ INTEGRAÇÃO COMPLETA! SISTEMA PRONTO PARA USO!")
        print("="*70)
        print("\n  🚀 Para iniciar o bot, execute:")
        print("     python main.py")
        print("\n  ⌨️ Hotkeys disponíveis:")
        print("     F9: Iniciar bot")
        print("     F1: Pausar/Despausar")
        print("     F2: Parar")
        print("     F6: Alimentação manual")
        print("     F5: Limpeza manual")
        print("     Page Down: Manutenção de vara")
        print("     ESC: Parada de emergência")
        return 0
    else:
        print("\n" + "="*70)
        print("  ⚠️ INTEGRAÇÃO PARCIAL - ALGUNS COMPONENTES FALHARAM")
        print("="*70)

        if results['imports']['errors']:
            print("\n  ❌ Erros de import:")
            for module, cls, error in results['imports']['errors']:
                print(f"     {module}.{cls}: {error}")

        return 1

if __name__ == "__main__":
    sys.exit(main())
