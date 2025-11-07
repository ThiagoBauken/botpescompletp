#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Simplificado de Validacao de Integracao - Ultimate Fishing Bot v4.0
"""

import sys
import os

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Executar validacao simples"""
    print("\n" + "="*70)
    print("  VALIDACAO DE INTEGRACAO - ULTIMATE FISHING BOT V4.0")
    print("="*70)

    success_count = 0
    fail_count = 0

    # 1. Testar imports
    print("\n[1/10] Testando imports...")
    try:
        from core.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        from core.input_manager import InputManager
        from core.chest_manager import ChestManager
        from core.rod_manager import RodManager
        from core.feeding_system import FeedingSystem
        from core.inventory_manager import InventoryManager
        from core.fishing_engine import FishingEngine
        from core.chest_operation_coordinator import ChestOperationCoordinator
        from core.game_state import GameState
        from ui.main_window import FishingBotUI
        print("   [OK] Todos os imports foram bem-sucedidos")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] Falha nos imports: {e}")
        fail_count += 1
        return 1

    # 2. ConfigManager
    print("\n[2/10] Inicializando ConfigManager...")
    try:
        config = ConfigManager()
        print("   [OK] ConfigManager inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        return 1

    # 3. TemplateEngine
    print("\n[3/10] Inicializando TemplateEngine...")
    try:
        template_engine = TemplateEngine(config_manager=config)
        template_count = len(template_engine.template_cache)
        print(f"   [OK] TemplateEngine inicializado ({template_count} templates)")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        return 1

    # 4. InputManager
    print("\n[4/10] Inicializando InputManager...")
    try:
        input_manager = InputManager(config_manager=config)
        print("   [OK] InputManager inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        input_manager = None

    # 5. GameState
    print("\n[5/10] Inicializando GameState...")
    try:
        game_state = GameState()
        print("   [OK] GameState inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        game_state = None

    # 6. ChestManager
    print("\n[6/10] Inicializando ChestManager...")
    try:
        chest_manager = ChestManager(
            config_manager=config,
            input_manager=input_manager,
            game_state=game_state
        )
        print("   [OK] ChestManager inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        chest_manager = None

    # 7. RodManager
    print("\n[7/10] Inicializando RodManager...")
    try:
        rod_manager = RodManager(
            template_engine=template_engine,
            input_manager=input_manager,
            config_manager=config,
            chest_manager=chest_manager
        )
        print("   [OK] RodManager inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        rod_manager = None

    # 8. FeedingSystem
    print("\n[8/10] Inicializando FeedingSystem...")
    try:
        feeding_system = FeedingSystem(
            config_manager=config,
            template_engine=template_engine,
            chest_manager=chest_manager
        )
        print("   [OK] FeedingSystem inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        feeding_system = None

    # 9. InventoryManager
    print("\n[9/10] Inicializando InventoryManager...")
    try:
        inventory_manager = InventoryManager(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config
        )
        print("   [OK] InventoryManager inicializado")
        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        fail_count += 1
        inventory_manager = None

    # 10. FishingEngine - O CORAÇÃO!
    print("\n[10/10] Inicializando FishingEngine...")
    try:
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
        print("   [OK] FishingEngine inicializado com TODOS os componentes!")

        # Validar componentes internos
        print("\n   Validando componentes internos do FishingEngine:")
        print(f"      TemplateEngine: {'OK' if fishing_engine.template_engine else 'FALTANDO'}")
        print(f"      InputManager: {'OK' if fishing_engine.input_manager else 'FALTANDO'}")
        print(f"      RodManager: {'OK' if fishing_engine.rod_manager else 'FALTANDO'}")
        print(f"      FeedingSystem: {'OK' if fishing_engine.feeding_system else 'FALTANDO'}")
        print(f"      InventoryManager: {'OK' if fishing_engine.inventory_manager else 'FALTANDO'}")
        print(f"      ChestManager: {'OK' if fishing_engine.chest_manager else 'FALTANDO'}")
        print(f"      ChestCoordinator: {'OK' if fishing_engine.chest_coordinator else 'FALTANDO'}")

        success_count += 1
    except Exception as e:
        print(f"   [ERRO] {e}")
        import traceback
        traceback.print_exc()
        fail_count += 1
        return 1

    # Resumo Final
    print("\n" + "="*70)
    print(f"  RESUMO: {success_count} OK | {fail_count} ERROS")
    print("="*70)

    if fail_count == 0:
        print("\n  [SUCCESS] INTEGRACAO COMPLETA!")
        print("\n  Para iniciar o bot:")
        print("     python main.py")
        print("\n  Hotkeys disponiveis:")
        print("     F9: Iniciar bot")
        print("     F1: Pausar/Despausar")
        print("     F2: Parar")
        print("     F6: Alimentacao manual")
        print("     F5: Limpeza manual")
        print("     Page Down: Manutencao de vara")
        print("     ESC: Parada de emergencia")
        return 0
    else:
        print("\n  [WARNING] Alguns componentes falharam")
        return 1

if __name__ == "__main__":
    sys.exit(main())
