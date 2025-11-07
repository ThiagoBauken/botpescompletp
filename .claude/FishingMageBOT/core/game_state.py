#!/usr/bin/env python3
"""
🎮 GameState - Gerenciamento de Estado Global do Jogo
Ultimate Fishing Bot v4.0

Extrai e consolida o gerenciamento de estado do botpesca.py
"""

import threading
import time
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class GameMode(Enum):
    """Modos de operação do jogo"""
    IDLE = "idle"
    FISHING = "fishing"
    INVENTORY_OPEN = "inventory_open"
    CHEST_OPEN = "chest_open"
    FEEDING = "feeding"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class RodState(Enum):
    """Estados das varas"""
    EMPTY = "empty"              # Vazia (sem isca)
    WITH_BAIT = "with_bait"      # Com isca
    BROKEN = "broken"            # Quebrada
    UNKNOWN = "unknown"          # Estado desconhecido

@dataclass
class RodInfo:
    """Informações de uma vara"""
    slot: int
    state: RodState = RodState.UNKNOWN
    uses_remaining: int = 0
    bait_type: str = ""
    last_check: float = 0.0

@dataclass
class InventoryState:
    """Estado do inventário"""
    is_open: bool = False
    selected_slot: int = 1
    last_update: float = 0.0
    items_count: Dict[str, int] = field(default_factory=dict)

@dataclass
class SessionStats:
    """Estatísticas da sessão"""
    fish_caught: int = 0
    session_start: float = 0.0
    last_catch_time: float = 0.0
    feeding_count: int = 0
    rod_breaks: int = 0
    chest_openings: int = 0
    total_actions: int = 0

class GameState:
    """
    🎮 Gerenciador de Estado Global do Jogo
    
    Responsabilidades:
    - Rastrear estado atual do jogo
    - Gerenciar informações das varas
    - Controlar estado do inventário/chest
    - Manter estatísticas da sessão
    - Coordenar ações entre sistemas
    """
    
    def __init__(self, config_manager=None):
        """Inicializar GameState"""
        self.config_manager = config_manager
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Estado principal
        self.current_mode = GameMode.IDLE
        self.previous_mode = GameMode.IDLE
        
        # Estados de interface
        self.inventory = InventoryState()
        self.chest_open = False
        self.feeding_active = False
        
        # Sistema de varas (6 varas em 3 pares)
        self.rods: Dict[int, RodInfo] = {}
        self.current_rod_pair = 0  # Par atual (0=slots 1-2, 1=slots 3-4, 2=slots 5-6)
        self.active_rod = 1        # Vara ativa no par
        
        # Estatísticas
        self.stats = SessionStats(session_start=time.time())
        
        # Callbacks para notificação de mudanças
        self.state_change_callbacks: List[Callable] = []
        self.rod_change_callbacks: List[Callable] = []
        
        # Inicializar sistema
        self._initialize_rods()
        
        _safe_print("🎮 GameState inicializado")
    
    def _initialize_rods(self):
        """Inicializar sistema de varas"""
        try:
            # Configurar 6 varas
            for slot in range(1, 7):
                self.rods[slot] = RodInfo(slot=slot)
            
            # Configurar pares de varas do config
            if self.config_manager:
                rod_config = self.config_manager.get_rod_config()
                initial_uses = rod_config.get('initial_uses', 20)
                
                # Definir usos iniciais
                for rod in self.rods.values():
                    rod.uses_remaining = initial_uses
            
            _safe_print(f"🎣 Sistema de varas inicializado: {len(self.rods)} varas")
            
        except Exception as e:
            _safe_print(f"❌ Erro ao inicializar varas: {e}")
    
    # ===== GESTÃO DE ESTADO PRINCIPAL =====
    
    def change_mode(self, new_mode: GameMode, context: str = ""):
        """Alterar modo de operação"""
        with self._lock:
            old_mode = self.current_mode
            self.previous_mode = old_mode
            self.current_mode = new_mode
            
            _safe_print(f"🔄 Modo: {old_mode.value} → {new_mode.value}" + 
                  (f" ({context})" if context else ""))
            
            # Notificar callbacks
            self._notify_state_change(old_mode, new_mode, context)
    
    def get_current_mode(self) -> GameMode:
        """Obter modo atual"""
        with self._lock:
            return self.current_mode
    
    def is_mode(self, mode: GameMode) -> bool:
        """Verificar se está em modo específico"""
        with self._lock:
            return self.current_mode == mode
    
    def can_perform_action(self, action: str) -> bool:
        """Verificar se pode executar ação no estado atual"""
        with self._lock:
            # Regras de bloqueio por modo
            blocked_modes = {
                'fishing': [GameMode.INVENTORY_OPEN, GameMode.CHEST_OPEN, GameMode.FEEDING],
                'inventory': [GameMode.CHEST_OPEN, GameMode.FEEDING],
                'chest': [GameMode.INVENTORY_OPEN, GameMode.FEEDING],
                'feeding': [GameMode.CHEST_OPEN, GameMode.INVENTORY_OPEN],
                'maintenance': [GameMode.FISHING]
            }
            
            if action in blocked_modes:
                return self.current_mode not in blocked_modes[action]
            
            return True
    
    # ===== GESTÃO DE VARAS =====
    
    def update_rod_state(self, slot: int, state: RodState, bait_type: str = "", uses: int = -1):
        """Atualizar estado de uma vara"""
        with self._lock:
            if slot not in self.rods:
                _safe_print(f"⚠️ Slot {slot} inválido")
                return False
            
            rod = self.rods[slot]
            old_state = rod.state
            
            rod.state = state
            rod.last_check = time.time()
            
            if bait_type:
                rod.bait_type = bait_type
            
            if uses >= 0:
                rod.uses_remaining = uses
            
            _safe_print(f"🎣 Vara {slot}: {old_state.value} → {state.value}" + 
                  (f" ({bait_type})" if bait_type else ""))
            
            # Notificar callbacks
            self._notify_rod_change(slot, old_state, state)
            
            return True
    
    def get_rod_state(self, slot: int) -> Optional[RodInfo]:
        """Obter estado de uma vara"""
        with self._lock:
            return self.rods.get(slot)
    
    def get_active_rod_pair(self) -> tuple:
        """Obter par de varas ativo"""
        with self._lock:
            pairs = [(1, 2), (3, 4), (5, 6)]
            return pairs[self.current_rod_pair]
    
    def switch_rod_pair(self) -> bool:
        """Alternar para próximo par de varas"""
        with self._lock:
            old_pair = self.current_rod_pair
            self.current_rod_pair = (self.current_rod_pair + 1) % 3
            
            new_pair = self.get_active_rod_pair()
            _safe_print(f"🔄 Par de varas: {old_pair} → {self.current_rod_pair} (slots {new_pair})")
            
            # Resetar vara ativa no par
            self.active_rod = new_pair[0]
            
            return True
    
    def get_rods_with_bait(self) -> List[int]:
        """Obter lista de varas com isca"""
        with self._lock:
            return [slot for slot, rod in self.rods.items() 
                   if rod.state == RodState.WITH_BAIT and rod.uses_remaining > 0]
    
    def get_broken_rods(self) -> List[int]:
        """Obter lista de varas quebradas"""
        with self._lock:
            return [slot for slot, rod in self.rods.items() 
                   if rod.state == RodState.BROKEN]
    
    def use_rod(self, slot: int) -> bool:
        """Usar vara (decrementar usos)"""
        with self._lock:
            if slot not in self.rods:
                return False
            
            rod = self.rods[slot]
            if rod.uses_remaining > 0:
                rod.uses_remaining -= 1
                
                # Se acabaram os usos, marcar como vazia
                if rod.uses_remaining == 0:
                    rod.state = RodState.EMPTY
                    rod.bait_type = ""
                    _safe_print(f"🎣 Vara {slot} sem usos restantes")
                
                return True
            
            return False
    
    # ===== GESTÃO DE INVENTÁRIO =====
    
    def set_inventory_open(self, is_open: bool):
        """Definir estado do inventário"""
        with self._lock:
            old_state = self.inventory.is_open
            self.inventory.is_open = is_open
            self.inventory.last_update = time.time()
            
            if old_state != is_open:
                _safe_print(f"🎒 Inventário: {'Aberto' if is_open else 'Fechado'}")
                
                # Atualizar modo se necessário
                if is_open:
                    self.change_mode(GameMode.INVENTORY_OPEN, "inventário aberto")
                elif self.current_mode == GameMode.INVENTORY_OPEN:
                    self.change_mode(GameMode.IDLE, "inventário fechado")
    
    def is_inventory_open(self) -> bool:
        """Verificar se inventário está aberto"""
        with self._lock:
            return self.inventory.is_open
    
    def set_selected_slot(self, slot: int):
        """Definir slot selecionado no inventário"""
        with self._lock:
            self.inventory.selected_slot = slot
            self.active_rod = slot
            _safe_print(f"🎯 Slot selecionado: {slot}")
    
    def get_selected_slot(self) -> int:
        """Obter slot selecionado"""
        with self._lock:
            return self.inventory.selected_slot
    
    # ===== GESTÃO DE CHEST =====
    
    def set_chest_open(self, is_open: bool):
        """Definir estado do chest"""
        with self._lock:
            old_state = self.chest_open
            self.chest_open = is_open
            
            if old_state != is_open:
                _safe_print(f"📦 Chest: {'Aberto' if is_open else 'Fechado'}")
                
                # Atualizar estatísticas
                if is_open:
                    self.stats.chest_openings += 1
                    self.change_mode(GameMode.CHEST_OPEN, "chest aberto")
                elif self.current_mode == GameMode.CHEST_OPEN:
                    self.change_mode(GameMode.IDLE, "chest fechado")
    
    def is_chest_open(self) -> bool:
        """Verificar se chest está aberto"""
        with self._lock:
            return self.chest_open
    
    # ===== GESTÃO DE ALIMENTAÇÃO =====
    
    def set_feeding_active(self, active: bool):
        """Definir estado de alimentação"""
        with self._lock:
            old_state = self.feeding_active
            self.feeding_active = active
            
            if old_state != active:
                _safe_print(f"🍽️ Alimentação: {'Ativa' if active else 'Inativa'}")
                
                if active:
                    self.stats.feeding_count += 1
                    self.change_mode(GameMode.FEEDING, "alimentação iniciada")
                elif self.current_mode == GameMode.FEEDING:
                    self.change_mode(GameMode.IDLE, "alimentação concluída")
    
    def is_feeding_active(self) -> bool:
        """Verificar se alimentação está ativa"""
        with self._lock:
            return self.feeding_active
    
    # ===== ESTATÍSTICAS =====
    
    def increment_fish_caught(self):
        """Incrementar contador de peixes"""
        with self._lock:
            self.stats.fish_caught += 1
            self.stats.last_catch_time = time.time()
            self.stats.total_actions += 1
            _safe_print(f"🐟 Peixe #{self.stats.fish_caught} capturado!")
    
    def increment_rod_breaks(self):
        """Incrementar contador de varas quebradas"""
        with self._lock:
            self.stats.rod_breaks += 1
            self.stats.total_actions += 1
            _safe_print(f"💔 Vara quebrada #{self.stats.rod_breaks}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obter estatísticas da sessão"""
        with self._lock:
            current_time = time.time()
            session_duration = current_time - self.stats.session_start
            
            return {
                'fish_caught': self.stats.fish_caught,
                'session_duration': session_duration,
                'feeding_count': self.stats.feeding_count,
                'rod_breaks': self.stats.rod_breaks,
                'chest_openings': self.stats.chest_openings,
                'total_actions': self.stats.total_actions,
                'last_catch_time': self.stats.last_catch_time,
                'catches_per_hour': (self.stats.fish_caught / (session_duration / 3600)) if session_duration > 0 else 0
            }
    
    def reset_session_stats(self):
        """Resetar estatísticas da sessão"""
        with self._lock:
            self.stats = SessionStats(session_start=time.time())
            _safe_print("📊 Estatísticas resetadas")
    
    # ===== SISTEMA DE CALLBACKS =====
    
    def add_state_change_callback(self, callback: Callable):
        """Adicionar callback para mudança de estado"""
        self.state_change_callbacks.append(callback)
    
    def add_rod_change_callback(self, callback: Callable):
        """Adicionar callback para mudança de vara"""
        self.rod_change_callbacks.append(callback)
    
    def _notify_state_change(self, old_mode: GameMode, new_mode: GameMode, context: str):
        """Notificar callbacks de mudança de estado"""
        for callback in self.state_change_callbacks:
            try:
                callback(old_mode, new_mode, context)
            except Exception as e:
                _safe_print(f"❌ Erro em callback de estado: {e}")
    
    def _notify_rod_change(self, slot: int, old_state: RodState, new_state: RodState):
        """Notificar callbacks de mudança de vara"""
        for callback in self.rod_change_callbacks:
            try:
                callback(slot, old_state, new_state)
            except Exception as e:
                _safe_print(f"❌ Erro em callback de vara: {e}")
    
    # ===== MÉTODOS DE UTILIDADE =====
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Obter resumo completo do estado"""
        with self._lock:
            rods_summary = {}
            for slot, rod in self.rods.items():
                rods_summary[slot] = {
                    'state': rod.state.value,
                    'bait': rod.bait_type,
                    'uses': rod.uses_remaining
                }
            
            return {
                'mode': self.current_mode.value,
                'inventory_open': self.inventory.is_open,
                'chest_open': self.chest_open,
                'feeding_active': self.feeding_active,
                'active_rod_pair': self.get_active_rod_pair(),
                'selected_slot': self.inventory.selected_slot,
                'rods': rods_summary,
                'stats': self.get_session_stats()
            }
    
    def can_start_fishing(self) -> tuple[bool, str]:
        """Verificar se pode iniciar pesca"""
        with self._lock:
            # Verificar modo atual
            if self.current_mode not in [GameMode.IDLE]:
                return False, f"Não pode pescar no modo {self.current_mode.value}"
            
            # Verificar se há varas com isca
            rods_with_bait = self.get_rods_with_bait()
            if not rods_with_bait:
                return False, "Nenhuma vara com isca disponível"
            
            return True, "Pronto para pescar"
    
    def is_busy(self) -> bool:
        """Verificar se sistema está ocupado"""
        with self._lock:
            busy_modes = [GameMode.FEEDING, GameMode.MAINTENANCE, GameMode.CHEST_OPEN]
            return self.current_mode in busy_modes
    
    def __str__(self) -> str:
        """Representação string do GameState"""
        return f"GameState(mode={self.current_mode.value}, fish={self.stats.fish_caught}, rods_with_bait={len(self.get_rods_with_bait())})"