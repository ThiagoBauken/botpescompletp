#!/usr/bin/env python3
"""
🔧 RodMaintenanceSystem - Sistema Completo de Manutenção de Varas v4.0

Baseado na lógica FUNCIONAL do auto_rod_maintenance_system() do botpesca - Copia (19)
que JÁ FUNCIONA no v3.

Funcionalidades:
- Detecção completa de status das 6 varas
- Remoção/armazenamento de varas quebradas
- Reposição de varas vazias do baú
- Recarregamento automático de iscas
- Coordenação com ChestManager
- Thread-safe com game state coordination
"""

import time
import threading
from typing import Optional, Dict, List, Tuple, Set
from enum import Enum
import re
from .chest_manager import ChestOperation

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class MaintenanceOperation(Enum):
    """Operações de manutenção disponíveis"""
    CLEAN_BROKEN = "clean_broken"
    REFILL_EMPTY = "refill_empty"
    RELOAD_BAIT = "reload_bait"
    VERIFY_STATUS = "verify_status"

class RodMaintenanceSystem:
    """
    🔧 Sistema Completo de Manutenção de Varas

    Baseado na lógica comprovada do botpesca - Copia (19) que FUNCIONA
    """

    def __init__(self, template_engine, chest_manager, input_manager, rod_manager=None, config_manager=None):
        """Inicializar sistema de manutenção"""
        self.template_engine = template_engine
        self.chest_manager = chest_manager
        self.input_manager = input_manager
        self.rod_manager = rod_manager
        self.config_manager = config_manager

        # Lock para thread safety
        self.maintenance_lock = threading.RLock()

        # Estado do sistema
        self.maintenance_in_progress = False
        self.last_maintenance_time = 0

        # ===== CONFIGURAÇÃO BASEADA NO V3 (COORDENADAS FIXAS) =====

        # ✅ SOLUÇÃO CORRETA: Capturar APENAS a janela do jogo!
        # O rod_viewer_background.py agora captura só a janela do Rust
        # Então as coordenadas retornadas JÁ são relativas à janela
        # E precisam apenas do OFFSET da janela para virar coordenadas absolutas

        import win32gui

        # Encontrar janela do Rust para pegar offset
        hwnd = win32gui.FindWindow(None, "Rust")
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            self.game_offset_x = rect[0]
            self.game_offset_y = rect[1]
            _safe_print(f"📐 Janela do jogo encontrada em: ({self.game_offset_x}, {self.game_offset_y})")
        else:
            _safe_print("⚠️ Janela do Rust não encontrada - usando offset (0,0)")
            self.game_offset_x = 0
            self.game_offset_y = 0

        # ✅ COORDENADAS FIXAS DO V3 (1920x1080) - PARA CLIQUES NO JOGO
        # Estas coordenadas NUNCA mudam - são as posições reais dos slots no jogo
        self.slot_positions = {
            1: (709, 1005),   # Slot 1
            2: (805, 1005),   # Slot 2
            3: (899, 1005),   # Slot 3
            4: (992, 1005),   # Slot 4
            5: (1092, 1005),  # Slot 5
            6: (1188, 1005)   # Slot 6
        }

        # Área do inventário (lado esquerdo) - valores FIXOS do v3
        self.inventory_area = {
            'left': 633,
            'top': 541,
            'width': 600,
            'height': 412
        }

        # Área do baú (lado direito) - valores EXATOS do v3
        self.chest_area = {
            'left': 1214,
            'top': 117,
            'right': 1834,
            'bottom': 928,  # ✅ CORRIGIDO: v3 usa 928, não 500!
            'width': 620,
            'height': 811
        }

        # Divisor entre inventário e baú (coordenada X fixa)
        self.divider_x = 1242

        # Posição de descarte (EXATA DO V3) - fora do inventário
        self.discard_position = (1400, 1000)

        # Posição FIXA da isca na vara selecionada (EXATA DO V3)
        self.bait_position = (721, 359)

        # Prioridade de iscas (baseada no v3)
        self.bait_priority = [
            'carne de urso',    # Prioridade 1
            'carne de lobo',    # Prioridade 2
            'trout',            # Prioridade 3
            'grub',             # Prioridade 4
            'worm'              # Prioridade 5
        ]

        # Templates de varas
        self.rod_templates = {
            'broken': 'varaquebrada.png',
            'with_bait': 'varacomisca.png',
            'without_bait': 'varasemisca.png',
            'empty': 'varavazia.png'  # Se existir
        }

        # Estatísticas
        self.stats = {
            'total_maintenances': 0,
            'successful_maintenances': 0,
            'broken_rods_cleaned': 0,
            'rods_refilled': 0,
            'baits_reloaded': 0
        }

        # ✅ PROTEÇÃO CONTRA LOOP INFINITO: Cooldown após falhas de detecção
        self.last_no_rods_found_time = 0
        self.last_no_baits_found_time = 0
        self.no_resources_cooldown = 60  # 60 segundos de cooldown após não encontrar recursos

        # ✅ NOVO: Sistema de análise background (usa lógica perfeita da UI)
        from .rod_viewer_background import RodViewerBackground
        self.rod_viewer = RodViewerBackground(template_engine, config_manager)

        _safe_print("🔧 RodMaintenanceSystem inicializado com viewer background v4")

    def _convert_to_game_coords(self, relative_x: int, relative_y: int) -> tuple:
        """
        Converter coordenadas RELATIVAS à janela para coordenadas ABSOLUTAS da tela

        Como rod_viewer agora captura APENAS a janela do jogo:
        - OpenCV retorna coordenadas RELATIVAS à janela (ex: 100, 50)
        - PyAutoGUI precisa de coordenadas ABSOLUTAS da tela
        - Solução: adicionar offset da janela

        Exemplo:
        - Janela do jogo em: (0, 0) [Monitor 1]
        - OpenCV detecta vara em: (1687, 164) [relativo à janela]
        - Coordenada absoluta: (1687 + 0, 164 + 0) = (1687, 164)
        """
        screen_x = relative_x + self.game_offset_x
        screen_y = relative_y + self.game_offset_y

        return (screen_x, screen_y)

    def execute_full_maintenance(self, chest_already_open: bool = False) -> bool:
        """
        🔧 Executar manutenção completa - TECLA PAGE DOWN

        Baseado na lógica EXATA do auto_rod_maintenance_system() do botpesca - Copia (19)

        Args:
            chest_already_open (bool): Se True, pula abertura/fechamento do baú
                                     (usado quando chamado via ChestOperationCoordinator)
        """
        try:
            with self.maintenance_lock:
                if self.maintenance_in_progress:
                    _safe_print("⚠️ Manutenção já em progresso")
                    return False

                self.maintenance_in_progress = True

                _safe_print("\n" + "="*70)
                _safe_print("🔧 SISTEMA DE MANUTENÇÃO AUTOMÁTICA DE VARAS - INICIADO")
                _safe_print("="*70)

                self.stats['total_maintenances'] += 1

                # PASSO 1: Abrir baú (só se não estiver aberto)
                if not chest_already_open:
                    _safe_print("📦 PASSO 1: Abrindo baú via ChestManager...")
                    # ✅ USAR APENAS ChestManager para evitar conflito de ALT!
                    if not self.chest_manager.open_chest(ChestOperation.MAINTENANCE, "Manutenção de varas"):
                        _safe_print("❌ Falha ao abrir baú")
                        return False
                    _safe_print("✅ Baú aberto com sucesso via ChestManager")
                else:
                    _safe_print("📦 PASSO 1: ✅ Baú já está aberto (via coordenador)")

                # PASSO 2: Aguardar carregamento
                _safe_print("⏳ PASSO 2: Aguardando carregamento dos itens...")
                # ✅ REDUZIDO: Aguardar tempo mínimo necessário para estabilizar
                wait_time = 0.5  # ✅ REDUZIDO: 1.5s → 0.5s (mais rápido)
                _safe_print(f"   ⏳ Aguardando {wait_time}s (chest_already_open={chest_already_open})...")
                time.sleep(wait_time)

                # ✅ REMOVIDO: NÃO liberar ALT aqui!
                # ALT deve permanecer pressionado durante TODO o arrasto de varas e iscas
                # Será liberado apenas em _close_chest() ANTES de TAB
                _safe_print("🛡️ [SAFETY] ALT permanece pressionado durante manutenção...")

                # ============ SEQUÊNCIA SIMPLES E DIRETA ============

                # PASSO 3: DETECTAR STATUS usando o VIEWER (mesma lógica da UI)
                _safe_print("🔍 PASSO 3: Detectando status das varas nos slots 1-6...")
                rod_status = self.rod_viewer.analyze_rods_background(force_analysis=True)
                _safe_print(f"📊 STATUS DETECTADO: {rod_status}")

                # ✅ OTIMIZAÇÃO: Processar slots da ESQUERDA para DIREITA (1→6)
                broken_slots = [slot for slot in range(1, 7) if rod_status.get(slot) == "broken"]
                empty_slots = [slot for slot in range(1, 7) if rod_status.get(slot) == "empty"]
                # ✅ CORRIGIDO: Função retorna "without_bait" não "no_bait"
                no_bait_slots = [slot for slot in range(1, 7) if rod_status.get(slot) == "without_bait"]
                with_bait_slots = [slot for slot in range(1, 7) if rod_status.get(slot) == "with_bait"]

                # ✅ CONSIDERAR SLOTS QUEBRADOS E VAZIOS para preencher (ordenado 1→6)
                slots_to_fill = sorted(broken_slots + empty_slots)

                _safe_print(f"\n📊 SLOTS A PROCESSAR:")
                _safe_print(f"   ❌ Quebradas: {broken_slots}")
                _safe_print(f"   ⚪ Vazios: {empty_slots}")
                _safe_print(f"   🔧 Total a preencher: {slots_to_fill}")
                _safe_print(f"   ⚠️ Sem isca (ANTES): {no_bait_slots}")
                _safe_print(f"   ✅ Com isca: {with_bait_slots}")

                # ✅ ESCANEAR BAÚ UMA VEZ (não repetir)
                _safe_print(f"\n🔍 Escaneando baú...")
                available_rods = self._scan_chest_for_rods()
                available_baits = self._scan_chest_for_baits()
                _safe_print(f"   📦 Varas: {len(available_rods)} | Iscas: {len(available_baits)}")

                # Separar varas por tipo
                rods_with_bait = [r for r in available_rods if r['has_bait']]
                rods_without_bait = [r for r in available_rods if not r['has_bait']]
                all_rods = rods_with_bait + rods_without_bait  # Priorizar COM isca

                _safe_print(f"   📊 Priorizando varas: {len(rods_with_bait)} COM isca primeiro, depois {len(rods_without_bait)} SEM isca")
                _safe_print(f"   📊 Total de slots a preencher: {len(slots_to_fill)}")
                if len(rods_with_bait) < len(slots_to_fill):
                    _safe_print(f"   ⚠️ Varas COM isca insuficientes! Vai precisar usar {len(slots_to_fill) - len(rods_with_bait)} varas SEM isca")

                # PASSO 4: PROCESSAR SLOTS DA ESQUERDA → DIREITA (1,2,3,4,5,6)
                _safe_print(f"\n🔧 PASSO 4: Processando slots sequencialmente (1→6)...")

                for slot in slots_to_fill:
                    # Se slot tem vara quebrada, limpar primeiro
                    if slot in broken_slots:
                        _safe_print(f"   ❌ Slot {slot}: Removendo vara quebrada...")
                        self._process_broken_rod(slot)

                    # Preencher com nova vara do baú
                    if all_rods:
                        rod = all_rods.pop(0)  # Pegar primeira vara disponível
                        _safe_print(f"   🎣 Slot {slot}: Colocando {rod['template']} ({'COM' if rod['has_bait'] else 'SEM'} isca)")
                        self._drag_rod_to_slot(rod['position'], slot)

                        # Se vara não tem isca, anotar para aplicar depois
                        if not rod['has_bait']:
                            no_bait_slots.append(slot)
                    else:
                        _safe_print(f"   ⚠️ Slot {slot}: Sem varas disponíveis no baú")

                # PASSO 5: RE-DETECTAR STATUS para saber exatamente quais slots precisam de isca
                _safe_print(f"\n🔍 PASSO 5a: Re-detectando status após preencher slots...")
                time.sleep(1.0)
                updated_rod_status = self.rod_viewer.analyze_rods_background(force_analysis=True)
                _safe_print(f"📊 STATUS ATUALIZADO: {updated_rod_status}")

                # ✅ COMBINAR: Slots detectados SEM isca + slots que arrastamos SEM isca
                # Isso garante que varas arrastadas sem isca SEMPRE recebam isca, mesmo se detectadas incorretamente
                detected_no_bait = [slot for slot in range(1, 7) if updated_rod_status.get(slot) == "without_bait"]
                all_no_bait_slots = list(set(detected_no_bait + no_bait_slots))  # União sem duplicatas
                all_no_bait_slots.sort()  # Ordenar da esquerda para direita

                _safe_print(f"   ⚠️ Slots SEM isca (APÓS preencher): {all_no_bait_slots}")
                if no_bait_slots:
                    _safe_print(f"   📝 Incluindo slots arrastados SEM isca: {no_bait_slots}")

                if all_no_bait_slots and available_baits:
                    _safe_print(f"\n🥩 PASSO 5: Aplicando iscas nos slots: {all_no_bait_slots}")
                    _safe_print(f"   📊 Sistema de prioridade: Usa TODAS as iscas de maior prioridade primeiro")

                    # ✅ NOVA LÓGICA: Usar TODAS as iscas de uma prioridade antes de passar para próxima
                    # available_baits já está ordenado por prioridade (1, 2, 3, ...)
                    bait_index = 0

                    for slot in all_no_bait_slots:
                        if bait_index >= len(available_baits):
                            _safe_print(f"   ⚠️ Slot {slot}: Sem mais iscas disponíveis (usadas {bait_index}/{len(available_baits)})")
                            break

                        # ✅ APLICAR ISCA: Se está na lista all_no_bait_slots, DEVE receber isca
                        bait = available_baits[bait_index]
                        _safe_print(f"   🎯 Slot {slot}: Aplicando {bait['type']} (prioridade {bait['priority']})")
                        self._drag_bait_to_slot(bait['position'], slot)
                        bait_index += 1
                elif all_no_bait_slots and not available_baits:
                    _safe_print(f"\n⚠️ PASSO 5: Slots {all_no_bait_slots} precisam de isca, mas não há iscas no baú!")
                elif not all_no_bait_slots:
                    _safe_print(f"\n✅ PASSO 5: Todos os slots já têm isca!")

                # PASSO 6: VERIFICAÇÃO FINAL (opcional, sem delay)
                _safe_print("\n✅ PASSO 6: Verificação final...")
                final_status = self._analyze_all_slots()

                for slot in range(1, 7):
                    status = final_status.get(slot, "unknown")
                    icon = {"with_bait": "✅", "without_bait": "⚠️", "broken": "❌", "empty": "⚪"}.get(status, "❓")
                    _safe_print(f"   Slot {slot}: {icon} {status}")

                # ❌ DEBUG DESATIVADO: Screenshots não são mais salvos (economizar espaço em disco)
                # self._save_maintenance_screenshot("final_manutencao")

                # PASSO 9: Fechar baú (só se foi nós que abrimos)
                if not chest_already_open:
                    _safe_print("📦 PASSO 9: Fechando baú via ChestManager...")
                    # ✅ USAR APENAS ChestManager.close_chest() para consistência!
                    # (igual feeding/cleaning)
                    if not self.chest_manager.close_chest("Manutenção concluída"):
                        _safe_print("⚠️ Falha ao fechar baú, mas manutenção foi concluída")
                else:
                    _safe_print("📦 PASSO 9: ✅ Baú permanece aberto (controlado por coordenador)")

                self.stats['successful_maintenances'] += 1
                self.last_maintenance_time = time.time()

                # ✅ CORREÇÃO CRÍTICA: NÃO resetar contadores durante manutenção!
                # Os contadores (rod_uses) são usados para determinar QUANDO TROCAR DE PAR.
                # Eles devem ser resetados APENAS quando o par é realmente trocado (confirm_pair_switch),
                # NÃO durante manutenção (que apenas recarrega isca).
                #
                # Exemplo com rod_switch_limit=3:
                # - Peixe #1 slot 1: rod_uses[1]=1
                # - Peixe #2 slot 2: rod_uses[2]=1
                # - Manutenção (recarrega isca) → rod_uses DEVE permanecer [1]=1, [2]=1
                # - Peixe #3 slot 1: rod_uses[1]=2
                # - Peixe #4 slot 2: rod_uses[2]=2
                # - Peixe #5 slot 1: rod_uses[1]=3 → TROCA PAR → reset apenas NOVO par
                #
                # if self.rod_manager:
                #     _safe_print("\n🔄 Resetando contadores de uso após manutenção...")
                #     self.rod_manager.reset_pair_uses_after_maintenance()

                _safe_print("✅ MANUTENÇÃO COMPLETA FINALIZADA COM SUCESSO!")
                _safe_print("="*70)
                return True

        except Exception as e:
            _safe_print(f"❌ Erro na manutenção: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.maintenance_in_progress = False
            # Tentar fechar baú em caso de erro (só se foi nós que abrimos)
            if not chest_already_open:
                try:
                    _safe_print("📦 Fechando baú via ChestManager...")
                    # ✅ USAR APENAS ChestManager para consistência!
                    self.chest_manager.close_chest("Manutenção finalizada")
                except:
                    pass

    # ❌ MÉTODO REMOVIDO: _open_chest_for_maintenance()
    # MOTIVO: Causava conflito com ChestManager (dois sistemas tentando controlar ALT)
    # SOLUÇÃO: Usar APENAS ChestManager.open_chest() para todas as operações de baú
    # BUG CORRIGIDO: ALT travado e cursor preso em loop infinito

    # ❌ MÉTODO REMOVIDO: _close_chest_after_maintenance()
    # MOTIVO: Usar APENAS ChestManager.close_chest() para consistência
    # Todos os fechamentos de baú devem passar pelo ChestManager


    def _detect_all_rod_status(self) -> Dict[int, str]:
        """
        Detectar status de todas as varas nos slots 1-6

        Baseado na lógica do detect_all_rod_status() do v3
        """
        try:
            rod_status = {}

            _safe_print("📊 Detectando status das varas...")

            # Múltiplas verificações para garantir consistência (como no v3)
            consistent_detections = 0
            max_attempts = 3

            for attempt in range(max_attempts):
                _safe_print(f"   🔍 Tentativa {attempt + 1}/{max_attempts}: Detectando status...")
                current_detection = {}

                for slot in range(1, 7):
                    status = self._detect_single_rod_status(slot)
                    current_detection[slot] = status
                    _safe_print(f"     Slot {slot}: {status}")

                if attempt == 0:
                    rod_status = current_detection
                    consistent_detections = 1
                    _safe_print(f"   📊 Primeira detecção: {rod_status}")
                else:
                    # Verificar consistência
                    if current_detection == rod_status:
                        consistent_detections += 1
                        _safe_print(f"   ✅ Detecção consistente #{consistent_detections}")
                    else:
                        _safe_print(f"   ⚠️ Detecção inconsistente: {current_detection}")
                        rod_status = current_detection

                # Se já temos 2 detecções consistentes, parar
                if consistent_detections >= 2:
                    _safe_print(f"   🎯 {consistent_detections} detecções consistentes - usando resultado")
                    break

                if attempt < max_attempts - 1:
                    time.sleep(0.5)

            _safe_print(f"📊 STATUS FINAL DETECTADO: {rod_status}")
            return rod_status

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar status das varas: {e}")
            return {}

    def _detect_single_rod_status(self, slot: int) -> str:
        """Detectar status de uma vara específica"""
        try:
            if not self.template_engine:
                return "unknown"

            # Verificar vara quebrada primeiro
            broken_result = self.template_engine.detect_template('varaquebrada')
            if broken_result and broken_result.found:
                # Verificar se a detecção está na região do slot
                if self._is_detection_in_slot(broken_result.location, slot):
                    return "broken"

            # Verificar vara com isca
            with_bait_result = self.template_engine.detect_template('varacomisca')
            if with_bait_result and with_bait_result.found:
                if self._is_detection_in_slot(with_bait_result.location, slot):
                    return "with_bait"

            # Verificar vara sem isca
            no_bait_result = self.template_engine.detect_template('varasemisca')
            if no_bait_result and no_bait_result.found:
                if self._is_detection_in_slot(no_bait_result.location, slot):
                    return "without_bait"  # Consistência com RodViewerBackground

            # Se não detectou nada, assumir vazio
            return "empty"

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar status do slot {slot}: {e}")
            return "unknown"

    def _is_detection_in_slot(self, location: Tuple[int, int], slot: int) -> bool:
        """Verificar se uma detecção está na região de um slot específico"""
        try:
            if slot not in self.slot_positions:
                return False

            slot_x, slot_y = self.slot_positions[slot]
            det_x, det_y = location

            # Tolerância de 50 pixels (baseada no v3)
            tolerance = 50

            return (abs(det_x - slot_x) <= tolerance and
                   abs(det_y - slot_y) <= tolerance)

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar detecção no slot {slot}: {e}")
            return False

    def _categorize_rods(self, rod_status: Dict[int, str]) -> Dict:
        """Separar varas por categoria"""
        categories = {
            'broken_slots': [],
            'empty_slots': [],
            'no_bait_slots': [],
            'with_bait_slots': []
        }

        for slot, status in rod_status.items():
            if status == "broken":
                categories['broken_slots'].append(slot)
            elif status == "empty":
                categories['empty_slots'].append(slot)
            elif status == "without_bait":  # Corrigido: RodViewerBackground usa "without_bait"
                categories['no_bait_slots'].append(slot)
            elif status == "with_bait":
                categories['with_bait_slots'].append(slot)

        return categories

    def _print_rod_categories(self, categories: Dict):
        """Imprimir categorização das varas"""
        _safe_print("\n📊 CATEGORIZAÇÃO DAS VARAS:")
        _safe_print(f"   ❌ Quebradas: {categories['broken_slots']}")
        _safe_print(f"   ⚪ Vazios: {categories['empty_slots']}")
        _safe_print(f"   ⚠️ Sem isca: {categories['no_bait_slots']}")
        _safe_print(f"   ✅ Com isca: {categories['with_bait_slots']}")

    def _clean_broken_rods(self, broken_slots: List[int]) -> bool:
        """
        Limpar varas quebradas

        Baseado na lógica EXATA do clean_broken_rods_maintenance() do v3
        """
        try:
            _safe_print("🔧 [MANUTENÇÃO] Removendo varas quebradas...")

            for slot in broken_slots:
                if slot not in self.slot_positions:
                    continue

                # IMPORTANTE: Usar coordenada da DETECÇÃO, não do slot
                detection_pos = self._get_broken_rod_detection_position(slot)
                if not detection_pos:
                    _safe_print(f"⚠️ Não foi possível obter posição da detecção da vara quebrada no slot {slot}")
                    continue

                det_x, det_y = detection_pos
                _safe_print(f"🗑️ Removendo vara quebrada do slot {slot} em detecção ({det_x}, {det_y})")

                # [1] Clique na detecção da vara quebrada (IGUAL V3)
                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'click'):
                    self.input_manager.click(det_x, det_y, button='left')
                else:
                    import pyautogui
                    pyautogui.click(det_x, det_y, button='left')
                time.sleep(0.5)  # Timing do v3

                # [2] Remove isca se houver (clique direito na região da isca) (IGUAL V3)
                bait_x, bait_y = self.bait_position
                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'move_to'):
                    self.input_manager.move_to(bait_x, bait_y)
                else:
                    import pyautogui
                    pyautogui.moveTo(bait_x, bait_y)
                time.sleep(0.3)

                # 🔓 CRÍTICO: SOLTAR ALT antes do clique direito (jogo não permite com ALT!)
                _safe_print(f"       🔓 Soltando ALT temporariamente para clique direito...")
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                else:
                    import pyautogui
                    pyautogui.keyUp('alt')
                time.sleep(0.2)

                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'click'):
                    self.input_manager.click(bait_x, bait_y, button='right')
                else:
                    import pyautogui
                    pyautogui.click(bait_x, bait_y, button='right')
                time.sleep(0.5)  # Timing do v3

                # 🔒 RE-PRESSIONAR ALT após clique direito
                _safe_print(f"       🔒 Re-pressionando ALT...")
                if self.input_manager and hasattr(self.input_manager, 'key_down'):
                    self.input_manager.key_down('ALT')
                else:
                    import pyautogui
                    pyautogui.keyDown('alt')
                time.sleep(0.2)

                # [3] Retornar para vara quebrada
                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'move_to'):
                    self.input_manager.move_to(det_x, det_y)
                else:
                    import pyautogui
                    pyautogui.moveTo(det_x, det_y)
                time.sleep(0.3)

                # [3] Verificar configuração: descartar ou guardar no baú
                action = self._get_broken_rod_action()

                if action == "discard":
                    # DESCARTE: Arrastar vara quebrada para fora (v3 logic EXATO)
                    _safe_print(f"  🗑️ Descartando vara quebrada do slot {slot} - detecção ({det_x}, {det_y})")
                    self._drag_to_discard_area_v3_exact(det_x, det_y)
                else:
                    # GUARDAR: Clique direito na detecção da vara (v3 logic EXATO)
                    _safe_print(f"  💾 Guardando vara quebrada do slot {slot} no baú - detecção ({det_x}, {det_y})")
                    _safe_print(f"     🎯 Método: CLIQUE DIREITO na vara (não slot!)")
                    self._save_to_chest_rightclick_v3_exact(det_x, det_y)

                time.sleep(0.8)  # Aguardar operação completar (como v3)

            _safe_print(f"✅ {len(broken_slots)} varas quebradas processadas")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao limpar varas quebradas: {e}")
            return False

    def _get_broken_rod_action(self) -> str:
        """Obter ação para vara quebrada da configuração"""
        if self.config_manager:
            # Verificar múltiplos locais possíveis da configuração
            action = self.config_manager.get('broken_rod_action')  # Formato direto (config.json)
            if not action:
                action = self.config_manager.get('rod_system.broken_rod_action')  # Formato aninhado
            if not action:
                action = 'save'  # Padrão: salvar no baú

            _safe_print(f"🔧 [CONFIG] Ação para vara quebrada: {action}")
            return action
        return 'save'  # Padrão: salvar

    def _get_broken_rod_detection_position(self, slot: int) -> Optional[Tuple[int, int]]:
        """Obter posição CENTRAL da detecção da vara quebrada no slot especificado"""
        try:
            # Usar o viewer background para obter detecções precisas
            if hasattr(self, 'rod_viewer') and self.rod_viewer:
                # Usar o método direto do template_engine para obter detecções com tamanho
                slot_x, slot_y = self.slot_positions[slot]

                # Procurar templates de vara quebrada
                for template_name in ['varaquebrada', 'nobauquebrada']:
                    try:
                        result = self.template_engine.detect_template(template_name)
                        if result and result.found:
                            # OBTER COORDENADA DO CENTRO (não canto superior esquerdo)
                            corner_x, corner_y = result.location
                            width, height = result.size if hasattr(result, 'size') and result.size else (50, 50)

                            # CALCULAR CENTRO DA DETECÇÃO
                            center_x = corner_x + width // 2
                            center_y = corner_y + height // 2

                            # Verificar se está próximo ao slot (tolerância de 100px)
                            distance = ((center_x - slot_x)**2 + (center_y - slot_y)**2)**0.5
                            if distance < 100:
                                _safe_print(f"  🎯 Detecção de vara quebrada encontrada: {template_name}")
                                _safe_print(f"     📍 Canto: ({corner_x}, {corner_y}) | Centro: ({center_x}, {center_y})")
                                _safe_print(f"     📏 Tamanho: {width}x{height} | Distância do slot: {distance:.1f}px")
                                return (center_x, center_y)  # RETORNAR CENTRO

                    except Exception as e:
                        _safe_print(f"  ⚠️ Erro ao detectar {template_name}: {e}")
                        continue

                _safe_print(f"  ⚠️ Detecção de vara quebrada não encontrada perto do slot {slot} - usando posição do slot")
                return (slot_x, slot_y)
            else:
                # Fallback: usar posição do slot
                return self.slot_positions[slot]

        except Exception as e:
            _safe_print(f"❌ Erro ao obter posição da detecção: {e}")
            # Fallback: usar posição do slot
            return self.slot_positions.get(slot)

    def _drag_to_discard_area_v3_exact(self, from_x: int, from_y: int):
        """Arrastar vara quebrada para região de descarte (LÓGICA EXATA DO V3)"""
        if self.input_manager:
            # Coordenadas EXATAS do v3 para descarte
            discard_x, discard_y = 1400, 1000
            _safe_print(f"     🗑️ Arrastando de ({from_x}, {from_y}) para descarte ({discard_x}, {discard_y})")

            # Sequência EXATA do v3: moveTo → mouseDown → moveTo → mouseUp
            # ✅ USAR ARDUINO via InputManager (drag)
            if self.input_manager and hasattr(self.input_manager, 'drag'):
                self.input_manager.drag(from_x, from_y, discard_x, discard_y, duration=0.7)
            else:
                # Fallback para pyautogui
                import pyautogui
                pyautogui.moveTo(from_x, from_y)
                time.sleep(0.3)
                pyautogui.mouseDown(button='left')
                time.sleep(0.3)
                pyautogui.moveTo(discard_x, discard_y, duration=0.7)
                self.input_manager._focus_game_window()
                pyautogui.mouseUp(button='left')
            time.sleep(0.5)

    def _save_to_chest_rightclick_v3_exact(self, det_x: int, det_y: int):
        """Guardar vara quebrada no baú com clique direito (LÓGICA EXATA DO V3)"""
        if self.input_manager:
            _safe_print(f"     💾 Guardando vara quebrada no baú - sequência completa do v3")

            # Sequência COMPLETA do v3:
            # [1/5] Clicar na vara quebrada (selecionar)
            _safe_print(f"       [1/5] Selecionando vara quebrada em ({det_x}, {det_y})")
            if self.input_manager and hasattr(self.input_manager, 'click'):
                self.input_manager.click(det_x, det_y, button='left')
            else:
                import pyautogui
                pyautogui.click(det_x, det_y, button='left')
            time.sleep(0.3)

            # [2/5] Mover para posição FIXA da isca
            bait_x, bait_y = self.bait_position
            _safe_print(f"       [2/5] Movendo para posição da isca ({bait_x}, {bait_y})")
            if self.input_manager and hasattr(self.input_manager, 'move_to'):
                self.input_manager.move_to(bait_x, bait_y)
            else:
                import pyautogui
                pyautogui.moveTo(bait_x, bait_y)
            time.sleep(0.3)

            # 🔓 CRÍTICO: SOLTAR ALT antes do clique direito (jogo não permite com ALT!)
            _safe_print(f"       🔓 [3.1/5] Soltando ALT temporariamente...")
            if self.input_manager and hasattr(self.input_manager, 'key_up'):
                self.input_manager.key_up('ALT')
            else:
                import pyautogui
                pyautogui.keyUp('alt')
            time.sleep(0.2)

            # [3/5] Remover isca com clique direito
            _safe_print(f"       [3/5] Removendo isca (clique direito)")
            if self.input_manager and hasattr(self.input_manager, 'click'):
                self.input_manager.click(bait_x, bait_y, button='right')
            else:
                import pyautogui
                pyautogui.click(bait_x, bait_y, button='right')
            time.sleep(0.5)

            # [4/5] Retornar para vara quebrada
            _safe_print(f"       [4/5] Retornando para vara quebrada ({det_x}, {det_y})")
            if self.input_manager and hasattr(self.input_manager, 'move_to'):
                self.input_manager.move_to(det_x, det_y)
            else:
                import pyautogui
                pyautogui.moveTo(det_x, det_y)
            time.sleep(0.3)

            # [5/5] Clique direito na vara para guardar no baú (ALT já solto!)
            _safe_print(f"       [5/5] Clique direito na vara para guardar no baú")
            if self.input_manager and hasattr(self.input_manager, 'click'):
                self.input_manager.click(det_x, det_y, button='right')
            else:
                import pyautogui
                pyautogui.click(det_x, det_y, button='right')
            time.sleep(0.8)

            # 🔒 RE-PRESSIONAR ALT após operação completa
            _safe_print(f"       🔒 [5.1/5] Re-pressionando ALT...")
            if self.input_manager and hasattr(self.input_manager, 'key_down'):
                self.input_manager.key_down('ALT')
            else:
                import pyautogui
                pyautogui.keyDown('alt')
            time.sleep(0.2)

    def _drag_to_discard_area(self, from_x: int, from_y: int):
        """Arrastar vara quebrada para região de descarte (LÓGICA EXATA DO V3)"""
        if self.input_manager:
            # Coordenadas EXATAS do v3 para descarte
            discard_x, discard_y = 1050, 650
            _safe_print(f"     🗑️ Arrastando de ({from_x}, {from_y}) para descarte ({discard_x}, {discard_y})")

            # Sequência exata do v3: mouseDown → moveTo → mouseUp
            # ✅ USAR ARDUINO via InputManager (drag)
            if self.input_manager and hasattr(self.input_manager, 'drag'):
                self.input_manager.drag(from_x, from_y, discard_x, discard_y, duration=0.3)
            else:
                # Fallback para pyautogui
                self.input_manager.move_to(from_x, from_y)
                time.sleep(0.3)
                import pyautogui
                pyautogui.mouseDown(button='left')
                time.sleep(0.3)
                pyautogui.moveTo(discard_x, discard_y)
                pyautogui.mouseUp(button='left')

    def _save_to_chest_rightclick(self, slot_x: int, slot_y: int):
        """Guardar vara quebrada no baú com clique direito (LÓGICA EXATA DO V3)"""
        if self.input_manager:
            _safe_print(f"     💾 Clique direito no slot ({slot_x}, {slot_y}) para guardar no baú")

            # Retornar para vara quebrada
            self.input_manager.move_to(slot_x, slot_y)
            time.sleep(0.3)

            # 🔓 CRÍTICO: SOLTAR ALT antes do clique direito
            _safe_print(f"     🔓 Soltando ALT antes do clique direito...")
            if hasattr(self.input_manager, 'key_up'):
                self.input_manager.key_up('ALT')
            else:
                import pyautogui
                pyautogui.keyUp('alt')
            time.sleep(0.2)

            # Clique direito
            self.input_manager.right_click(slot_x, slot_y)
            time.sleep(0.5)

            # 🔒 RE-PRESSIONAR ALT
            _safe_print(f"     🔒 Re-pressionando ALT...")
            if hasattr(self.input_manager, 'key_down'):
                self.input_manager.key_down('ALT')
            else:
                import pyautogui
                pyautogui.keyDown('alt')
            time.sleep(0.2)

    def _refill_empty_slots(self, empty_slots: List[int]) -> bool:
        """
        Repor varas em slots vazios

        Baseado na lógica do fill_empty_slots_from_chest() do v3
        """
        try:
            _safe_print("🎣 [MANUTENÇÃO] Preenchendo slots vazios...")

            # Buscar varas disponíveis no baú
            available_rods = self._find_rods_in_chest()

            if not available_rods:
                _safe_print("⚠️ Nenhuma vara encontrada no baú")
                return False

            _safe_print(f"🎣 Varas disponíveis no baú: {len(available_rods)}")

            # ✅ ESTRATÉGIA OTIMIZADA: Priorizar varas COM isca primeiro
            # Isso reduz o trabalho da Fase 3 (recarregamento de iscas)
            rods_with_bait = [rod for rod in available_rods if rod.get('has_bait', False)]
            rods_without_bait = [rod for rod in available_rods if not rod.get('has_bait', False)]

            # Ordenar cada categoria por confiança (maior confiança primeiro)
            rods_with_bait.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            rods_without_bait.sort(key=lambda x: x.get('confidence', 0), reverse=True)

            _safe_print(f"📊 ESTRATÉGIA DE COLOCAÇÃO PRIORIZADA:")
            _safe_print(f"   🏆 Varas COM isca: {len(rods_with_bait)} (PRIORIDADE MÁXIMA)")
            _safe_print(f"   ⚠️ Varas SEM isca: {len(rods_without_bait)} (prioridade secundária)")
            _safe_print(f"   💡 Lógica: COM isca primeiro = menos trabalho na Fase 3")
            _safe_print(f"   🎯 Cada categoria ordenada por confiança (melhor detecção primeiro)")

            # Log das varas priorizadas
            _safe_print(f"\n📋 ORDEM DE COLOCAÇÃO:")
            for i, rod in enumerate(rods_with_bait, 1):
                _safe_print(f"   {i}. COM ISCA: {rod['template']} (conf: {rod['confidence']:.2f})")

            for i, rod in enumerate(rods_without_bait, len(rods_with_bait) + 1):
                _safe_print(f"   {i}. SEM ISCA: {rod['template']} (conf: {rod['confidence']:.2f})")

            # Usar primeiro varas com isca (menos trabalho depois), depois sem isca
            sorted_rods = rods_with_bait + rods_without_bait

            # Preencher slots vazios COM VERIFICAÇÃO EM TEMPO REAL
            successfully_filled = 0

            for slot in empty_slots:
                if successfully_filled >= len(sorted_rods):
                    _safe_print(f"⚠️ Sem mais varas disponíveis - {successfully_filled} slots preenchidos")
                    break

                # ✅ VERIFICAÇÃO CRÍTICA: Slot ainda está realmente vazio?
                _safe_print(f"\n🔍 Verificando se slot {slot} ainda está vazio...")
                current_slot_status = self._verify_single_slot_status(slot)

                if current_slot_status != "empty":
                    _safe_print(f"⚠️ SLOT {slot} NÃO está mais vazio (status: {current_slot_status}) - PULANDO!")
                    continue

                # Obter próxima vara disponível
                if successfully_filled >= len(sorted_rods):
                    break

                rod = sorted_rods[successfully_filled]
                rod_x, rod_y = rod['position']
                slot_x, slot_y = self.slot_positions[slot]

                bait_status = "com isca" if rod.get('has_bait', False) else "sem isca"
                _safe_print(f"🎣 Movendo vara {bait_status} do baú ({rod_x}, {rod_y}) para slot {slot} ({slot_x}, {slot_y})")

                # Arrastar vara do baú para slot
                if self.input_manager:
                    _safe_print(f"   🐛 [DEBUG] InputManager disponível: {self.input_manager is not None}")
                    _safe_print(f"   🐛 [DEBUG] Chamando input_manager.drag({rod_x}, {rod_y}, {slot_x}, {slot_y})...")
                    self.input_manager.drag(rod_x, rod_y, slot_x, slot_y, duration=0.6)
                    _safe_print(f"   🐛 [DEBUG] Drag completado, aguardando 1.2s...")
                    time.sleep(1.2)  # ✅ Aguardar movimento completar (IGUAL PAGE DOWN)

                    # ✅ VERIFICAÇÃO PÓS-MOVIMENTO: Vara foi colocada com sucesso?
                    post_move_status = self._verify_single_slot_status(slot)
                    if post_move_status != "empty":
                        _safe_print(f"   ✅ Vara colocada com sucesso no slot {slot} (status: {post_move_status})")
                        successfully_filled += 1
                    else:
                        _safe_print(f"   ❌ Falha ao colocar vara no slot {slot} - slot ainda vazio")
                else:
                    successfully_filled += 1  # Assumir sucesso se não tem input_manager

            _safe_print(f"✅ {successfully_filled} slots preenchidos com sucesso de {len(empty_slots)} solicitados")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao preencher slots vazios: {e}")
            return False

    def _verify_single_slot_status(self, slot: int) -> str:
        """
        Verificar status de um slot específico em tempo real

        Returns:
            str: 'empty', 'with_bait', 'without_bait', 'broken'
        """
        try:
            if slot not in self.slot_positions:
                return "unknown"

            slot_x, slot_y = self.slot_positions[slot]
            _safe_print(f"   🔍 Verificando slot {slot} em ({slot_x}, {slot_y})...")

            # Usar o viewer background para verificação rápida e precisa
            if hasattr(self, 'rod_viewer') and self.rod_viewer:
                # Fazer nova análise focada apenas neste slot
                current_detections = self.rod_viewer._detect_all_rod_templates()
                rod_templates = self.rod_viewer.rod_templates

                # Sistema de prioridades igual ao viewer
                best_detection = None
                best_priority = -1

                # Analisar cada detecção encontrada
                for template_name, detections in current_detections.items():
                    template_clean = template_name.replace('.png', '')

                    if template_clean in rod_templates:
                        rod_type = rod_templates[template_clean]
                        priority = self.rod_viewer.rod_priority.get(rod_type, 0)

                        # Verificar cada detecção deste template
                        for det_x, det_y, confidence in detections:
                            # Verificar se está próximo ao slot
                            distance = ((det_x - slot_x)**2 + (det_y - slot_y)**2)**0.5

                            if distance < 100:  # Tolerance igual ao viewer
                                if priority > best_priority:
                                    best_detection = rod_type
                                    best_priority = priority
                                    _safe_print(f"     📍 Detecção: {template_clean} ({rod_type}) conf={confidence:.2f} dist={distance:.1f}")

                if best_detection:
                    _safe_print(f"   ✅ Slot {slot}: {best_detection}")
                    return best_detection
                else:
                    _safe_print(f"   ⚪ Slot {slot}: empty")
                    return "empty"

            # Fallback: assumir vazio se não conseguir detectar
            return "empty"

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar slot {slot}: {e}")
            return "unknown"

    def _check_remaining_empty_slots(self) -> List[int]:
        """
        Verificar quais slots ainda estão vazios após tentativa de preenchimento

        Returns:
            List[int]: Lista de slots que ainda estão vazios
        """
        try:
            remaining_empty = []

            _safe_print(f"   🔍 Verificando status atual de todos os 6 slots...")

            for slot in range(1, 7):
                current_status = self._verify_single_slot_status(slot)
                if current_status == "empty":
                    remaining_empty.append(slot)
                    _safe_print(f"     ⚪ Slot {slot}: AINDA VAZIO")
                else:
                    _safe_print(f"     ✅ Slot {slot}: {current_status}")

            return remaining_empty

        except Exception as e:
            _safe_print(f"❌ Erro ao verificar slots restantes: {e}")
            return []

    def _find_rods_in_chest(self) -> List[Dict]:
        """Encontrar varas no baú usando LÓGICA COMPLETA DO VIEWER (que funciona perfeitamente)"""
        try:
            # ✅ PROTEÇÃO: Se recentemente não encontrou varas, aplicar cooldown
            time_since_last_failure = time.time() - self.last_no_rods_found_time
            if time_since_last_failure < self.no_resources_cooldown:
                remaining = self.no_resources_cooldown - time_since_last_failure
                _safe_print(f"⏸️ [COOLDOWN] Varas não encontradas recentemente. Aguardando {remaining:.0f}s antes de tentar novamente...")
                return []

            _safe_print("🔍 Escaneando varas no baú (LÓGICA COMPLETA DO VIEWER)...")

            # ✅ USAR VIEWER BACKGROUND (que já tem toda a lógica perfeita)
            chest_detections = self.rod_viewer.analyze_rods_background(force_analysis=True)

            # Agora vamos usar o viewer para detectar varas ESPECIFICAMENTE na área do baú
            rods = self._extract_rods_from_viewer_analysis()

            # ✅ REGISTRAR FALHA se não encontrou nada
            if not rods:
                self.last_no_rods_found_time = time.time()
                _safe_print(f"⚠️ [COOLDOWN] Nenhuma vara encontrada - cooldown de {self.no_resources_cooldown}s ativado")

            return rods

        except Exception as e:
            _safe_print(f"❌ Erro ao encontrar varas no baú: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_rods_from_viewer_analysis(self) -> List[Dict]:
        """Extrair varas do baú - SIMPLES: pega TUDO que detectar e depois filtra por posição"""
        try:
            rods = []

            # Templates de vara (EXATOS do viewer)
            rod_templates = self.rod_viewer.rod_templates

            _safe_print(f"🔍 Escaneando TODAS as varas (SEM FILTRO DE ÁREA - igual viewer)...")

            # ✅ USAR DETECÇÃO MÚLTIPLA (mesmo método do rod_viewer_background)
            current_detections = self.rod_viewer._detect_all_rod_templates()

            # PRIMEIRO: Pegar TODAS as detecções (sem filtrar por área ainda)
            all_detections = []

            # Processar cada detecção encontrada
            for template_name, detections in current_detections.items():
                template_clean = template_name.replace('.png', '')

                if template_clean in rod_templates:
                    rod_type = rod_templates[template_clean]

                    # Processar TODAS as detecções deste template
                    for center_x, center_y, confidence in detections:
                        # ✅ CONVERTER coordenadas da CAPTURA para coordenadas do JOGO
                        game_x, game_y = self._convert_to_game_coords(center_x, center_y)

                        all_detections.append({
                            'x': game_x,  # ✅ Coordenadas DO JOGO
                            'y': game_y,  # ✅ Coordenadas DO JOGO
                            'type': rod_type,
                            'template': template_clean,
                            'confidence': confidence
                        })

            # AGORA: Separar detecções por região (inventário vs baú)
            _safe_print(f"\n📊 Total de detecções: {len(all_detections)}")

            # Agrupar por região usando coordenadas DO JOGO
            chest_detections = []
            inventory_detections = []

            for det in all_detections:
                # Baú: X=1214-1834, Y=117-928 (coordenadas EXATAS do v3)
                if 1214 <= det['x'] <= 1834 and 117 <= det['y'] <= 928:
                    chest_detections.append(det)
                # Inventário: X=633-1233, Y=541-953 (coordenadas do jogo)
                elif 633 <= det['x'] <= 1233 and 541 <= det['y'] <= 953:
                    inventory_detections.append(det)

            _safe_print(f"   📦 Detecções no BAÚ (X=1214-1834): {len(chest_detections)}")
            _safe_print(f"   🎒 Detecções no INVENTÁRIO (X=633-1233): {len(inventory_detections)}")

            # Processar varas do baú
            for det in chest_detections:
                # ❌ FILTRAR VARAS QUEBRADAS - NÃO INCLUIR!
                if det['type'] == 'broken':
                    _safe_print(f"   🚫 Vara quebrada ignorada: {det['template']} em ({det['x']}, {det['y']})")
                    continue

                has_bait = (det['type'] == 'with_bait')

                rod_info = {
                    'position': (det['x'], det['y']),
                    'has_bait': has_bait,
                    'type': det['type'],
                    'template': det['template'],
                    'confidence': det['confidence']
                }

                rods.append(rod_info)
                bait_status = "COM ISCA" if has_bait else "SEM ISCA"
                det_info = f"Det=({det.get('detection_x', '?')},{det.get('detection_y', '?')})" if 'detection_x' in det else ""
                _safe_print(f"   ✅ Vara no baú: {det['template']} - {bait_status} | Jogo=({det['x']},{det['y']}) {det_info}")

            # ✅ FILTRAR DUPLICATAS (varas próximas são provavelmente a mesma)
            filtered_rods = self._remove_duplicate_rods(rods)

            # Log final
            with_bait = [r for r in filtered_rods if r['has_bait']]
            without_bait = [r for r in filtered_rods if not r['has_bait']]

            _safe_print(f"📊 RESULTADO DO ESCANEAMENTO:")
            _safe_print(f"   📦 Total varas detectadas: {len(filtered_rods)}")
            _safe_print(f"   🏆 COM isca: {len(with_bait)} varas")
            _safe_print(f"   ⚠️ SEM isca: {len(without_bait)} varas")

            return filtered_rods

        except Exception as e:
            _safe_print(f"❌ Erro ao extrair varas do viewer: {e}")
            return []

    def _remove_duplicate_rods(self, rods: List[Dict]) -> List[Dict]:
        """
        Remover varas duplicatas (detecções próximas da mesma vara)

        CRÍTICO: Mesma vara pode ser detectada por múltiplos templates:
        - varacomisca (3204,995)
        - namaocomisca (3199,995)  ← Diferença de 5px apenas!
        - comiscanamao (3198,994)  ← É A MESMA VARA!
        """
        if not rods:
            return rods

        filtered = []
        DISTANCE_THRESHOLD = 20  # Pixels - MAIS RESTRITIVO (antes era 50)
        # Se varas estão a menos de 20px de distância, são a mesma vara

        for rod in rods:
            rod_x, rod_y = rod['position']
            is_duplicate = False

            # Verificar se já temos uma vara muito próxima
            for existing in filtered:
                exist_x, exist_y = existing['position']
                distance = ((rod_x - exist_x)**2 + (rod_y - exist_y)**2)**0.5

                if distance < DISTANCE_THRESHOLD:
                    # É duplicata - manter a com maior confiança
                    _safe_print(f"   🔍 Duplicata detectada: {rod['template']} em ({rod_x},{rod_y}) vs {existing['template']} em ({exist_x},{exist_y}) | dist={distance:.1f}px")

                    if rod['confidence'] > existing['confidence']:
                        # Substituir pela vara com maior confiança
                        _safe_print(f"      → Mantendo {rod['template']} (conf={rod['confidence']:.2f} > {existing['confidence']:.2f})")
                        filtered.remove(existing)
                        filtered.append(rod)
                    else:
                        _safe_print(f"      → Mantendo {existing['template']} (conf={existing['confidence']:.2f} >= {rod['confidence']:.2f})")

                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(rod)

        if len(rods) != len(filtered):
            _safe_print(f"   🧹 Duplicatas removidas: {len(rods)} varas → {len(filtered)} varas únicas")
            _safe_print(f"      Varas finais:")
            for i, rod in enumerate(filtered, 1):
                _safe_print(f"         {i}. {rod['template']} em ({rod['position'][0]},{rod['position'][1]}) conf={rod['confidence']:.2f}")

        return filtered

    def _reload_bait_for_slots(self, slots_needing_bait: List[int]) -> bool:
        """
        Recarregar iscas para varas

        Baseado na lógica do reload_rods_without_bait() do v3
        """
        try:
            _safe_print("🥩 [MANUTENÇÃO] Recarregando varas sem isca...")

            # Buscar iscas disponíveis no baú
            available_baits = self._find_baits_in_chest()

            if not available_baits:
                _safe_print("⚠️ Nenhuma isca encontrada no baú")
                return False

            _safe_print(f"🥩 Iscas disponíveis: {len(available_baits)}")

            # APLICAR ISCAS COM VERIFICAÇÃO EM TEMPO REAL
            baits_applied = 0

            for slot in slots_needing_bait:
                if baits_applied >= len(available_baits):
                    _safe_print(f"⚠️ Sem mais iscas disponíveis - {baits_applied} iscas aplicadas")
                    break

                # ✅ VERIFICAÇÃO CRÍTICA: Slot ainda precisa de isca?
                _safe_print(f"\n🔍 Verificando se slot {slot} ainda precisa de isca...")
                current_slot_status = self._verify_single_slot_status(slot)

                if current_slot_status == "with_bait":
                    _safe_print(f"⚠️ SLOT {slot} JÁ TEM ISCA (status: {current_slot_status}) - PULANDO!")
                    continue
                elif current_slot_status == "empty":
                    _safe_print(f"⚠️ SLOT {slot} ESTÁ VAZIO (sem vara) - PULANDO aplicação de isca!")
                    continue
                elif current_slot_status == "broken":
                    _safe_print(f"⚠️ SLOT {slot} TEM VARA QUEBRADA - PULANDO aplicação de isca!")
                    continue
                elif current_slot_status != "without_bait":
                    _safe_print(f"⚠️ SLOT {slot} tem status inesperado ({current_slot_status}) - PULANDO!")
                    continue

                # Slot realmente precisa de isca - aplicar
                bait = available_baits[baits_applied]
                bait_x, bait_y = bait['position']
                bait_type = bait['type']
                slot_x, slot_y = self.slot_positions[slot]

                _safe_print(f"🥩 Aplicando {bait_type} na vara SEM ISCA do slot {slot}")
                _safe_print(f"   🎯 DRAG & DROP: isca ({bait_x}, {bait_y}) → vara ({slot_x}, {slot_y})")

                # DRAG & DROP da isca do baú DIRETAMENTE para a vara (IGUAL V3)
                if self.input_manager:
                    _safe_print(f"   🐛 [DEBUG] InputManager disponível: {self.input_manager is not None}")
                    _safe_print(f"   🐛 [DEBUG] Chamando _execute_drag_drop_bait_v3_exact...")
                    success = self._execute_drag_drop_bait_v3_exact(bait_x, bait_y, slot_x, slot_y, slot)
                    _safe_print(f"   🐛 [DEBUG] Resultado drag: {success}")
                    if success:
                        # ✅ VERIFICAÇÃO PÓS-APLICAÇÃO: Isca foi aplicada com sucesso?
                        time.sleep(0.8)  # Aguardar aplicação completar
                        post_bait_status = self._verify_single_slot_status(slot)
                        if post_bait_status == "with_bait":
                            _safe_print(f"   ✅ Isca {bait_type} aplicada com sucesso no slot {slot}")
                            baits_applied += 1
                        else:
                            _safe_print(f"   ❌ Falha na aplicação - slot {slot} ainda: {post_bait_status}")
                    else:
                        _safe_print(f"   ❌ Falha no drag & drop da isca {bait_type} no slot {slot}")
                else:
                    baits_applied += 1  # Assumir sucesso se não tem input_manager

            _safe_print(f"✅ {baits_applied} iscas aplicadas com sucesso de {len(slots_needing_bait)} slots solicitados")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao recarregar iscas: {e}")
            return False

    def _execute_drag_drop_bait_v3_exact(self, bait_x: int, bait_y: int, slot_x: int, slot_y: int, slot: int) -> bool:
        """🎣 Executar operação de drag & drop IGUAL ao sistema da tecla '0' do V3"""
        try:
            _safe_print(f"   🎯 DRAG & DROP IGUAL TECLA '0' - Processo robusto")

            # ✅ USAR ARDUINO via InputManager (drag)
            if self.input_manager and hasattr(self.input_manager, 'drag'):
                _safe_print(f"   🚀 Usando InputManager.drag() com Arduino")
                success = self.input_manager.drag(bait_x, bait_y, slot_x, slot_y, duration=1.0)
                if success:
                    _safe_print(f"   ✅ DRAG & DROP COMPLETO: Isca aplicada no slot {slot}")
                    time.sleep(0.6)  # Aguardar aplicação completar
                    return True
                else:
                    _safe_print(f"   ⚠️ Drag via InputManager falhou, tentando fallback...")
                    # Continua para fallback pyautogui abaixo

            # Fallback para pyautogui se InputManager não disponível ou falhou
            _safe_print(f"   ⚠️ Usando pyautogui fallback para drag & drop")
            import pyautogui
            original_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False

            try:
                # PASSO 1: Movimento inicial LENTO para isca (igual V3)
                _safe_print(f"   1️⃣ [MOVIMENTO] Movendo para ISCA: ({bait_x}, {bait_y})")
                pyautogui.moveTo(bait_x, bait_y, duration=0.5)  # Movimento mais lento
                time.sleep(0.5)  # Aguardar chegada completa

                # PASSO 2: Segurar botão esquerdo FIRME (igual V3)
                _safe_print(f"   2️⃣ [PEGAR] Segurando isca FIRMEMENTE")
                pyautogui.mouseDown(button='left')
                time.sleep(0.4)  # Aguardar pegar firme

                # PASSO 3: Arrastar com duração controlada (igual V3)
                _safe_print(f"   3️⃣ [ARRASTO] Arrastando para vara slot {slot}: ({slot_x}, {slot_y})")
                pyautogui.moveTo(slot_x, slot_y, duration=1.0)  # Arrasto mais lento e seguro
                time.sleep(0.4)  # Aguardar chegada

                # PASSO 4: Soltar com confirmação (igual V3)
                _safe_print(f"   4️⃣ [APLICAR] Soltando isca sobre vara - slot {slot}")
                self.input_manager._focus_game_window()  # Garantir foco
                pyautogui.mouseUp(button='left')
                time.sleep(0.4)  # Aguardar completar

                # PASSO 5: Validação visual (igual V3)
                _safe_print(f"   5️⃣ [VALIDAR] Aguardando isca ser aplicada...")
                time.sleep(0.2)

                _safe_print(f"   ✅ DRAG & DROP COMPLETO: Isca aplicada no slot {slot}")
                return True

            finally:
                # CRÍTICO: Garantir que mouse não fique pressionado
                try:
                    self.input_manager._focus_game_window()
                    pyautogui.mouseUp(button='left')
                except:
                    pass
                # Restaurar fail-safe
                pyautogui.FAILSAFE = original_failsafe

        except Exception as e:
            _safe_print(f"❌ Erro no drag & drop para slot {slot}: {e}")
            # CRÍTICO: Garantir que mouse não fique pressionado
            try:
                import pyautogui
                pyautogui.mouseUp(button='left')
            except:
                pass
            return False

    def _find_baits_in_chest(self) -> List[Dict]:
        """Encontrar iscas no baú usando LÓGICA COMPLETA DO VIEWER"""
        try:
            # ✅ PROTEÇÃO: Se recentemente não encontrou iscas, aplicar cooldown
            time_since_last_failure = time.time() - self.last_no_baits_found_time
            if time_since_last_failure < self.no_resources_cooldown:
                remaining = self.no_resources_cooldown - time_since_last_failure
                _safe_print(f"⏸️ [COOLDOWN] Iscas não encontradas recentemente. Aguardando {remaining:.0f}s antes de tentar novamente...")
                return []

            _safe_print("🔍 Escaneando iscas no baú (LÓGICA COMPLETA DO VIEWER)...")

            baits = []

            if not self.template_engine:
                return baits

            # ✅ ISCAS USANDO CONFIGURAÇÃO DA UI (prioridades e enabled)
            bait_config = self._get_bait_configuration()

            _safe_print(f"🎯 Usando configuração de iscas da UI:")
            for bait_name, config in bait_config.items():
                enabled_status = "✅" if config['enabled'] else "❌"
                _safe_print(f"   {enabled_status} {bait_name}: prioridade {config['priority']}")

            # Mapeamento de templates para nomes da configuração (baseado em arquivos EXISTENTES)
            template_to_config_name = {
                # Carnés existentes
                'carneurso': 'carne de urso',     # carneurso.png existe
                'carnedelobo': 'carne de lobo',   # carnedelobo.png existe

                # Trutas existentes
                'TROUTT': 'trout',                # TROUTT.png existe

                # Iscas existentes
                'grub': 'grub',                   # grub.png existe
                'minhoca': 'worm',                # minhoca.png existe

                # Outros peixes
                'crocodilo': 'crocodilo',         # crocodilo.png existe
                'anchovy': 'anchovy',             # anchovy.png existe
                'herring': 'herring',             # herring.png existe
                'roughy': 'roughy',               # roughy.png existe
                'shark': 'shark',                 # shark.png existe
                'yellowperch': 'yellowperch',     # yellowperch.png existe
                'catfish': 'catfish',             # catfish.png existe
                'peixecru': 'peixecru',           # peixecru.png existe
                'sardine': 'sardine',             # sardine.png existe

                # Comidas processadas
                'filefrito': 'filefrito',         # filefrito.png existe

                # Items especiais
                'BONE': 'BONE',                   # BONE.png existe
                'bullet': 'bullet',               # bullet.png existe
                'fat': 'fat',                     # fat.png existe
                'flare': 'flare',                 # flare.png existe
                'SALMONN': 'SALMONN'              # SALMONN.png existe
            }

            # Área do baú - VALORES FIXOS DO V3
            CHEST_AREA = {
                'x_min': 1214,  # Início do baú (v3)
                'x_max': 1834,  # Fim do baú (v3)
                'y_min': 117,   # Topo do baú (v3)
                'y_max': 928    # Base do baú (v3)
            }

            _safe_print(f"📐 Área do baú: X={CHEST_AREA['x_min']}-{CHEST_AREA['x_max']}, Y={CHEST_AREA['y_min']}-{CHEST_AREA['y_max']}")

            # Detectar cada template de isca USANDO CONFIGURAÇÃO DA UI
            for template_name, config_name in template_to_config_name.items():
                # Verificar se esta isca está habilitada na UI
                if config_name not in bait_config or not bait_config[config_name]['enabled']:
                    continue

                try:
                    result = self.template_engine.detect_template(template_name)
                    if result and result.found:
                        bait_x, bait_y = result.location

                        # ✅ CONVERTER coordenadas de DETECÇÃO para coordenadas de CLIQUE
                        game_x, game_y = self._convert_detection_to_game_coords(bait_x, bait_y)

                        # Verificar se está NO BAÚ (não no inventário!)
                        # Baú: X=1214-1834, Y=117-928 (valores EXATOS do v3)
                        if (CHEST_AREA['x_min'] <= game_x <= CHEST_AREA['x_max'] and
                            CHEST_AREA['y_min'] <= game_y <= CHEST_AREA['y_max']):

                            bait_obj = {
                                'position': (game_x, game_y),  # ✅ Coordenadas convertidas
                                'type': config_name,
                                'template': template_name,
                                'priority': bait_config[config_name]['priority'],
                                'confidence': result.confidence,
                                'detection_pos': (bait_x, bait_y)  # DEBUG: original
                            }

                            baits.append(bait_obj)
                            _safe_print(f"   ✅ Isca: {config_name} | Det=({bait_x},{bait_y}) → Jogo=({game_x},{game_y}) | Prior={bait_config[config_name]['priority']}, Conf={result.confidence:.2f}")

                except Exception as e:
                    # Ignorar erros de templates específicos
                    continue

            # ✅ FILTRAR DUPLICATAS (iscas próximas são provavelmente a mesma)
            filtered_baits = self._remove_duplicate_baits(baits)

            # Ordenar por prioridade (menor número = maior prioridade)
            filtered_baits.sort(key=lambda x: x['priority'])

            _safe_print(f"📊 RESULTADO DO ESCANEAMENTO DE ISCAS:")
            _safe_print(f"   🎣 Total iscas detectadas: {len(filtered_baits)}")

            if filtered_baits:
                _safe_print("   📋 Iscas por prioridade:")
                for i, bait in enumerate(filtered_baits, 1):
                    _safe_print(f"      {i}. {bait['type']} (prioridade {bait['priority']})")
            else:
                # ✅ REGISTRAR FALHA se não encontrou nada
                self.last_no_baits_found_time = time.time()
                _safe_print(f"⚠️ [COOLDOWN] Nenhuma isca encontrada - cooldown de {self.no_resources_cooldown}s ativado")

            return filtered_baits

        except Exception as e:
            _safe_print(f"❌ Erro ao encontrar iscas no baú: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _remove_duplicate_baits(self, baits: List[Dict]) -> List[Dict]:
        """Remover iscas duplicatas (detecções próximas da mesma isca)"""
        if not baits:
            return baits

        filtered = []
        DISTANCE_THRESHOLD = 30  # Pixels - iscas mais próximas que isso são consideradas duplicatas

        for bait in baits:
            bait_x, bait_y = bait['position']
            is_duplicate = False

            # Verificar se já temos uma isca muito próxima
            for existing in filtered:
                exist_x, exist_y = existing['position']
                distance = ((bait_x - exist_x)**2 + (bait_y - exist_y)**2)**0.5

                if distance < DISTANCE_THRESHOLD:
                    # É duplicata - manter a com maior prioridade (menor número)
                    if bait['priority'] < existing['priority']:
                        # Substituir pela isca com maior prioridade
                        filtered.remove(existing)
                        filtered.append(bait)
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(bait)

        if len(baits) != len(filtered):
            _safe_print(f"   🧹 Duplicatas de iscas removidas: {len(baits)} → {len(filtered)} iscas")

        return filtered

    def _get_bait_configuration(self) -> Dict[str, Dict]:
        """Obter configuração de iscas da UI (prioridades e enabled)"""
        try:
            if not self.config_manager:
                return self._get_default_bait_config()

            # Obter configuração de prioridade da UI (estrutura correta: bait_system.priority e bait_system.enabled)
            bait_priorities = self.config_manager.get('bait_system.priority', {})
            bait_enabled = self.config_manager.get('bait_system.enabled', {})

            _safe_print(f"🎯 [CONFIG] Prioridades lidas: {bait_priorities}")
            _safe_print(f"🎯 [CONFIG] Iscas habilitadas: {bait_enabled}")

            # Combinar prioridade e enabled
            bait_config = {}
            for bait_name in bait_priorities.keys():
                bait_config[bait_name] = {
                    'priority': bait_priorities.get(bait_name, 99),  # 99 = baixa prioridade
                    'enabled': bait_enabled.get(bait_name, True)
                }

            # Se não temos configuração, usar padrão
            if not bait_config:
                _safe_print("⚠️ [CONFIG] Configuração vazia - usando padrão")
                return self._get_default_bait_config()

            _safe_print(f"✅ [CONFIG] Configuração final de iscas: {bait_config}")
            return bait_config

        except Exception as e:
            _safe_print(f"❌ Erro ao obter configuração de iscas: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_bait_config()

    def _get_default_bait_config(self) -> Dict[str, Dict]:
        """Configuração padrão de iscas baseada nos templates existentes"""
        return {
            'crocodilo': {'priority': 1, 'enabled': True},
            'carne de urso': {'priority': 2, 'enabled': True},
            'carne de lobo': {'priority': 3, 'enabled': True},
            'trout': {'priority': 6, 'enabled': True},
            'grub': {'priority': 4, 'enabled': True},
            'worm': {'priority': 5, 'enabled': True},
            'smalltrout': {'priority': 3, 'enabled': True}
        }

    def _print_final_verification(self, final_status: Dict[int, str]):
        """Imprimir verificação final"""
        _safe_print("🔍 VERIFICAÇÃO FINAL:")
        for slot in range(1, 7):
            status = final_status.get(slot, "unknown")
            status_icon = {
                "broken": "❌",
                "empty": "⚪",
                "without_bait": "⚠️",
                "with_bait": "✅",
                "unknown": "❓"
            }.get(status, "❓")
            _safe_print(f"   Slot {slot}: {status_icon} {status}")

    def get_maintenance_stats(self) -> Dict:
        """Obter estatísticas de manutenção"""
        stats = self.stats.copy()
        stats['last_maintenance_time'] = self.last_maintenance_time
        stats['maintenance_in_progress'] = self.maintenance_in_progress

        if stats['total_maintenances'] > 0:
            stats['success_rate'] = stats['successful_maintenances'] / stats['total_maintenances']
        else:
            stats['success_rate'] = 0.0

        return stats

    def _camera_turn_in_game(self, dx, dy):
        """Movimento de câmera usando API Windows - IMPLEMENTAÇÃO EXATA DO V3"""
        import ctypes
        from ctypes import wintypes
        import time

        _safe_print(f"   🎮 Movimento no jogo: DX={dx}, DY={dy}")

        try:
            # Estruturas Windows para SendInput (IGUAL AO V3)
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [("dx", wintypes.LONG),
                           ("dy", wintypes.LONG),
                           ("mouseData", wintypes.DWORD),
                           ("dwFlags", wintypes.DWORD),
                           ("time", wintypes.DWORD),
                           ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    _fields_ = [("mi", MOUSEINPUT)]
                _fields_ = [("type", wintypes.DWORD),
                           ("_input", _INPUT)]

            # Constantes
            INPUT_MOUSE = 0
            MOUSEEVENTF_MOVE = 0x0001

            # Dividir movimento em passos menores para suavidade
            steps = 10
            dx_step = dx // steps
            dy_step = dy // steps

            for i in range(steps):
                # Criar input
                x = INPUT()
                x.type = INPUT_MOUSE
                x._input.mi.dx = dx_step
                x._input.mi.dy = dy_step
                x._input.mi.dwFlags = MOUSEEVENTF_MOVE
                x._input.mi.time = 0
                x._input.mi.dwExtraInfo = None

                # Enviar input
                ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
                time.sleep(0.01)  # Pequeno delay entre movimentos

            # Movimento restante
            remainder_x = dx - (dx_step * steps)
            remainder_y = dy - (dy_step * steps)

            if remainder_x != 0 or remainder_y != 0:
                x = INPUT()
                x.type = INPUT_MOUSE
                x._input.mi.dx = remainder_x
                x._input.mi.dy = remainder_y
                x._input.mi.dwFlags = MOUSEEVENTF_MOVE
                x._input.mi.time = 0
                x._input.mi.dwExtraInfo = None

                ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

            return True

        except Exception as e:
            _safe_print(f"   ❌ Erro na API Windows: {e}")
            return False

    def _save_maintenance_screenshot(self, stage_name: str):
        """
        📸 Capturar e salvar screenshot com marcações visuais para debug

        Args:
            stage_name: Nome do estágio da manutenção (ex: "inicio", "apos_limpeza", etc)
        """
        try:
            import mss
            import cv2
            import numpy as np
            from datetime import datetime
            import os

            _safe_print(f"\n📸 Capturando screenshot: {stage_name}...")

            # Capturar tela inteira
            with mss.mss() as sct:
                monitor = sct.monitors[0]
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # Adicionar marcações visuais
            self._add_visual_markers(img)

            # ✅ CORRIGIDO: Salvar em data/screenshots/maintenance/ (padrão do sistema)
            screenshots_dir = "data/screenshots/maintenance"
            if not os.path.exists(screenshots_dir):
                os.makedirs(screenshots_dir)

            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{screenshots_dir}/{timestamp}_{stage_name}.png"

            # Salvar imagem
            cv2.imwrite(filename, img)
            _safe_print(f"   ✅ Screenshot salvo: {filename}")

            # Informações da resolução
            height, width = img.shape[:2]
            _safe_print(f"   📐 Resolução: {width}x{height}")

            # Detectar e mostrar onde estão os elementos
            self._log_detected_elements(img)

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao salvar screenshot: {e}")

    def _add_visual_markers(self, img):
        """Adicionar marcações visuais no screenshot"""
        try:
            import cv2
            height, width = img.shape[:2]

            # Cores para marcações
            COLOR_INVENTORY = (0, 255, 0)     # Verde para inventário
            COLOR_CHEST = (255, 0, 0)         # Azul para baú
            COLOR_SLOT = (0, 255, 255)        # Amarelo para slots
            COLOR_TEXT = (255, 255, 255)      # Branco para texto

            # Desenhar área do inventário
            cv2.rectangle(img,
                        (self.inventory_area['left'], self.inventory_area['top']),
                        (self.inventory_area['left'] + self.inventory_area['width'],
                         self.inventory_area['top'] + self.inventory_area['height']),
                        COLOR_INVENTORY, 2)
            cv2.putText(img, "INVENTARIO",
                       (self.inventory_area['left'], self.inventory_area['top'] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_INVENTORY, 2)

            # Desenhar área do baú
            cv2.rectangle(img,
                        (self.chest_area['left'], self.chest_area['top']),
                        (self.chest_area['left'] + self.chest_area['width'],
                         self.chest_area['top'] + self.chest_area['height']),
                        COLOR_CHEST, 2)
            cv2.putText(img, "BAU",
                       (self.chest_area['left'], self.chest_area['top'] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_CHEST, 2)

            # Desenhar slots
            for slot, (x, y) in self.slot_positions.items():
                cv2.circle(img, (x, y), 20, COLOR_SLOT, 2)
                cv2.putText(img, str(slot), (x - 10, y + 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_SLOT, 2)

            # Adicionar informações
            info_text = f"Coordenadas Fixas V3 | Resolucao: {width}x{height}"
            cv2.putText(img, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_TEXT, 2)

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao adicionar marcações: {e}")

    def _log_detected_elements(self, img):
        """Logar informações sobre elementos detectados no screenshot"""
        try:
            _safe_print(f"\n   📊 ANÁLISE DO SCREENSHOT:")
            _safe_print(f"   • Área do Inventário: X={self.inventory_area['left']}-{self.inventory_area['left']+self.inventory_area['width']}, Y={self.inventory_area['top']}-{self.inventory_area['top']+self.inventory_area['height']}")
            _safe_print(f"   • Área do Baú: X={self.chest_area['left']}-{self.chest_area['left']+self.chest_area['width']}, Y={self.chest_area['top']}-{self.chest_area['top']+self.chest_area['height']}")
            _safe_print(f"   • Slots configurados:")
            for slot, (x, y) in self.slot_positions.items():
                _safe_print(f"     Slot {slot}: ({x}, {y})")
            _safe_print("")  # ✅ CORRIGIDO: passar string vazia ao invés de nada

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao logar elementos: {e}")

    def _analyze_all_slots(self) -> Dict[int, str]:
        """Analisar status de todos os 6 slots - SIMPLES"""
        _safe_print("   🔍 Detectando varas em todos os slots...")
        slot_status = {}

        # Fazer detecção completa uma vez
        detections = self.rod_viewer._detect_all_rod_templates()

        for slot in range(1, 7):
            slot_x, slot_y = self.slot_positions[slot]
            best_match = None
            best_distance = float('inf')

            # Procurar detecção mais próxima do slot
            for template_name, dets in detections.items():
                template_clean = template_name.replace('.png', '')
                if template_clean in self.rod_viewer.rod_templates:
                    rod_type = self.rod_viewer.rod_templates[template_clean]

                    for x, y, conf in dets:
                        distance = ((x - slot_x)**2 + (y - slot_y)**2)**0.5
                        if distance < 100 and distance < best_distance:
                            best_match = rod_type
                            best_distance = distance

            slot_status[slot] = best_match if best_match else "empty"

        return slot_status

    def _process_broken_rod(self, slot: int):
        """Processar uma vara quebrada - remover isca e descartar/guardar"""
        try:
            slot_x, slot_y = self.slot_positions[slot]
            _safe_print(f"   🔧 Processando vara quebrada no slot {slot}")

            # Clicar na vara quebrada (LEFT click)
            self.input_manager.click(slot_x, slot_y)
            time.sleep(0.3)

            # 🔓 CRÍTICO: SOLTAR ALT antes dos cliques direitos
            _safe_print(f"   🔓 Soltando ALT antes dos cliques direitos...")
            if hasattr(self.input_manager, 'key_up'):
                self.input_manager.key_up('ALT')
            else:
                import pyautogui
                pyautogui.keyUp('alt')
            time.sleep(0.2)

            # Remover isca (clique direito na posição da isca)
            bait_x, bait_y = self.bait_position
            self.input_manager.right_click(bait_x, bait_y)
            time.sleep(0.3)

            # Descartar ou guardar conforme configuração
            action = self._get_broken_rod_action()
            if action == "discard":
                # Arrastar para fora do inventário
                discard_x, discard_y = self.discard_position
                self.input_manager.drag(slot_x, slot_y, discard_x, discard_y, duration=0.6)
                time.sleep(1.2)  # ✅ Aguardar movimento completar (IGUAL PAGE DOWN)
            else:
                # Clique direito para guardar no baú
                self.input_manager.right_click(slot_x, slot_y)
                time.sleep(0.5)  # ✅ Aguardar ação completar

            # 🔒 RE-PRESSIONAR ALT
            _safe_print(f"   🔒 Re-pressionando ALT...")
            if hasattr(self.input_manager, 'key_down'):
                self.input_manager.key_down('ALT')
            else:
                import pyautogui
                pyautogui.keyDown('alt')
            time.sleep(0.2)

            _safe_print(f"   ✅ Vara quebrada {action}")

        except Exception as e:
            _safe_print(f"   ❌ Erro ao processar vara quebrada: {e}")

    def _scan_chest_for_rods(self) -> List[Dict]:
        """Escanear baú por varas disponíveis - SIMPLES"""
        rods = []
        detections = self.rod_viewer._detect_all_rod_templates()

        for template_name, dets in detections.items():
            template_clean = template_name.replace('.png', '')
            if template_clean in self.rod_viewer.rod_templates:
                rod_type = self.rod_viewer.rod_templates[template_clean]

                # Ignorar varas quebradas
                if rod_type == 'broken':
                    continue

                # Processar cada detecção
                for x, y, conf in dets:
                    # ✅ CONVERTER coordenadas da CAPTURA para coordenadas do JOGO
                    game_x, game_y = self._convert_to_game_coords(x, y)

                    # Verificar se está NO BAÚ usando coordenadas DO JOGO
                    # Baú: X=1214-1834, Y=117-928 (valores EXATOS do v3)
                    if 1214 <= game_x <= 1834 and 117 <= game_y <= 928:
                        rods.append({
                            'position': (game_x, game_y),  # ✅ Coordenadas DO JOGO
                            'has_bait': rod_type == 'with_bait',
                            'template': template_clean,
                            'confidence': conf
                        })
                        _safe_print(f"   🎣 Vara no BAÚ: {template_clean} | Captura=({x},{y}) → Jogo=({game_x},{game_y})")

        return rods

    def _scan_chest_for_baits(self) -> List[Dict]:
        """Escanear baú por iscas disponíveis - DETECTAR TODAS AS OCORRÊNCIAS"""
        baits = []
        bait_config = self._get_bait_configuration()

        # Mapeamento template → nome do config
        # Config usa: crocodilo, bigcat, carneurso, carnedelobo, TROUTT, grub, minhoca
        template_to_config = {
            'crocodilo': 'crocodilo',
            'bigcat': 'bigcat',
            'carneurso': 'carneurso',
            'carnedelobo': 'carnedelobo',
            'TROUTT': 'TROUTT',
            'grub': 'grub',
            'minhoca': 'minhoca'
        }

        # Templates de iscas (ordem de prioridade)
        bait_templates = ['crocodilo', 'bigcat', 'carneurso', 'carnedelobo', 'TROUTT', 'grub', 'minhoca']

        _safe_print(f"🔍 Escaneando TODAS as iscas (múltiplas ocorrências)...")

        for template in bait_templates:
            config_name = template_to_config.get(template, template)

            # ✅ VERIFICAR SE A ISCA ESTÁ HABILITADA
            bait_info = bait_config.get(config_name, {})
            is_enabled = bait_info.get('enabled', True)
            priority = bait_info.get('priority', 99)

            if not is_enabled:
                _safe_print(f"   ⏭️ Isca {template} DESABILITADA - pulando...")
                continue

            # ✅ DETECTAR MÚLTIPLAS OCORRÊNCIAS (não apenas 1!)
            screenshot = self.template_engine.capture_screen()
            if screenshot is None:
                continue

            # Detectar múltiplas ocorrências deste template
            multiple_results = self._detect_multiple_bait_occurrences(template, screenshot)

            for x, y in multiple_results:
                # ✅ CONVERTER coordenadas de CAPTURA para coordenadas de JOGO
                game_x, game_y = self._convert_to_game_coords(x, y)

                # Verificar se está NO BAÚ (não no inventário!)
                # Baú: X=1214-1834, Y=117-928 (valores EXATOS do v3)
                if 1214 <= game_x <= 1834 and 117 <= game_y <= 928:
                    baits.append({
                        'position': (game_x, game_y),  # ✅ Coordenadas convertidas
                        'type': template,
                        'priority': priority,  # ✅ Prioridade REAL do config
                        'detection_pos': (x, y)  # DEBUG: manter original
                    })
                    _safe_print(f"   🥩 Isca no BAÚ: {template} (prioridade {priority}) | Captura=({x},{y}) → Jogo=({game_x},{game_y})")

        # ✅ Ordenar por prioridade (MENOR número = MAIOR prioridade)
        # Isso garante que TODAS as iscas P1 vêm primeiro, depois TODAS as P2, etc.
        baits.sort(key=lambda x: x['priority'])
        bait_order = [f"{b['type']}(P{b['priority']})" for b in baits]
        _safe_print(f"   📊 Ordem final de iscas: {bait_order}")
        _safe_print(f"   ✅ Total de iscas encontradas: {len(baits)}")
        return baits

    def _detect_multiple_bait_occurrences(self, template_name: str, screenshot) -> List[Tuple[int, int]]:
        """Detectar múltiplas ocorrências de uma isca"""
        import cv2
        import numpy as np

        detections = []

        try:
            if not self.template_engine.has_template(template_name):
                return detections

            template = self.template_engine.template_cache.get(template_name)
            if template is None:
                return detections

            # Threshold de confiança
            confidence_threshold = self.template_engine.confidence_config.get(template_name, 0.7)

            # Template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

            # Encontrar todas as localizações acima do threshold
            locations = np.where(result >= confidence_threshold)

            # Obter tamanho do template
            template_height, template_width = template.shape[:2]

            # Processar cada detecção
            for y, x in zip(locations[0], locations[1]):
                # Calcular centro (não canto)
                center_x = x + template_width // 2
                center_y = y + template_height // 2
                detections.append((center_x, center_y))

            # Remover duplicatas próximas (NMS simples)
            filtered = self._remove_close_detections(detections, min_distance=30)

            return filtered

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar {template_name}: {e}")
            return detections

    def _remove_close_detections(self, detections: List[Tuple[int, int]], min_distance: int = 30) -> List[Tuple[int, int]]:
        """Remover detecções muito próximas (duplicatas)"""
        if len(detections) <= 1:
            return detections

        filtered = []

        for det in detections:
            x, y = det
            is_duplicate = False

            # Verificar se já existe uma detecção próxima
            for existing in filtered:
                ex_x, ex_y = existing
                distance = ((x - ex_x)**2 + (y - ex_y)**2)**0.5

                if distance < min_distance:
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(det)

        return filtered

    def _drag_rod_to_slot(self, rod_pos: Tuple[int, int], slot: int):
        """Arrastar vara do baú para slot - IDÊNTICO AO PAGE DOWN"""
        slot_x, slot_y = self.slot_positions[slot]
        rod_x, rod_y = rod_pos

        # ✅ DRAG com duration maior (mais humano)
        self.input_manager.drag(rod_x, rod_y, slot_x, slot_y, duration=0.6)

        # ✅ CRÍTICO: Aguardar o item REALMENTE chegar ao destino
        time.sleep(1.2)

        _safe_print(f"   ⏱️ Aguardado 1.2s após drag (vara → slot {slot})")

    def _drag_bait_to_slot(self, bait_pos: Tuple[int, int], slot: int):
        """Arrastar isca do baú para vara no slot - IDÊNTICO AO PAGE DOWN"""
        slot_x, slot_y = self.slot_positions[slot]
        bait_x, bait_y = bait_pos

        # ✅ DRAG com duration maior (mais humano)
        self.input_manager.drag(bait_x, bait_y, slot_x, slot_y, duration=0.6)

        # ✅ CRÍTICO: Aguardar o item REALMENTE chegar ao destino
        time.sleep(1.2)

        _safe_print(f"   ⏱️ Aguardado 1.2s após drag (isca → slot {slot})")