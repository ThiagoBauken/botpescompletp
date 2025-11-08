#!/usr/bin/env python3
"""
🎣 FishingEngine - Core do Sistema de Pesca v4.0

Baseado na análise completa do sistema v3, este módulo implementa:
- Ciclos de pesca com timeout de 122 segundos
- Detecção de peixes capturados via template matching
- Coordenação com rod_manager, feeding_manager e inventory_manager
- Estado thread-safe e sistema de callbacks para UI
- Estatísticas em tempo real

Extrai e consolida a lógica de pesca funcional do botpesca.py
"""

import threading
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
import logging
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


# Import GameMode from game_state module
try:
    from .game_state import GameMode
except ImportError:
    GameMode = None

# Import RodManager e InventoryManager
try:
    from .rod_manager import RodManager
except ImportError:
    RodManager = None
    _safe_print("⚠️ RodManager não encontrado")

try:
    from .inventory_manager import InventoryManager
except ImportError:
    InventoryManager = None
    _safe_print("⚠️ InventoryManager não encontrado")

# Setup logging
logger = logging.getLogger(__name__)

class FishingState(Enum):
    """Estados do sistema de pesca"""
    STOPPED = "stopped"
    STARTING = "starting"
    FISHING = "fishing"
    RUNNING = "running"
    PAUSED = "paused"
    FISH_CAUGHT = "fish_caught"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class FishingCycle:
    """Dados de um ciclo de pesca"""
    start_time: float
    end_time: Optional[float] = None
    fish_caught: bool = False
    timeout_reached: bool = False
    rod_used: Optional[int] = None
    errors: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def duration(self) -> float:
        """Duração do ciclo em segundos"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def is_successful(self) -> bool:
        """Se o ciclo foi bem-sucedido (peixe capturado)"""
        return self.fish_caught and not self.timeout_reached

class FishingEngine:
    """
    🎣 Motor Principal de Pesca
    
    Responsabilidades:
    - Detectar peixes capturados (catch.png)
    - Executar sequência de captura
    - Gerenciar estado da pesca
    - Coordenar com outros sistemas
    """
    
    def __init__(self, template_engine=None, input_manager=None, rod_manager=None,
                 feeding_system=None, inventory_manager=None, chest_manager=None,
                 game_state=None, config_manager=None, ws_client=None):
        """
        Inicializar motor de pesca com TODOS os componentes integrados

        Args:
            template_engine: Sistema de detecção de templates
            input_manager: Controle de mouse/teclado
            rod_manager: Sistema de gerenciamento de varas
            feeding_system: Sistema de alimentação
            inventory_manager: Sistema de limpeza de inventário
            chest_manager: Sistema de gerenciamento de baú
            game_state: Estado global do jogo
            config_manager: Gerenciador de configuração
            ws_client: Cliente WebSocket para servidor multi-usuário (opcional)
        """
        self.template_engine = template_engine
        self.input_manager = input_manager
        self.rod_manager = rod_manager
        self.feeding_system = feeding_system
        self.inventory_manager = inventory_manager
        self.chest_manager = chest_manager
        self.config_manager = config_manager
        self.ws_client = ws_client  # ✅ Cliente WebSocket (opcional)
        
        # GameState - criar se não fornecido
        if game_state:
            self.game_state = game_state
        else:
            try:
                from .game_state import GameState
                self.game_state = GameState(config_manager=config_manager)
                _safe_print("🎮 GameState criado internamente")
            except ImportError:
                # Criar game state básico se não existir
                self.game_state = {
                    'fishing_active': False,
                    'action_in_progress': False,
                    'chest_open': False,
                    'feeding_active': False,
                    'cleaning_active': False,
                    'rod_switching': False
                }
                _safe_print("🎮 GameState básico criado")
        
        # Validar componentes essenciais
        if not self.template_engine:
            _safe_print("⚠️ TemplateEngine não fornecido")
        if not self.input_manager:
            _safe_print("⚠️ InputManager não fornecido")
        
        _safe_print(f"🎣 FishingEngine inicializado com componentes:")
        _safe_print(f"  📋 TemplateEngine: {'✅' if self.template_engine else '❌'}")
        _safe_print(f"  🖱️ InputManager: {'✅' if self.input_manager else '❌'}")
        _safe_print(f"  🎣 RodManager: {'✅' if self.rod_manager else '❌'}")
        _safe_print(f"  🍖 FeedingSystem: {'✅' if self.feeding_system else '❌'}")
        _safe_print(f"  📦 InventoryManager: {'✅' if self.inventory_manager else '❌'}")
        _safe_print(f"  🎁 ChestManager: {'✅' if self.chest_manager else '❌'}")
        _safe_print(f"  🌐 WebSocket Client: {'✅ Conectado' if self.ws_client and self.ws_client.is_connected() else '❌ Offline'}")

        # Inicializar Coordenador de Operações de Baú
        try:
            from .chest_operation_coordinator import ChestOperationCoordinator
            self.chest_coordinator = ChestOperationCoordinator(
                config_manager=config_manager,
                template_engine=template_engine,  # ✅ CORRIGIDO: Passar template_engine para verificação de baú
                feeding_system=feeding_system,
                rod_maintenance_system=getattr(rod_manager, 'maintenance_system', None) if rod_manager else None,
                inventory_manager=inventory_manager,
                input_manager=input_manager,  # ✅ NOVO: Para atualizar estado interno dos botões
                ws_client=ws_client,  # ✅ NOVO: Para notificar servidor após operações
                on_batch_complete=self._on_batch_complete  # ✅ NOVO: Callback para sincronização cliente-servidor
            )
            _safe_print(f"  🏪 ChestCoordinator: ✅")
        except ImportError as e:
            _safe_print(f"  🏪 ChestCoordinator: ❌ ({e})")
            self.chest_coordinator = None

        # ✅ NOVO: Inicializar DetectionHandler (para detecções e reports)
        try:
            import sys
            import os
            # ✅ Adicionar diretório client ao path (funciona em .exe)
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(__file__))

            client_path = os.path.join(base_dir, 'client')
            if client_path not in sys.path:
                sys.path.insert(0, client_path)

            from detection_handler import DetectionHandler
            self.detection_handler = DetectionHandler(template_engine, config_manager, chest_manager)
            _safe_print(f"  🔍 DetectionHandler: ✅")
        except ImportError as e:
            _safe_print(f"  🔍 DetectionHandler: ❌ ({e})")
            self.detection_handler = None

        # ✅ NOVO: Inicializar ActionExecutor (para executar sequências do servidor - DEPRECATED)
        try:
            from action_executor import ActionExecutor
            self.action_executor = ActionExecutor(
                input_manager=input_manager,
                template_engine=template_engine,
                fishing_engine=self
            )
            _safe_print(f"  ⚡ ActionExecutor: ✅ (DEPRECATED)")
        except ImportError as e:
            _safe_print(f"  ⚡ ActionExecutor: ❌ ({e})")
            self.action_executor = None

        # ✅ ChestOperationCoordinator já está inicializado em __init__ (self.chest_coordinator)
        # Não precisa criar novo BatchCoordinator - usar ChestOperationCoordinator existente!
        _safe_print(f"  🏪 ChestOperationCoordinator: {'✅' if self.chest_coordinator else '❌'}")

        # Estado interno
        self.state = FishingState.STOPPED
        self.is_running = False
        self.is_paused = False

        # ✅ NOVO: Flag de controle pelo servidor
        # Quando True, desativa prioridades locais (feeding, cleaning, maintenance)
        # O servidor passa a controlar TUDO via WebSocket
        self.server_controlled = False

        # ✅ NOVO: Flag para aguardar batch completar
        # Quando True, NÃO volta ao estado FISHING até batch completar
        # Evita conflito entre fishing cycle e operações de baú
        self.waiting_for_batch_completion = False

        # ✅ NOVO: Callback de switch_rod pendente
        # Armazena comando switch_rod do servidor para executar APÓS fechar baú
        self.pending_switch_rod_callback = None
        self.had_chest_operations = False  # Flag para indicar se batch teve operações de baú
        _safe_print("📋 Sistema de switch_rod pendente inicializado")

        # ✅ NOVO: Fila de comandos do servidor
        # Comandos recebidos via WebSocket são enfileirados e executados entre ciclos
        self.pending_server_commands = []
        self.command_lock = threading.Lock()
        _safe_print("📋 Fila de comandos do servidor inicializada")

        # Contadores de timeout para triggers automáticos
        self.timeout_count = 0
        self.consecutive_timeouts = 0
        self.last_rod_used = 1
        self.rod_timeout_history = {}  # {rod_id: consecutive_timeouts}

        # Flag para identificar troca manual de vara
        self._manual_rod_switch = False
        
        # Threading
        self.fishing_thread = None
        self.stop_event = threading.Event()
        
        # Callbacks para UI
        self.on_state_change: Optional[Callable] = None
        self.on_fish_caught: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        self.on_stats_update: Optional[Callable] = None
        
        # Estatísticas
        self.stats = {
            'fish_caught': 0,
            'session_start_time': 0,
            'fishing_time': 0,
            'last_catch_time': 0,
            'catches_per_hour': 0.0,
            'timeouts': 0
        }
        
        # Configurações (extraídas do botpesca.py)
        self.catch_detection_interval = 0.1  # 100ms
        self.catch_confidence_threshold = 0.8
        self.max_fishing_time = 120  # timeout em segundos
        
        # Sistema de prioridades (baseado no botpesca.py)
        self.priority_task_queue = []
        self.priority_lock = threading.RLock()

        # ☕ SISTEMA DE PAUSAS NATURAIS (anti-detecção) - Carregado do config
        default_breaks = {
            'enabled': False,
            'mode': 'catches',  # 'time' ou 'catches'
            'time_interval': 45,  # minutos
            'catches_interval': 50,  # número de peixes
            'pause_duration_min': 120,  # segundos (2 min)
            'pause_duration_max': 300,  # segundos (5 min)
            'last_break_time': time.time(),  # timestamp da última pausa
            'catches_since_break': 0  # contador de peixes desde última pausa
        }

        # Carregar configurações do ConfigManager se disponível
        if self.config_manager:
            try:
                self.natural_breaks = {
                    'enabled': self.config_manager.get('anti_detection.natural_breaks', default_breaks['enabled']),
                    'mode': self.config_manager.get('anti_detection.break_mode', default_breaks['mode']),
                    'time_interval': self.config_manager.get('anti_detection.break_minutes', default_breaks['time_interval']),
                    'catches_interval': self.config_manager.get('anti_detection.break_catches', default_breaks['catches_interval']),
                    'pause_duration_min': default_breaks['pause_duration_min'],  # Não configurável pela UI
                    'pause_duration_max': default_breaks['pause_duration_max'],  # Não configurável pela UI
                    'last_break_time': time.time(),
                    'catches_since_break': 0
                }
                _safe_print(f"☕ Pausas naturais carregadas: enabled={self.natural_breaks['enabled']}, mode={self.natural_breaks['mode']}")
            except Exception as e:
                _safe_print(f"⚠️ Erro ao carregar config de pausas naturais: {e}")
                self.natural_breaks = default_breaks
        else:
            self.natural_breaks = default_breaks

        _safe_print("🎣 FishingEngine inicializado com sistema de prioridades e pausas naturais")

    def set_server_controlled(self, enabled: bool):
        """
        ✅ NOVO: Ativar/desativar controle pelo servidor

        Quando ativado (True):
        - Desativa prioridades locais (feeding, cleaning, maintenance)
        - Servidor controla TUDO via WebSocket
        - Cliente apenas executa ciclo de pesca e comandos do servidor

        Quando desativado (False):
        - Reativa prioridades locais
        - Bot funciona standalone (sem servidor)

        Args:
            enabled: True para ativar controle servidor, False para desativar
        """
        self.server_controlled = enabled

        if enabled:
            _safe_print("🌐 [SERVER-MODE] Controle transferido para servidor")
            _safe_print("   ✅ Prioridades locais DESATIVADAS")
            _safe_print("   ✅ Servidor controlará: feeding, cleaning, maintenance")
        else:
            _safe_print("🖥️  [LOCAL-MODE] Controle local ativado")
            _safe_print("   ✅ Prioridades locais ATIVADAS")
            _safe_print("   ✅ Bot funcionará standalone")

    def start(self) -> bool:
        """Iniciar sistema de pesca"""
        try:
            if self.is_running:
                _safe_print("⚠️ Sistema de pesca já está rodando")
                return False
            
            _safe_print("🚀 Iniciando sistema de pesca...")
            self.change_state(FishingState.STARTING)
            
            # Validar dependências
            _safe_print("🔍 Validando dependências...")
            if not self._validate_dependencies():
                _safe_print("❌ Falha na validação de dependências")
                self.change_state(FishingState.ERROR)
                return False
            _safe_print("✅ Dependências validadas com sucesso")
            
            # Resetar estatísticas
            self.stats['session_start_time'] = time.time()
            self.stats['fish_caught'] = 0
            
            # Atualizar GameState se disponível
            if self.game_state:
                if GameMode:
                    self.game_state.change_mode(GameMode.FISHING, "FishingEngine iniciado")
            
            # Iniciar thread principal
            self.stop_event.clear()
            self.is_running = True
            self.is_paused = False
            
            self.fishing_thread = threading.Thread(target=self._fishing_loop, daemon=True)
            self.fishing_thread.start()
            
            self.change_state(FishingState.FISHING)
            _safe_print("✅ Sistema de pesca iniciado com sucesso")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar pesca: {e}")
            self.change_state(FishingState.ERROR)
            if self.on_error:
                self.on_error(f"Erro ao iniciar: {e}")
            return False
    
    def stop(self) -> bool:
        """Parar sistema de pesca"""
        try:
            if not self.is_running:
                _safe_print("⚠️ Sistema de pesca não está rodando")
                return False
            
            _safe_print("🛑 Parando sistema de pesca...")
            
            # Sinalizar parada
            self.stop_event.set()
            self.is_running = False
            self.is_paused = False
            
            # IMPORTANTE: Liberar todos os inputs ativos antes de parar
            if self.input_manager:
                try:
                    _safe_print("🔧 Liberando todos os inputs...")
                    self.input_manager.stop_fishing()  # Soltar botão direito
                    self.input_manager.stop_continuous_clicking()  # Parar cliques contínuos
                    self.input_manager.emergency_stop()  # Limpeza geral
                except Exception as e:
                    _safe_print(f"⚠️ Erro ao liberar inputs: {e}")
            
            # Aguardar thread terminar
            if self.fishing_thread and self.fishing_thread.is_alive():
                self.fishing_thread.join(timeout=5.0)
            
            self.change_state(FishingState.STOPPED)
            _safe_print("✅ Sistema de pesca parado")
            
            # Atualizar GameState se disponível
            if self.game_state:
                if GameMode:
                    self.game_state.change_mode(GameMode.IDLE, "FishingEngine parado")
            
            # Calcular estatísticas finais
            self._calculate_final_stats()
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao parar pesca: {e}")
            if self.on_error:
                self.on_error(f"Erro ao parar: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausar/Despausar sistema de pesca"""
        try:
            if not self.is_running:
                _safe_print("⚠️ Sistema de pesca não está rodando")
                return False

            self.is_paused = not self.is_paused

            if self.is_paused:
                _safe_print("⏸️ Sistema de pesca pausado")
                self.change_state(FishingState.PAUSED)
            else:
                _safe_print("▶️ Sistema de pesca despausado")
                self.change_state(FishingState.FISHING)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao pausar/despausar: {e}")
            return False

    def on_server_connection_lost(self):
        """
        ✅ NOVO: Callback chamado quando conexão WebSocket é perdida

        AÇÕES:
        1. Pausa bot automaticamente
        2. Mostra popup de aviso (se UI disponível)
        3. Aguarda usuário reconectar e pressionar F9

        Chamado por: WebSocketClient.on_connection_lost_callback
        """
        _safe_print("\n" + "=" * 70)
        _safe_print("🛑 SERVIDOR DESCONECTADO - BOT PAUSADO AUTOMATICAMENTE")
        _safe_print("=" * 70)

        # Pausar bot (força pausa, não toggle)
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.change_state(FishingState.PAUSED)
            _safe_print("⏸️ Bot pausado devido à perda de conexão")

        # Mostrar popup de aviso (se UI disponível)
        try:
            # Verificar se tem referência para UI (main_window)
            if hasattr(self, 'ui_callback') and self.ui_callback:
                # Chamar callback da UI para mostrar popup
                self.ui_callback('show_connection_lost_dialog')
            else:
                # Tentar importar diretamente (fallback)
                try:
                    from tkinter import messagebox
                    messagebox.showwarning(
                        "Servidor Desconectado",
                        "Conexão com servidor foi perdida!\n\n"
                        "O bot foi pausado automaticamente.\n\n"
                        "Passos para retomar:\n"
                        "1. Verifique sua conexão de internet\n"
                        "2. Aguarde alguns segundos\n"
                        "3. Pressione F9 para retomar\n\n"
                        "O servidor tentará reconectar automaticamente."
                    )
                except:
                    # Se não conseguir mostrar popup, só logar
                    pass
        except Exception as e:
            _safe_print(f"⚠️ Não foi possível mostrar popup: {e}")

        _safe_print("")
        _safe_print("💡 Para retomar a pesca:")
        _safe_print("   1. Verifique sua conexão de internet")
        _safe_print("   2. Aguarde o servidor reconectar")
        _safe_print("   3. Pressione F9 para continuar")
        _safe_print("=" * 70)
    
    def _fishing_loop(self):
        """
        Loop principal de pesca baseado no botpesca.py

        Implementa o ciclo completo:
        1. Capturar posição inicial
        2. Iniciar pesca (botão direito)
        3. Fase rápida (cliques iniciais)
        4. Fase lenta (A/D + cliques contínuos)
        5. Detecção contínua de peixe
        6. Processar captura quando detectado
        """
        try:
            _safe_print("🔄 Iniciando loop principal de pesca baseado no botpesca.py...")

            # ✅ CORREÇÃO 1: Capturar e SALVAR posição inicial (igual v3)
            if self.input_manager:
                import pyautogui

                # 🔍 DEBUG: Capturar posição ANTES e DEPOIS para detectar movimento
                _safe_print("")
                _safe_print("🔍 [FISHING_LOOP] DEBUG CAPTURA DE POSIÇÃO:")
                pos_before = pyautogui.position()
                _safe_print(f"   📍 Posição ANTES de capturar: ({pos_before.x}, {pos_before.y})")

                initial_mouse_pos = pyautogui.position()
                _safe_print(f"   📍 Posição CAPTURADA: ({initial_mouse_pos.x}, {initial_mouse_pos.y})")

                pos_after = pyautogui.position()
                _safe_print(f"   📍 Posição DEPOIS de capturar: ({pos_after.x}, {pos_after.y})")

                delta_x = pos_after.x - pos_before.x
                delta_y = pos_after.y - pos_before.y
                if delta_x != 0 or delta_y != 0:
                    _safe_print(f"   🚨 MOVIMENTO DETECTADO DURANTE CAPTURA: ({delta_x:+d}, {delta_y:+d}) pixels!")
                _safe_print("")

                # Salvar no config_manager (igual v3)
                if self.config_manager:
                    self.config_manager.set('initial_camera_pos', {
                        'x': initial_mouse_pos.x,
                        'y': initial_mouse_pos.y
                    })
                    _safe_print("✅ Posição inicial salva no config")

            # ✅ CORREÇÃO 2: Inicializar vara na primeira execução (igual v3)
            first_cycle = True

            while not self.stop_event.is_set():
                try:
                    # Verificar se pausado
                    if self.is_paused:
                        time.sleep(0.5)
                        continue

                    # ✅ CRÍTICO: Verificar se aguardando batch completar
                    if self.waiting_for_batch_completion:
                        time.sleep(0.5)
                        continue

                    # ✅ DEBUG: Loop retomado após batch (só aparece quando NÃO está mais waiting)
                    if hasattr(self, '_was_waiting_for_batch') and self._was_waiting_for_batch:
                        _safe_print("\n🔄 [LOOP] ✅ Batch completado! Retomando pesca...")
                        _safe_print(f"   🔍 waiting_for_batch_completion = {self.waiting_for_batch_completion}")
                        _safe_print(f"   🔍 Estado = {self.state}\n")
                        self._was_waiting_for_batch = False

                    _safe_print("🔍 [LOOP-DEBUG] Checkpoint 1: Verificando pausas naturais...")

                    # ☕ SISTEMA DE PAUSAS NATURAIS (com verificação de segurança)
                    if self._should_execute_natural_break():
                        # Verificar se é seguro pausar (sem operações em andamento)
                        if not self._is_safe_to_pause():
                            _safe_print("⏸️ [PAUSA NATURAL] Operações em andamento - aguardando...")
                            time.sleep(1.0)
                            continue  # Aguardar próximo loop

                        # Seguro para pausar - executar pausa natural
                        self._execute_natural_break()
                        continue

                    # ✅ CORREÇÃO 3: Inicializar vara no primeiro ciclo (igual v3)
                    if first_cycle:
                        # 🔍 DEBUG: Posição ANTES de inicializar varas
                        import pyautogui
                        pos_antes_varas = pyautogui.position()
                        _safe_print("")
                        _safe_print("🔍 [INIT_VARAS] Posição ANTES: ({}, {})".format(pos_antes_varas.x, pos_antes_varas.y))

                        _safe_print("🎣 Primeira execução - inicializando sistema de varas...")
                        if self.rod_manager:
                            # ✅ Garantir que tracking começa no par 1, slot 1
                            # Usuário já preparou: vara slot 1 na mão + botão direito pressionado
                            self.rod_manager.current_pair_index = 0  # Par 1: (1,2)
                            self.rod_manager.current_rod_in_pair = 0  # Primeiro do par = slot 1
                            _safe_print("✅ Sistema de varas inicializado no slot 1")

                        # 🔍 DEBUG: Posição DEPOIS de inicializar varas
                        pos_depois_varas = pyautogui.position()
                        _safe_print("🔍 [INIT_VARAS] Posição DEPOIS: ({}, {})".format(pos_depois_varas.x, pos_depois_varas.y))
                        delta_x = pos_depois_varas.x - pos_antes_varas.x
                        delta_y = pos_depois_varas.y - pos_antes_varas.y
                        if delta_x != 0 or delta_y != 0:
                            _safe_print("   🚨 MOVIMENTO DETECTADO: ({:+d}, {:+d}) pixels!".format(delta_x, delta_y))
                        _safe_print("")

                        first_cycle = False

                    # ✅ LÓGICA DE PRIORIDADES REMOVIDA - SERVIDOR DECIDE TUDO!
                    # Cliente apenas executa ciclo de pesca e aguarda comandos do servidor

                    # 🔄 VERIFICAR TROCA DE VARA ANTES DE PESCAR
                    # ✅ CRÍTICO: Só trocar se inventário/baú estiver FECHADO
                    if self.rod_manager and self.rod_manager.needs_rod_switch():
                        # Verificar se há operações de baú em progresso
                        inventory_open = False
                        chest_open = False

                        if isinstance(self.game_state, dict):
                            inventory_open = self.game_state.get('inventory_open', False)
                            chest_open = self.game_state.get('chest_open', False)
                        elif hasattr(self.game_state, 'inventory_open'):
                            inventory_open = self.game_state.inventory_open
                            chest_open = self.game_state.chest_open

                        if inventory_open or chest_open:
                            _safe_print("⏸️ [TROCA VARA] Inventário/baú aberto - aguardando fechar...")
                            _safe_print("   ℹ️ Troca será executada após operação de baú terminar")
                            # Não continuar - aguardar próximo loop
                            time.sleep(0.5)
                            continue

                        _safe_print("🔄 Vara precisa ser trocada (inventário fechado)...")
                        if self.rod_manager.switch_rod():
                            _safe_print("✅ Vara trocada com sucesso")
                        else:
                            _safe_print("⚠️ Falha na troca de vara, continuando...")

                    _safe_print(f"\n🎣 Iniciando ciclo de pesca...")
                    self.change_state(FishingState.FISHING)

                    # EXECUTAR CICLO COMPLETO DE PESCA
                    fish_caught = self._execute_complete_fishing_cycle()

                    # ✅ Se retornou None = coordenador está ocupado, NÃO REGISTRAR uso
                    if fish_caught is None:
                        _safe_print("⏸️ Ciclo pulado (coordenador ocupado) - não conta uso de vara")
                        continue  # Próxima iteração do loop

                    # ✅ CRÍTICO: PROCESSAR PEIXE PRIMEIRO (incrementa contadores)
                    # Isso DEVE acontecer ANTES de verificar will_open_chest!
                    if fish_caught:
                        _safe_print("\n" + "="*70)
                        _safe_print("🐟 PEIXE CAPTURADO - INICIANDO PROCESSAMENTO")
                        _safe_print("="*70)

                        # ✅ IMPORTANTE: Processar captura SEM pair_switched ainda
                        # Porque ainda não chamamos register_rod_use()!
                        self.change_state(FishingState.FISH_CAUGHT)
                        self._execute_catch_sequence()

                        # Incrementar contadores IMEDIATAMENTE
                        old_count = self.stats['fish_caught']
                        self.stats['fish_caught'] += 1
                        self.stats['last_catch_time'] = time.time()
                        _safe_print(f"📊 Contador de peixes: {old_count} → {self.stats['fish_caught']}")

                        # Resetar timeout counter
                        current_rod = self.rod_manager.get_current_rod() if self.rod_manager else 1
                        if current_rod in self.rod_timeout_history:
                            self.rod_timeout_history[current_rod] = 0

                        # Incrementar pausas naturais
                        self.natural_breaks['catches_since_break'] += 1

                        # ✅ CRÍTICO: PRIMEIRO registrar uso da vara (incrementa rod_uses)
                        # DEPOIS enviar fish_caught (com rod_uses correto)
                        _safe_print("📝 [REGISTRO PRÉ] Registrando uso da vara ANTES de notificar servidor...")
                        if self.rod_manager:
                            current_rod = self.rod_manager.get_current_rod()
                            self.rod_manager.rod_uses[current_rod] += 1
                            _safe_print(f"   ✅ Vara {current_rod}: {self.rod_manager.rod_uses[current_rod]} usos")

                        # AGORA sim notificar sistemas (com rod_uses correto!)
                        _safe_print("📢 Notificando sistemas e servidor...")
                        self.increment_fish_count()
                        self._force_stats_update()

                        if self.on_fish_caught:
                            self.on_fish_caught(self.stats['fish_caught'])

                        _safe_print(f"✅ Peixe #{self.stats['fish_caught']} processado! Contadores atualizados.")
                        _safe_print("="*70 + "\n")
                    else:
                        _safe_print("⏰ Ciclo finalizado sem captura")

                    # ✅ AGORA verificar will_open_chest (com contadores JÁ atualizados!)
                    _safe_print("\n🔍 [VERIFICAÇÃO] Checando se precisa abrir baú...")
                    will_open_chest = self._will_open_chest_next_cycle()
                    _safe_print(f"📋 [RESULTADO] will_open_chest = {will_open_chest}\n")

                    # ✅ Se tem comandos enfileirados, executar AGORA (entre ciclos)
                    if will_open_chest:
                        self._execute_pending_commands()

                    # 🎣 REGISTRAR USO DA VARA (peixe OU timeout)
                    _safe_print("\n📝 [REGISTRO] Registrando uso da vara...")
                    _safe_print(f"   • Peixe capturado: {fish_caught}")
                    _safe_print(f"   • Vai abrir baú: {will_open_chest}")

                    pair_switched = False
                    if self.rod_manager:
                        pair_switched = self.rod_manager.register_rod_use(
                            caught_fish=fish_caught,
                            will_open_chest=will_open_chest
                        )
                        if pair_switched:
                            _safe_print(f"\n🔄 [TROCA DE PAR DETECTADA] Par mudou! Nova vara: {pair_switched}")

                            # ✅ CRÍTICO: Se vai abrir baú E par mudou, SALVAR vara para equipar após fechar
                            if will_open_chest and isinstance(pair_switched, int) and self.chest_coordinator:
                                _safe_print(f"💾 [SALVANDO] Vara {pair_switched} será equipada APÓS fechar baú")
                                self.chest_coordinator.rod_to_equip_after_pair_switch = pair_switched
                                _safe_print("✅ [CONFIRMADO] Troca de vara ADIADA até baú fechar\n")
                            elif not will_open_chest:
                                _safe_print(f"⚡ [SEM BAÚ] Troca será executada AGORA (não há operações de baú)\n")
                        else:
                            _safe_print("   ✅ Mesmo par - sem mudança de par detectada")

                    # ✅ AGORA chamar troca de vara (se necessário)
                    if fish_caught:
                        # Verificar troca APÓS register_rod_use
                        if will_open_chest:
                            _safe_print("\n" + "="*70)
                            _safe_print("⏸️ [DECISÃO] OPERAÇÃO DE BAÚ PENDENTE")
                            _safe_print("="*70)
                            _safe_print("❌ NÃO VOLTAR A PESCAR AGORA!")
                            _safe_print("✅ Aguardar batch completar ANTES de voltar a pescar")
                            _safe_print("="*70 + "\n")

                            # ✅ CRÍTICO: Marcar flag para aguardar batch completar
                            self.waiting_for_batch_completion = True
                            _safe_print("🔒 [FLAG] waiting_for_batch_completion = True")
                            _safe_print("⏸️ [PAUSA] Estado permanece FISH_CAUGHT até batch completar\n")

                            if self.rod_manager and self.rod_manager.needs_rod_switch():
                                _safe_print("   🔄 Marcando troca de vara para após fechar baú...")
                                self.rod_manager.pending_rod_switch = True
                        else:
                            # ✅ CORREÇÃO: Cliente NÃO decide mais - aguarda comando do servidor!
                            # Servidor envia `switch_rod` no batch após cada peixe
                            # ✅ IMPORTANTE: NÃO marcar waiting_for_batch_completion aqui!
                            # handle_execute_batch() JÁ marca a flag quando batch chega
                            _safe_print("\n" + "="*70)
                            _safe_print("🌐 [SERVIDOR] Aguardando batch do servidor...")
                            _safe_print("="*70)
                            _safe_print("⏸️ Cliente NÃO troca localmente - apenas obedece servidor")
                            _safe_print("✅ Servidor vai enviar 'switch_rod' no próximo batch")
                            _safe_print("✅ handle_execute_batch() já marcou waiting_for_batch_completion")
                            _safe_print("="*70 + "\n")

                            # ✅ CORREÇÃO CRÍTICA: NÃO re-marcar flag aqui!
                            # O batch já foi processado durante os 2s de espera em _will_open_chest_next_cycle()
                            # Se re-marcarmos, o bot fica travado esperando algo que já aconteceu!
                            # handle_execute_batch() marca a flag E reseta via callback
                    
                    # Atualizar estatísticas
                    self._update_stats()
                    
                    # Pausa entre ciclos
                    time.sleep(0.5)
                    
                except Exception as cycle_error:
                    _safe_print(f"❌ Erro no ciclo de pesca: {cycle_error}")
                    time.sleep(2)  # Pausa em caso de erro
                    continue
            
            _safe_print("🔄 Loop de pesca finalizado (stop_event foi setado)")
            
        except Exception as e:
            _safe_print(f"❌ Erro no loop de pesca: {e}")
            self.change_state(FishingState.ERROR)
            if self.on_error:
                self.on_error(f"Erro no loop: {e}")
    
    def _execute_complete_fishing_cycle(self) -> bool:
        """
        Executar ciclo completo de pesca baseado no botpesca.py

        Returns:
            bool: True se peixe foi capturado, False caso contrário
        """
        try:
            if not self.input_manager:
                _safe_print("⚠️ InputManager não disponível - simulando ciclo")
                time.sleep(5)
                return False

            # ✅ CRÍTICO: NÃO INICIAR CICLO se coordenador está executando operações de baú!
            if self.chest_coordinator and self.chest_coordinator.execution_in_progress:
                time.sleep(0.5)
                return None  # ✅ RETORNAR None = não conta como timeout

            # ✅ CRÍTICO: NÃO iniciar novo ciclo se há operações PENDENTES na fila
            if self.chest_coordinator and hasattr(self.chest_coordinator, 'has_pending_operations'):
                if self.chest_coordinator.has_pending_operations():
                    time.sleep(0.5)
                    return None  # ✅ RETORNAR None = não conta como timeout

            _safe_print("🎯 Executando ciclo completo de pesca...")
            
            # ====== IMPLEMENTAÇÃO BASEADA NO EXECUTAR_CICLO_COMPLETO_YOLO() V3 ======
            
            # FASE 1: INICIAR PESCA - Botão direito + 4 cliques lentos (EXATO v3 linha 12809-12820)
            _safe_print("🎣 FASE 1: Iniciando pesca...")
            if self.input_manager:
                # ✅ SOLUÇÃO DEFINITIVA: Usar Mouse RELATIVO para fishing!
                # Mouse.press() NÃO precisa de coordenadas → SEM drift!
                # AbsoluteMouse.press() precisa de coordenadas → COM drift se não sincronizar!
                _safe_print("🎯 Usando Mouse RELATIVO para eliminar drift!")

                # Usar mouse_down_relative (Mouse.press) ao invés de mouse_down (AbsoluteMouse.press)
                # ✅ CRÍTICO: Verificar se botão JÁ está pressionado (por equip_rod)
                if hasattr(self.input_manager, 'mouse_state'):
                    already_pressed = self.input_manager.mouse_state.get('right_button_down', False)
                else:
                    already_pressed = False

                if already_pressed:
                    _safe_print("✅ Botão direito JÁ está pressionado (por equip_rod) - pulando mouse_down")
                elif hasattr(self.input_manager, 'mouse_down_relative'):
                    self.input_manager.mouse_down_relative('right')
                    _safe_print("✅ Botão direito pressionado (Mouse relativo - SEM drift!)")
                else:
                    # Fallback: método antigo
                    self.input_manager.mouse_down('right')
                    _safe_print("✅ Botão direito pressionado (fallback)")

                # 🐌 4 CLIQUES LENTOS com intervalos alternados (1s e 0.5s)
                _safe_print("🐌 Executando 4 cliques lentos iniciais (Mouse RELATIVO)...")

                # Clique 1 → aguardar 1 segundo
                self.input_manager.mouse_down_relative('left')
                time.sleep(0.02)
                self.input_manager.mouse_up_relative('left')
                _safe_print("   🐌 Clique 1/4")
                time.sleep(1.0)

                # Clique 2 → aguardar 0.5 segundo
                self.input_manager.mouse_down_relative('left')
                time.sleep(0.02)
                self.input_manager.mouse_up_relative('left')
                _safe_print("   🐌 Clique 2/4")
                time.sleep(0.5)

                # Clique 3 → aguardar 1 segundo
                self.input_manager.mouse_down_relative('left')
                time.sleep(0.02)
                self.input_manager.mouse_up_relative('left')
                _safe_print("   🐌 Clique 3/4")
                time.sleep(1.0)

                # Clique 4 → aguardar 0.5 segundo
                self.input_manager.mouse_down_relative('left')
                time.sleep(0.02)
                self.input_manager.mouse_up_relative('left')
                _safe_print("   🐌 Clique 4/4")
                time.sleep(0.5)

                _safe_print("✅ 4 cliques lentos concluídos - botão direito MANTIDO pressionado")
            else:
                _safe_print("⚠️ InputManager não disponível")
                return False

            # FASE 2: FASE RÁPIDA - 7.65s de cliques após os 4 lentos (EXATO v3 linha 12826)
            _safe_print("⚡ FASE 2: Fase rápida (7.65s de cliques após 4 cliques lentos)...")
            fish_caught = self._execute_rapid_phase_v3()
            if fish_caught:
                # Soltar botão direito ao capturar peixe
                if self.input_manager:
                    if hasattr(self.input_manager, 'mouse_up_relative'):
                        self.input_manager.mouse_up_relative('right')
                    else:
                        self.input_manager.mouse_up('right')
                return True

            # FASE 3: FASE LENTA - A/D + cliques contínuos até timeout
            _safe_print("🐢 FASE 3: Fase lenta (A/D + cliques até timeout)...")
            fish_caught, maintenance_executed = self._execute_slow_phase_v3()

            # ✅ CRÍTICO: NÃO soltar botão direito se manutenção foi executada!
            # Manutenção já equipou nova vara com botão direito pressionado
            if fish_caught:
                # Soltar botão direito ao capturar peixe
                if self.input_manager:
                    if hasattr(self.input_manager, 'mouse_up_relative'):
                        self.input_manager.mouse_up_relative('right')
                    else:
                        self.input_manager.mouse_up('right')
                return True

            # ✅ CRÍTICO: Verificar se há manutenção PENDENTE na fila!
            # Se adicionamos manutenção à fila, NÃO soltar botão direito
            # porque o coordenador vai equipar vara em background
            has_pending_maintenance = False
            if self.chest_coordinator and hasattr(self.chest_coordinator, 'has_operation_in_queue'):
                has_pending_maintenance = self.chest_coordinator.has_operation_in_queue('maintenance')

            if maintenance_executed or has_pending_maintenance:
                # ✅ Manutenção executada OU pendente - vara será/foi equipada com botão direito
                if has_pending_maintenance:
                    _safe_print("✅ Manutenção PENDENTE - botão direito será segurado pelo coordenador")
                else:
                    _safe_print("✅ Manutenção executada - botão direito já segurado pela nova vara")
                return False  # Timeout, mas não soltar botão

            # ✅ Timeout normal (sem manutenção) - soltar botão direito
            if self.input_manager:
                if hasattr(self.input_manager, 'mouse_up_relative'):
                    self.input_manager.mouse_up_relative('right')
                else:
                    self.input_manager.mouse_up('right')
                _safe_print("🔄 Botão direito solto")

            _safe_print("⏰ Ciclo finalizado sem captura")
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro no ciclo completo: {e}")
            # Garantir que pare a pesca em caso de erro
            if self.input_manager:
                self.input_manager.stop_all_actions()
            return False
    
    def _execute_rapid_phase_v3(self) -> bool:
        """
        🚀 Fase rápida baseada no executar_fase_rapida_com_tempo() do v3

        Lógica EXATA:
        - 7.65 segundos de cliques contínuos (v3 linha 12829)
        - Intervalo VARIÁVEL: 0.15s a 0.5s por clique (anti-detecção)
        - Detecção de peixe durante os cliques
        - Botão direito JÁ ESTÁ pressionado (fase anterior)

        ✅ CORREÇÃO: Flag para parar cliques IMEDIATAMENTE ao detectar peixe
        """
        try:
            _safe_print("⚡ Iniciando fase rápida (7.65s de cliques com variação aleatória 0.15-0.5s)...")

            rapid_duration = 7.65  # Duração da fase rápida (v3 linha 12829)
            start_time = time.time()
            click_count = 0

            # ✅ CORREÇÃO: Flag para parar cliques IMEDIATAMENTE
            clicking_active = True

            while time.time() - start_time < rapid_duration and clicking_active:
                # Verificar se ainda está rodando
                if not self.is_running or self.is_paused:
                    clicking_active = False  # Parar cliques
                    return False

                # ✅ CORREÇÃO: Verificar flag ANTES de clicar
                if not clicking_active:
                    _safe_print("🛑 Cliques pausados na fase rápida (flag desativada)")
                    break

                # Verificar se peixe foi capturado ANTES de clicar
                if self.template_engine:
                    found, confidence = self.template_engine.detect_fish_caught()
                    if found:
                        clicking_active = False  # ✅ PARAR CLIQUES IMEDIATAMENTE!
                        _safe_print(f"🐟 Peixe capturado na fase rápida! Confiança: {confidence:.3f}")
                        _safe_print(f"📊 Total de {click_count} cliques executados")
                        _safe_print("🛑 Cliques interrompidos IMEDIATAMENTE")
                        return True

                # ✅ SOLUÇÃO FINAL: Usar Mouse.press/release() relativo (SEM AbsoluteMouse)
                # Mouse RELATIVO NÃO move o cursor, apenas clica onde está
                # Isso elimina 100% do drift sem precisar de sincronizações
                if clicking_active and self.input_manager:
                    # Usar mouse_down_relative + mouse_up_relative (Mouse.press/release)
                    self.input_manager.mouse_down_relative('left')
                    time.sleep(0.02)  # Duração do clique
                    self.input_manager.mouse_up_relative('left')
                    click_count += 1

                # ✅ NOVO: Intervalo VARIÁVEL entre 0.15s e 0.5s (anti-detecção)
                if clicking_active:
                    import random
                    click_interval = random.uniform(0.15, 0.5)
                    time.sleep(click_interval)

            _safe_print(f"⚡ Fase rápida concluída ({click_count} cliques em 7.65s)")
            return False

        except Exception as e:
            _safe_print(f"❌ Erro na fase rápida: {e}")
            return False
    
    def _execute_slow_phase_v3(self) -> tuple[bool, bool]:
        """
        🐢 Fase lenta baseada no executar_fase_lenta_com_cliques() do v3

        Lógica EXATA:
        - Movimento A/D alternado
        - Cliques contínuos durante movimentos
        - Detecção de peixe até timeout
        - Duração configurável via config (padrão 120s)

        ✅ CORREÇÃO: Flag para parar cliques IMEDIATAMENTE ao detectar peixe

        Returns:
            tuple[bool, bool]: (fish_caught, maintenance_executed)
        """
        try:
            _safe_print("🐢 Iniciando fase lenta (A/D + S em ciclo + cliques até timeout)...")

            # ✅ CRÍTICO: Obter timeout do config DA UI (não fixo!)
            timeout = 120
            if self.config_manager:
                timeout = self.config_manager.get('timeouts.fishing_cycle_timeout', 120)

            _safe_print(f"⏱️ Usando timeout da UI: {timeout}s")

            # ✅ CRÍTICO: Usar clicks_per_second da UI (não fixo)
            clicks_per_second = 12  # Padrão
            if self.config_manager:
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)

            click_interval = 1.0 / clicks_per_second  # Calcular intervalo baseado na UI
            _safe_print(f"🖱️ Usando {clicks_per_second} cliques/segundo da UI (intervalo: {click_interval:.3f}s)")

            # ✅ CORREÇÃO: ALT removido! ALT só deve ser usado ao abrir baú, não durante pesca normal!
            # O ciclo de S ajuda a puxar o peixe sem precisar do ALT

            _safe_print("🔄 Iniciando ciclo aleatório de S (ajuda puxar peixe)...")
            if self.input_manager:
                self.input_manager.start_continuous_s_press()

            start_time = time.time()

            movement_direction = 'a'  # Começar com A

            # ✅ CORREÇÃO: Flag para parar cliques IMEDIATAMENTE
            clicking_active = True

            while time.time() - start_time < timeout:
                # Verificar se ainda está rodando
                if not self.is_running or self.is_paused:
                    clicking_active = False  # Parar cliques

                    # ✅ PARAR ciclo de S ao pausar/parar
                    _safe_print("🛑 Parando ciclo de S (bot parado/pausado)...")
                    if self.input_manager:
                        self.input_manager.stop_continuous_s_press()

                    return (False, False)  # (não capturou, sem manutenção)

                # ✅ VARIAÇÃO ALEATÓRIA: Obter duração baseada em A ou D (anti-detecção)
                import random
                if movement_direction == 'a':
                    # Movimento A: 1.2s a 1.8s (do InputManager timing_config)
                    movement_duration = random.uniform(1.2, 1.8)
                else:
                    # Movimento D: 1.0s a 1.4s (do InputManager timing_config)
                    movement_duration = random.uniform(1.0, 1.4)

                # ===== FASE DE MOVIMENTO =====
                # Log removido para evitar poluição do console

                if self.input_manager:
                    # Pressionar tecla de movimento
                    self.input_manager.key_down(movement_direction)

                    # Cliques durante o movimento
                    movement_start = time.time()
                    while time.time() - movement_start < movement_duration and clicking_active:
                        # Verificar parada
                        if not self.is_running or self.is_paused:
                            clicking_active = False  # Parar cliques IMEDIATAMENTE
                            self.input_manager.key_up(movement_direction)
                            return (False, False)  # (não capturou, sem manutenção)

                        # ✅ CORREÇÃO: Verificar flag ANTES de clicar
                        if not clicking_active:
                            _safe_print("🛑 Cliques pausados (flag desativada)")
                            break

                        # ✅ SOLUÇÃO DEFINITIVA: Usar mouse_down_relative + mouse_up_relative
                        # Mouse RELATIVO elimina 100% do drift!
                        self.input_manager.mouse_down_relative('left')
                        time.sleep(0.02)  # Duração do clique
                        self.input_manager.mouse_up_relative('left')

                        # Verificar peixe
                        if self.template_engine:
                            found, confidence = self.template_engine.detect_fish_caught()
                            if found:
                                clicking_active = False  # ✅ PARAR CLIQUES IMEDIATAMENTE!
                                self.input_manager.key_up(movement_direction)

                                # ✅ PARAR ciclo de S ao capturar peixe
                                _safe_print("🛑 Parando ciclo de S (peixe capturado)...")
                                if self.input_manager:
                                    self.input_manager.stop_continuous_s_press()

                                _safe_print(f"🐟 Peixe capturado na fase lenta! Confiança: {confidence:.3f}")
                                _safe_print("🛑 Cliques interrompidos IMEDIATAMENTE")
                                return (True, False)  # (capturou peixe, sem manutenção)

                        # Aguardar próximo clique (só se ainda ativo)
                        if clicking_active:
                            time.sleep(click_interval)

                    # Soltar tecla de movimento
                    self.input_manager.key_up(movement_direction)

                # Alternar direção (A -> D -> A -> D...)
                movement_direction = 'd' if movement_direction == 'a' else 'a'

                # ✅ PAUSA VARIÁVEL entre movimentos (0.2s a 0.5s, anti-detecção)
                pause_duration = random.uniform(0.2, 0.5)
                time.sleep(pause_duration)
            
            # ✅ Incrementar contador de timeouts E REGISTRAR VARA ATUAL
            current_rod = self.rod_manager.get_current_rod() if self.rod_manager else 1

            with self.priority_lock:
                self.stats['timeouts'] += 1

                # ✅ CRÍTICO: Tracking de timeout por vara (INDIVIDUAL)
                if current_rod not in self.rod_timeout_history:
                    self.rod_timeout_history[current_rod] = 0
                self.rod_timeout_history[current_rod] += 1

                # ✅ IMPORTANTE: NÃO resetar outras varas!
                # Timeout só reseta quando PEIXE É CAPTURADO com aquela vara específica

            # ✅ PARAR ciclo de S ao atingir timeout
            _safe_print("🛑 Parando ciclo de S (timeout)...")
            if self.input_manager:
                self.input_manager.stop_continuous_s_press()

            _safe_print(f"⏰ Timeout de {timeout}s alcançado na fase lenta")
            _safe_print(f"📊 Total de timeouts: {self.stats['timeouts']}")
            _safe_print(f"🎣 Vara {current_rod}: {self.rod_timeout_history[current_rod]} timeout(s) consecutivo(s)")

            # ✅ NOVO: Enviar timeout ao SERVIDOR (servidor decide se limpa)
            if self.ws_client and self.ws_client.is_connected():
                _safe_print(f"📡 Enviando timeout ao servidor (vara {current_rod})...")
                self.ws_client.send_timeout(current_rod)
                _safe_print("⏸️ Aguardando servidor enviar batch de cleaning + maintenance...")
            else:
                # ✅ CORREÇÃO #7: HÍBRIDO - Offline não tem limpeza automática
                _safe_print("⚠️ [OFFLINE] Servidor desconectado")
                _safe_print("   ℹ️ Limpeza é MANUAL no modo offline (use F5)")
                _safe_print(f"   📊 Timeouts consecutivos vara {current_rod}: {self.rod_timeout_history.get(current_rod, 0)}")

            # ✅ Timeout normal - retornar
            return (False, False)  # (timeout sem peixe)

        except Exception as e:
            _safe_print(f"❌ Erro na fase lenta: {e}")
            return (False, False)  # (erro, sem manutenção)

        finally:
            # ✅ CRÍTICO: SEMPRE soltar S, A e D, independente de como a função termina
            # Isso garante que nenhuma tecla fica presa, mesmo em caso de exceção!
            # NOTA: ALT não é usado durante pesca - apenas ao abrir baú!
            _safe_print("🔧 [FINALLY] Garantindo que S, A e D sejam liberados...")
            if self.input_manager:
                try:
                    self.input_manager.stop_continuous_s_press()
                    self.input_manager.key_up('a')
                    self.input_manager.key_up('d')
                    _safe_print("✅ [FINALLY] S, A e D liberados com sucesso")
                except Exception as cleanup_error:
                    _safe_print(f"⚠️ [FINALLY] Erro ao liberar teclas: {cleanup_error}")
    
    def _detect_fish_caught(self) -> bool:
        """
        Detectar se um peixe foi capturado (extraído do botpesca.py)
        
        Lógica original funcionando:
        - Template matching para catch.png
        - Confidence threshold configurável
        - Otimizações de performance
        """
        try:
            if not self.template_engine:
                return False
            
            # Usar template engine para detectar catch.png
            result = self.template_engine.detect_template(
                template_name='catch',
                confidence_threshold=self.catch_confidence_threshold
            )
            
            return result is not None and result.confidence >= self.catch_confidence_threshold
            
        except Exception as e:
            _safe_print(f"❌ Erro na detecção de peixe: {e}")
            return False
    
    def _handle_fish_caught(self, pair_switched=False):
        """
        Processar peixe capturado (extraído do botpesca.py)

        Args:
            pair_switched: Se True, indica que o par de varas acabou de mudar
                          e NÃO deve alternar vara (já está no slot correto do novo par)

        Sequência original que funciona:
        1. Soltar botão do mouse
        2. Aguardar estabilização
        3. Pressionar novamente
        4. Atualizar estatísticas
        5. Notificar sistemas dependentes
        """
        try:
            _safe_print("🐟 Peixe detectado! Processando captura...")
            self.change_state(FishingState.FISH_CAUGHT)
            
            # Sequência de captura (lógica do botpesca.py)
            self._execute_catch_sequence()
            
            # Atualizar contador de peixes
            self.stats['fish_caught'] += 1
            self.stats['last_catch_time'] = time.time()

            # ✅ RESETAR contador de timeout da vara atual (peixe capturado = vara funcionando)
            current_rod = self.rod_manager.get_current_rod() if self.rod_manager else 1
            if current_rod in self.rod_timeout_history:
                self.rod_timeout_history[current_rod] = 0
                _safe_print(f"🎣 Vara {current_rod}: contador de timeouts resetado (peixe capturado)")

            # ☕ INCREMENTAR contador de pausas naturais
            self.natural_breaks['catches_since_break'] += 1

            # 🔥 NOTIFICAR TODOS OS SISTEMAS DEPENDENTES
            self.increment_fish_count()

            # ✅ ATUALIZAR estatísticas IMEDIATAMENTE (não esperar 5s)
            self._force_stats_update()

            # Callback para UI
            if self.on_fish_caught:
                self.on_fish_caught(self.stats['fish_caught'])

            _safe_print(f"✅ Peixe #{self.stats['fish_caught']} capturado! Sistemas notificados.")

            # ✅ CRÍTICO: VERIFICAR SE VAI ABRIR BAÚ antes de trocar vara
            # Lógica: Se próximo ciclo vai executar alimentação/limpeza, NÃO trocar agora
            # A troca será feita pelo coordinator com will_open_chest=True
            will_open_chest = self._will_open_chest_next_cycle()

            if will_open_chest:
                _safe_print("⏸️ [TROCA VARA] Operação de baú pendente - troca será feita pelo coordinator")
                _safe_print("   ℹ️ A vara será trocada APÓS fechar o baú (com botão direito já pressionado)")

                # ✅ NOVO: Marcar que precisa trocar vara após baú fechar
                if self.rod_manager and self.rod_manager.needs_rod_switch():
                    _safe_print("   🔄 Marcando troca de vara para após fechar baú...")
                    self.rod_manager.pending_rod_switch = True
            else:
                # ✅ CRÍTICO: Se mudou de par, EQUIPAR DIRETAMENTE primeiro slot do novo par!
                if pair_switched and self.rod_manager:
                    _safe_print("🔄 [TROCA DE PAR] Par mudou - EQUIPANDO primeiro slot do novo par...")
                    try:
                        # pair_switched agora é o NÚMERO da primeira vara do novo par!
                        first_slot = pair_switched if isinstance(pair_switched, int) else None

                        if first_slot:
                            _safe_print(f"   📍 Equipando vara {first_slot} (primeira do novo par)")

                            # Equipar diretamente com botão direito
                            if self.rod_manager.equip_rod(first_slot, hold_right_button=True):
                                _safe_print(f"✅ Vara {first_slot} do novo par equipada com sucesso")
                            else:
                                _safe_print("⚠️ Falha ao equipar vara do novo par")
                        else:
                            _safe_print("❌ Erro: first_slot não foi retornado corretamente")
                    except Exception as e:
                        _safe_print(f"❌ Erro ao equipar vara do novo par: {e}")
                # ✅ Se não mudou de par, apenas alternar no mesmo par (1→2 ou 3→4)
                elif self.rod_manager and not pair_switched:
                    _safe_print("🔄 Alternando vara após captura (sem baú)...")
                    try:
                        if self.rod_manager.switch_rod(will_open_chest=False):
                            _safe_print("✅ Vara alternada com sucesso após peixe")
                        else:
                            _safe_print("⚠️ Falha ao alternar vara, continuando com vara atual")
                    except Exception as e:
                        _safe_print(f"❌ Erro ao alternar vara: {e}")

            # Voltar ao estado de pesca
            self.change_state(FishingState.FISHING)
            
        except Exception as e:
            _safe_print(f"❌ Erro ao processar peixe capturado: {e}")
            if self.on_error:
                self.on_error(f"Erro na captura: {e}")
            
            # Em caso de erro, ainda incrementar contador
            self.stats['fish_caught'] += 1
            self.stats['last_catch_time'] = time.time()
            
            # Voltar ao estado de pesca mesmo com erro
            self.change_state(FishingState.FISHING)
    
    def _execute_catch_sequence(self):
        """
        Executar sequência de captura EXATA do botpesca.py
        
        Baseado na análise:
        1. Soltar botão direito (parar pesca)
        2. Aguardar 3 segundos (coleta do peixe)
        3. NÃO pressionar novamente (aguardar próximo ciclo)
        """
        try:
            if not self.input_manager:
                _safe_print("⚠️ InputManager não disponível - usando simulação")
                time.sleep(3.0)
                return
            
            _safe_print("🐟 Executando sequência de captura REAL...")
            
            # Usar a sequência exata do InputManager
            success = self.input_manager.catch_fish()
            
            if success:
                _safe_print("✅ Sequência de captura executada com sucesso")
            else:
                _safe_print("⚠️ Problemas na sequência de captura")
            
        except Exception as e:
            _safe_print(f"❌ Erro na sequência de captura: {e}")
            raise
    
    def _check_fishing_timeout(self) -> bool:
        """Verificar se excedeu timeout de pesca"""
        if not hasattr(self, '_last_action_time'):
            self._last_action_time = time.time()
            return False
        
        elapsed = time.time() - self._last_action_time
        return elapsed > self.max_fishing_time
    
    def _handle_fishing_timeout(self):
        """Processar timeout de pesca - TRIGGERS AUTOMÁTICOS baseados no v3"""
        _safe_print("⏰ Timeout de pesca detectado!")

        # Incrementar contadores
        self.timeout_count += 1
        self.consecutive_timeouts += 1

        # Obter vara atual
        current_rod = self.rod_manager.get_current_rod() if self.rod_manager else 1

        # Histórico de timeouts por vara
        if current_rod not in self.rod_timeout_history:
            self.rod_timeout_history[current_rod] = 0
        self.rod_timeout_history[current_rod] += 1

        _safe_print(f"📊 Timeout #{self.timeout_count} (consecutivos: {self.consecutive_timeouts})")
        _safe_print(f"🎣 Vara {current_rod}: {self.rod_timeout_history[current_rod]} timeouts")

        # TRIGGER 1: Vara quebrada após 1 pesca ou timeout
        if self.chest_coordinator and self.rod_manager:
            # Verificar se há vara quebrada
            rod_status = self.rod_manager._scan_all_rods()
            broken_rods = [rod for rod, status in rod_status.items() if status.name == 'BROKEN']

            if broken_rods:
                _safe_print(f"🔧 TRIGGER: Vara quebrada detectada - slots {broken_rods}")
                from .chest_operation_coordinator import trigger_maintenance_operation, TriggerReason
                trigger_maintenance_operation(self.chest_coordinator, TriggerReason.BROKEN_ROD_DETECTED)

        # ❌ DESABILITADO: Trigger automático de manutenção por timeout removido
        # Use Page Down para manutenção manual quando necessário

        # TRIGGER 3: Inventário cheio (detectar via template ou contador)
        # TODO: Implementar detecção de inventário cheio

        # Reset timeouts consecutivos ao trocar de vara
        if current_rod != self.last_rod_used:
            _safe_print(f"🔄 Vara mudou de {self.last_rod_used} para {current_rod} - reset timeouts consecutivos")
            self.consecutive_timeouts = 0
            self.last_rod_used = current_rod

        self._last_action_time = time.time()
    
    def _force_stats_update(self):
        """
        ✅ Forçar atualização imediata de estatísticas (não esperar intervalo de 5s)
        Usado após eventos importantes como captura de peixe ou feeding
        """
        try:
            current_time = time.time()
            self.stats['fishing_time'] = current_time - self.stats['session_start_time']

            # Calcular capturas por hora
            if self.stats['fishing_time'] > 0:
                hours = self.stats['fishing_time'] / 3600
                self.stats['catches_per_hour'] = self.stats['fish_caught'] / hours

            # ✅ INCLUIR estatísticas de feeding e cleaning
            if self.feeding_system and hasattr(self.feeding_system, 'stats'):
                self.stats.update(self.feeding_system.stats)

            if self.inventory_manager and hasattr(self.inventory_manager, 'stats'):
                self.stats.update(self.inventory_manager.stats)

            # Atualizar UI IMEDIATAMENTE
            if self.on_stats_update:
                self.on_stats_update(self.stats.copy())

            self._last_stats_update = current_time

        except Exception as e:
            _safe_print(f"❌ Erro ao forçar atualização de stats: {e}")

    def _update_stats(self):
        """Atualizar estatísticas em tempo real"""
        try:
            current_time = time.time()
            self.stats['fishing_time'] = current_time - self.stats['session_start_time']

            # Calcular capturas por hora
            if self.stats['fishing_time'] > 0:
                hours = self.stats['fishing_time'] / 3600
                self.stats['catches_per_hour'] = self.stats['fish_caught'] / hours

            # ✅ INCLUIR estatísticas de feeding e cleaning
            if self.feeding_system and hasattr(self.feeding_system, 'stats'):
                self.stats.update(self.feeding_system.stats)

            if self.inventory_manager and hasattr(self.inventory_manager, 'stats'):
                self.stats.update(self.inventory_manager.stats)

            # Callback para UI (atualizar a cada 5 segundos)
            if hasattr(self, '_last_stats_update'):
                if current_time - self._last_stats_update > 5.0:
                    if self.on_stats_update:
                        self.on_stats_update(self.stats.copy())
                    self._last_stats_update = current_time
            else:
                self._last_stats_update = current_time

        except Exception as e:
            _safe_print(f"❌ Erro ao atualizar stats: {e}")
    
    def _calculate_final_stats(self):
        """Calcular estatísticas finais da sessão"""
        try:
            total_time = time.time() - self.stats['session_start_time']
            
            _safe_print(f"📊 Estatísticas da sessão:")
            _safe_print(f"  🐟 Peixes capturados: {self.stats['fish_caught']}")
            _safe_print(f"  ⏱️ Tempo total: {total_time:.1f}s ({total_time/60:.1f}min)")
            _safe_print(f"  📈 Capturas/hora: {self.stats['catches_per_hour']:.1f}")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao calcular stats finais: {e}")
    
    # ===== SISTEMA DE PRIORIDADES (BASEADO NO BOTPESCA.PY) =====
    
    # ✅ MÉTODO REMOVIDO: process_priority_tasks()
    # Lógica de decisão agora está no SERVIDOR (server.py)
    # Cliente apenas executa comandos recebidos do servidor

    def _set_action_in_progress(self, in_progress: bool):
        """Definir flag de ação em progresso no game state"""
        try:
            if isinstance(self.game_state, dict):
                self.game_state['action_in_progress'] = in_progress
            elif hasattr(self.game_state, 'action_in_progress'):
                self.game_state.action_in_progress = in_progress
        except Exception as e:
            _safe_print(f"❌ Erro ao definir action_in_progress: {e}")

    def _will_open_chest_next_cycle(self) -> bool:
        """
        🔍 Verificar se o próximo ciclo vai abrir o baú

        ✅ ARQUITETURA SERVIDOR:
        - Se conectado: aguarda comandos do servidor (2s)
        - Se offline: retorna False (sem lógica local)

        Servidor decide TUDO via comandos enfileirados:
        - feed → callback abre baú
        - clean → callback abre baú
        - switch_rod_pair → callback abre baú

        Returns:
            bool: True se servidor enviou comandos
        """
        try:
            # Se conectado ao servidor, aguardar comandos
            if self.ws_client and self.ws_client.is_connected():
                _safe_print("🌐 [SERVER] Aguardando comandos do servidor (2s)...")
                time.sleep(2.0)

                # Verificar se tem comandos na fila
                with self.command_lock:
                    has_commands = len(self.pending_server_commands) > 0
                    if has_commands:
                        _safe_print(f"📋 [SERVER] {len(self.pending_server_commands)} comando(s) recebido(s)")
                    return has_commands

            # Se offline, não abre baú (sem lógica local)
            _safe_print("💻 [LOCAL] Modo offline - sem operações de baú")
            return False

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar operações pendentes: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_pending_commands(self):
        """
        Transferir comandos do servidor para o ChestOperationCoordinator

        ✅ ARQUITETURA CONSOLIDADA:
        - Comandos são transferidos para o coordinator
        - Coordinator agrupa operações em janela de 2 segundos
        - Uma única sessão de baú para múltiplas operações
        - Manutenção oportunística executada automaticamente
        - Notificações ao servidor enviadas pelo coordinator
        """
        _safe_print("\n📋 [TRANSFER] Transferindo comandos para ChestCoordinator...")

        if not self.chest_coordinator:
            _safe_print("❌ ChestCoordinator não disponível - executando diretamente")
            # Fallback: executar diretamente (modo offline)
            self._execute_commands_directly()
            return

        # Importar funções trigger
        from .chest_operation_coordinator import trigger_feeding_operation, trigger_cleaning_operation, TriggerReason

        with self.command_lock:
            commands_count = len(self.pending_server_commands)
            _safe_print(f"   📊 {commands_count} comando(s) a transferir")

            while self.pending_server_commands:
                cmd, params = self.pending_server_commands.pop(0)
                _safe_print(f"   ➡️  Transferindo: {cmd}")

                try:
                    if cmd == 'feed':
                        # Adicionar feeding ao coordinator
                        success = trigger_feeding_operation(
                            self.chest_coordinator,
                            TriggerReason.FEEDING_SCHEDULE
                        )
                        if success:
                            _safe_print("      ✅ Feeding adicionado à fila do coordinator")
                        else:
                            _safe_print("      ⚠️ Feeding já está na fila (duplicata ignorada)")

                    elif cmd == 'clean':
                        # Adicionar cleaning ao coordinator
                        success = trigger_cleaning_operation(
                            self.chest_coordinator,
                            TriggerReason.INVENTORY_FULL
                        )
                        if success:
                            _safe_print("      ✅ Cleaning adicionado à fila do coordinator")
                        else:
                            _safe_print("      ⚠️ Cleaning já está na fila (duplicata ignorada)")

                    elif cmd == 'switch_rod_pair':
                        # Sinalizar troca de par para coordinator
                        target_rod = params.get('target_rod')
                        if target_rod and self.chest_coordinator:
                            self.chest_coordinator.rod_to_equip_after_pair_switch = target_rod
                            _safe_print(f"      ✅ Troca de par sinalizada: vara {target_rod}")

                    elif cmd == 'break':
                        # Pausas são executadas diretamente (não dependem de baú)
                        duration = params.get('duration', 2700)
                        _safe_print(f"      ⏸️ Pausando por {duration}s...")
                        self.pause()
                        time.sleep(duration)
                        self.resume()
                        _safe_print("      ▶️ Retomando operação")

                except Exception as e:
                    _safe_print(f"      ❌ Erro ao transferir {cmd}: {e}")
                    import traceback
                    traceback.print_exc()

        _safe_print(f"✅ [TRANSFER] {commands_count} comando(s) transferido(s)")
        _safe_print("⏱️  Coordinator agrupará operações em janela de 2s\n")

    def _execute_commands_directly(self):
        """
        Fallback: Executar comandos diretamente sem coordinator (modo offline)
        Usado apenas quando chest_coordinator não está disponível
        """
        _safe_print("\n🚀 [EXEC DIRECT] Executando comandos diretamente (sem coordinator)...")

        with self.command_lock:
            while self.pending_server_commands:
                cmd, params = self.pending_server_commands.pop(0)
                _safe_print(f"   📤 Executando: {cmd}")

                try:
                    if cmd == 'feed':
                        if self.feeding_system:
                            success = self.feeding_system.execute_feeding(force=True)
                            if success and self.ws_client:
                                self.ws_client.send_feeding_done()

                    elif cmd == 'clean':
                        if self.inventory_manager:
                            success = self.inventory_manager.execute_cleaning()
                            if success and self.ws_client:
                                self.ws_client.send_cleaning_done()

                    elif cmd == 'switch_rod_pair':
                        target_rod = params.get('target_rod')
                        if self.rod_manager and target_rod:
                            self.rod_manager.equip_rod(target_rod)

                    elif cmd == 'break':
                        duration = params.get('duration', 2700)
                        self.pause()
                        time.sleep(duration)
                        self.resume()

                except Exception as e:
                    _safe_print(f"   ❌ Erro: {e}")

        _safe_print("✅ [EXEC DIRECT] Comandos executados\n")

    def increment_fish_count(self):
        """
        Incrementar contador de peixes e enviar evento ao servidor

        ✅ ARQUITETURA DISTRIBUÍDA:
        - Cliente detecta peixe e ENVIA dados ao servidor
        - Servidor DECIDE se precisa alimentar/limpar/trocar vara
        - Servidor ENVIA comandos de volta
        """
        try:
            # ✅ OBTER dados da vara atual para enviar ao servidor
            current_rod = 1  # Default
            rod_uses = 0     # Default

            if self.rod_manager:
                try:
                    current_rod = self.rod_manager.get_current_rod()
                    rod_uses = self.rod_manager.rod_uses.get(current_rod, 0)
                except Exception as e:
                    _safe_print(f"⚠️ Erro ao obter dados da vara: {e}")

            # ✅ ENVIAR fish_caught para servidor
            if self.ws_client and self.ws_client.is_connected():
                # MODO ONLINE: Servidor controla feeding/cleaning/maintenance
                self.ws_client.send_fish_caught(rod_uses=rod_uses, current_rod=current_rod)
                _safe_print(f"🌐 [ENGINE→WS] fish_caught enviado (vara {current_rod}: {rod_uses} usos)")
                logger.info(f"🌐 Evento fish_caught enviado (vara {current_rod}: {rod_uses} usos)")
            else:
                # MODO OFFLINE (HÍBRIDO):
                # ✅ Pesca FUNCIONA localmente (cliques, A/D, detecção)
                # ✅ Troca de varas FUNCIONA localmente
                # ❌ Feeding/Cleaning/Maintenance são MANUAIS (hotkeys: F6, F5, Page Down)
                _safe_print(f"📊 [OFFLINE] Peixe #{self.stats['fish_caught']} capturado")
                _safe_print("   ℹ️ Servidor offline - Operações de baú são MANUAIS (F6=feed, F5=clean, PgDn=manutenção)")
                logger.info(f"Peixe capturado em modo offline (vara {current_rod})")

        except Exception as e:
            _safe_print(f"❌ Erro ao processar fish_caught: {e}")
            logger.error(f"Erro ao processar fish_caught: {e}", exc_info=True)
    
    # ===== MÉTODOS DE TRIGGER MANUAL (PARA HOTKEYS) =====
    
    def trigger_feeding(self) -> bool:
        """Trigger manual de alimentação (F6) - usa coordenador para agrupamento"""
        try:
            _safe_print("🔧 [F6] Trigger manual de alimentação ativado")

            if self.chest_coordinator and self.feeding_system:
                # Usar coordenador para permitir agrupamento
                from .chest_operation_coordinator import trigger_feeding_operation, TriggerReason
                success = trigger_feeding_operation(self.chest_coordinator, TriggerReason.MANUAL)

                if success:
                    _safe_print("✅ [F6] Alimentação adicionada à fila do coordenador")
                    return True
                else:
                    _safe_print("❌ [F6] Falha ao adicionar alimentação à fila")
                    return False

            elif self.feeding_system:
                # Fallback: execução direta sem coordenador
                _safe_print("🔧 [F6] Executando alimentação diretamente (sem coordenador)")
                return self.feeding_system.manual_trigger()
            else:
                _safe_print("⚠️ [F6] Sistema de alimentação não disponível")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro no trigger de alimentação: {e}")
            return False
    
    def trigger_cleaning(self) -> bool:
        """Trigger manual de limpeza (F5) - usa coordenador para agrupamento"""
        try:
            _safe_print("🔧 [F5] Trigger manual de limpeza ativado")

            if self.chest_coordinator and self.inventory_manager:
                # Usar coordenador para permitir agrupamento (igual ao F6)
                from .chest_operation_coordinator import trigger_cleaning_operation, TriggerReason
                success = trigger_cleaning_operation(self.chest_coordinator, TriggerReason.MANUAL)

                if success:
                    _safe_print("✅ [F5] Limpeza adicionada à fila do coordenador")
                    return True
                else:
                    _safe_print("❌ [F5] Falha ao adicionar limpeza à fila")
                    return False

            elif self.inventory_manager:
                # Fallback: execução direta sem coordenador
                _safe_print("⚠️ [F5] Coordenador não disponível - execução direta")
                return self.inventory_manager.manual_trigger()
            else:
                _safe_print("⚠️ [F5] InventoryManager não disponível")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro no trigger de limpeza: {e}")
            return False

    # ===== CALLBACKS DE SINCRONIZAÇÃO =====

    def _on_batch_complete(self):
        """
        ✅ NOVO: Callback chamado quando ChestOperationCoordinator termina todas as operações

        Fluxo de sincronização:
        1. ChestCoordinator executa feeding/cleaning/maintenance
        2. ChestCoordinator fecha baú
        3. ChestCoordinator chama este callback
        4. Executar switch_rod pendente (APENAS se NÃO houve operações de baú!)
        5. Resetar flag waiting_for_batch_completion
        6. Retornar ao estado FISHING

        Isso garante que o cliente NÃO volta a pescar enquanto baú está aberto!
        """
        _safe_print("\n" + "="*80)
        _safe_print("🔔 [CALLBACK] Batch completado - processando finalização...")
        _safe_print("="*80)

        try:
            # PASSO 1: Executar switch_rod pendente (APENAS se NÃO houve operações de baú!)
            if self.pending_switch_rod_callback:
                if self.had_chest_operations:
                    _safe_print("🔄 [PASSO 1] switch_rod pendente detectado")
                    _safe_print("   ⚠️ MAS houve operações de baú - ChestCoordinator JÁ escolheu a vara correta!")
                    _safe_print("   ❌ NÃO executar switch_rod - vara já foi equipada pelo ChestCoordinator")
                    _safe_print("   🎯 Mantendo vara escolhida pelo ChestCoordinator (baseado em usos)")
                else:
                    _safe_print("🔄 [PASSO 1] Executando switch_rod pendente...")
                    _safe_print("   ℹ️ SEM operações de baú - switch_rod deve ser executado")
                    try:
                        success = self.pending_switch_rod_callback()
                        if success:
                            _safe_print("   ✅ Switch rod executado com sucesso")
                        else:
                            _safe_print("   ⚠️ Switch rod falhou ou não necessário")
                    except Exception as e:
                        _safe_print(f"   ❌ Erro ao executar switch_rod: {e}")

                # Limpar callback e flag após processar
                self.pending_switch_rod_callback = None
                self.had_chest_operations = False
            else:
                _safe_print("ℹ️ [PASSO 1] Nenhum switch_rod pendente")
                self.had_chest_operations = False  # Limpar flag mesmo sem switch_rod

            # PASSO 2: Resetar flag de espera
            _safe_print("🔓 [PASSO 2] Resetando flag waiting_for_batch_completion...")
            self.waiting_for_batch_completion = False
            _safe_print(f"   🔍 DEBUG: waiting_for_batch_completion = {self.waiting_for_batch_completion}")
            _safe_print(f"   🔍 DEBUG: stop_event.is_set() = {self.stop_event.is_set()}")
            _safe_print(f"   🔍 DEBUG: is_paused = {self.is_paused}")

            # PASSO 3: Retornar ao estado FISHING
            _safe_print("🎣 [PASSO 3] Retornando ao estado FISHING...")
            self.change_state(FishingState.FISHING)
            _safe_print(f"   🔍 DEBUG: Estado atual = {self.state}")

            _safe_print("✅ Sincronização completa - cliente pode pescar novamente!")
            _safe_print("🔔 [WAKE UP] Loop principal deve retomar pesca na próxima iteração...")
            _safe_print("="*80 + "\n")

        except Exception as e:
            _safe_print(f"❌ Erro no callback de conclusão: {e}")
            _safe_print("🔓 Resetando flag de emergência...")
            self.waiting_for_batch_completion = False
            self.had_chest_operations = False

    # ===== HANDLERS DE COMANDOS DO SERVIDOR =====

    def handle_server_command(self, command: dict):
        """
        ✅ NOVO: Handler para comandos do servidor

        Processa comandos recebidos via WebSocket:
        - execute_batch: NOVA ARQUITETURA - Executar batch de operações coordenadas
        - request_template_detection: DEPRECATED - Detectar templates e enviar coordenadas
        - request_inventory_scan: DEPRECATED - Escanear inventário e enviar peixes
        - request_rod_analysis: DEPRECATED - Analisar varas e enviar status
        - execute_sequence: DEPRECATED - Executar sequência de ações

        Args:
            command: Dicionário com comando do servidor
        """
        try:
            cmd = command.get("cmd")

            if not cmd:
                _safe_print("⚠️ Comando sem tipo (cmd)")
                return

            # ═════════════════════════════════════════════════════════════
            # ✅ NOVA ARQUITETURA: Execute Batch (v5 antigo style)
            # Servidor envia batch → Cliente adiciona operações à fila do ChestOperationCoordinator
            # ChestOperationCoordinator usa timer de 2s e executa tudo coordenado!
            # ═════════════════════════════════════════════════════════════
            if cmd == "execute_batch":
                operations = command.get("operations", [])

                _safe_print(f"\n🏪 [SERVER→CLIENT] BATCH RECEBIDO: {len(operations)} operação(ões)")
                _safe_print(f"🏪 Operações: {[op['type'] for op in operations]}")

                if not self.chest_coordinator:
                    _safe_print("❌ ChestOperationCoordinator não disponível")
                    if self.ws_client:
                        self.ws_client.send({
                            "event": "batch_failed",
                            "data": {
                                "operation": "batch",
                                "error": "ChestOperationCoordinator não disponível"
                            }
                        })
                    return

                # Importar enums do ChestOperationCoordinator
                try:
                    from chest_operation_coordinator import OperationType, TriggerReason
                except:
                    from .chest_operation_coordinator import OperationType, TriggerReason

                # ✅ SINCRONIZAÇÃO: Marcar flag para aguardar batch completar
                _safe_print("🔒 [SYNC] Marcando waiting_for_batch_completion = True")
                self.waiting_for_batch_completion = True

                # ✅ SEPARAR: switch_rod das operações de baú
                # switch_rod NÃO precisa de baú aberto - executar DEPOIS que baú fechar
                # switch_rod_pair PRECISA de baú aberto - vai para ChestOperationCoordinator
                chest_operations = []
                switch_rod_op = None
                switch_rod_pair_op = None

                for op in operations:
                    op_type_str = op.get("type")

                    if op_type_str == "switch_rod":
                        _safe_print(f"🔄 switch_rod detectado - será executado APÓS fechar baú")
                        switch_rod_op = op
                    elif op_type_str == "switch_rod_pair":
                        _safe_print(f"🔄 switch_rod_pair detectado - PRECISA abrir baú!")
                        switch_rod_pair_op = op
                        chest_operations.append(op)  # Adicionar às operações de baú
                    else:
                        chest_operations.append(op)

                # PASSO 1: Adicionar operações de baú ao ChestOperationCoordinator
                operations_added = 0
                for op in chest_operations:
                    op_type_str = op.get("type")

                    # Mapear string do servidor para callback apropriado
                    if op_type_str == "feeding":
                        operation_type = OperationType.FEEDING
                        # ✅ CORRETO: execute_feeding com chest_already_open=True
                        callback = (lambda: self.feeding_system.execute_feeding(chest_already_open=True)) if self.feeding_system else (lambda: False)
                    elif op_type_str == "cleaning":
                        operation_type = OperationType.CLEANING
                        # ✅ CORRETO: execute_auto_clean com chest_managed_externally=True
                        callback = (lambda: self.inventory_manager.execute_auto_clean(chest_managed_externally=True)) if self.inventory_manager else (lambda: False)
                    elif op_type_str == "maintenance":
                        operation_type = OperationType.MAINTENANCE
                        # ✅ CORRETO: execute_full_maintenance com chest_already_open=True
                        callback = (lambda: self.rod_manager.execute_full_maintenance(chest_already_open=True)) if self.rod_manager else (lambda: False)
                    elif op_type_str == "switch_rod_pair":
                        # ✅ NOVO: Troca de par (precisa baú aberto)
                        # Extrair vara do novo par dos params
                        target_rod = op.get("params", {}).get("target_rod")
                        if target_rod and self.rod_manager:
                            _safe_print(f"🔄 switch_rod_pair → equipar vara {target_rod} do novo par")

                            # Calcular índice do novo par baseado na vara alvo
                            new_pair_index = None
                            for idx, pair in enumerate(self.rod_manager.rod_pairs):
                                if target_rod in pair:
                                    new_pair_index = idx
                                    break

                            if new_pair_index is not None:
                                _safe_print(f"   📊 Novo par calculado: índice {new_pair_index} = {self.rod_manager.rod_pairs[new_pair_index]}")

                                # ✅ CRÍTICO: Setar pending_pair_switch_data no RodManager
                                self.rod_manager.pending_pair_switch_data = {
                                    'new_pair_index': new_pair_index,
                                    'first_rod': target_rod
                                }
                                _safe_print(f"   ✅ pending_pair_switch_data setado no RodManager")

                                # Informar ChestCoordinator qual vara equipar após fechar baú
                                if self.chest_coordinator:
                                    self.chest_coordinator.rod_to_equip_after_pair_switch = target_rod
                            else:
                                _safe_print(f"   ❌ ERRO: Vara {target_rod} não encontrada em nenhum par!")
                        # switch_rod_pair não precisa de callback (ChestCoordinator já vai equipar vara)
                        continue  # Pular add_operation (não é operação executável)
                    else:
                        _safe_print(f"⚠️ Tipo de operação desconhecido: {op_type_str}")
                        continue

                    # Adicionar à fila (trigger reason = FEEDING_SCHEDULE pois vem do servidor)
                    self.chest_coordinator.add_operation(
                        operation_type=operation_type,
                        trigger_reason=TriggerReason.FEEDING_SCHEDULE,  # Ou poderia ser SERVER_COMMAND
                        callback=callback,
                        context=f"Servidor solicitou {op_type_str}"
                    )
                    _safe_print(f"➕ {op_type_str} adicionado à fila do ChestOperationCoordinator")
                    operations_added += 1

                # PASSO 2: Armazenar switch_rod para executar DEPOIS
                if switch_rod_op:
                    _safe_print("💾 Armazenando callback de switch_rod para executar após fechar baú...")
                    will_open_chest = switch_rod_op.get("params", {}).get("will_open_chest", False)
                    self.pending_switch_rod_callback = (lambda: self.rod_manager.switch_rod(will_open_chest=will_open_chest)) if self.rod_manager else (lambda: False)

                # ✅ MARCAR: Se houve operações de baú (para decisão em _on_batch_complete)
                self.had_chest_operations = (operations_added > 0)
                if self.had_chest_operations:
                    _safe_print(f"🏪 [FLAG] had_chest_operations = True ({operations_added} operações de baú)")
                else:
                    _safe_print(f"🏪 [FLAG] had_chest_operations = False (sem operações de baú)")

                # ✅ EDGE CASE: Se NÃO há operações de baú, executar switch_rod imediatamente
                if operations_added == 0 and switch_rod_op:
                    _safe_print("\n⚡ [EDGE CASE] Apenas switch_rod no batch - executando imediatamente!")
                    self._on_batch_complete()  # Executa switch_rod e volta ao FISHING
                elif operations_added > 0:
                    _safe_print(f"✅ Batch processado: {operations_added} operações de baú + {1 if switch_rod_op else 0} switch_rod")
                    if switch_rod_op:
                        _safe_print("   ⚠️ IMPORTANTE: switch_rod NÃO será executado (ChestCoordinator escolhe vara)")
                    _safe_print(f"🔔 ChestCoordinator vai executar em 2s e chamar _on_batch_complete!")
                    # ChestOperationCoordinator vai executar operações e chamar _on_batch_complete quando terminar
                else:
                    _safe_print("\n⚠️ [EDGE CASE] Batch vazio - nada para executar")
                    _safe_print("🔓 Resetando flag e voltando ao FISHING...")
                    self.waiting_for_batch_completion = False
                    self.change_state(FishingState.FISHING)

                return  # Early return para evitar executar handlers antigos

            # ═════════════════════════════════════════════════════════════
            # ⚠️ DEPRECATED: Handlers antigos (manter por compatibilidade)
            # ═════════════════════════════════════════════════════════════

            # ─────────────────────────────────────────────────
            # 1. Request Template Detection (Feeding) - DEPRECATED
            # ─────────────────────────────────────────────────
            if cmd == "request_template_detection":
                _safe_print("⚠️ DEPRECATED: request_template_detection - Use execute_batch")
                templates = command.get("templates", [])
                _safe_print(f"🔍 [SERVER→CLIENT] Solicitação de detecção: {templates}")

                if not self.detection_handler:
                    _safe_print("❌ DetectionHandler não disponível")
                    return

                # Detectar comida e botão eat
                if "filefrito" in templates and "eat" in templates:
                    result = self.detection_handler.detect_food_and_eat()

                    if result and self.ws_client:
                        # Enviar coordenadas detectadas ao servidor
                        self.ws_client.send_feeding_locations_detected(
                            result["food_location"],
                            result["eat_location"]
                        )
                    elif not result:
                        _safe_print("❌ Comida ou botão eat não detectado")

            # ─────────────────────────────────────────────────
            # 2. Request Inventory Scan (Cleaning)
            # ─────────────────────────────────────────────────
            elif cmd == "request_inventory_scan":
                _safe_print("🔍 [SERVER→CLIENT] Solicitação de scan de inventário")

                if not self.detection_handler:
                    _safe_print("❌ DetectionHandler não disponível")
                    return

                result = self.detection_handler.scan_inventory()

                if result and self.ws_client:
                    # Enviar lista de peixes ao servidor
                    self.ws_client.send_fish_locations_detected(
                        result["fish_locations"]
                    )
                elif not result:
                    _safe_print("❌ Nenhum peixe detectado no inventário")

            # ─────────────────────────────────────────────────
            # 3. Request Rod Analysis (Maintenance)
            # ─────────────────────────────────────────────────
            elif cmd == "request_rod_analysis":
                _safe_print("🔍 [SERVER→CLIENT] Solicitação de análise de varas")

                if not self.detection_handler:
                    _safe_print("❌ DetectionHandler não disponível")
                    return

                result = self.detection_handler.analyze_rod_slots()

                if result and self.ws_client:
                    # Enviar status das varas ao servidor
                    self.ws_client.send_rod_status_detected(
                        result["rod_status"],
                        result["available_items"]
                    )

            # ─────────────────────────────────────────────────
            # 4. Execute Sequence (Executar sequência do servidor)
            # ─────────────────────────────────────────────────
            elif cmd == "execute_sequence":
                actions = command.get("actions", [])
                operation = command.get("operation", "unknown")

                _safe_print(f"⚡ [SERVER→CLIENT] Executando sequência: {operation} ({len(actions)} ações)")

                if not self.action_executor:
                    _safe_print("❌ ActionExecutor não disponível")
                    if self.ws_client:
                        self.ws_client.send_sequence_failed(operation, 0, "ActionExecutor não disponível")
                    return

                # Executar sequência
                success = self.action_executor.execute_sequence(actions)

                if success:
                    _safe_print(f"✅ Sequência {operation} concluída")
                    if self.ws_client:
                        self.ws_client.send_sequence_completed(operation)
                else:
                    _safe_print(f"❌ Sequência {operation} falhou")
                    if self.ws_client:
                        self.ws_client.send_sequence_failed(operation, -1, "Falha na execução")

            # ─────────────────────────────────────────────────
            # Comandos antigos (manter por compatibilidade)
            # ─────────────────────────────────────────────────
            else:
                _safe_print(f"⚠️ Comando desconhecido: {cmd}")

        except Exception as e:
            _safe_print(f"❌ Erro ao processar comando do servidor: {e}")
            import traceback
            traceback.print_exc()
    
    def trigger_rod_switch(self) -> bool:
        """Trigger manual de troca de vara (TAB) - APENAS TROCA, SEM OUTRAS AÇÕES"""
        try:
            if self.rod_manager:
                _safe_print("🔧 [MANUAL] Trigger de troca de vara ativado")
                
                # Flag para indicar que é uma troca manual
                self._manual_rod_switch = True
                
                # Chamar método de troca manual (apenas troca, sem outros triggers)
                success = self.rod_manager.manual_rod_switch()
                
                # Resetar flag
                self._manual_rod_switch = False
                
                return success
            else:
                _safe_print("⚠️ [MANUAL] RodManager não disponível")
                return False
        except Exception as e:
            _safe_print(f"❌ Erro no trigger de troca de vara: {e}")
            self._manual_rod_switch = False
            return False

    def trigger_rod_maintenance(self) -> bool:
        """
        🔧 Sistema Completo de Manutenção de Varas - TECLA PAGE DOWN

        NOVO: Usa ChestOperationCoordinator como F5 e F6
        """
        try:
            if self.chest_coordinator and self.rod_manager:
                _safe_print("🔧 [PAGE DOWN] SISTEMA DE MANUTENÇÃO COORDENADA ATIVADO")

                # Usar chest coordinator como F5 (limpeza) e F6 (alimentação)
                from .chest_operation_coordinator import trigger_maintenance_operation, TriggerReason
                success = trigger_maintenance_operation(self.chest_coordinator, TriggerReason.MANUAL)

                if success:
                    _safe_print("✅ [PAGE DOWN] Manutenção coordenada executada com sucesso!")

                    # Atualizar estatísticas se disponível
                    if hasattr(self, 'stats'):
                        self.stats['maintenance_executions'] = self.stats.get('maintenance_executions', 0) + 1

                    return True
                else:
                    _safe_print("❌ [PAGE DOWN] Falha na manutenção coordenada")
                    return False
            else:
                _safe_print("⚠️ [PAGE DOWN] RodManager não disponível")
                return False

        except Exception as e:
            _safe_print(f"❌ [PAGE DOWN] Erro no sistema de manutenção: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ===== SISTEMA DE PAUSAS NATURAIS (ANTI-DETECÇÃO) =====

    def _should_execute_natural_break(self) -> bool:
        """
        ☕ Verificar se é hora de fazer uma pausa natural (baseado no v3)

        Melhoria vs v3: Respeita operações de baú/inventário em progresso

        Returns:
            bool: True se deve executar pausa natural
        """
        try:
            # Verificar se pausas naturais estão ativadas
            if not self.natural_breaks['enabled']:
                return False

            # Modo por tempo
            if self.natural_breaks['mode'] == 'time':
                time_since_break = time.time() - self.natural_breaks['last_break_time']
                minutes_since_break = time_since_break / 60

                if minutes_since_break >= self.natural_breaks['time_interval']:
                    _safe_print(f"⏰ [PAUSA NATURAL] Tempo decorrido: {minutes_since_break:.1f} min")
                    return True

            # Modo por capturas
            elif self.natural_breaks['mode'] == 'catches':
                if self.natural_breaks['catches_since_break'] >= self.natural_breaks['catches_interval']:
                    _safe_print(f"🐟 [PAUSA NATURAL] Peixes capturados: {self.natural_breaks['catches_since_break']}")
                    return True

            return False

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar pausa natural: {e}")
            return False

    def _is_safe_to_pause(self) -> bool:
        """
        🔒 Verificar se é seguro pausar (sem operações em andamento)

        DIFERENÇA DO V3: V3 NÃO fazia essa verificação!
        V5 verifica se há operações de baú/inventário antes de pausar

        Returns:
            bool: True se seguro para pausar
        """
        try:
            # Verificar se baú/inventário está aberto
            inventory_open = False
            chest_open = False

            if isinstance(self.game_state, dict):
                inventory_open = self.game_state.get('inventory_open', False)
                chest_open = self.game_state.get('chest_open', False)
            elif hasattr(self.game_state, 'inventory_open'):
                inventory_open = self.game_state.inventory_open
                chest_open = self.game_state.chest_open

            if inventory_open or chest_open:
                _safe_print("⏸️ [PAUSA NATURAL] Inventário/baú aberto - aguardando...")
                return False

            # Verificar se há ação em progresso
            action_in_progress = False
            if isinstance(self.game_state, dict):
                action_in_progress = self.game_state.get('action_in_progress', False)
            elif hasattr(self.game_state, 'action_in_progress'):
                action_in_progress = self.game_state.action_in_progress

            if action_in_progress:
                _safe_print("⏸️ [PAUSA NATURAL] Ação em progresso - aguardando...")
                return False

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar segurança para pausar: {e}")
            return False

    def _execute_natural_break(self):
        """
        ☕ Executar uma pausa natural (baseado no v3)

        Melhoria vs v3:
        - V3: Solta todos os inputs sem verificar estado
        - V5: Verifica segurança antes de soltar inputs

        Processo:
        1. Calcular duração aleatória da pausa
        2. Soltar todos os inputs
        3. Executar pausa
        4. Atualizar contadores
        """
        try:
            import random

            # Calcular duração da pausa (aleatória)
            pause_duration = random.uniform(
                self.natural_breaks['pause_duration_min'],
                self.natural_breaks['pause_duration_max']
            )

            _safe_print(f"\n☕ PAUSA NATURAL - Simulando comportamento humano...")
            _safe_print(f"   • Duração: {pause_duration:.1f} segundos ({pause_duration/60:.1f} minutos)")
            _safe_print(f"   • Modo: {self.natural_breaks['mode']}")

            # Soltar todos os botões antes da pausa
            if self.input_manager:
                try:
                    self.input_manager.emergency_stop()
                    _safe_print("   • Todos os inputs foram soltos")
                except Exception as e:
                    _safe_print(f"⚠️ Erro ao soltar inputs: {e}")

            # Executar a pausa
            start_time = time.time()
            while time.time() - start_time < pause_duration and self.is_running:
                if self.stop_event.is_set():
                    _safe_print("   ⚠️ Pausa natural interrompida (stop_event)")
                    break
                time.sleep(0.5)

            # Atualizar contadores
            self.natural_breaks['last_break_time'] = time.time()
            self.natural_breaks['catches_since_break'] = 0

            _safe_print("   ✅ Pausa natural concluída, retomando pesca...")

        except Exception as e:
            _safe_print(f"❌ Erro ao executar pausa natural: {e}")

    def _validate_dependencies(self) -> bool:
        """Validar se todas as dependências estão disponíveis"""
        try:
            # Verificar template engine
            if not self.template_engine:
                _safe_print("❌ TemplateEngine não disponível")
                return False
            
            # Verificar se template catch.png existe
            if not self.template_engine.has_template('catch'):
                _safe_print("❌ Template 'catch.png' não encontrado")
                return False
            
            # Verificar GameState se disponível
            if self.game_state:
                can_fish, reason = self.game_state.can_start_fishing()
                if not can_fish:
                    _safe_print(f"⚠️ GameState: {reason}")
                    # Não bloquear por enquanto, apenas avisar
            
            _safe_print("✅ Dependências validadas")
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro na validação: {e}")
            return False
    
    def change_state(self, new_state: FishingState):
        """Alterar estado e notificar observers"""
        old_state = self.state
        self.state = new_state
        
        _safe_print(f"🔄 Estado: {old_state.value} → {new_state.value}")
        
        # Callback para UI
        if self.on_state_change:
            self.on_state_change(old_state, new_state)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas atuais"""
        return self.stats.copy()
    
    def get_state(self) -> FishingState:
        """Obter estado atual"""
        return self.state
    
    def is_active(self) -> bool:
        """Verificar se o sistema está ativo"""
        return self.is_running and not self.is_paused
    
    def set_callbacks(self, **callbacks):
        """Configurar callbacks para UI"""
        self.on_state_change = callbacks.get('on_state_change')
        self.on_fish_caught = callbacks.get('on_fish_caught') 
        self.on_error = callbacks.get('on_error')
        self.on_stats_update = callbacks.get('on_stats_update')
        
        _safe_print("✅ Callbacks configurados para UI")