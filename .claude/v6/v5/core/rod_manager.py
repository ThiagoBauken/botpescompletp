#!/usr/bin/env python3
"""
🎣 RodManager - Sistema de Gerenciamento de Varas v4.0

Baseado na lógica FUNCIONAL do perform_rod_switch_sequence_SLOTS_REAIS() 
do botpesca.py linha 15013 que JÁ FUNCIONA no v3.

Funcionalidades:
- 6 varas em 3 pares: [(1,2), (3,4), (5,6)]
- Detecção inteligente de status: com_isca, sem_isca, quebrada, vazio
- Troca automática priorizando varas com isca
- Coordenadas exatas do v3
- Thread-safe com game state coordination
"""

import time
import threading
from typing import Optional, Dict, List, Tuple
from enum import Enum
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class RodStatus(Enum):
    """Status possíveis da vara"""
    COM_ISCA = "com_isca"
    SEM_ISCA = "sem_isca"
    QUEBRADA = "quebrada"
    VAZIO = "vazio"

class RodManager:
    """
    🎣 Gerenciador de Varas Inteligente
    
    Baseado na lógica comprovada do v3 que FUNCIONA
    """
    
    def __init__(self, template_engine, input_manager, config_manager=None, game_state=None, chest_manager=None):
        """Inicializar gerenciador de varas"""
        self.template_engine = template_engine
        self.input_manager = input_manager
        self.config_manager = config_manager
        self.game_state = game_state or {}
        self.chest_manager = chest_manager

        # Instanciar sistema de manutenção completo
        from .rod_maintenance_system import RodMaintenanceSystem
        self.maintenance_system = RodMaintenanceSystem(
            template_engine=template_engine,
            chest_manager=chest_manager,
            input_manager=input_manager,
            rod_manager=self,
            config_manager=config_manager
        )
        
        # Lock para thread safety
        self.rod_lock = threading.RLock()
        
        # ===== CONFIGURAÇÃO BASEADA NO V3 =====
        
        # 6 varas em 3 pares (exato do v3)
        self.rod_pairs = [(1, 2), (3, 4), (5, 6)]
        self.current_pair_index = 0
        self.current_rod_in_pair = 0
        
        # Coordenadas dos slots (EXATAS do v3)
        self.slot_positions = {
            1: (709, 1005),   # Slot 1
            2: (805, 1005),   # Slot 2
            3: (899, 1005),   # Slot 3
            4: (992, 1005),   # Slot 4
            5: (1092, 1005),  # Slot 5
            6: (1188, 1005)   # Slot 6
        }
        
        # Contador de usos por vara (baseado no v3)
        self.rod_uses = {
            1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0
        }

        # ✅ Limites de uso - LER DA UI/CONFIG (não hardcoded!)
        if config_manager:
            # Usar apenas rod_switch_limit da UI para ambos (inicial e reload)
            rod_switch_limit = config_manager.get('rod_system.rod_switch_limit', 20)
            self.use_limit_initial = rod_switch_limit
            self.use_limit_after_reload = rod_switch_limit
        else:
            # Fallback se não tiver config
            self.use_limit_initial = 20
            self.use_limit_after_reload = 20
        self.first_round_completed = False  # Flag para controlar limite
        
        # Cache de status das varas
        self.rod_status_cache = {}
        self.last_status_update = 0
        self.cache_timeout = 5.0  # Cache válido por 5s
        
        # Estatísticas
        self.stats = {
            'total_switches': 0,
            'successful_switches': 0,
            'rods_replaced': 0
        }

        # Flag de troca pendente (marcada pelo fishing_engine quando detecta operação de baú pendente)
        self.pending_rod_switch = False

        # ✅ NOVO: Dados de troca de par pendente (para não modificar estado até confirmar)
        self.pending_pair_switch_data = None  # {'new_pair_index': int, 'first_rod': int}

        _safe_print("🎣 RodManager inicializado com lógica do v3")
    
    def get_current_rod(self) -> int:
        """Obter vara atual sendo usada"""
        with self.rod_lock:
            pair = self.rod_pairs[self.current_pair_index]
            rod = pair[self.current_rod_in_pair]
            _safe_print(f"🔍 [GET_CURRENT_ROD] Par {self.current_pair_index+1}{pair}, pos={self.current_rod_in_pair}, pending_data={self.pending_pair_switch_data} → RETORNA vara {rod}")
            return rod

    def detect_rod_in_hand(self) -> Optional[int]:
        """
        🔍 Detectar qual vara está na mão do jogador

        Usa template matching para identificar templates "na mão":
        - namaocomisca / comiscanamao - Vara COM isca na mão
        - namaosemisca / semiscanam - Vara SEM isca na mão

        Returns:
            int: Número do slot da vara (1-6) ou None se nenhuma detectada
        """
        try:
            if not self.template_engine:
                return None

            _safe_print("🔍 Detectando vara na mão do jogador...")

            # Templates que indicam vara na mão
            hand_templates = [
                'namaocomisca',
                'comiscanamao',
                'namaosemisca',
                'semiscanam'
            ]

            # Buscar qualquer template de "na mão"
            for template in hand_templates:
                result = self.template_engine.detect_template(template, confidence_threshold=0.75)
                if result and result.found:
                    _safe_print(f"✅ Detectado template '{template}' na mão (conf: {result.confidence:.3f})")

                    # Determinar qual slot baseado na posição Y
                    # A vara na mão aparece na parte inferior da tela
                    # Usar vara atual como melhor guess
                    current = self.get_current_rod()
                    _safe_print(f"   📍 Vara atual identificada: slot {current}")
                    return current

            _safe_print("   ℹ️ Nenhuma vara detectada na mão")
            return None

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar vara na mão: {e}")
            return None

    def remove_rod_from_hand(self, slot: int) -> bool:
        """
        🎣 Remover vara da mão pressionando o número do slot

        Args:
            slot: Número do slot (1-6)

        Returns:
            bool: True se executado com sucesso
        """
        try:
            if slot < 1 or slot > 6:
                _safe_print(f"❌ Slot inválido: {slot}")
                return False

            _safe_print(f"🎣 Removendo vara do slot {slot} da mão...")

            if not self.input_manager:
                _safe_print("❌ InputManager não disponível")
                return False

            # Pressionar número do slot (press_key JÁ faz down+up automaticamente!)
            import inspect
            caller = inspect.stack()[1].function if len(inspect.stack()) > 1 else "desconhecido"
            _safe_print(f"🔢 [LOG BOTÃO {slot}] Chamado por: {caller}")
            _safe_print(f"🔢 [LOG BOTÃO {slot}] Ação: REMOVER vara da mão")

            self.input_manager.press_key(str(slot), duration=0.05)  # Clique rápido!
            time.sleep(0.3)  # Aguardar jogo processar

            _safe_print(f"✅ Tecla '{slot}' pressionada - vara removida da mão")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao remover vara da mão: {e}")
            return False

    def equip_rod(self, slot: int, hold_right_button: bool = False) -> bool:
        """
        🎣 Equipar vara pressionando o número do slot

        Args:
            slot: Número do slot (1-6)
            hold_right_button: Se True, mantém botão direito pressionado antes de equipar

        Returns:
            bool: True se executado com sucesso
        """
        try:
            if slot < 1 or slot > 6:
                _safe_print(f"❌ Slot inválido: {slot}")
                return False

            _safe_print(f"🎣 Equipando vara do slot {slot}...")

            if not self.input_manager:
                _safe_print("❌ InputManager não disponível")
                return False

            # Se solicitado, segurar botão direito ANTES de equipar (USAR RELATIVO!)
            if hold_right_button:
                _safe_print("   🖱️ Segurando botão direito...")
                if hasattr(self.input_manager, 'mouse_down_relative'):
                    self.input_manager.mouse_down_relative('right')
                else:
                    self.input_manager.mouse_down('right')  # Fallback
                time.sleep(0.8)  # ✅ Aumentado de 0.5s para 0.8s (Arduino precisa processar)

            # Pressionar número do slot
            time.sleep(0.3)
            _safe_print(f"   ⌨️ Equipando vara slot {slot}...")
            self.input_manager.press_key(str(slot), duration=0.05)

            # ✅ CRÍTICO: Delay maior após equipar para jogo processar
            time.sleep(0.6)  # ✅ Aumentado de 0.5s para 0.6s

            _safe_print(f"✅ Vara do slot {slot} equipada")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao equipar vara: {e}")
            return False

    def equip_next_rod_after_chest(self) -> bool:
        """
        🎣 Equipar PRÓXIMA vara após operações de baú

        Chamado após fechar baú quando switch_rod(will_open_chest=True) foi usado.
        Equipa a próxima vara do par baseado no CONTADOR DE USOS.

        Lógica:
        - Escolhe a vara do par com MENOS usos
        - Se ambas têm mesmo número de usos, escolhe a próxima na sequência

        Returns:
            bool: True se executado com sucesso
        """
        try:
            with self.rod_lock:
                # Pegar par atual e verificar usos
                current_pair = self.rod_pairs[self.current_pair_index]
                vara1_slot, vara2_slot = current_pair

                vara1_usos = self.rod_uses[vara1_slot]
                vara2_usos = self.rod_uses[vara2_slot]
                limite = self.use_limit_initial

                _safe_print(f"\n🎣 Escolhendo próxima vara após baú:")
                _safe_print(f"   Par atual: {current_pair}")
                _safe_print(f"   Vara {vara1_slot}: {vara1_usos}/{limite} usos")
                _safe_print(f"   Vara {vara2_slot}: {vara2_usos}/{limite} usos")

                # ✅ LÓGICA CORRETA: Escolher vara com MENOS usos
                if vara1_usos < limite and vara2_usos >= limite:
                    # Vara 2 atingiu limite, usar vara 1
                    next_rod = vara1_slot
                    next_rod_in_pair = 0
                    _safe_print(f"   ✅ Escolhida vara {next_rod} (vara 2 atingiu limite)")
                elif vara2_usos < limite and vara1_usos >= limite:
                    # Vara 1 atingiu limite, usar vara 2
                    next_rod = vara2_slot
                    next_rod_in_pair = 1
                    _safe_print(f"   ✅ Escolhida vara {next_rod} (vara 1 atingiu limite)")
                elif vara1_usos < vara2_usos:
                    # Vara 1 tem menos usos
                    next_rod = vara1_slot
                    next_rod_in_pair = 0
                    _safe_print(f"   ✅ Escolhida vara {next_rod} (menos usos: {vara1_usos} vs {vara2_usos})")
                elif vara2_usos < vara1_usos:
                    # Vara 2 tem menos usos
                    next_rod = vara2_slot
                    next_rod_in_pair = 1
                    _safe_print(f"   ✅ Escolhida vara {next_rod} (menos usos: {vara2_usos} vs {vara1_usos})")
                else:
                    # Ambas têm mesmo número de usos
                    # ✅ CRÍTICO: Verificar se AMBAS atingiram limite (par esgotado!)
                    if vara1_usos >= limite and vara2_usos >= limite:
                        _safe_print(f"\n❌ [ERRO LÓGICO DETECTADO] AMBAS as varas atingiram limite de {limite} usos!")
                        _safe_print(f"   Vara {vara1_slot}: {vara1_usos}/{limite} usos >= limite")
                        _safe_print(f"   Vara {vara2_slot}: {vara2_usos}/{limite} usos >= limite")
                        _safe_print(f"   📍 Isso significa que register_rod_use() deveria ter detectado troca de par")
                        _safe_print(f"   📍 E coordinator deveria ter usado rod_to_equip_after_pair_switch!")
                        _safe_print(f"   ❌ NÃO POSSO escolher vara do mesmo par esgotado!")
                        _safe_print(f"   🔄 Retornando False - coordinator deve tratar isso\n")
                        return False

                    # Ambas têm mesmo número de usos MAS não atingiram limite → alternar
                    if self.current_rod_in_pair == 0:
                        next_rod = vara2_slot
                        next_rod_in_pair = 1
                    else:
                        next_rod = vara1_slot
                        next_rod_in_pair = 0
                    _safe_print(f"   ✅ Escolhida vara {next_rod} (alternância - usos iguais: {vara1_usos}/{limite})")

                if not self.input_manager:
                    _safe_print("❌ InputManager não disponível")
                    return False

                # ✅ CRÍTICO: SEGURAR botão direito AQUI!
                # Após operações de baú (feeding/cleaning/maintenance), precisamos segurar
                # o botão direito para que os cliques comecem quando voltar ao loop

                # Segurar botão direito ANTES de equipar (USAR RELATIVO para evitar drift!)
                _safe_print(f"   🖱️ Segurando botão direito...")
                if hasattr(self.input_manager, 'mouse_down_relative'):
                    self.input_manager.mouse_down_relative('right')
                else:
                    self.input_manager.mouse_down('right')  # Fallback
                time.sleep(0.8)  # ✅ Aumentado de 0.5s para 0.8s (Arduino precisa processar)

                # Apertar número da próxima vara
                _safe_print(f"   🔄 Equipando vara {next_rod}...")
                self.input_manager.press_key(str(next_rod), duration=0.05)
                time.sleep(0.6)  # ✅ Aumentado de 0.3s para 0.6s (jogo precisa processar)

                # ✅ ATUALIZAR tracking
                self.current_rod_in_pair = next_rod_in_pair

                _safe_print(f"✅ Vara {next_rod} equipada e tracking atualizado (botão direito segurado)!")
                return True

        except Exception as e:
            _safe_print(f"❌ Erro ao equipar próxima vara: {e}")
            return False
    
    def needs_rod_switch(self) -> bool:
        """
        ❌ DESABILITADO - Troca agora é SEMPRE após cada peixe

        Sistema novo:
        - Troca automática após CADA peixe (1→2→1→2)
        - Mudança de par baseada em contagem de usos (20 primeira, 10 depois)
        - Este método NÃO é mais usado!
        """
        return False  # Nunca triggerar troca automática aqui
    
    def switch_rod(self, will_open_chest: bool = False) -> bool:
        """
        🔄 Trocar vara pressionando número - LÓGICA NOVA

        Modos de troca:
        1. TROCA DIRETA (after fish, no chest): Apenas apertar próxima vara
        2. TROCA COM BAÚ (feeding/cleaning/maintenance): Tirar vara → operações → equipar nova

        Lógica de alternação:
        - Par 1: 1→2→1→2 (até limite)
        - Par 2: 3→4→3→4 (até limite)
        - Par 3: 5→6→5→6 (até limite)

        Args:
            will_open_chest: Se True, apenas TIRA vara da mão (antes de abrir baú)
                           Se False, TROCA DIRETA para próxima vara
        """
        try:
            with self.rod_lock:
                _safe_print("\n" + "="*50)
                _safe_print("🔄 TROCA DE VARA")
                _safe_print("="*50)

                self.stats['total_switches'] += 1

                # PROTEÇÃO: Não trocar durante outras operações
                if self._is_other_operation_active():
                    _safe_print("⚠️ [PROTEÇÃO] Outras operações ativas, adiando troca")
                    return False

                if not self.input_manager:
                    _safe_print("❌ InputManager não disponível")
                    return False

                # Obter vara atual e calcular próxima do par
                current_rod = self.get_current_rod()
                current_pair = self.rod_pairs[self.current_pair_index]

                # Alternar entre as duas varas do par
                if self.current_rod_in_pair == 0:
                    next_rod = current_pair[1]
                    next_rod_in_pair = 1
                else:
                    next_rod = current_pair[0]
                    next_rod_in_pair = 0

                if will_open_chest:
                    # ✅ MODO 1: VAI ABRIR BAÚ - Apenas TIRAR vara da mão
                    _safe_print(f"📍 Vara atual: {current_rod}")
                    _safe_print(f"🎣 TIRANDO vara da mão (apertar {current_rod}) - vai abrir baú")
                    _safe_print(f"   Próxima vara após baú: {next_rod}")

                    import inspect
                    caller = inspect.stack()[1].function if len(inspect.stack()) > 1 else "desconhecido"
                    _safe_print(f"🔢 [LOG BOTÃO {current_rod}] Chamado por: {caller}")
                    _safe_print(f"🔢 [LOG BOTÃO {current_rod}] Ação: TIRAR vara (vai abrir baú)")

                    self.input_manager.press_key(str(current_rod), duration=0.05)  # Clique rápido!
                    time.sleep(0.3)  # Aguardar jogo processar

                    _safe_print(f"✅ Vara {current_rod} removida da mão")
                    # NÃO atualiza current_rod_in_pair ainda - será feito ao equipar depois
                else:
                    # ✅ MODO 2: TROCA DIRETA - Segurar botão direito + Apertar próxima vara
                    _safe_print(f"📍 Par {self.current_pair_index + 1}: {current_pair}")
                    _safe_print(f"   Vara atual: {current_rod} → Próxima: {next_rod}")
                    _safe_print(f"🔄 TROCA DIRETA")

                    # SEMPRE segurar botão direito antes de trocar (USAR RELATIVO!)
                    _safe_print("   🖱️ Segurando botão direito (Mouse relativo)...")
                    if hasattr(self.input_manager, 'mouse_down_relative'):
                        _safe_print(f"      📤 Chamando mouse_down_relative('right')...")
                        result = self.input_manager.mouse_down_relative('right')
                        _safe_print(f"      📥 Resultado: {'✅ Sucesso' if result else '❌ Falhou'}")
                    else:
                        _safe_print(f"      ⚠️ mouse_down_relative não disponível - usando fallback")
                        self.input_manager.mouse_down('right')  # Fallback
                    _safe_print(f"      ⏳ Aguardando 0.5s para Arduino processar...")
                    time.sleep(0.5)  # ✅ Aumentado de 0.3s para 0.5s

                    # Apertar próxima vara
                    import inspect
                    caller = inspect.stack()[1].function if len(inspect.stack()) > 1 else "desconhecido"
                    _safe_print(f"🔢 [LOG BOTÃO {next_rod}] Chamado por: {caller}")
                    _safe_print(f"🔢 [LOG BOTÃO {next_rod}] Ação: TROCA DIRETA (sem baú)")
                    _safe_print(f"   🔢 Pressionando tecla {next_rod}...")
                    self.input_manager.press_key(str(next_rod), duration=0.05)  # Clique rápido!
                    time.sleep(0.3)  # Aguardar jogo processar

                    # Atualizar tracking
                    self.current_rod_in_pair = next_rod_in_pair

                    _safe_print(f"✅ Troca para vara {next_rod} executada (botão direito segurado)!")

                self.stats['successful_switches'] += 1
                _safe_print("="*50)
                return True

        except Exception as e:
            _safe_print(f"❌ Erro na troca de vara: {e}")
            return False
    
    def _is_other_operation_active(self) -> bool:
        """Verificar se outras operações estão ativas"""
        if not self.game_state:
            return False
        
        active_operations = [
            'chest_open',
            'cleaning_active', 
            'feeding_active',
            'maintenance_active'
        ]
        
        for operation in active_operations:
            if self.game_state.get(operation, False):
                _safe_print(f"⚠️ Operação ativa detectada: {operation}")
                return True
        
        return False
    
    def _open_inventory(self) -> bool:
        """Abrir inventário (Tab)"""
        try:
            if self.input_manager:
                _safe_print("📦 Pressionando Tab para abrir inventário...")
                self.input_manager.press_key('tab')
                time.sleep(0.8)  # Aguardar abertura (tempo do v3)
                
                # Verificar se abriu usando template
                if self.template_engine and self.template_engine.detect_inventory_state():
                    _safe_print("✅ Inventário aberto com sucesso")
                    return True
                else:
                    _safe_print("⚠️ Inventário pode não ter aberto (sem detecção)")
                    return True  # Continuar mesmo sem detecção
            
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao abrir inventário: {e}")
            return False
    
    def _close_inventory(self) -> bool:
        """Fechar inventário (Tab)"""
        try:
            if self.input_manager:
                _safe_print("📦 Pressionando Tab para fechar inventário...")
                self.input_manager.press_key('tab')
                time.sleep(0.5)  # Aguardar fechamento
                return True
            
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao fechar inventário: {e}")
            return False
    
    def _scan_all_rods(self) -> Dict[int, RodStatus]:
        """
        Detectar status de todas as varas
        
        Baseado na lógica de detecção do v3
        """
        try:
            rod_status = {}
            
            for slot in range(1, 7):
                _safe_print(f"  🔍 Analisando vara no slot {slot}...")
                
                if self.template_engine:
                    status_str = self.template_engine.detect_rod_status(slot)
                    
                    # Converter string para enum
                    status_map = {
                        "com_isca": RodStatus.COM_ISCA,
                        "sem_isca": RodStatus.SEM_ISCA,
                        "quebrada": RodStatus.QUEBRADA,
                        "vazio": RodStatus.VAZIO
                    }
                    
                    rod_status[slot] = status_map.get(status_str, RodStatus.VAZIO)
                    _safe_print(f"    ✅ Slot {slot}: {rod_status[slot].value}")
                else:
                    # Fallback se não tiver template engine
                    rod_status[slot] = RodStatus.VAZIO
                    _safe_print(f"    ⚠️ Slot {slot}: sem detecção (assumindo vazio)")
            
            # Atualizar cache
            self.rod_status_cache = rod_status
            self.last_status_update = time.time()
            
            return rod_status
            
        except Exception as e:
            _safe_print(f"❌ Erro ao escanear varas: {e}")
            return {}
    
    def _find_best_rod(self, rod_status: Dict[int, RodStatus]) -> Optional[int]:
        """
        Encontrar melhor vara para trocar
        
        Prioridade (baseada no v3):
        1. Varas do par atual com isca
        2. Varas de outros pares com isca 
        3. Varas sem isca como último recurso
        """
        try:
            current_rod = self.get_current_rod()
            
            # PRIORIDADE 1: Varas do par atual com isca
            current_pair = self.rod_pairs[self.current_pair_index]
            _safe_print(f"  🎯 Verificando par atual: {current_pair}")
            
            for rod in current_pair:
                if rod != current_rod and rod_status.get(rod) == RodStatus.COM_ISCA:
                    _safe_print(f"    ✅ Encontrada vara {rod} com isca no par atual")
                    return rod
            
            # PRIORIDADE 2: Varas de outros pares com isca
            _safe_print("  🔍 Procurando em outros pares...")
            for pair in self.rod_pairs:
                if pair != current_pair:
                    for rod in pair:
                        if rod_status.get(rod) == RodStatus.COM_ISCA:
                            _safe_print(f"    ✅ Encontrada vara {rod} com isca em outro par")
                            return rod
            
            # PRIORIDADE 3: Qualquer vara sem isca (melhor que quebrada)
            _safe_print("  ⚠️ Procurando varas sem isca como último recurso...")
            for rod in range(1, 7):
                if rod != current_rod and rod_status.get(rod) == RodStatus.SEM_ISCA:
                    _safe_print(f"    ⚠️ Encontrada vara {rod} sem isca (último recurso)")
                    return rod
            
            _safe_print("❌ Nenhuma vara adequada encontrada")
            return None
            
        except Exception as e:
            _safe_print(f"❌ Erro ao encontrar melhor vara: {e}")
            return None
    
    def _execute_rod_click(self, target_rod: int) -> bool:
        """Executar clique na vara target"""
        try:
            if target_rod not in self.slot_positions:
                _safe_print(f"❌ Posição do slot {target_rod} não encontrada")
                return False
            
            x, y = self.slot_positions[target_rod]
            _safe_print(f"  🖱️ Clicando na posição ({x}, {y}) para vara {target_rod}")
            
            if self.input_manager:
                self.input_manager.click(x, y)
                time.sleep(0.5)  # Aguardar clique processar
                return True
            
            return False
            
        except Exception as e:
            _safe_print(f"❌ Erro ao clicar na vara {target_rod}: {e}")
            return False
    
    def manual_rod_switch(self) -> bool:
        """
        🔄 Troca manual de vara (TAB) - APENAS TROCA, SEM OUTRAS AÇÕES
        
        Versão simplificada para uso manual que evita triggerar outras funcionalidades
        """
        try:
            with self.rod_lock:
                _safe_print("\n" + "="*50)
                _safe_print("🔄 TROCA MANUAL DE VARA - SIMPLES")
                _safe_print("="*50)
                
                # PASSO 1: Abrir inventário
                _safe_print("📦 PASSO 1: Abrindo inventário...")
                if not self._open_inventory():
                    return False
                
                # PASSO 2: Detectar status das varas
                _safe_print("🔍 PASSO 2: Detectando status de todas as varas...")
                rod_status = self._scan_all_rods()
                
                # PASSO 3: Encontrar melhor vara
                _safe_print("🎯 PASSO 3: Encontrando melhor vara...")
                best_rod = self._find_best_rod_simple(rod_status)
                
                if best_rod is None:
                    _safe_print("❌ Nenhuma vara adequada encontrada")
                    self._close_inventory()
                    return False
                
                # PASSO 4: Trocar para a vara
                _safe_print(f"🔄 PASSO 4: Trocando para vara {best_rod}...")
                success = self._execute_rod_click(best_rod)
                
                if success:
                    _safe_print(f"✅ Troca para vara {best_rod} bem-sucedida!")
                    self._update_current_rod(best_rod)
                else:
                    _safe_print(f"❌ Falha ao trocar para vara {best_rod}")
                
                # PASSO 5: Fechar inventário
                _safe_print("📦 PASSO 5: Fechando inventário...")
                self._close_inventory()
                
                _safe_print("="*50)
                if success:
                    _safe_print("✅ [TAB] Troca manual de vara executada com sucesso")
                else:
                    _safe_print("❌ [TAB] Falha na troca manual de vara")
                    
                return success
                
        except Exception as e:
            _safe_print(f"❌ Erro na troca manual de vara: {e}")
            return False
    
    def _find_best_rod_simple(self, rod_status: Dict[int, RodStatus]) -> Optional[int]:
        """Encontrar melhor vara para troca manual (versão simplificada)"""
        try:
            # 1. Prioridade: Varas com isca
            for rod_slot in range(1, 7):
                if rod_status.get(rod_slot) == RodStatus.COM_ISCA:
                    _safe_print(f"    ✅ Encontrada vara {rod_slot} com isca")
                    return rod_slot

            # 2. Alternativa: Varas sem isca (para colocar isca depois)
            for rod_slot in range(1, 7):
                if rod_status.get(rod_slot) == RodStatus.SEM_ISCA:
                    _safe_print(f"    ⚠️ Encontrada vara {rod_slot} sem isca (último recurso)")
                    return rod_slot

            # 3. Último recurso: qualquer vara válida
            for rod_slot in range(1, 7):
                if rod_status.get(rod_slot) in [RodStatus.COM_ISCA, RodStatus.SEM_ISCA]:
                    _safe_print(f"    🔄 Usando vara {rod_slot} como último recurso")
                    return rod_slot
            
            _safe_print("    ❌ Nenhuma vara válida encontrada")
            return None
            
        except Exception as e:
            _safe_print(f"❌ Erro ao encontrar melhor vara: {e}")
            return None
    
    def _update_current_rod(self, new_rod: int):
        """Atualizar vara atual após troca bem-sucedida"""
        try:
            # Encontrar em qual par está a nova vara
            for pair_index, pair in enumerate(self.rod_pairs):
                if new_rod in pair:
                    self.current_pair_index = pair_index
                    self.current_rod_in_pair = pair.index(new_rod)
                    _safe_print(f"📍 Vara atual atualizada: {new_rod} (par {pair_index}, pos {self.current_rod_in_pair})")
                    break
                    
        except Exception as e:
            _safe_print(f"❌ Erro ao atualizar vara atual: {e}")
    
    def get_rod_status(self, slot: int) -> RodStatus:
        """Obter status de uma vara específica"""
        try:
            # Verificar cache primeiro
            if (time.time() - self.last_status_update < self.cache_timeout and 
                slot in self.rod_status_cache):
                return self.rod_status_cache[slot]
            
            # Cache expirado, detectar novamente
            if self.template_engine:
                status_str = self.template_engine.detect_rod_status(slot)
                status_map = {
                    "com_isca": RodStatus.COM_ISCA,
                    "sem_isca": RodStatus.SEM_ISCA,
                    "quebrada": RodStatus.QUEBRADA,
                    "vazio": RodStatus.VAZIO
                }
                return status_map.get(status_str, RodStatus.VAZIO)
            
            return RodStatus.VAZIO
            
        except Exception as e:
            _safe_print(f"❌ Erro ao obter status da vara {slot}: {e}")
            return RodStatus.VAZIO
    
    def register_rod_use(self, rod: Optional[int] = None, caught_fish: bool = True, will_open_chest: bool = False):
        """
        📊 Registrar uso de uma vara (peixe OU timeout)

        Args:
            rod: Número da vara (None = vara atual)
            caught_fish: True se pegou peixe, False se deu timeout (ambos contam como uso!)
            will_open_chest: True se vai abrir baú no próximo ciclo (feeding/cleaning/maintenance)

        Returns:
            int ou bool: Se mudou de par, retorna número da primeira vara do novo par (int)
                        Se não mudou de par, retorna False
        """
        try:
            if rod is None:
                rod = self.get_current_rod()

            # 📊 DEBUG: Mostrar estado ANTES do incremento
            current_pair = self.rod_pairs[self.current_pair_index]
            vara1_slot, vara2_slot = current_pair
            vara1_usos_before = self.rod_uses[vara1_slot]
            vara2_usos_before = self.rod_uses[vara2_slot]
            limite = self.use_limit_initial

            _safe_print(f"\n📊 [REGISTER_ROD_USE] ANTES do incremento:")
            _safe_print(f"   Par atual: {self.current_pair_index + 1} {current_pair}")
            _safe_print(f"   Vara {vara1_slot}: {vara1_usos_before}/{limite} usos")
            _safe_print(f"   Vara {vara2_slot}: {vara2_usos_before}/{limite} usos")
            _safe_print(f"   Registrando uso da vara {rod}")

            # Incrementar contador de usos
            self.rod_uses[rod] += 1

            status = "🐟 Peixe" if caught_fish else "⏱️ Timeout"
            _safe_print(f"\n📊 {status} - Vara {rod}: {self.rod_uses[rod]} usos")

            # Mostrar estado DEPOIS do incremento
            vara1_usos_after = self.rod_uses[vara1_slot]
            vara2_usos_after = self.rod_uses[vara2_slot]
            _safe_print(f"📊 [REGISTER_ROD_USE] DEPOIS do incremento:")
            _safe_print(f"   Vara {vara1_slot}: {vara1_usos_before} → {vara1_usos_after} usos")
            _safe_print(f"   Vara {vara2_slot}: {vara2_usos_before} → {vara2_usos_after} usos")

            # ✅ CRÍTICO: SEMPRE verificar mudança de par (mesmo se vai abrir baú!)
            # Mas NÃO executar a troca agora se will_open_chest=True
            pair_switch_result = self._check_pair_switch_needed()

            if pair_switch_result:
                # Par mudou!
                if will_open_chest:
                    _safe_print("⏸️ [TROCA DE PAR] Operação de baú pendente")
                    _safe_print(f"   📍 Coordinator vai equipar vara {pair_switch_result} APÓS fechar baú")
                    # ✅ RETORNAR número da vara para o coordinator equipar depois
                    return pair_switch_result  # int (ex: 5)
                else:
                    _safe_print(f"✅ [TROCA DE PAR] Sem operação de baú - retornando slot {pair_switch_result}")
                    return pair_switch_result  # int (ex: 5)
            else:
                # Não mudou de par
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao registrar uso: {e}")
            return False

    def reset_pair_uses_after_maintenance(self, pair_index: Optional[int] = None):
        """
        🔧 Resetar contadores de uso após manutenção

        Args:
            pair_index: Índice do par (0, 1, 2). None = par atual
        """
        try:
            with self.rod_lock:
                if pair_index is None:
                    pair_index = self.current_pair_index

                pair = self.rod_pairs[pair_index]
                vara1, vara2 = pair

                _safe_print(f"\n🔧 RESETANDO usos do Par {pair_index + 1} {pair} após manutenção")
                _safe_print(f"   Vara {vara1}: {self.rod_uses[vara1]} → 0")
                _safe_print(f"   Vara {vara2}: {self.rod_uses[vara2]} → 0")

                # Resetar para 0
                self.rod_uses[vara1] = 0
                self.rod_uses[vara2] = 0

                _safe_print(f"✅ Par {pair_index + 1} resetado - pronto para {self._get_current_limit()} usos cada")

        except Exception as e:
            _safe_print(f"❌ Erro ao resetar usos: {e}")

    def _get_current_limit(self) -> int:
        """Retorna o limite atual de usos (sempre o mesmo valor configurado na UI)"""
        return self.use_limit_initial

    def confirm_pair_switch(self) -> bool:
        """
        ✅ Confirmar que a troca de par foi executada pelo coordinator

        Aplica as mudanças de par que estavam pendentes.

        Returns:
            bool: True se havia mudanças pendentes que foram aplicadas
        """
        try:
            with self.rod_lock:
                if self.pending_pair_switch_data:
                    _safe_print(f"\n✅ Confirmando troca de par...")

                    # Aplicar mudanças
                    old_pair_index = self.current_pair_index
                    self.current_pair_index = self.pending_pair_switch_data['new_pair_index']
                    self.current_rod_in_pair = 0  # Sempre primeiro slot do novo par

                    new_pair = self.rod_pairs[self.current_pair_index]
                    _safe_print(f"   🔄 Par atualizado: {old_pair_index + 1} → {self.current_pair_index + 1}")
                    _safe_print(f"   📍 Novo par ativo: {new_pair}")
                    _safe_print(f"   🎣 Vara ativa: {self.pending_pair_switch_data['first_rod']}")

                    # ✅ CRÍTICO: RESETAR contadores de uso do NOVO par para 0
                    # (quando mudamos de par, começamos com contadores zerados)
                    vara1, vara2 = new_pair
                    old_uses_1 = self.rod_uses[vara1]
                    old_uses_2 = self.rod_uses[vara2]
                    self.rod_uses[vara1] = 0
                    self.rod_uses[vara2] = 0
                    _safe_print(f"   🔄 RESETANDO contadores do novo par:")
                    _safe_print(f"      Vara {vara1}: {old_uses_1} → 0 usos")
                    _safe_print(f"      Vara {vara2}: {old_uses_2} → 0 usos")

                    # Limpar dados pendentes
                    self.pending_pair_switch_data = None

                    return True
                else:
                    _safe_print("   ℹ️ Nenhuma troca de par pendente")
                    return False

        except Exception as e:
            _safe_print(f"❌ Erro ao confirmar troca de par: {e}")
            return False

    def _check_pair_switch_needed(self) -> bool:
        """
        🔄 Verificar se precisa mudar de par

        Lógica:
        - Usa o valor configurado na UI (rod_switch_limit)
        - Muda de par quando AMBAS as varas do par atingirem limite

        Returns:
            bool: True se mudou de par
        """
        try:
            with self.rod_lock:
                current_pair = self.rod_pairs[self.current_pair_index]
                vara1_slot, vara2_slot = current_pair

                vara1_usos = self.rod_uses[vara1_slot]
                vara2_usos = self.rod_uses[vara2_slot]

                # Usar limite configurado na UI
                limite = self.use_limit_initial

                _safe_print(f"📊 Par {self.current_pair_index + 1} {current_pair}: "
                          f"Vara {vara1_slot}={vara1_usos}/{limite}, "
                          f"Vara {vara2_slot}={vara2_usos}/{limite}")

                # Checar se AMBAS atingiram o limite
                if vara1_usos >= limite and vara2_usos >= limite:
                    _safe_print(f"\n🔄 AMBAS as varas do Par {self.current_pair_index + 1} atingiram limite de {limite} usos!")
                    _safe_print(f"   Vara {vara1_slot}: {vara1_usos} usos >= {limite}")
                    _safe_print(f"   Vara {vara2_slot}: {vara2_usos} usos >= {limite}")

                    # Calcular novo par
                    old_pair_index = self.current_pair_index
                    new_pair_index = (self.current_pair_index + 1) % len(self.rod_pairs)
                    new_pair = self.rod_pairs[new_pair_index]

                    _safe_print(f"🔄 MUDANDO: Par {old_pair_index + 1} → Par {new_pair_index + 1}")
                    _safe_print(f"   Novo par: {new_pair}")

                    # ✅ SALVAR dados para aplicar DEPOIS (quando coordinator confirmar)
                    self.pending_pair_switch_data = {
                        'new_pair_index': new_pair_index,
                        'first_rod': new_pair[0]
                    }
                    _safe_print(f"   💾 Dados salvos - mudanças serão aplicadas após coordinator confirmar")
                    _safe_print(f"   📍 Próxima vara a equipar: {new_pair[0]} (primeira do par)")

                    # ✅ RETORNAR O NÚMERO DA PRIMEIRA VARA DO NOVO PAR
                    return new_pair[0]  # Retorna int (ex: 3, 5)

                return False  # Não mudou de par

        except Exception as e:
            _safe_print(f"❌ Erro ao checar mudança de par: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obter estatísticas do sistema"""
        stats = self.stats.copy()
        stats['current_rod'] = self.get_current_rod()
        stats['rod_uses'] = self.rod_uses.copy()
        
        if stats['total_switches'] > 0:
            stats['success_rate'] = stats['successful_switches'] / stats['total_switches']
        else:
            stats['success_rate'] = 0.0
            
        return stats
    
    def force_rod_detection(self) -> Dict[int, RodStatus]:
        """Forçar nova detecção de todas as varas"""
        _safe_print("🔄 Forçando nova detecção de todas as varas...")
        self.rod_status_cache.clear()
        self.last_status_update = 0
        return self._scan_all_rods()

    def execute_full_maintenance(self) -> bool:
        """
        🔧 Executar manutenção completa de varas - TECLA PAGE DOWN

        Delega para o sistema de manutenção completo
        """
        _safe_print("🔧 RodManager: Delegando para sistema de manutenção completo...")
        return self.maintenance_system.execute_full_maintenance()

    def get_maintenance_stats(self) -> Dict:
        """Obter estatísticas de manutenção"""
        return self.maintenance_system.get_maintenance_stats()

    def analyze_rod_pairs_for_maintenance(self) -> Dict:
        """
        🎯 Analisar pares de varas para decisão inteligente de manutenção

        Retorna análise completa:
        - Par atual e status das varas
        - Quantos usos faltam para troca de par
        - Próximo par e se tem vara com isca
        - Recomendação: fazer manutenção agora ou esperar

        Returns:
            Dict com análise completa
        """
        try:
            with self.rod_lock:
                _safe_print("\n" + "="*60)
                _safe_print("🎯 ANÁLISE INTELIGENTE DE PARES DE VARAS")
                _safe_print("="*60)

                # Obter status atual de todas as varas
                rod_status = self._scan_all_rods() if hasattr(self, '_scan_all_rods') else {}

                # Par atual
                current_pair = self.rod_pairs[self.current_pair_index]
                current_rod = self.get_current_rod()

                _safe_print(f"\n📍 PAR ATUAL: {current_pair} (vara ativa: {current_rod})")

                # Analisar par atual
                pair_1_rod = current_pair[0]
                pair_2_rod = current_pair[1]

                pair_1_status = rod_status.get(pair_1_rod, RodStatus.VAZIO)
                pair_2_status = rod_status.get(pair_2_rod, RodStatus.VAZIO)

                pair_1_uses = self.rod_uses.get(pair_1_rod, 0)
                pair_2_uses = self.rod_uses.get(pair_2_rod, 0)

                _safe_print(f"  🎣 Vara {pair_1_rod}: {pair_1_status.value} ({pair_1_uses} usos restantes)")
                _safe_print(f"  🎣 Vara {pair_2_rod}: {pair_2_status.value} ({pair_2_uses} usos restantes)")

                # Usos mínimos no par atual (quanto falta para trocar)
                min_uses_in_pair = min(pair_1_uses, pair_2_uses)
                _safe_print(f"  ⏱️ Usos até troca de par: ~{min_uses_in_pair} pescas")

                # Calcular próximo par
                next_pair_index = (self.current_pair_index + 1) % len(self.rod_pairs)
                next_pair = self.rod_pairs[next_pair_index]

                _safe_print(f"\n📍 PRÓXIMO PAR: {next_pair}")

                # Analisar próximo par
                next_1_rod = next_pair[0]
                next_2_rod = next_pair[1]

                next_1_status = rod_status.get(next_1_rod, RodStatus.VAZIO)
                next_2_status = rod_status.get(next_2_rod, RodStatus.VAZIO)

                _safe_print(f"  🎣 Vara {next_1_rod}: {next_1_status.value}")
                _safe_print(f"  🎣 Vara {next_2_rod}: {next_2_status.value}")

                # Verificar se próximo par tem vara com isca
                next_pair_has_bait = (next_1_status == RodStatus.COM_ISCA or
                                     next_2_status == RodStatus.COM_ISCA)

                # Calcular pares depois do próximo (fallback)
                fallback_pair_index = (next_pair_index + 1) % len(self.rod_pairs)
                fallback_pair = self.rod_pairs[fallback_pair_index]

                fallback_1_rod = fallback_pair[0]
                fallback_2_rod = fallback_pair[1]

                fallback_1_status = rod_status.get(fallback_1_rod, RodStatus.VAZIO)
                fallback_2_status = rod_status.get(fallback_2_rod, RodStatus.VAZIO)

                fallback_has_bait = (fallback_1_status == RodStatus.COM_ISCA or
                                    fallback_2_status == RodStatus.COM_ISCA)

                _safe_print(f"\n📍 PAR FALLBACK: {fallback_pair}")
                _safe_print(f"  🎣 Vara {fallback_1_rod}: {fallback_1_status.value}")
                _safe_print(f"  🎣 Vara {fallback_2_rod}: {fallback_2_status.value}")

                # DECISÃO INTELIGENTE
                _safe_print("\n🧠 DECISÃO INTELIGENTE:")

                should_maintain_now = False
                reason = ""

                if not next_pair_has_bait and not fallback_has_bait:
                    should_maintain_now = True
                    reason = "⚠️ Próximo par e fallback SEM isca - manutenção URGENTE"
                elif not next_pair_has_bait:
                    should_maintain_now = True
                    reason = "⚠️ Próximo par SEM isca - manutenção RECOMENDADA (fallback tem isca)"
                elif min_uses_in_pair <= 5:
                    should_maintain_now = True
                    reason = "⏰ Par atual quase acabando - manutenção PREVENTIVA"
                else:
                    should_maintain_now = False
                    reason = "✅ Próximo par OK - manutenção pode esperar"

                _safe_print(f"  {reason}")
                _safe_print("="*60 + "\n")

                return {
                    'current_pair': current_pair,
                    'current_rod': current_rod,
                    'min_uses_in_pair': min_uses_in_pair,
                    'next_pair': next_pair,
                    'next_pair_has_bait': next_pair_has_bait,
                    'fallback_pair': fallback_pair,
                    'fallback_has_bait': fallback_has_bait,
                    'should_maintain_now': should_maintain_now,
                    'reason': reason,
                    'all_rod_status': rod_status
                }

        except Exception as e:
            _safe_print(f"❌ Erro ao analisar pares: {e}")
            import traceback
            traceback.print_exc()
            return {
                'should_maintain_now': False,
                'reason': f"Erro na análise: {e}"
            }