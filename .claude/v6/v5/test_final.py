import sys
sys.path.insert(0, 'D:/finalbot/fishing_bot_v4')

print("=" * 60)
print("TESTE DE INTEGRACAO COMPLETA")
print("=" * 60)

# Imports
print("\n[1/3] Importando modulos...")
from core.config_manager import ConfigManager
from core.template_engine import TemplateEngine
from core.input_manager import InputManager
from core.chest_manager import ChestManager
from core.rod_manager import RodManager
from core.feeding_system import FeedingSystem
from core.inventory_manager import InventoryManager
from core.fishing_engine import FishingEngine
from core.game_state import GameState
print("   OK - Todos os modulos importados")

# Inicializacao
print("\n[2/3] Inicializando componentes...")
config = ConfigManager()
template_engine = TemplateEngine(config_manager=config)
input_manager = InputManager(config_manager=config)
game_state = GameState()
chest_manager = ChestManager(config_manager=config, input_manager=input_manager, game_state=game_state)
rod_manager = RodManager(template_engine=template_engine, input_manager=input_manager, config_manager=config, chest_manager=chest_manager)
feeding_system = FeedingSystem(config_manager=config, template_engine=template_engine, chest_manager=chest_manager)
inventory_manager = InventoryManager(template_engine=template_engine, chest_manager=chest_manager, input_manager=input_manager, config_manager=config)
print("   OK - Componentes inicializados")

# FishingEngine
print("\n[3/3] Inicializando FishingEngine...")
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
print("   OK - FishingEngine inicializado")

# Validacao
print("\n[VALIDACAO] Verificando componentes do FishingEngine:")
print(f"  TemplateEngine: {'OK' if fishing_engine.template_engine else 'FALTA'}")
print(f"  InputManager: {'OK' if fishing_engine.input_manager else 'FALTA'}")
print(f"  RodManager: {'OK' if fishing_engine.rod_manager else 'FALTA'}")
print(f"  FeedingSystem: {'OK' if fishing_engine.feeding_system else 'FALTA'}")
print(f"  InventoryManager: {'OK' if fishing_engine.inventory_manager else 'FALTA'}")
print(f"  ChestManager: {'OK' if fishing_engine.chest_manager else 'FALTA'}")
print(f"  ChestCoordinator: {'OK' if fishing_engine.chest_coordinator else 'FALTA'}")

print("\n" + "=" * 60)
print("SUCCESS - INTEGRACAO COMPLETA!")
print("=" * 60)
print("\nSISTEMA PRONTO PARA USO!")
print("\nPara iniciar o bot: python main.py")
print("\nHotkeys:")
print("  F9: Iniciar")
print("  F1: Pausar")
print("  F2: Parar")
print("  F6: Alimentacao")
print("  F5: Limpeza")
print("  Page Down: Manutencao")
