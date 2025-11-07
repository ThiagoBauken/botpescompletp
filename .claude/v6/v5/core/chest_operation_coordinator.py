#!/usr/bin/env python3
"""
🏪 ChestOperationCoordinator - Sistema de Fila de Prioridades para Operações de Baú

Sistema que coordena TODAS as operações que precisam do baú:
- Alimentação (Prioridade 1 - EXECUTA PRIMEIRO)
- Limpeza de Inventário (Prioridade 2 - EXECUTA SEGUNDO)
- Manutenção de Varas (Prioridade 3 - EXECUTA TERCEIRO)

Garante que o baú seja aberto APENAS UMA VEZ para executar todas as operações necessárias.
"""

import time
import threading
from typing import List, Dict, Any, Callable, Optional
from enum import Enum
from dataclasses import dataclass, field
import pyautogui
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)



class OperationType(Enum):
    """Tipos de operações que usam o baú"""
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    FEEDING = "feeding"


class TriggerReason(Enum):
    """Motivos que triggeram operações"""
    MANUAL = "manual"                    # F6, F5, 0 manual
    INVENTORY_FULL = "inventory_full"    # Inventário cheio
    BROKEN_ROD_DETECTED = "broken_rod"   # Vara quebrada detectada
    TIMEOUT_SINGLE = "timeout_single"    # 1 timeout
    TIMEOUT_DOUBLE = "timeout_double"    # 2 timeouts seguidos
    FEEDING_SCHEDULE = "feeding_schedule" # Tempo/pescas de alimentação


@dataclass
class ChestOperation:
    """Operação que precisa do baú"""
    operation_type: OperationType
    trigger_reason: TriggerReason
    priority: int
    callback: Callable
    context: str = ""
    timestamp: float = field(default_factory=time.time)


class ChestOperationCoordinator:
    """
    🏪 Coordenador Central de Operações de Baú

    Agrupa operações que acontecem SIMULTANEAMENTE para economizar aberturas.
    Se operações chegam em momentos diferentes, cada uma abre/fecha seu próprio baú.
    """

    def __init__(self, config_manager, template_engine=None, feeding_system=None, rod_maintenance_system=None, inventory_manager=None, input_manager=None):
        self.config_manager = config_manager
        self.template_engine = template_engine  # ✅ CORRIGIDO: Adicionar template_engine para verificação de baú
        self.feeding_system = feeding_system
        self.rod_maintenance_system = rod_maintenance_system
        self.inventory_manager = inventory_manager
        self.input_manager = input_manager  # ✅ NOVO: Para atualizar estado interno dos botões

        # Sistema de fila com janela de tempo
        self.operation_queue: List[ChestOperation] = []
        self.queue_lock = threading.RLock()
        self.execution_lock = threading.RLock()

        # Configuração da janela de agrupamento
        self.grouping_window = 2.0  # Segundos - operações dentro desta janela são agrupadas
        self.execution_timer = None

        # Estado
        self.chest_is_open = False
        self.execution_in_progress = False

        # ✅ CORRIGIDO: Prioridades invertidas (menor número = executa PRIMEIRO)
        # ORDEM CORRETA: 1. Alimentação → 2. Limpeza → 3. Manutenção
        self.priorities = {
            OperationType.FEEDING: 1,        # ✅ PRIMEIRO: Alimentação
            OperationType.CLEANING: 2,       # ✅ SEGUNDO: Limpeza
            OperationType.MAINTENANCE: 3     # ✅ TERCEIRO: Manutenção
        }

        # Estatísticas
        self.stats = {
            'total_sessions': 0,
            'individual_operations': 0,
            'grouped_operations': 0,
            'chest_openings_saved': 0,
            'operations_executed': 0,  # Adicionado campo faltando
            'last_execution': 0
        }

        # ✅ NOVO: Tracking de vara removida/para equipar após operações de baú
        self.rod_to_equip_after_pair_switch = None  # Setado por fishing_engine quando par muda

        _safe_print("🏪 ChestOperationCoordinator inicializado com janela de agrupamento de 2s")

    def add_operation(self, operation_type: OperationType, trigger_reason: TriggerReason,
                     callback: Callable, context: str = "") -> bool:
        """
        Adicionar operação com janela de agrupamento

        Se for a primeira operação, inicia timer de 2s para aguardar outras.
        Se chegarem outras operações dentro de 2s, são agrupadas.
        Se não, a operação é executada sozinha.
        """
        try:
            with self.queue_lock:
                # Verificar se já existe operação do mesmo tipo na fila
                existing = [op for op in self.operation_queue if op.operation_type == operation_type]
                if existing:
                    _safe_print(f"⚠️ Operação {operation_type.value} já na fila, ignorando duplicata")
                    return False

                # ✅ CORREÇÃO: Se execução já está em progresso, IGNORAR (evita loop infinito)
                if self.execution_in_progress:
                    _safe_print(f"⏳ Execução em progresso, {operation_type.value} será ignorada (evita loop)")
                    return False  # ✅ CRÍTICO: Retornar False para evitar novas threads

                # Criar nova operação
                operation = ChestOperation(
                    operation_type=operation_type,
                    trigger_reason=trigger_reason,
                    priority=self.priorities[operation_type],
                    callback=callback,
                    context=context
                )

                # Adicionar à fila
                self.operation_queue.append(operation)
                self.operation_queue.sort(key=lambda op: op.priority)

                _safe_print(f"➕ {operation_type.value} adicionada à fila (motivo: {trigger_reason.value})")

                # Se é a primeira operação, iniciar timer de agrupamento
                if len(self.operation_queue) == 1:
                    _safe_print(f"⏱️ Iniciando janela de agrupamento de {self.grouping_window}s...")
                    self._start_grouping_timer()
                else:
                    _safe_print(f"🔄 Operação agrupada! Total na fila: {len(self.operation_queue)}")
                    self._print_queue_status()

                return True

        except Exception as e:
            _safe_print(f"❌ Erro ao adicionar operação: {e}")
            return False

    def _start_grouping_timer(self):
        """Iniciar timer para aguardar outras operações"""
        if self.execution_timer:
            self.execution_timer.cancel()

        self.execution_timer = threading.Timer(self.grouping_window, self._execute_queue)
        self.execution_timer.start()

    def _execute_single_operation(self, operation_type: OperationType, trigger_reason: TriggerReason,
                                callback: Callable, context: str):
        """Executar uma única operação (não agrupada)"""
        try:
            _safe_print(f"\n🔧 EXECUÇÃO INDIVIDUAL: {operation_type.value}")
            _safe_print(f"   Motivo: {trigger_reason.value}")
            _safe_print(f"   Contexto: {context}")

            self.stats['individual_operations'] += 1

            # Abrir baú
            if not self._open_chest():
                _safe_print("❌ Falha ao abrir baú")
                return

            # Aguardar carregamento
            time.sleep(1.5)

            # Executar operação
            try:
                success = callback()
                if success:
                    _safe_print(f"✅ {operation_type.value} executada com sucesso")
                else:
                    _safe_print(f"❌ Falha na {operation_type.value}")
            except Exception as e:
                _safe_print(f"❌ Erro na {operation_type.value}: {e}")

            # Fechar baú
            self._close_chest()

        except Exception as e:
            _safe_print(f"❌ Erro na execução individual: {e}")
            try:
                self._close_chest()
            except:
                pass

    def _print_queue_status(self):
        """Imprimir status atual da fila"""
        if not self.operation_queue:
            _safe_print("📋 Fila vazia")
            return

        _safe_print("📋 Fila atual:")
        for i, op in enumerate(self.operation_queue):
            _safe_print(f"   {i+1}. {op.operation_type.value} (P{op.priority}) - {op.trigger_reason.value}")

    def _execute_queue(self):
        """Executar toda a fila em uma única sessão de baú"""
        try:
            with self.execution_lock:
                if self.execution_in_progress:
                    _safe_print("⚠️ Execução já em progresso, aguardando...")
                    return

                if not self.operation_queue:
                    _safe_print("📋 Fila vazia, nada para executar")
                    return

                self.execution_in_progress = True
                self.stats['total_sessions'] += 1

                _safe_print("\n" + "="*80)
                _safe_print("🏪 EXECUTANDO FILA DE OPERAÇÕES DE BAÚ")
                _safe_print("="*80)

                # ✅ CRÍTICO: PARAR FISHING CYCLE IMEDIATAMENTE (antes de qualquer coisa)
                # Se um segundo ciclo iniciou antes da fila ser processada, PARAR AGORA!
                _safe_print("🛑 [CRITICAL] Parando fishing cycle ANTES de processar fila...")
                try:
                    if self.input_manager:
                        # Parar cliques contínuos
                        if hasattr(self.input_manager, 'stop_continuous_clicking'):
                            self.input_manager.stop_continuous_clicking()
                            _safe_print("   ✅ Cliques contínuos interrompidos")

                        # Parar movimentos A/D
                        if hasattr(self.input_manager, 'stop_camera_movement'):
                            self.input_manager.stop_camera_movement()
                            _safe_print("   ✅ Movimentos A/D interrompidos")

                        # Soltar botões
                        if hasattr(self.input_manager, 'mouse_up'):
                            self.input_manager.mouse_up('right')
                            self.input_manager.mouse_up('left')
                            _safe_print("   ✅ Botões do mouse liberados")

                        # Aguardar threads pararem COMPLETAMENTE
                        time.sleep(0.6)  # ✅ Aumentado de 0.3s para 0.6s (threads precisam parar)
                        _safe_print("   🛡️ Fishing cycle COMPLETAMENTE parado - pronto para operações de baú")
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro ao parar fishing cycle: {e}")

                operations_to_execute = self.operation_queue.copy()
                operations_count = len(operations_to_execute)

                if operations_count == 1:
                    self.stats['individual_operations'] += 1
                    _safe_print("🔧 Executando operação individual")
                else:
                    self.stats['grouped_operations'] += operations_count
                    self.stats['chest_openings_saved'] += operations_count - 1
                    _safe_print(f"🔄 AGRUPAMENTO ATIVO: {operations_count} operações juntas!")
                    _safe_print(f"💡 Economizando {operations_count - 1} aberturas de baú!")

                # PASSO 0: Tirar vara da mão ANTES de abrir baú
                _safe_print("🎣 PASSO 0: Removendo vara da mão antes de abrir baú...")
                rod_to_equip_after = self._remove_rod_from_hand_before_chest()

                # PASSO 1: Abrir baú UMA VEZ
                _safe_print("📦 PASSO 1: Abrindo baú...")
                if not self._open_chest():
                    _safe_print("❌ Falha ao abrir baú - cancelando todas as operações")
                    self._clear_queue()
                    return

                # PASSO 2: Aguardar carregamento
                _safe_print("⏳ PASSO 2: Aguardando carregamento dos itens...")
                time.sleep(1.5)

                # PASSO 3: Executar todas as operações em ordem de prioridade
                _safe_print("🔄 PASSO 3: Executando operações...")

                for i, operation in enumerate(operations_to_execute):
                    _safe_print(f"\n   🔹 Operação {i+1}/{operations_count}: {operation.operation_type.value}")
                    _safe_print(f"     Motivo: {operation.trigger_reason.value}")
                    _safe_print(f"     Contexto: {operation.context}")

                    try:
                        success = operation.callback()
                        if success:
                            _safe_print(f"     ✅ {operation.operation_type.value} executada com sucesso")
                            self.stats['operations_executed'] += 1
                        else:
                            _safe_print(f"     ❌ Falha na {operation.operation_type.value}")
                    except Exception as e:
                        _safe_print(f"     ❌ Erro na {operation.operation_type.value}: {e}")
                    # ✅ REMOVIDO: NÃO soltar ALT após cada operação!
                    # ALT deve ficar pressionado durante FEEDING e MAINTENANCE
                    # Será solto apenas em _close_chest() ANTES de TAB
                    # Isso garante: ALT pressionado → comer → repor iscas → soltar ALT → TAB

                # ✅ MANUTENÇÃO OPORTUNÍSTICA APÓS LIMPEZA/ALIMENTAÇÃO
                # Executar manutenção APENAS se:
                # 1. Foi executada limpeza OU alimentação (automática ou manual)
                # 2. Manutenção NÃO está na fila (evita duplicata)
                # 3. Manutenção é necessária (varas quebradas/vazias/sem isca)
                _safe_print("\n🔍 VERIFICAÇÃO OPORTUNÍSTICA DE MANUTENÇÃO...")

                # Verificar se manutenção já não está na fila OU foi executada
                maintenance_in_queue = any(op.operation_type == OperationType.MAINTENANCE
                                          for op in operations_to_execute)

                # ✅ Detectar se limpeza OU alimentação foram executadas (automáticas ou manuais)
                has_cleaning_or_feeding = any(op.operation_type in [OperationType.CLEANING, OperationType.FEEDING]
                                             for op in operations_to_execute)

                if maintenance_in_queue:
                    _safe_print("   ℹ️ Manutenção já foi executada nesta sessão")
                elif not has_cleaning_or_feeding:
                    _safe_print("   ℹ️ Nenhuma operação de limpeza/alimentação - pulando verificação")
                else:
                    # ✅ Limpeza OU Alimentação executadas - verificar se manutenção é necessária
                    _safe_print("   💡 Limpeza/Alimentação detectada - verificando necessidade de manutenção...")
                    time.sleep(1.0)
                    maintenance_needed = self._check_maintenance_needed()

                    if maintenance_needed:
                        _safe_print("   🔧 Executando manutenção usando lógica do Page Down (baú já aberto)...")

                        # ✅ CRÍTICO: Garantir que fishing cycle está parado ANTES da manutenção
                        # Durante F9, o fishing_engine pode ter REINICIADO cliques/movimentos
                        _safe_print("   🛡️ [SAFETY] Parando fishing cycle ANTES da manutenção oportunística...")
                        try:
                            if self.input_manager:
                                if hasattr(self.input_manager, 'stop_continuous_clicking'):
                                    self.input_manager.stop_continuous_clicking()
                                    _safe_print("      ✅ Cliques contínuos interrompidos")

                                if hasattr(self.input_manager, 'stop_camera_movement'):
                                    self.input_manager.stop_camera_movement()
                                    _safe_print("      ✅ Movimentos A/D interrompidos")

                                # Aguardar threads pararem
                                time.sleep(0.3)
                                _safe_print("      🛡️ Fishing cycle limpo - pronto para arrasto")
                        except Exception as e:
                            _safe_print(f"      ⚠️ Erro ao parar fishing cycle: {e}")

                        try:
                            if self.rod_maintenance_system:
                                # ✅ USAR LÓGICA DO PAGE DOWN
                                maintenance_success = self.rod_maintenance_system.execute_full_maintenance(
                                    chest_already_open=True
                                )

                                if maintenance_success:
                                    _safe_print("   ✅ Manutenção executada com sucesso!")
                                    self.stats['operations_executed'] += 1
                                    self.stats['chest_openings_saved'] += 1  # Economizou 1 abertura!
                                else:
                                    _safe_print("   ⚠️ Manutenção parcial ou sem vara/isca disponível")
                        except Exception as e:
                            _safe_print(f"   ❌ Erro na manutenção oportunística: {e}")
                    else:
                        _safe_print("   ✅ Todas as varas OK - manutenção não necessária")

                # ✅ REMOVIDO: NÃO soltar ALT aqui!
                # ALT deve permanecer pressionado até _close_chest()
                # Sequência: ALT pressionado → operações (feeding/maintenance) → soltar ALT em _close_chest → TAB
                _safe_print("🛡️ [SAFETY] ALT permanece pressionado até fechar baú...")

                # PASSO 4: Fechar baú UMA VEZ
                _safe_print("\n📦 PASSO 4: Fechando baú...")
                self._close_chest()

                # ✅ AGUARDAR baú fechar completamente antes de equipar vara
                _safe_print("⏳ Aguardando baú fechar completamente...")
                time.sleep(1.2)  # ✅ Aumentado de 0.8s para 1.2s (jogo precisa processar fechamento)

                # PASSO 5: Equipar vara APÓS fechar baú (priorizar troca de par)
                _safe_print("\n" + "="*70)
                _safe_print("🎣 PASSO 5: EQUIPANDO VARA APÓS FECHAR BAÚ")
                _safe_print("="*70)
                _safe_print(f"📊 [DEBUG] rod_to_equip_after = {rod_to_equip_after}")
                _safe_print(f"📊 [DEBUG] rod_to_equip_after_pair_switch = {self.rod_to_equip_after_pair_switch}")

                # ✅ PRIORIDADE 1: Troca de par detectada pelo fishing_engine
                if self.rod_to_equip_after_pair_switch:
                    _safe_print(f"\n🔄 [OPÇÃO 1] TROCA DE PAR detectada!")
                    _safe_print(f"   ➡️ Equipando vara {self.rod_to_equip_after_pair_switch}...")
                    success = self._equip_specific_rod_after_chest(self.rod_to_equip_after_pair_switch)
                    _safe_print(f"   📊 Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")

                    # ✅ CONFIRMAR troca de par no rod_manager (aplica mudanças de estado)
                    if self.rod_maintenance_system:
                        rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
                        if rod_manager:
                            _safe_print("   📝 Confirmando troca de par no RodManager...")
                            rod_manager.confirm_pair_switch()

                    # Limpar flag após usar
                    self.rod_to_equip_after_pair_switch = None

                # ✅ PRIORIDADE 2: Escolher PRÓXIMA vara baseado em USOS (não reequipar a mesma!)
                elif rod_to_equip_after:
                    _safe_print(f"\n📍 [OPÇÃO 2] Escolhendo PRÓXIMA vara do par baseado em usos")
                    _safe_print(f"   (Vara removida foi: {rod_to_equip_after})")

                    # Usar equip_next_rod_after_chest() que escolhe baseado em usos!
                    if self.rod_maintenance_system:
                        rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
                        if rod_manager and hasattr(rod_manager, 'equip_next_rod_after_chest'):
                            _safe_print("   🎯 Chamando equip_next_rod_after_chest()...")
                            success = rod_manager.equip_next_rod_after_chest()
                            _safe_print(f"   📊 Resultado: {'✅ Sucesso' if success else '❌ Falhou'}")
                        else:
                            _safe_print("   ⚠️ equip_next_rod_after_chest() não disponível - usando vara removida")
                            success = self._equip_specific_rod_after_chest(rod_to_equip_after)
                    else:
                        _safe_print("   ⚠️ rod_maintenance_system não disponível")
                        success = False

                else:
                    _safe_print("\n⚠️ [OPÇÃO 3] Nenhuma vara para equipar!")
                    _safe_print("   Motivo: rod_to_equip_after = None e rod_to_equip_after_pair_switch = None")
                    _safe_print("   Isso significa que já estava sem vara na mão ANTES de abrir baú")

                _safe_print("="*70)

                # PASSO 6: Limpar fila
                self._clear_queue()

                self.stats['last_execution'] = time.time()

                _safe_print("✅ FILA DE OPERAÇÕES EXECUTADA COM SUCESSO!")
                _safe_print(f"📊 Estatísticas: {self.stats['operations_executed']} operações, "
                      f"{self.stats['chest_openings_saved']} aberturas economizadas")
                _safe_print("="*80)

        except Exception as e:
            _safe_print(f"❌ Erro crítico na execução da fila: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.execution_in_progress = False
            # Tentar fechar baú APENAS se ainda estiver aberto (erro detectado)
            try:
                if self.chest_is_open:
                    _safe_print("🔧 Fechamento de emergência (erro detectado)...")
                    self._close_chest()
            except:
                pass

    def _open_chest(self) -> bool:
        """Abrir baú usando SEQUÊNCIA EXATA DO V3 - open_chest()"""
        _safe_print("\n" + "="*50)
        _safe_print("📦 ABRINDO BAÚ - SEQUÊNCIA ALT+MOVIMENTO+E")
        _safe_print("="*50)

        # ✅ CRÍTICO: Desabilitar fail-safe do PyAutoGUI durante abertura do baú
        # Durante ALT+movimento, o mouse pode ir para canto da tela
        original_failsafe = pyautogui.FAILSAFE
        pyautogui.FAILSAFE = False
        _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI desabilitado temporariamente")

        try:
            # Usar configurações exatas do v3
            chest_side = self.config_manager.get('chest_side', 'left') if self.config_manager else 'left'
            chest_distance = self.config_manager.get('chest_distance', 1200) if self.config_manager else 1200
            _safe_print(f"Config: lado={chest_side}, distância={chest_distance}px")

            # ✅ REMOVIDO: SAFETY preventivo de ALT (desnecessário - vamos pressionar ALT em seguida)
            # Se houvesse ALT preso, o fishing_engine já teria limpado ao parar

            # PASSO 1: ✅ CRÍTICO - Soltar botões do mouse ANTES de ALT
            _safe_print("\n[1/5] Soltando botões do mouse...")
            try:
                # ✅ CRÍTICO: Usar InputManager se disponível para atualizar estado interno
                if self.input_manager and hasattr(self.input_manager, 'mouse_up'):
                    self.input_manager.mouse_up('right')  # Atualiza right_button_down = False
                    self.input_manager.mouse_up('left')   # Atualiza left_button_down = False
                    _safe_print("   🛡️ [SAFETY] Botões liberados via InputManager (estado atualizado)")
                else:
                    # Fallback para pyautogui (não atualiza estado interno)
                    pyautogui.mouseUp(button='left')
                    pyautogui.mouseUp(button='right')
                    pyautogui.mouseUp(button='middle')
                    _safe_print("   ⚠️ [SAFETY] Botões liberados via pyautogui (InputManager não disponível)")
                time.sleep(0.1)
            except Exception as e:
                _safe_print(f"⚠️ Erro ao soltar botões: {e}")

            # PASSO 1.5: ✅ NOVO - PARAR AÇÕES CONTÍNUAS DO FISHING CYCLE (cliques e A/D)
            # CRITICAL: Durante manutenção oportunística, o fishing cycle continua rodando
            # causando cliques e movimentos A/D que interferem nos drags de itens
            _safe_print("\n[1.5/5] Parando ações contínuas do fishing cycle...")
            try:
                if self.input_manager:
                    # Parar cliques contínuos (Phase 2/3 do fishing cycle)
                    if hasattr(self.input_manager, 'stop_continuous_clicking'):
                        self.input_manager.stop_continuous_clicking()
                        _safe_print("   ✅ Cliques contínuos interrompidos")

                    # Parar movimentos A/D (Phase 3 do fishing cycle)
                    # Este método já libera teclas A/D automaticamente
                    if hasattr(self.input_manager, 'stop_camera_movement'):
                        self.input_manager.stop_camera_movement()
                        _safe_print("   ✅ Movimentos A/D interrompidos (teclas liberadas)")

                    _safe_print("   🛡️ [SAFETY] Fishing cycle limpo - pronto para operações de baú")
                    time.sleep(0.2)  # Aguardar threads pararem completamente
                else:
                    _safe_print("   ⚠️ InputManager não disponível - não foi possível parar ações contínuas")
            except Exception as e:
                _safe_print(f"⚠️ Erro ao parar ações contínuas: {e}")

            # PASSO 2: Pressionar ALT via Arduino (se disponível)
            _safe_print("[2/5] Pressionando ALT...")
            if self.input_manager and hasattr(self.input_manager, 'key_down'):
                self.input_manager.key_down('ALT')
                _safe_print("   ✅ ALT pressionado via Arduino")
            else:
                pyautogui.keyDown('alt')
                _safe_print("   ⚠️ ALT pressionado via PyAutoGUI (Arduino não disponível)")
            time.sleep(0.8)  # ✅ Aumentado de 0.5s para 0.8s (Arduino precisa processar)

            # PASSO 3: Calcular deslocamento
            _safe_print("[3/5] Calculando movimento da câmera...")

            # ✅ CORREÇÃO: Windows SendInput com ALT tem eixo X invertido!
            # Positivo = esquerda | Negativo = direita
            if chest_side == 'left':
                delta_x = chest_distance   # POSITIVO = esquerda
            else:
                delta_x = -chest_distance  # NEGATIVO = direita

            _safe_print(f"   Movimento: {chest_side} → {delta_x}px")

            # PASSO 4: Movimento da câmera via ARDUINO
            _safe_print("[4/5] Movendo câmera...")

            # Configuração vertical igual ao v3
            chest_vertical = self.config_manager.get('chest_vertical_offset', 200) if self.config_manager else 200
            dy = abs(chest_vertical)

            # ✅ USAR ARDUINO com MOVE_REL - replica EXATAMENTE a API Windows!
            if delta_x != 0 or dy != 0:
                if self.input_manager and hasattr(self.input_manager, 'move_camera_windows_style'):
                    self.input_manager.move_camera_windows_style(delta_x, dy, steps=10)
                    _safe_print("   ✅ Câmera movida!")
                else:
                    # Fallback para API Windows se Arduino não disponível
                    self._camera_turn_in_game(delta_x, dy)
                    _safe_print("   ⚠️ Câmera movida (fallback)")

            time.sleep(0.3)

            # PASSO 5: Pressionar E via Arduino (se disponível)
            _safe_print("[5/5] Pressionando E...")
            if self.input_manager and hasattr(self.input_manager, 'press_key'):
                self.input_manager.press_key('e')
                _safe_print("   ✅ E pressionado via Arduino")
            else:
                pyautogui.press('e')
                _safe_print("   ⚠️ E pressionado via PyAutoGUI (Arduino não disponível)")
            time.sleep(0.3)  # Aguardar baú abrir

            # ✅ NÃO SOLTAR ALT AQUI!
            # ALT deve ficar pressionado durante TODAS as operações no baú
            # Será solto em _close_chest() ANTES do TAB
            _safe_print("   ⚠️ ALT permanece pressionado durante operações...")
            time.sleep(0.2)

            # ❌ REMOVIDO: pyautogui.moveTo() causava movimento indesejado antes do RESET_POS
            # O jogo já posicionou o mouse em (959, 539) - NÃO MOVER!
            # Deixar mouse onde o jogo colocou para calibração funcionar corretamente

            # Marcar estado como aberto
            self.chest_is_open = True
            _safe_print("\\n✅ BAÚ ABERTO COM SUCESSO!")
            _safe_print("="*50 + "\\n")

            # ✅ Restaurar fail-safe
            pyautogui.FAILSAFE = original_failsafe
            _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado")

            # ✅ CORREÇÃO: NÃO chamar calibrate_mouseto() porque causa movimento!
            # O jogo coloca o mouse em (959, 539) automaticamente
            # O primeiro move_to() para clicar nos slots já sincroniza naturalmente
            _safe_print("")
            _safe_print("✅ [COORDINATOR] Baú aberto, aguardando estabilização...")
            time.sleep(0.5)  # Aguardar jogo posicionar mouse
            _safe_print("")

            return True

        except Exception as e:
            _safe_print(f"\\n❌ ERRO ao abrir baú: {e}")
            _safe_print("   Tentando liberar ALT...")
            try:
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                    _safe_print("   ✅ ALT liberado via Arduino (recuperação de erro)")
                else:
                    pyautogui.keyUp('alt')
                    _safe_print("   ⚠️ ALT liberado via PyAutoGUI (recuperação de erro)")
            except Exception as alt_error:
                _safe_print(f"   ❌ Falha ao liberar ALT: {alt_error}")
            _safe_print("="*50 + "\\n")

            # ✅ Restaurar fail-safe mesmo em caso de erro
            pyautogui.FAILSAFE = original_failsafe
            _safe_print("🛡️ [SAFETY] Fail-safe do PyAutoGUI restaurado (após erro)")
            return False

    def _close_chest(self) -> bool:
        """Fechar baú - usar TAB via Arduino conforme v3"""
        try:
            _safe_print("📦 Fechando baú com TAB...")

            # ✅ CRÍTICO: SEMPRE liberar ALT ANTES de fechar baú (bug do loop infinito de cursor)
            try:
                _safe_print("🛡️ [SAFETY] Liberando ALT antes de TAB...")
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                    _safe_print("   ✅ ALT liberado via Arduino")
                else:
                    pyautogui.keyUp('alt')
                    _safe_print("   ⚠️ ALT liberado via PyAutoGUI")

                # ✅ CRÍTICO: Aguardar 1 SEGUNDO antes de apertar TAB!
                # Usuário confirmou que precisa deste tempo para funcionar
                _safe_print("   ⏳ Aguardando 1 segundo antes de TAB...")
                time.sleep(1.0)  # ← MUDADO: 0.1s → 1.0s
            except Exception as e:
                _safe_print(f"   ⚠️ Erro ao liberar ALT: {e}")

            # Pressionar TAB via Arduino (press_key = pressiona E solta)
            _safe_print("📋 Pressionando TAB ÚNICO para fechar baú...")
            if self.input_manager and hasattr(self.input_manager, 'press_key'):
                # ✅ press_key faz: key_down(TAB) → aguarda 0.05s → key_up(TAB)
                self.input_manager.press_key('TAB')
                _safe_print("   ✅ TAB pressionado e solto via Arduino")

                # ✅ GARANTIR que TAB foi solto com delay extra
                time.sleep(0.15)
                _safe_print("   🛡️ [SAFETY] Aguardando TAB ser processado pelo jogo...")

                # 🔴 CRITICAL FIX: FORCE RELEASE TAB!
                # Enviar KEY_UP:tab diretamente via serial, ignorando keyboard_state
                _safe_print("🔴 [FORCE] Enviando KEY_UP:tab forçado...")
                try:
                    response = self.input_manager._send_command("KEY_UP:tab")
                    _safe_print(f"   📥 Resposta: {response}")
                    # Limpar do keyboard_state se existir
                    if 'tab' in self.input_manager.keyboard_state['keys_down']:
                        self.input_manager.keyboard_state['keys_down'].discard('tab')
                        _safe_print("   🧹 'tab' removido do keyboard_state")
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro no force release: {e}")

            else:
                pyautogui.press('tab')
                _safe_print("   ⚠️ TAB pressionado via PyAutoGUI (Arduino não disponível)")
                time.sleep(0.1)

            # Aguardar baú fechar completamente
            time.sleep(0.6)
            _safe_print("   ✅ Baú fechado, aguardando animação...")

            self.chest_is_open = False

            # ✅ Aguardar animação de fechamento (reduzido para ser mais rápido)
            _safe_print("⏳ Aguardando baú fechar completamente...")
            time.sleep(0.8)  # ✅ REDUZIDO: 1.5s → 0.8s (mais rápido!)

            # ✅ REMOVIDO: Loop de verificação de 5 tentativas (causava delay de 2.5s)
            # O sleep acima já é suficiente para o baú fechar

            return True
        except Exception as e:
            _safe_print(f"❌ Erro ao fechar baú: {e}")
            return False

    def _check_rod_switch_needed(self) -> bool:
        """
        🎣 Verificar se precisa trocar vara APÓS operações de baú

        Returns:
            bool: True se precisa trocar vara
        """
        try:
            if not self.rod_maintenance_system:
                return False

            rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
            if not rod_manager:
                return False

            # ✅ Verificar se há troca pendente (marcada pelo fishing_engine)
            pending_switch = getattr(rod_manager, 'pending_rod_switch', False)

            # ✅ Verificar se precisa trocar por uso/quebra
            needs_switch = rod_manager.needs_rod_switch() if hasattr(rod_manager, 'needs_rod_switch') else False

            # ✅ Verificar se precisa trocar de par
            needs_pair_switch = self._check_pair_switch_needed_after_chest()

            if pending_switch:
                _safe_print("   🔔 Troca de vara pendente detectada (fishing_engine)")
                return True
            elif needs_switch:
                _safe_print("   🔄 Troca de vara necessária (uso/quebra)")
                return True
            elif needs_pair_switch:
                _safe_print("   🔄 Troca de par necessária")
                return True
            else:
                return False

        except Exception as e:
            _safe_print(f"   ❌ Erro ao verificar troca: {e}")
            return False

    def _check_pair_switch_needed_after_chest(self) -> bool:
        """
        🔄 Verificar se precisa trocar de par APÓS fechar baú

        Returns:
            bool: True se precisa trocar de par
        """
        try:
            if not self.rod_maintenance_system:
                return False

            rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
            if not rod_manager:
                return False

            # Chamar método interno de verificação
            if hasattr(rod_manager, '_check_pair_switch_needed'):
                return rod_manager._check_pair_switch_needed()
            else:
                return False

        except Exception as e:
            _safe_print(f"   ❌ Erro ao verificar troca de par: {e}")
            return False

    def _remove_rod_from_hand_before_chest(self) -> int:
        """
        🎣 Remover vara da mão ANTES de abrir baú

        Isso é CRÍTICO para evitar confusão do jogo sobre qual vara está equipada.

        Returns:
            int: Número da vara que foi removida (para equipar depois), ou None
        """
        try:
            if not self.rod_maintenance_system:
                _safe_print("   ⚠️ RodMaintenanceSystem não disponível")
                return None

            rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
            if not rod_manager:
                _safe_print("   ⚠️ RodManager não disponível")
                return None

            # Detectar vara atual na mão
            current_rod = rod_manager.get_current_rod()

            if current_rod:
                _safe_print(f"   🎣 Vara {current_rod} na mão - removendo...")

                # Remover vara usando o método do rod_manager
                success = rod_manager.remove_rod_from_hand(current_rod)

                if success:
                    _safe_print(f"   ✅ Vara {current_rod} removida - vai equipar após baú")
                    return current_rod  # ✅ RETORNA O NÚMERO DA VARA
                else:
                    _safe_print(f"   ⚠️ Falha ao remover vara {current_rod}")
                    return None
            else:
                _safe_print("   ℹ️ Nenhuma vara na mão - pronto para abrir baú")
                return None

        except Exception as e:
            _safe_print(f"   ❌ Erro ao remover vara da mão: {e}")
            return None

    def _equip_specific_rod_after_chest(self, rod_slot: int) -> bool:
        """
        🎣 Equipar uma vara específica APÓS fechar baú

        Args:
            rod_slot: Número do slot da vara (1-6)

        Returns:
            bool: True se equipada com sucesso
        """
        try:
            _safe_print(f"\n🔍 [DEBUG EQUIP] _equip_specific_rod_after_chest chamado para slot {rod_slot}")

            if not self.rod_maintenance_system:
                _safe_print(f"   ❌ rod_maintenance_system não disponível")
                return False

            rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
            if not rod_manager:
                _safe_print(f"   ❌ rod_manager não disponível")
                return False

            _safe_print(f"   🎣 Equipando vara {rod_slot} com botão direito...")
            _safe_print(f"   📍 Chamando rod_manager.equip_rod({rod_slot}, hold_right_button=True)")

            # Equipar vara específica com botão direito pressionado
            success = rod_manager.equip_rod(rod_slot, hold_right_button=True)

            if success:
                _safe_print(f"   ✅ Vara {rod_slot} equipada - botão direito pressionado!")
                return True
            else:
                _safe_print(f"   ⚠️ Falha ao equipar vara {rod_slot}")
                return False

        except Exception as e:
            _safe_print(f"   ❌ Erro ao equipar vara {rod_slot}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _switch_rod_after_chest(self) -> bool:
        """
        🎣 Trocar vara APÓS fechar baú

        Sequência:
        1. Baú já fechado
        2. Trocar vara (switch_rod com will_open_chest=False)
        3. Botão direito já fica pressionado automaticamente

        Returns:
            bool: True se trocada com sucesso
        """
        try:
            if not self.rod_maintenance_system:
                return False

            rod_manager = getattr(self.rod_maintenance_system, 'rod_manager', None)
            if not rod_manager:
                return False

            import inspect
            _safe_print(f"🔢 [LOG COORDINATOR] Chamando switch_rod APÓS fechar baú")
            _safe_print(f"🔢 [LOG COORDINATOR] Caller: ChestOperationCoordinator._switch_rod_after_chest")
            _safe_print("   🔄 Executando troca de vara APÓS fechar baú...")

            # ✅ Trocar vara com will_open_chest=False (baú já fechado)
            # O switch_rod vai automaticamente:
            # 1. Tirar vara atual da mão (slot → inventário)
            # 2. Pegar próxima vara (inventário → mão com botão direito)
            # 3. Manter botão direito pressionado
            success = rod_manager.switch_rod(will_open_chest=False)

            if success:
                _safe_print("   ✅ Vara trocada com sucesso - botão direito pressionado!")
                # Limpar flag de troca pendente (se existir)
                if hasattr(rod_manager, 'pending_rod_switch'):
                    rod_manager.pending_rod_switch = False
                return True
            else:
                _safe_print("   ⚠️ Falha ao trocar vara")
                return False

        except Exception as e:
            _safe_print(f"   ❌ Erro ao trocar vara: {e}")
            return False


    def _check_maintenance_needed(self) -> bool:
        """
        ✅ Verificar se manutenção é necessária (LÓGICA IGUAL AO PAGE DOWN)

        Chamado APÓS feeding/cleaning para aproveitar baú já aberto
        Usa a MESMA lógica do Page Down manual para consistência
        """
        try:
            if not self.rod_maintenance_system:
                return False

            # ✅ USAR RodViewerBackground para análise (IGUAL AO PAGE DOWN)
            rod_viewer = getattr(self.rod_maintenance_system, 'rod_viewer', None)
            if not rod_viewer:
                _safe_print("   ⚠️ RodViewerBackground não disponível")
                return False

            # ✅ Usar check_if_maintenance_needed() - MESMA LÓGICA DO PAGE DOWN
            maintenance_check = rod_viewer.check_if_maintenance_needed()

            if not maintenance_check['maintenance_needed']:
                _safe_print("   ✅ Todas as varas OK - sem necessidade de manutenção")
                return False

            _safe_print(f"   ⚠️ Problemas detectados: {maintenance_check['summary']}")

            if maintenance_check['broken_slots']:
                _safe_print(f"      💥 Varas quebradas: {maintenance_check['broken_slots']}")

            if maintenance_check['empty_slots']:
                _safe_print(f"      ⚪ Slots vazios: {maintenance_check['empty_slots']}")

            if maintenance_check['no_bait_slots']:
                _safe_print(f"      🎣 Sem isca: {maintenance_check['no_bait_slots']}")

            # ✅ EXECUTAR se tiver 1+ problema (quebrada, vazio, sem isca)
            total_problems = len(maintenance_check.get('broken_slots', [])) + \
                           len(maintenance_check.get('empty_slots', [])) + \
                           len(maintenance_check.get('no_bait_slots', []))

            if total_problems > 0:
                _safe_print(f"   💡 MANUTENÇÃO NECESSÁRIA: {total_problems} problema(s) detectado(s)")
                return True
            else:
                _safe_print(f"   ✅ Todas as varas OK - sem necessidade de manutenção")
                return False

        except Exception as e:
            _safe_print(f"   ❌ Erro ao verificar necessidade de manutenção: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _clear_queue(self):
        """Limpar fila de operações"""
        with self.queue_lock:
            self.operation_queue.clear()
            _safe_print("🗑️ Fila de operações limpa")

    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do coordenador"""
        return self.stats.copy()

    def is_execution_in_progress(self) -> bool:
        """Verificar se há execução em progresso"""
        return self.execution_in_progress

    def get_queue_size(self) -> int:
        """Obter tamanho atual da fila"""
        return len(self.operation_queue)

    def has_operation_in_queue(self, operation_type_str: str) -> bool:
        """
        ✅ Verificar se operação específica está na fila (evita duplicatas)

        Args:
            operation_type_str: Nome da operação ('feeding', 'cleaning', 'maintenance')

        Returns:
            bool: True se operação já está na fila
        """
        try:
            with self.queue_lock:
                for op in self.operation_queue:
                    if op.operation_type.value == operation_type_str:
                        return True
                return False
        except Exception as e:
            _safe_print(f"❌ Erro ao verificar fila: {e}")
            return False

    def has_pending_operations(self) -> bool:
        """
        ✅ CRÍTICO: Verificar se há QUALQUER operação pendente na fila

        Usado pelo fishing cycle para aguardar antes de iniciar novo ciclo.

        Returns:
            bool: True se há operações na fila (aguardando timer ou execução)
        """
        try:
            with self.queue_lock:
                return len(self.operation_queue) > 0
        except Exception as e:
            _safe_print(f"❌ Erro ao verificar operações pendentes: {e}")
            return False

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


# Funções de conveniência para integrar com outros sistemas
def trigger_cleaning_operation(coordinator: ChestOperationCoordinator, reason: TriggerReason = TriggerReason.INVENTORY_FULL):
    """Triggerar operação de limpeza"""
    if coordinator.inventory_manager:
        # ✅ CRÍTICO: execute_cleaning() não recebe parâmetros, mas precisa wrapper
        return coordinator.add_operation(
            OperationType.CLEANING,
            reason,
            lambda: coordinator.inventory_manager.execute_cleaning(),
            "Limpeza automática de inventário"
        )
    return False


def trigger_maintenance_operation(coordinator: ChestOperationCoordinator, reason: TriggerReason = TriggerReason.BROKEN_ROD_DETECTED):
    """Triggerar operação de manutenção"""
    if coordinator.rod_maintenance_system:
        return coordinator.add_operation(
            OperationType.MAINTENANCE,
            reason,
            lambda: coordinator.rod_maintenance_system.execute_full_maintenance(chest_already_open=True),
            "Manutenção completa de varas"
        )
    return False


def trigger_feeding_operation(coordinator: ChestOperationCoordinator, reason: TriggerReason = TriggerReason.FEEDING_SCHEDULE):
    """Triggerar operação de alimentação"""
    if coordinator.feeding_system:
        return coordinator.add_operation(
            OperationType.FEEDING,
            reason,
            lambda: coordinator.feeding_system.execute_feeding(chest_already_open=True),
            "Alimentação automática"
        )
    return False