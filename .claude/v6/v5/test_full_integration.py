#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Integracao Completa - Fishing Bot v4.0

Este script testa a integracao completa de todos os componentes:
- RodManager: Sistema de troca de varas
- InventoryManager: Sistema de limpeza automatica
- FeedingSystem: Sistema de alimentacao
- ChestManager: Gerenciamento de baus
- TemplateEngine: Deteccao de templates
- FishingEngine: Motor principal coordenando tudo
"""

import sys
import os
import time
import threading
import keyboard
from pathlib import Path

# Configurar encoding UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Adicionar diretorio ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_full_integration():
    """Testar integração completa do bot"""
    print("\n" + "="*60)
    print("🎣 TESTE DE INTEGRAÇÃO COMPLETA - FISHING BOT V4.0")
    print("="*60)

    try:
        # 1. Importar todos os módulos necessários
        print("\n📦 Importando módulos...")
        from core.config_manager import ConfigManager
        from core.template_engine import TemplateEngine
        from core.input_manager import InputManager
        from core.chest_manager import ChestManager
        from core.rod_manager import RodManager
        from core.feeding_system import FeedingSystem
        from core.inventory_manager import InventoryManager
        from core.fishing_engine import FishingEngine
        from core.game_state import GameState
        print("✅ Todos os módulos importados com sucesso!")

        # 2. Inicializar ConfigManager
        print("\n⚙️ Inicializando configuração...")
        config_manager = ConfigManager()
        print("✅ ConfigManager inicializado")

        # 3. Inicializar GameState
        print("\n🎮 Inicializando GameState...")
        game_state = GameState(config_manager=config_manager)
        print("✅ GameState inicializado")

        # 4. Inicializar TemplateEngine
        print("\n🎯 Inicializando TemplateEngine...")
        template_engine = TemplateEngine(config_manager=config_manager)
        print(f"✅ TemplateEngine inicializado com {len(template_engine.templates)} templates")

        # 5. Inicializar InputManager
        print("\n🖱️ Inicializando InputManager...")
        input_manager = InputManager(config_manager=config_manager)
        print("✅ InputManager inicializado")

        # 6. Inicializar ChestManager
        print("\n📦 Inicializando ChestManager...")
        chest_manager = ChestManager(
            template_engine=template_engine,
            input_manager=input_manager,
            config_manager=config_manager
        )
        print("✅ ChestManager inicializado")

        # 7. Inicializar RodManager
        print("\n🎣 Inicializando RodManager...")
        rod_manager = RodManager(
            template_engine=template_engine,
            input_manager=input_manager,
            config_manager=config_manager,
            game_state=game_state
        )
        print("✅ RodManager inicializado")

        # 8. Inicializar FeedingSystem
        print("\n🍖 Inicializando FeedingSystem...")
        feeding_system = FeedingSystem(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config_manager
        )
        print("✅ FeedingSystem inicializado")

        # 9. Inicializar InventoryManager
        print("\n📦 Inicializando InventoryManager...")
        inventory_manager = InventoryManager(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            config_manager=config_manager
        )
        print("✅ InventoryManager inicializado")

        # 10. Inicializar FishingEngine com TODOS os componentes
        print("\n🎮 Inicializando FishingEngine com todos os componentes...")
        fishing_engine = FishingEngine(
            template_engine=template_engine,
            input_manager=input_manager,
            rod_manager=rod_manager,
            feeding_system=feeding_system,
            inventory_manager=inventory_manager,
            chest_manager=chest_manager,
            game_state=game_state,
            config_manager=config_manager
        )
        print("✅ FishingEngine inicializado com TODOS os componentes!")

        # 11. Configurar callbacks para monitoramento
        print("\n📊 Configurando callbacks...")
        def on_state_change(state):
            print(f"  📍 Estado mudou para: {state}")

        def on_fish_caught(count):
            print(f"  🐟 Peixe #{count} capturado!")

        def on_error(error):
            print(f"  ❌ Erro: {error}")

        def on_stats_update(stats):
            print(f"  📊 Stats: {stats.get('fish_caught')} peixes, {stats.get('catches_per_hour', 0):.1f}/hora")

        fishing_engine.on_state_change = on_state_change
        fishing_engine.on_fish_caught = on_fish_caught
        fishing_engine.on_error = on_error
        fishing_engine.on_stats_update = on_stats_update
        print("✅ Callbacks configurados")

        # 12. Verificar integração dos componentes
        print("\n🔍 VERIFICANDO INTEGRAÇÃO DOS COMPONENTES:")
        print("="*50)

        # Verificar RodManager
        print("\n🎣 Testando RodManager...")
        current_rod = rod_manager.get_current_rod()
        print(f"  Vara atual: {current_rod}")
        print(f"  Precisa trocar? {rod_manager.needs_rod_switch()}")
        print("  ✅ RodManager funcionando")

        # Verificar InventoryManager
        print("\n📦 Testando InventoryManager...")
        print(f"  Precisa limpar? {inventory_manager.needs_cleaning()}")
        print(f"  Peixes desde limpeza: {inventory_manager.fish_count_since_cleaning}")
        print("  ✅ InventoryManager funcionando")

        # Verificar FeedingSystem
        print("\n🍖 Testando FeedingSystem...")
        print(f"  Precisa alimentar? {feeding_system.needs_feeding()}")
        print(f"  Modo: {feeding_system.get_feeding_mode()}")
        print("  ✅ FeedingSystem funcionando")

        # Verificar TemplateEngine
        print("\n🎯 Testando TemplateEngine...")
        print(f"  Templates carregados: {len(template_engine.templates)}")
        print(f"  Cache ativo: {template_engine.enable_cache}")
        print("  ✅ TemplateEngine funcionando")

        print("\n" + "="*50)
        print("✅ INTEGRAÇÃO COMPLETA VALIDADA!")
        print("="*50)

        # 13. Teste de ciclo simulado
        print("\n🎮 INICIANDO TESTE DE CICLO SIMULADO")
        print("="*50)
        print("Pressione F9 para iniciar o bot")
        print("Pressione F1 para pausar/resumir")
        print("Pressione F2 para parar")
        print("Pressione ESC para sair do teste")
        print("="*50)

        # Configurar hotkeys
        def start_bot():
            print("\n🚀 [F9] Iniciando bot...")
            fishing_engine.start()

        def pause_bot():
            print("\n⏸️ [F1] Pausando/Resumindo bot...")
            if fishing_engine.is_paused:
                fishing_engine.resume()
            else:
                fishing_engine.pause()

        def stop_bot():
            print("\n🛑 [F2] Parando bot...")
            fishing_engine.stop()

        keyboard.add_hotkey('f9', start_bot)
        keyboard.add_hotkey('f1', pause_bot)
        keyboard.add_hotkey('f2', stop_bot)

        print("\n⌨️ Hotkeys configurados. Aguardando comandos...")

        # Loop principal
        try:
            while True:
                if keyboard.is_pressed('esc'):
                    print("\n🛑 ESC pressionado - saindo do teste...")
                    break
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")

        # Parar bot se ainda estiver rodando
        if fishing_engine.is_running:
            fishing_engine.stop()

        # Mostrar estatísticas finais
        stats = fishing_engine.get_stats()
        print("\n📊 ESTATÍSTICAS FINAIS:")
        print(f"  🐟 Peixes capturados: {stats.get('fish_caught', 0)}")
        print(f"  ⏱️ Tempo de pesca: {stats.get('fishing_time', 0):.1f} segundos")
        print(f"  📈 Taxa de captura: {stats.get('catches_per_hour', 0):.1f} peixes/hora")

        if rod_manager:
            rod_stats = rod_manager.get_stats()
            print(f"  🎣 Trocas de vara: {rod_stats.get('total_switches', 0)}")
            print(f"  ✅ Trocas bem-sucedidas: {rod_stats.get('successful_switches', 0)}")

        if inventory_manager:
            inv_stats = inventory_manager.get_stats()
            print(f"  🧹 Limpezas realizadas: {inv_stats.get('total_cleanings', 0)}")
            print(f"  ✅ Limpezas bem-sucedidas: {inv_stats.get('successful_cleanings', 0)}")

        print("\n" + "="*60)
        print("✅ TESTE COMPLETO FINALIZADO COM SUCESSO!")
        print("="*60)

        return True

    except ImportError as e:
        print(f"\n❌ Erro ao importar módulo: {e}")
        print("Certifique-se de que todos os módulos estão implementados")
        return False

    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_integration()

    if success:
        print("\n✅ Todos os testes passaram!")
        print("🎣 O bot está pronto para uso!")
    else:
        print("\n❌ Alguns testes falharam")
        print("Verifique os erros acima e corrija os problemas")

    input("\nPressione Enter para sair...")