#!/usr/bin/env python3
"""
🍖 TESTE ISOLADO - Sistema de Alimentação F6
Testar comportamento do feeding system isoladamente
"""

import time
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_manager import ConfigManager
from core.template_engine import TemplateEngine
from core.input_manager import InputManager
from core.chest_manager import ChestManager
from core.feeding_system import FeedingSystem
from core.game_state import GameState

def main():
    print("="*60)
    print("🍖 TESTE DO SISTEMA DE ALIMENTAÇÃO (F6)")
    print("="*60)
    print()

    # 1. Inicializar componentes
    print("📋 PASSO 1: Inicializando componentes...")
    config = ConfigManager()
    template_engine = TemplateEngine(config)
    input_manager = InputManager(config)
    game_state = GameState()

    chest_manager = ChestManager(
        config_manager=config,
        input_manager=input_manager,
        game_state=game_state
    )

    feeding_system = FeedingSystem(
        config_manager=config,
        template_engine=template_engine,
        chest_manager=chest_manager,
        game_state=game_state,
        input_manager=input_manager
    )

    print("✅ Componentes inicializados")
    print()

    # 2. Mostrar configuração atual
    print("📊 PASSO 2: Configuração atual:")
    feeding_config = feeding_system.get_feeding_config()
    print(f"   feeds_per_session: {feeding_config.get('feeds_per_session', 'NÃO CONFIGURADO')}")
    print(f"   trigger_mode: {feeding_config.get('trigger_mode', 'NÃO CONFIGURADO')}")
    print(f"   trigger_catches: {feeding_config.get('trigger_catches', 'NÃO CONFIGURADO')}")
    print()

    # 3. Verificar se configuração está correta
    feeds_per_session = feeding_config.get('feeds_per_session')
    if feeds_per_session is None:
        print("❌ ERRO: feeds_per_session não está configurado!")
        print("   Verifique data/config.json")
        return

    print(f"✅ Configuração válida: {feeds_per_session} cliques no botão 'eat'")
    print()

    # 4. Aguardar confirmação
    print("⚠️ IMPORTANTE:")
    print("   1. Posicione o jogo na tela")
    print("   2. Certifique-se de que há comida no baú")
    print("   3. O bot irá:")
    print(f"      - Abrir o baú (ALT)")
    print(f"      - Clicar na comida 1x")
    print(f"      - Clicar no botão 'eat' {feeds_per_session}x")
    print(f"      - Fechar o baú (ALT)")
    print()

    input("Pressione ENTER para iniciar o teste de alimentação...")
    print()

    # 5. Executar alimentação
    print("🍖 PASSO 3: Executando alimentação...")
    print("="*60)
    print()

    start_time = time.time()
    success = feeding_system.execute_feeding(force=True)
    elapsed_time = time.time() - start_time

    print()
    print("="*60)
    print(f"⏱️ Tempo total: {elapsed_time:.2f}s")

    if success:
        print("✅ ALIMENTAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("❌ ALIMENTAÇÃO FALHOU!")

    print()
    print("📊 ESTATÍSTICAS:")
    stats = feeding_system.stats
    print(f"   Total de alimentações: {stats['total_feedings']}")
    print(f"   Sucessos: {stats['successful_feedings']}")
    print(f"   Falhas: {stats['failed_feedings']}")
    print()

    # 6. Análise do tempo
    expected_time = 1.0 + (feeds_per_session * 1.5) + 0.5  # 1s espera inicial + N*1.5s cliques + 0.5s final
    print("📈 ANÁLISE DE TEMPO:")
    print(f"   Tempo esperado: {expected_time:.2f}s")
    print(f"   Tempo real: {elapsed_time:.2f}s")
    print(f"   Diferença: {abs(elapsed_time - expected_time):.2f}s")

    if abs(elapsed_time - expected_time) > 3.0:
        print("   ⚠️ AVISO: Diferença significativa! Pode indicar:")
        print("      - Cliques extras no botão 'eat'")
        print("      - Detecções lentas")
        print("      - Busca de nova comida (BUG)")
    else:
        print("   ✅ Tempo dentro do esperado")

    print()
    print("="*60)
    print("🏁 TESTE CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
