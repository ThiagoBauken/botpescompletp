#!/usr/bin/env python3
"""
🍖 FeedingSystem - Sistema de Alimentação (F6)
Usa ChestManager para coordenação unificada de baú
"""

import time
import pyautogui
from typing import Optional, Dict, Any, Tuple
from enum import Enum
import threading

from .chest_manager import ChestManager, ChestOperation
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

# CRASH-SAFE LOGGER
try:
    from utils.crash_safe_logger import log_debug, log_info, log_warning, log_error, log_state, log_exception
    LOGGER_AVAILABLE = True
except:
    LOGGER_AVAILABLE = False
    def log_debug(m, msg, **k): pass
    def log_info(m, msg, **k): pass
    def log_warning(m, msg, **k): pass
    def log_error(m, msg, **k): pass
    def log_state(m, s): pass
    def log_exception(m, msg, **k): pass



class FeedingMode(Enum):
    AUTO_DETECTION = "detecao_auto"  # Detecção automática via templates
    FIXED_SLOTS = "slots_fixos"      # Posições fixas configuradas


class TriggerMode(Enum):
    TIME_BASED = "time"     # A cada X minutos
    CATCH_BASED = "catches" # A cada X peixes


class FeedingSystem:
    """
    🍖 Sistema de Alimentação Unificado
    
    Baseado na análise do f6_feeding_handler() original
    Usa ChestManager para abertura coordenada do baú
    """
    
    def __init__(self, config_manager, template_engine, chest_manager: ChestManager, game_state=None, input_manager=None):
        self.config_manager = config_manager
        self.template_engine = template_engine
        self.chest_manager = chest_manager
        self.game_state = game_state or {}
        self.input_manager = input_manager  # ✅ NOVO: InputManager para movimento de câmera

        # Estado do sistema
        self.feeding_lock = threading.RLock()
        self.last_feeding_time = 0
        self.fish_count_since_feeding = 0

        # ✅ Estatísticas
        self.stats = {
            'total_feedings': 0,
            'successful_feedings': 0,
            'failed_feedings': 0
        }

        # Registrar callback no ChestManager
        self.chest_manager.register_operation_callback(
            ChestOperation.FEEDING,
            self._on_chest_state_change
        )

        # Configurações padrão baseadas no código original
        self.default_config = {
            'feeding_mode': FeedingMode.FIXED_SLOTS.value,
            'trigger_mode': TriggerMode.CATCH_BASED.value,
            'trigger_minutes': 5,
            'trigger_catches': 3,
            'feeds_per_session': 2,
            'slot_positions': {
                1: [1306, 858],  # Slot1 baseado no original
                2: [1403, 877]   # Slot2 baseado no original
            },
            'eat_position': [1083, 373]  # Posição de comer baseada no original
        }

        # ✅ NOVO: Sistema de análise background para verificar manutenção
        from .rod_viewer_background import RodViewerBackground
        self.rod_viewer = RodViewerBackground(template_engine, config_manager)

    def get_feeding_config(self) -> Dict:
        """Obter configuração atual de alimentação diretamente da UI salva"""
        try:
            if self.config_manager:
                # OBRIGATÓRIO: Pegar valores salvos da UI
                config = {}

                # Obter feeds_per_session da UI (OBRIGATÓRIO)
                feeds_per_session = self.config_manager.get('feeding_system.feeds_per_session')
                if feeds_per_session is not None:
                    config['feeds_per_session'] = int(feeds_per_session)
                    # ✅ Log removido para evitar spam (chamado repetidamente em loop)
                else:
                    # ✅ Log removido para evitar spam (chamado repetidamente em loop)
                    pass

                # Outros valores opcionais
                trigger_mode = self.config_manager.get('feeding_system.trigger_mode')
                if trigger_mode:
                    config['trigger_mode'] = trigger_mode

                trigger_catches = self.config_manager.get('feeding_system.trigger_catches')
                if trigger_catches is not None:
                    config['trigger_catches'] = int(trigger_catches)

                trigger_minutes = self.config_manager.get('feeding_system.trigger_minutes')
                if trigger_minutes is not None:
                    config['trigger_minutes'] = int(trigger_minutes)

                return config
            else:
                _safe_print("❌ ConfigManager não disponível - não pode obter configuração da UI")
                return {}

        except Exception as e:
            _safe_print(f"❌ Erro ao carregar configuração de alimentação: {e}")
            return {}

    def _on_chest_state_change(self, opened: bool, context: str):
        """Callback chamado quando baú abre/fecha para alimentação"""
        if opened:
            _safe_print(f"📦 [FEEDING] Baú aberto para alimentação: {context}")
        else:
            _safe_print(f"📦 [FEEDING] Baú fechado após alimentação: {context}")

    # ✅ MÉTODOS REMOVIDOS: should_trigger_feeding() e increment_fish_count()
    # Lógica de decisão agora está no SERVIDOR (server.py)
    # Cliente apenas executa alimentação quando servidor comandar

    def execute_feeding(self, force=False, chest_already_open=False) -> bool:
        """
        🍖 Executar alimentação completa

        Baseado em find_and_click_food_automatically() do v3 linha 16651
        Lógica EXATA que FUNCIONA no v3

        Args:
            force: Forçar execução mesmo se não for necessário
            chest_already_open: Se True, baú já foi aberto (chamado pelo ChestCoordinator)
        """
        try:
            with self.feeding_lock:
                # ✅ Incrementar contador total
                self.stats['total_feedings'] += 1

                _safe_print("\n" + "="*50)
                _safe_print("🍖 EXECUTANDO ALIMENTAÇÃO AUTOMÁTICA")
                _safe_print("="*50)

                # PASSO 1: Abrir baú apenas se necessário
                if not chest_already_open:
                    _safe_print("📦 PASSO 1: Abrindo baú para alimentação...")
                    log_info("FEEDING", "Usando ChestManager.open_chest() para alimentação")

                    # ✅ USAR APENAS ChestManager para evitar conflito de ALT!
                    if not self.chest_manager.open_chest(ChestOperation.FEEDING, "Alimentação automática"):
                        _safe_print("❌ Falha ao abrir baú")
                        log_error("FEEDING", "ChestManager.open_chest() falhou")
                        return False

                    log_info("FEEDING", "Baú aberto com sucesso via ChestManager")
                    _safe_print("✅ Baú aberto com sucesso")
                else:
                    _safe_print("📦 Baú já está aberto (via ChestCoordinator)")
                    log_info("FEEDING", "Baú já aberto, pula abertura")

                # PASSO 3: Detectar e clicar na comida
                _safe_print("🔍 PASSO 3: Detectando e clicando na comida...")
                food_success = self._execute_food_sequence()

                # PASSO 4: Fechar baú apenas se abrimos aqui
                if not chest_already_open:
                    _safe_print("📦 PASSO 4: Fechando baú...")
                    log_info("FEEDING", "Usando ChestManager.close_chest() para fechar")
                    # ✅ USAR APENAS ChestManager para evitar conflito!
                    self.chest_manager.close_chest("Alimentação concluída")
                    log_info("FEEDING", "Baú fechado com sucesso via ChestManager")
                else:
                    _safe_print("📦 Baú será fechado pelo ChestCoordinator")
                    log_info("FEEDING", "Baú será fechado externamente")

                if food_success:
                    # ✅ Incrementar contador de sucesso
                    self.stats['successful_feedings'] += 1

                    # Resetar contadores
                    self.last_feeding_time = time.time()
                    self.fish_count_since_feeding = 0
                    _safe_print("✅ Alimentação executada com sucesso!")
                    _safe_print("="*50)
                    return True
                else:
                    # ✅ Incrementar contador de falhas
                    self.stats['failed_feedings'] += 1

                    # ✅ CRÍTICO: Resetar contadores para evitar loop infinito
                    # Se não tem comida, não adianta tentar novamente imediatamente
                    _safe_print("⚠️ Falha na alimentação - provavelmente sem comida disponível")
                    _safe_print("🔄 Resetando contadores para evitar tentativas repetidas...")
                    self.last_feeding_time = time.time()
                    self.fish_count_since_feeding = 0

                    _safe_print("❌ Falha na sequência de alimentação")
                    _safe_print("="*50)
                    return False

        except Exception as e:
            # ✅ Incrementar contador de falhas
            self.stats['failed_feedings'] += 1

            # ✅ CRÍTICO: Resetar contadores para evitar loop infinito após erro
            _safe_print("⚠️ Erro na alimentação - resetando contadores...")
            self.last_feeding_time = time.time()
            self.fish_count_since_feeding = 0

            _safe_print(f"❌ Erro na alimentação: {e}")
            log_exception("FEEDING", f"Exception durante alimentação: {e}")
            # Tentar fechar baú em caso de erro APENAS se abrimos aqui
            if not chest_already_open:
                try:
                    _safe_print("📦 Fechando baú após erro...")
                    log_warning("FEEDING", "Fechando baú após erro via ChestManager")
                    self.chest_manager.close_chest("Erro na alimentação")
                except Exception as e2:
                    log_error("FEEDING", f"Erro ao fechar baú após exception: {e2}")
                    pass
            else:
                _safe_print("📦 Erro: baú será fechado pelo ChestCoordinator")
                log_info("FEEDING", "Erro, mas baú será fechado externamente")
            return False
    
    # ❌ MÉTODO REMOVIDO: _open_chest_for_feeding()
    # MOTIVO: Causava conflito com ChestManager (dois sistemas tentando controlar ALT)
    # SOLUÇÃO: Usar APENAS ChestManager.open_chest() para todas as operações de baú
    # BUG CORRIGIDO: ALT travado e cursor preso em loop infinito

    # ❌ MÉTODO REMOVIDO: _close_chest_after_feeding()
    # MOTIVO: Usar APENAS ChestManager.close_chest() para consistência
    # Todos os fechamentos de baú devem passar pelo ChestManager
    
    def _execute_food_sequence(self) -> bool:
        """
        🍖 IMPLEMENTAÇÃO EXATA DO V3: find_and_click_food_automatically()

        Usa o método inteligente com detecção dinâmica do botão eat
        """
        try:
            _safe_print("🔍 Executando alimentação inteligente com detecção dinâmica...")

            # ✅ CRÍTICO: Verificar se há comida disponível ANTES de executar
            food_available = self._detect_food_position()
            if not food_available:
                _safe_print("❌ [FEEDING] Sem comida disponível - abortando alimentação")
                _safe_print("⚠️ [FEEDING] Resetando contadores para evitar loop infinito")
                self.last_feeding_time = time.time()
                self.fish_count_since_feeding = 0

                # ✅ CORREÇÃO BUG #2: Delay para não atrapalhar próxima operação
                # Quando feeding falha rapidamente (< 0.5s), se cleaning vier logo depois
                # não terá tempo de estabilizar UI/screenshot, causando falha no cleaning
                # Solução: Aguardar 1.0s antes de retornar para dar tempo de estabilização
                _safe_print("   ⏳ Aguardando 1.0s para estabilizar...")
                time.sleep(1.0)  # Dar tempo para screenshot/UI estabilizar

                return False

            return self._execute_intelligent_feeding()
        except Exception as e:
            _safe_print(f"❌ Erro na sequência de alimentação: {e}")
            # Resetar contadores para evitar loop
            self.last_feeding_time = time.time()
            self.fish_count_since_feeding = 0
            return False

    def _find_and_click_food_automatically_v3(self) -> bool:
        """
        🔍 IMPLEMENTAÇÃO EXATA DO V3: find_and_click_food_automatically()
        Buscar filé frito E botão eat automaticamente - versão simples e funcional
        """
        try:
            import cv2
            import numpy as np
            import mss
            import os

            _safe_print("🔍 Modo detecção automática - buscando filé frito e botão eat...")

            # PASSO 1: Detectar APENAS filé frito (EXATO DO V3)
            food_templates = [
                ('filefrito.png', 0.75),       # Filé frito (nome principal)
                ('file frito.png', 0.75)       # Filé frito (variação)
                # wolfmeat e carneurso REMOVIDOS - são ISCAS, não comida!
            ]

            # Capturar tela - área do BAÚ (não inventário!)
            # Área do baú conforme config: [1214, 117, 1834, 928]
            with mss.mss() as sct:
                monitor = {
                    "top": 117, "left": 1214,
                    "width": 620, "height": 811  # 1834-1214=620, 928-117=811
                }
                screenshot = sct.grab(monitor)
                screen_img = np.array(screenshot)
                screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

            food_position = None
            food_template_name = None

            # BUSCAR COMIDA no BAÚ (corrigido!)
            _safe_print("   🔍 Buscando filé frito no BAÚ...")
            for template_name, threshold in food_templates:
                try:
                    # Tentar carregar template
                    template_path = f"templates/{template_name}"
                    if not os.path.exists(template_path):
                        template_path = f"fishing_bot_v4/templates/{template_name}"

                    if os.path.exists(template_path):
                        template = cv2.imread(template_path)
                        if template is not None:
                            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
                            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

                            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                            if max_val >= threshold:
                                template_h, template_w = template_gray.shape
                                center_x = max_loc[0] + template_w // 2 + 1214  # Offset do baú
                                center_y = max_loc[1] + template_h // 2 + 117

                                food_position = (center_x, center_y)
                                food_template_name = template_name
                                _safe_print(f"   ✅ {template_name} encontrado em ({center_x}, {center_y}) - confiança: {max_val:.3f}")
                                break
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro com template {template_name}: {e}")
                    continue

            if not food_position:
                _safe_print("   ❌ Nenhuma comida encontrada no BAÚ!")
                return False

            # PASSO 2: Clicar na comida
            _safe_print(f"   🖱️ Clicando na comida ({food_template_name})...")
            # ✅ USAR ARDUINO via InputManager
            if self.input_manager and hasattr(self.input_manager, 'click'):
                self.input_manager.click(food_position[0], food_position[1])
                _safe_print("   ✅ Click via Arduino")
            else:
                import pyautogui
                pyautogui.click(food_position[0], food_position[1])
                _safe_print("   ⚠️ Click via pyautogui (fallback)")
            time.sleep(0.5)

            # PASSO 3: Buscar botão EAT
            _safe_print("   🔍 Buscando botão 'eat'...")
            eat_templates = [
                ('eat.png', 0.7),
                ('eat_button.png', 0.7),
                ('comer.png', 0.7)
            ]

            # Área onde o botão eat aparece (área geral da tela)
            with mss.mss() as sct:
                monitor = {
                    "top": 0, "left": 0,
                    "width": 1920, "height": 1080
                }
                screenshot = sct.grab(monitor)
                screen_img = np.array(screenshot)
                screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

            eat_position = None
            eat_template_name = None

            for template_name, threshold in eat_templates:
                try:
                    template_path = f"templates/{template_name}"
                    if not os.path.exists(template_path):
                        template_path = f"fishing_bot_v4/templates/{template_name}"

                    if os.path.exists(template_path):
                        template = cv2.imread(template_path)
                        if template is not None:
                            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
                            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

                            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                            if max_val >= threshold:
                                template_h, template_w = template_gray.shape
                                center_x = max_loc[0] + template_w // 2
                                center_y = max_loc[1] + template_h // 2

                                eat_position = (center_x, center_y)
                                eat_template_name = template_name
                                _safe_print(f"   ✅ {template_name} encontrado em ({center_x}, {center_y}) - confiança: {max_val:.3f}")
                                break
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro com template {template_name}: {e}")
                    continue

            if not eat_position:
                _safe_print("   ❌ Botão 'eat' não encontrado!")
                return False

            # PASSO 4: Clicar no botão eat múltiplas vezes
            # Pegar valor configurado da UI (OBRIGATÓRIO)
            config = self.get_feeding_config()
            feeds_per_session = config.get('feeds_per_session')
            if feeds_per_session is None:
                _safe_print("❌ [ERRO] feeds_per_session não configurado na UI!")
                return False
            _safe_print(f"   🍖 Clicando 'eat' {feeds_per_session} vezes...")

            for i in range(feeds_per_session):
                _safe_print(f"      Clique {i+1}/{feeds_per_session}")
                # ✅ USAR ARDUINO via InputManager
                if self.input_manager and hasattr(self.input_manager, 'click'):
                    self.input_manager.click(eat_position[0], eat_position[1])
                else:
                    import pyautogui
                    pyautogui.click(eat_position[0], eat_position[1])
                time.sleep(1.5)  # Delay igual ao v3 após clicar eat

            _safe_print("   ✅ Sequência de alimentação automática executada com sucesso!")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro na detecção automática de comida: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _execute_intelligent_feeding(self) -> bool:
        """
        🔍 Sistema de Alimentação Inteligente

        Baseado EXATAMENTE em find_and_click_food_automatically() do botpesca - Copia (19)
        Linha 16211-16390 - 180 linhas de lógica COMPROVADA
        """
        try:
            _safe_print("🔍 Modo detecção automática - buscando filé frito e botão eat...")

            # PASSO 1: Detectar APENAS filé frito (sem iscas!)
            food_templates = [
                ('filefrito', 0.75),  # ✅ Nome correto do template (sem espaço, sem .png)
                # wolfmeat e carneurso REMOVIDOS - são ISCAS, não comida!
            ]

            # Detectar comida primeiro
            food_found = False
            food_position = None

            for template_name, threshold in food_templates:
                if food_found:
                    break

                result = self.template_engine.detect_template(template_name)
                if result and result.found and result.confidence >= threshold:
                    food_position = result.location
                    food_found = True
                    _safe_print(f"✅ COMIDA ENCONTRADA: {template_name} em ({food_position[0]}, {food_position[1]}) - Conf: {result.confidence:.3f}")
                    break

            if not food_found:
                _safe_print("❌ Nenhuma comida encontrada automaticamente")
                return False

            # PASSO 2: Detectar botão 'eat'
            _safe_print("🔍 Procurando botão 'eat' na tela...")
            eat_position = self._detect_eat_button_position()

            if eat_position == [1083, 373]:  # Posição padrão = não encontrou
                _safe_print("⚠️ Botão 'eat' não detectado dinamicamente, usando posição padrão")
            else:
                _safe_print(f"✅ BOTÃO 'EAT' ENCONTRADO DINAMICAMENTE em ({eat_position[0]}, {eat_position[1]})")

            # PASSO 3: Executar sequência de alimentação
            _safe_print("🍽️ Executando sequência de alimentação automática...")

            # Obter quantidade de cliques configurada DA UI (OBRIGATÓRIO)
            config = self.get_feeding_config()
            feed_count = config.get('feeds_per_session')
            if feed_count is None:
                _safe_print("❌ [ERRO] feeds_per_session não configurado na UI!")
                return False
            _safe_print(f"🔢 Configurado para comer {feed_count} vezes")

            # PASSO 1: Clicar UMA vez na comida inicial (como estava antes)
            _safe_print(f"")
            _safe_print(f"🍖 [FEEDING] CLICANDO NA COMIDA INICIAL:")
            _safe_print(f"   📍 Posição: {food_position}")
            _safe_print(f"")
            if not self._click_at_location(food_position):
                _safe_print(f"❌ Erro no clique da comida inicial")
                return False

            _safe_print("⏳ Aguardando 1.0s para UI estabilizar...")
            time.sleep(1.0)

            # PASSO 2: Loop de alimentação - CADA CLIQUE = 1 COMIDA
            # ✅ IMPORTANTE: Botão "eat" MUDA DE POSIÇÃO quando é a última comida!
            # Por isso, DEVEMOS re-detectar a cada clique

            _safe_print(f"🔢 Loop de alimentação: {feed_count} cliques no botão 'eat'")
            _safe_print(f"⚠️ IMPORTANTE: Cada clique no 'eat' = 1 comida consumida")

            successful_feeds = 0  # Contador de comidas efetivamente consumidas
            MAX_FOOD_SEARCH_ATTEMPTS = 2  # ✅ CORREÇÃO: Máximo de tentativas de buscar comida

            for i in range(feed_count):
                _safe_print(f"\n🍽️ === COMIDA {i+1}/{feed_count} ===")

                food_search_attempts = 0  # ✅ CORREÇÃO: Contador de tentativas neste ciclo

                # Loop interno para tentar encontrar eat (máximo 2 tentativas)
                while food_search_attempts < MAX_FOOD_SEARCH_ATTEMPTS:
                    # SEMPRE re-detectar posição do botão eat (pode mudar!)
                    _safe_print(f"🔍 Detectando posição do botão eat (tentativa {food_search_attempts + 1}/{MAX_FOOD_SEARCH_ATTEMPTS})...")
                    eat_position = self._detect_eat_button_position()

                    # ✅ CRÍTICO: Verificar se botão eat foi REALMENTE detectado
                    # Posição [1083, 373] é a posição PADRÃO quando NÃO foi detectado
                    if eat_position == [1083, 373]:
                        food_search_attempts += 1  # ✅ CORREÇÃO: Incrementar tentativas

                        if food_search_attempts >= MAX_FOOD_SEARCH_ATTEMPTS:
                            _safe_print(f"❌ Botão 'eat' não detectado após {MAX_FOOD_SEARCH_ATTEMPTS} tentativas")
                            _safe_print(f"✅ Alimentação concluída: {successful_feeds}/{feed_count} comidas consumidas")
                            break  # Sair do while

                        _safe_print(f"⚠️ Botão 'eat' NÃO detectado - tentando buscar nova comida (tentativa {food_search_attempts}/{MAX_FOOD_SEARCH_ATTEMPTS})...")
                        _safe_print("🔍 Buscando NOVA comida em outro slot...")

                        # RE-DETECTAR comida (busca outro slot com comida)
                        new_food_position = self._detect_food_position()

                        if new_food_position is None:
                            _safe_print(f"❌ Não há mais comida disponível no baú!")
                            _safe_print(f"✅ Alimentação concluída: {successful_feeds}/{feed_count} comidas consumidas")
                            break  # Sair do while

                        _safe_print(f"✅ Nova comida encontrada em: {new_food_position}")
                        _safe_print(f"👆 Clicando na nova comida...")

                        # Clicar na NOVA comida
                        if not self._click_at_location(new_food_position):
                            _safe_print(f"❌ Erro ao clicar na nova comida - abortando")
                            _safe_print(f"✅ Alimentação parcial: {successful_feeds}/{feed_count} comidas consumidas")
                            break  # Sair do while

                        time.sleep(1.0)  # Aguardar UI estabilizar

                        # Atualizar food_position para próximas iterações
                        food_position = new_food_position

                        # Continuar no while para re-detectar eat
                        continue
                    else:
                        # ✅ Eat detectado! Sair do while
                        _safe_print(f"✅ Botão 'eat' detectado em: {eat_position}")
                        break  # Sair do while com sucesso

                # ✅ VERIFICAÇÃO FINAL: Se saiu do while sem detectar eat, ABORTAR FOR
                if eat_position == [1083, 373]:
                    _safe_print(f"❌ Botão 'eat' não foi detectado - ABORTANDO ciclo de alimentação")
                    _safe_print(f"✅ Alimentação final: {successful_feeds}/{feed_count} comidas consumidas")
                    break  # Sair do for

                # Clicar no botão eat (só executa se foi REALMENTE detectado)
                _safe_print(f"✅ Botão 'eat' confirmado em: {eat_position}")
                _safe_print(f"👆 Clicando no eat...")
                if not self._click_at_location(eat_position):
                    _safe_print(f"❌ Erro no clique do eat - abortando")
                    break

                # ✅ Incrementar contador de comidas bem-sucedidas
                successful_feeds += 1

                # Aguardar após eat (obrigatório 1.5s como v3)
                _safe_print(f"⏳ Aguardando 1.5s após eat... ({successful_feeds}/{feed_count} comidas)")
                time.sleep(1.5)

                # Pequena pausa antes do próximo ciclo (apenas se não for o último)
                if i < feed_count - 1:
                    _safe_print("⏳ Pausa de 0.5s antes do próximo ciclo...")
                    time.sleep(0.5)

            # ✅ Log final com contador real de comidas consumidas
            _safe_print(f"✅ Alimentação automática concluída: {successful_feeds}/{feed_count} comidas consumidas")

            # CORREÇÃO: Aguardar após última comida antes de sair
            if successful_feeds > 0:
                _safe_print("⏳ Aguardando 0.5s após última comida...")
                time.sleep(0.5)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro na alimentação inteligente: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _detect_eat_button_position(self, max_attempts=2) -> list:
        """
        Detectar posição do botão 'eat' dinamicamente com múltiplas tentativas

        IMPORTANTE: Botão só aparece APÓS clicar no peixe
        Posição muda apenas quando é a última comida

        Args:
            max_attempts: Número máximo de tentativas (padrão: 2)
        """
        try:
            import cv2
            import numpy as np
            import mss
            import os

            # Templates do botão eat
            eat_templates = [
                ('eat.png', 0.7),
                ('comer.png', 0.7),
                ('eat_button.png', 0.7)
            ]

            # Tentar múltiplas vezes com delay entre tentativas
            for attempt in range(max_attempts):
                if attempt > 0:
                    # Dar tempo para UI carregar entre tentativas
                    time.sleep(0.3)

                # Capturar tela inteira (botão pode aparecer em qualquer lugar)
                with mss.mss() as sct:
                    monitor = {
                        "top": 0, "left": 0,
                        "width": 1920, "height": 1080
                    }
                    screenshot = sct.grab(monitor)
                    screen_img = np.array(screenshot)
                    screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

                for template_name, threshold in eat_templates:
                    try:
                        template_path = f"templates/{template_name}"
                        if not os.path.exists(template_path):
                            template_path = f"fishing_bot_v4/templates/{template_name}"

                        if os.path.exists(template_path):
                            template = cv2.imread(template_path)
                            if template is not None:
                                screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
                                template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

                                result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                                if max_val >= threshold:
                                    template_h, template_w = template_gray.shape
                                    center_x = max_loc[0] + template_w // 2
                                    center_y = max_loc[1] + template_h // 2
                                    _safe_print(f"✅ Botão 'eat' detectado: {template_name} em ({center_x}, {center_y}) - conf: {max_val:.3f}")
                                    return [center_x, center_y]

                    except Exception as e:
                        continue

            # Fallback: posição padrão (indica que NÃO foi detectado)
            _safe_print("⚠️ Botão 'eat' não detectado após múltiplas tentativas")
            return [1083, 373]  # Posição padrão = NÃO DETECTADO

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar botão eat: {e}")
            return [1083, 373]

    def _detect_food_position(self) -> Optional[Tuple[int, int]]:
        """
        Detectar posição de comida disponível (busca no baú E inventário)
        """
        try:
            import cv2
            import numpy as np
            import mss
            import os

            # Detectar templates de comida
            food_templates = [
                ('filefrito.png', 0.75),
                ('file frito.png', 0.75)
            ]

            # BUSCAR PRIMEIRO NO BAÚ
            _safe_print("   🔍 Buscando comida no baú...")
            with mss.mss() as sct:
                # Área do baú
                monitor = {
                    "top": 117, "left": 1214,
                    "width": 620, "height": 811
                }
                screenshot = sct.grab(monitor)
                screen_img = np.array(screenshot)
                screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

            for template_name, threshold in food_templates:
                try:
                    template_path = f"templates/{template_name}"
                    if not os.path.exists(template_path):
                        template_path = f"fishing_bot_v4/templates/{template_name}"

                    if os.path.exists(template_path):
                        template = cv2.imread(template_path)
                        if template is not None:
                            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
                            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

                            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                            if max_val >= threshold:
                                template_h, template_w = template_gray.shape
                                center_x = max_loc[0] + template_w // 2 + 1214  # Offset do baú
                                center_y = max_loc[1] + template_h // 2 + 117
                                _safe_print(f"   ✅ {template_name} encontrada no BAÚ: ({center_x}, {center_y})")
                                return (center_x, center_y)
                except Exception as e:
                    continue

            # SE NÃO ENCONTROU NO BAÚ, BUSCAR NO INVENTÁRIO
            _safe_print("   🔍 Buscando comida no inventário...")
            with mss.mss() as sct:
                # Área do inventário
                monitor = {
                    "top": 541, "left": 633,
                    "width": 600, "height": 412
                }
                screenshot = sct.grab(monitor)
                screen_img = np.array(screenshot)
                screen_img = cv2.cvtColor(screen_img, cv2.COLOR_BGRA2BGR)

            for template_name, threshold in food_templates:
                try:
                    template_path = f"templates/{template_name}"
                    if not os.path.exists(template_path):
                        template_path = f"fishing_bot_v4/templates/{template_name}"

                    if os.path.exists(template_path):
                        template = cv2.imread(template_path)
                        if template is not None:
                            screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)
                            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

                            result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                            if max_val >= threshold:
                                template_h, template_w = template_gray.shape
                                center_x = max_loc[0] + template_w // 2 + 633  # Offset do inventário
                                center_y = max_loc[1] + template_h // 2 + 541
                                _safe_print(f"   ✅ {template_name} encontrada no INVENTÁRIO: ({center_x}, {center_y})")
                                return (center_x, center_y)
                except Exception as e:
                    continue

            _safe_print("   ❌ Comida não encontrada nem no baú nem no inventário")
            return None

        except Exception as e:
            _safe_print(f"❌ Erro ao detectar posição da comida: {e}")
            return None
    
    def _execute_fixed_position_feeding(self, config: Dict) -> bool:
        """
        Executar alimentação usando posições fixas
        
        Coordenadas EXATAS do v3 que FUNCIONAM
        """
        try:
            slot_positions = config['slot_positions']
            eat_position = config['eat_position']
            feeds_per_session = config.get('feeds_per_session', 2)
            
            _safe_print(f"🍖 Executando {feeds_per_session} alimentações...")
            
            # Sequência baseada no v3
            for i in range(feeds_per_session):
                _safe_print(f"  🍖 Alimentação {i+1}/{feeds_per_session}")
                
                # Alternar entre slot1 e slot2
                slot_key = 1 if i % 2 == 0 else 2
                
                if slot_key in slot_positions:
                    x, y = slot_positions[slot_key]
                    _safe_print(f"    📍 Clicando no slot {slot_key}: ({x}, {y})")
                    
                    if self._click_at_position(x, y):
                        time.sleep(0.3)  # Aguardar entre cliques
                    else:
                        _safe_print(f"    ❌ Falha ao clicar no slot {slot_key}")
                        return False
            
            # Clicar no botão "eat"
            _safe_print("🍽️ Clicando no botão 'eat'...")
            eat_x, eat_y = eat_position
            _safe_print(f"    📍 Posição eat: ({eat_x}, {eat_y})")
            
            if self._click_at_position(eat_x, eat_y):
                time.sleep(1.5)  # Delay igual ao v3 após clicar eat
                _safe_print("✅ Sequência de alimentação concluída")
                return True
            else:
                _safe_print("❌ Falha ao clicar no botão eat")
                return False
                
        except Exception as e:
            _safe_print(f"❌ Erro na alimentação por posições fixas: {e}")
            return False
    
    def _click_at_position(self, x: int, y: int) -> bool:
        """Clicar em uma posição específica"""
        try:
            # Tentar usar input manager do chest manager
            input_mgr = None
            
            if hasattr(self, 'input_manager') and self.input_manager:
                input_mgr = self.input_manager
            elif (self.chest_manager and 
                  hasattr(self.chest_manager, 'input_manager') and 
                  self.chest_manager.input_manager):
                input_mgr = self.chest_manager.input_manager
            
            if input_mgr:
                input_mgr.click(x, y)
                return True
            else:
                _safe_print("⚠️ Input manager não disponível para clique")
                return False
                
        except Exception as e:
            _safe_print(f"❌ Erro ao clicar em ({x}, {y}): {e}")
            return False
    
    def _click_at_location(self, location: Tuple[int, int]) -> bool:
        """Clicar em uma localização de template"""
        x, y = location
        return self._click_at_position(x, y)
    
    def _click_eat_button(self) -> bool:
        """Clicar no botão eat detectado por template"""
        try:
            if self.template_engine:
                eat_result = self.template_engine.detect_template('eat')
                if eat_result and eat_result.found:
                    _safe_print(f"🍽️ Botão 'eat' detectado: conf {eat_result.confidence:.3f}")
                    return self._click_at_location(eat_result.location)
            
            # Fallback para posição fixa
            config = self.get_feeding_config()
            eat_x, eat_y = config['eat_position']
            _safe_print(f"🍽️ Usando posição fixa do botão eat: ({eat_x}, {eat_y})")
            return self._click_at_position(eat_x, eat_y)
            
        except Exception as e:
            _safe_print(f"❌ Erro ao clicar no botão eat: {e}")
            return False
    
    def reset_feeding_counters(self):
        """Resetar contadores de alimentação"""
        with self.feeding_lock:
            self.last_feeding_time = time.time()
            self.fish_count_since_feeding = 0
            _safe_print("🔄 Contadores de alimentação resetados")
    
    def get_feeding_stats(self) -> Dict:
        """Obter estatísticas de alimentação"""
        return {
            'last_feeding_time': self.last_feeding_time,
            'fish_count_since_feeding': self.fish_count_since_feeding,
            'feeding_config': self.get_feeding_config()
        }
    
    def manual_trigger(self) -> bool:
        """Trigger manual de alimentação (F6)"""
        _safe_print("🔧 [FEEDING] Trigger manual ativado (F6)")
        return self.execute_feeding(force=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status atual do sistema de alimentação"""
        config = self.get_feeding_config()

        status = {
            'last_feeding_time': self.last_feeding_time,
            'fish_count_since_feeding': self.fish_count_since_feeding,
            'config': config
        }
        
        if config['trigger_mode'] == TriggerMode.TIME_BASED.value:
            minutes_passed = (time.time() - self.last_feeding_time) / 60
            status['minutes_until_next'] = max(0, config['trigger_minutes'] - minutes_passed)
        else:
            status['fish_until_next'] = max(0, config['trigger_catches'] - self.fish_count_since_feeding)
        
        return status

    def _check_maintenance_opportunity(self):
        """
        🔧 Verificar se vale a pena fazer manutenção já que o baú está aberto

        Checa se há:
        - Varas quebradas (PRIORIDADE MÁXIMA)
        - Slots vazios
        - Varas sem isca

        Se encontrar problemas, sugere manutenção.
        """
        try:
            _safe_print("\n🔍 [FEEDING] Verificando oportunidade de manutenção...")

            # Verificar status das varas usando viewer background
            maintenance_check = self.rod_viewer.check_if_maintenance_needed()

            if not maintenance_check['maintenance_needed']:
                _safe_print("✅ [FEEDING] Todas as varas estão em bom estado - sem necessidade de manutenção")
                return

            # Log dos problemas encontrados
            _safe_print(f"⚠️ [FEEDING] Problemas detectados: {maintenance_check['summary']}")

            if maintenance_check['broken_slots']:
                _safe_print(f"   💥 Varas quebradas: {maintenance_check['broken_slots']}")

            if maintenance_check['empty_slots']:
                _safe_print(f"   ⚪ Slots vazios: {maintenance_check['empty_slots']}")

            if maintenance_check['no_bait_slots']:
                _safe_print(f"   🎣 Sem isca: {maintenance_check['no_bait_slots']}")

            # Decisão inteligente baseada na prioridade
            if maintenance_check['maintenance_recommended']:
                _safe_print(f"💡 [FEEDING] RECOMENDAÇÃO: Vale a pena fazer manutenção agora!")
                _safe_print(f"   📊 Score de prioridade: {maintenance_check['priority_score']}/6")
                _safe_print(f"   💰 Economia: Aproveita baú aberto para resolver {maintenance_check['priority_score']} problemas")
                _safe_print(f"   🎯 Dica: Use Page Down para executar manutenção completa")
            else:
                _safe_print(f"ℹ️ [FEEDING] Problemas detectados, mas prioridade baixa ({maintenance_check['priority_score']}/6)")
                _safe_print(f"   💭 Sugestão: Aguardar mais problemas para economia de operações")

        except Exception as e:
            _safe_print(f"❌ [FEEDING] Erro ao verificar manutenção: {e}")
            # Não falhar a alimentação por causa disso
            pass