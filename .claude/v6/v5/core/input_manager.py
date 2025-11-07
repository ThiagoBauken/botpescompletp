#!/usr/bin/env python3
"""
🖱️ InputManager - Sistema de Mouse e Teclado
Ultimate Fishing Bot v4.0

Extraído e baseado nas ações específicas do botpesca - Copia (12).py
"""

import time
import threading
from typing import Tuple, Optional, Callable
import pyautogui
import ctypes
import ctypes.wintypes
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
    from utils.crash_safe_logger import log_debug, log_info, log_warning, log_error, log_state
    LOGGER_AVAILABLE = True
except:
    LOGGER_AVAILABLE = False
    def log_debug(m, msg, **k): pass
    def log_info(m, msg, **k): pass
    def log_warning(m, msg, **k): pass
    def log_error(m, msg, **k): pass
    def log_state(m, s): pass


# Imports para Windows API (win32)
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    _safe_print("⚠️ win32gui não disponível - funcionalidades de foco limitadas")

class InputManager:
    """
    🖱️ Gerenciador de Input - Mouse e Teclado
    
    Baseado nas ações específicas do botpesca que funciona:
    - Mouse press/release para pesca
    - Cliques contínuos
    - Movimentos A/D de câmera
    - Captura de posição inicial
    """
    
    def __init__(self, config_manager=None):
        """Inicializar InputManager"""
        log_info("INPUT_MGR", "Inicializando InputManager...")
        self.config_manager = config_manager

        # Estado atual de inputs
        self.mouse_state = {
            'right_button_down': False,
            'left_button_down': False,
            'last_position': (0, 0)
        }

        self.keyboard_state = {
            'a_pressed': False,
            'd_pressed': False,
            'keys_down': set()
        }

        # Threading para ações contínuas
        self.continuous_actions = {
            'clicking': False,
            'moving_camera': False,
            'pressing_s': False
        }

        # Threads ativas
        self.active_threads = []

        # Configurações de timing (extraídas do botpesca)
        self.timing_config = {
            'click_delay': 1.0 / 12,  # 12 cliques por segundo (padrão)
            'movement_a_duration': (1.2, 1.8),  # Duração movimento A (min, max)
            'movement_d_duration': (1.0, 1.4),  # Duração movimento D (min, max)
            'movement_pause': (0.2, 0.5),       # Pausa entre A/D (min, max)
            'fish_catch_delay': 3.0,             # Delay após capturar peixe
            'phase_transition_delay': 0.1        # Delay entre fases
        }

        # Callbacks para eventos
        self.on_mouse_action: Optional[Callable] = None
        self.on_keyboard_action: Optional[Callable] = None

        # Carregar configurações se disponível
        self._load_config()

        log_state("INPUT_MGR", self.get_state())
        _safe_print("🖱️ InputManager inicializado")
    
    def get_click_delay(self) -> float:
        """
        Obter delay variado para cliques - BASEADO NO BOTPESCA.PY

        CORRIGIDO: Usa clicks_per_second da config como BASE, e aplica
        variação PEQUENA se anti-detecção estiver ativa.

        Exemplo:
        - clicks_per_second = 9 → base_delay = 1/9 = 0.111s
        - Com anti-detecção: varia entre 0.08-0.15s (se configurado)
        - Sem anti-detecção: retorna exatamente 0.111s
        """
        try:
            # SEMPRE usar clicks_per_second da config como base
            if self.config_manager:
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)
                base_delay = 1.0 / clicks_per_second
            else:
                base_delay = self.timing_config['click_delay']

            # Aplicar variação APENAS se anti-detecção estiver ativa
            if self.config_manager:
                anti_detection = self.config_manager.get('anti_detection', {})
                click_variation = anti_detection.get('click_variation', {})

                if click_variation.get('enabled', False):
                    # Usar min/max configurados, MAS garantir que respeita velocidade base
                    min_delay = click_variation.get('min_delay', base_delay * 0.8)
                    max_delay = click_variation.get('max_delay', base_delay * 1.2)

                    import random
                    return random.uniform(min_delay, max_delay)

            # Retornar delay base se sem variação
            return base_delay

        except Exception as e:
            _safe_print(f"⚠️ Erro ao calcular delay: {e}")
            return self.timing_config['click_delay']
    
    def reload_timing_config(self):
        """Recarregar configurações de timing do ConfigManager"""
        try:
            _safe_print("🔄 Recarregando configurações de timing...")
            
            if self.config_manager:
                # Cliques por segundo (atualizado da UI)
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)
                self.timing_config['click_delay'] = 1.0 / clicks_per_second
                
                # Durações de movimento
                anti_detection = self.config_manager.get('anti_detection', {})
                if anti_detection.get('movement_variation', False):
                    # Usar variações se anti-detecção estiver ativa
                    self.timing_config['mouse_move_duration'] = (0.1, 0.3)
                    self.timing_config['key_press_duration'] = (0.05, 0.15)
                else:
                    # Configurações padrão (mais rápido)
                    self.timing_config['mouse_move_duration'] = 0.1
                    self.timing_config['key_press_duration'] = 0.05
                
                # Delays entre ações
                self.timing_config['action_delay'] = anti_detection.get('action_delay', 0.1)
                self.timing_config['fish_catch_delay'] = 3.0  # Fixo para coleta
                
                _safe_print(f"✅ Configurações atualizadas: {clicks_per_second} cliques/s, delay={self.timing_config['click_delay']:.3f}s")
            else:
                _safe_print("⚠️ ConfigManager não disponível para recarregar")
                
        except Exception as e:
            _safe_print(f"❌ Erro ao recarregar timing: {e}")
    
    def _load_config(self):
        """Carregar configurações de timing"""
        try:
            if self.config_manager:
                # Cliques por segundo
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)
                self.timing_config['click_delay'] = 1.0 / clicks_per_second
                
                # Durações de movimento
                anti_detection = self.config_manager.get('anti_detection', {})
                if anti_detection.get('movement_variation', False):
                    # Usar variações se anti-detecção estiver ativa
                    self.timing_config['movement_a_duration'] = (1.2, 1.8)
                    self.timing_config['movement_d_duration'] = (1.0, 1.4)
                else:
                    # Usar valores fixos se anti-detecção estiver desabilitada
                    self.timing_config['movement_a_duration'] = (1.5, 1.5)
                    self.timing_config['movement_d_duration'] = (1.2, 1.2)
                
                _safe_print("✅ Configurações de timing carregadas")
                
        except Exception as e:
            _safe_print(f"⚠️ Erro ao carregar config de timing: {e}")
    
    # ===== MÉTODOS DE MOUSE =====
    
    def start_fishing(self) -> bool:
        """
        Iniciar pesca - Pressionar e manter botão direito
        
        Baseado em: pyautogui.mouseDown(button='right')
        """
        try:
            if not self.mouse_state['right_button_down']:
                self._focus_game_window()
                pyautogui.mouseDown(button='right')
                self.mouse_state['right_button_down'] = True
                _safe_print("🎣 Botão direito pressionado - pesca iniciada")
                
                if self.on_mouse_action:
                    self.on_mouse_action('start_fishing', True)
                
                return True
            else:
                _safe_print("⚠️ Botão direito já está pressionado")
                return False
                
        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar pesca: {e}")
            return False
    
    def stop_fishing(self) -> bool:
        """
        Parar pesca - Soltar botão direito
        
        Baseado em: pyautogui.mouseUp(button='right')
        """
        try:
            if self.mouse_state['right_button_down']:
                self._focus_game_window()
                pyautogui.mouseUp(button='right')
                self.mouse_state['right_button_down'] = False
                _safe_print("🎣 Botão direito solto - pesca parada")
                
                if self.on_mouse_action:
                    self.on_mouse_action('stop_fishing', True)
                
                return True
            else:
                _safe_print("⚠️ Botão direito já está solto")
                return False
                
        except Exception as e:
            _safe_print(f"❌ Erro ao parar pesca: {e}")
            return False
    
    def mouse_down(self, button: str = 'left') -> bool:
        """
        Pressionar e manter botão do mouse
        
        Args:
            button: 'left', 'right', ou 'middle'
        """
        try:
            self._focus_game_window()
            pyautogui.mouseDown(button=button)
            
            # Atualizar estado
            if button == 'right':
                self.mouse_state['right_button_down'] = True
            elif button == 'left':
                self.mouse_state['left_button_down'] = True
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao pressionar botão {button}: {e}")
            return False
    
    def mouse_up(self, button: str = 'left') -> bool:
        """
        Soltar botão do mouse
        
        Args:
            button: 'left', 'right', ou 'middle'
        """
        try:
            self._focus_game_window()
            pyautogui.mouseUp(button=button)
            
            # Atualizar estado
            if button == 'right':
                self.mouse_state['right_button_down'] = False
            elif button == 'left':
                self.mouse_state['left_button_down'] = False
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao soltar botão {button}: {e}")
            return False
    
    def catch_fish(self) -> bool:
        """
        Capturar peixe - Sequência específica do botpesca
        
        Baseado na sequência:
        1. Soltar botão direito
        2. Aguardar 3 segundos
        3. Não pressionar novamente (aguardar próximo ciclo)
        """
        try:
            _safe_print("🐟 Executando sequência de captura...")
            
            # 1. Soltar botão direito se estiver pressionado
            if self.mouse_state['right_button_down']:
                self.stop_fishing()
            
            # 2. Aguardar coleta do peixe (3 segundos)
            _safe_print("⏱️ Aguardando coleta do peixe (3s)...")
            time.sleep(self.timing_config['fish_catch_delay'])
            
            _safe_print("✅ Sequência de captura concluída")
            
            if self.on_mouse_action:
                self.on_mouse_action('catch_fish', True)
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro na sequência de captura: {e}")
            return False
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Executar clique esquerdo em posição específica ou posição atual
        
        Args:
            x: Coordenada X (None = posição atual)
            y: Coordenada Y (None = posição atual)
        """
        try:
            self._focus_game_window()
            if x is not None and y is not None:
                pyautogui.click(x, y)
            else:
                pyautogui.click()
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro no clique: {e}")
            return False

    def click_left(self, duration: float = None) -> bool:
        """
        Executar clique esquerdo único - BASEADO NO BOTPESCA.PY

        No botpesca.py: click_esquerdo() usa mouseDown + sleep + mouseUp
        para simular pressão real do botão

        CORRIGIDO: Variação aleatória de 50-250ms (0.05-0.25s)
        para simular comportamento humano e garantir detecção pelo jogo!

        Args:
            duration: Duração da pressão do botão (None = aleatório 50-250ms)
        """
        try:
            import random

            # Se duration não especificado, usar variação aleatória
            if duration is None:
                duration = random.uniform(0.05, 0.25)  # 50-250ms

            self._focus_game_window()
            # Implementação EXATA do botpesca.py
            pyautogui.mouseDown(button='left')
            time.sleep(duration)
            pyautogui.mouseUp(button='left')
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique esquerdo: {e}")
            return False

    def click_right(self, x: Optional[int] = None, y: Optional[int] = None, duration: float = 0.02) -> bool:
        """
        Executar clique direito em posição específica ou posição atual
        Usa Windows API para maior confiabilidade

        Args:
            x: Coordenada X (None = posição atual)
            y: Coordenada Y (None = posição atual)
            duration: Duração da pressão do botão (padrão 0.02s)
        """
        try:
            import win32api, win32con

            self._focus_game_window()
            if x is not None and y is not None:
                # Mover mouse usando Windows API
                win32api.SetCursorPos((x, y))
                time.sleep(0.05)

            # Clique direito usando Windows API
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(duration)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique direito: {e}")
            # Fallback to pyautogui if Windows API fails
            try:
                if x is not None and y is not None:
                    pyautogui.moveTo(x, y, duration=0.05)
                    time.sleep(0.05)
                pyautogui.mouseDown(button='right')
                time.sleep(duration)
                pyautogui.mouseUp(button='right')
                return True
            except:
                return False

    def start_continuous_clicking(self) -> bool:
        """
        Iniciar cliques contínuos em thread separada

        Baseado na função clicar_continuamente() do botpesca
        """
        try:
            if self.continuous_actions['clicking']:
                _safe_print("⚠️ Cliques contínuos já estão ativos")
                return False

            self.continuous_actions['clicking'] = True

            def clicking_thread():
                # Calcular velocidade baseada na configuração atual
                clicks_per_second = 12  # padrão
                if self.config_manager:
                    clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)

                _safe_print(f"🖱️ Cliques contínuos iniciados ({clicks_per_second}/s da UI)")

                while self.continuous_actions['clicking']:
                    try:
                        if not self.continuous_actions['clicking']:
                            break

                        # Usar implementação melhorada de clique
                        self.click_left()

                        # Usar delay variável como no botpesca.py
                        delay = self.get_click_delay()
                        time.sleep(delay)

                    except Exception as e:
                        _safe_print(f"❌ Erro em clique contínuo: {e}")
                        break

                _safe_print("🛑 Cliques contínuos finalizados")

            thread = threading.Thread(target=clicking_thread, daemon=True)
            thread.start()
            self.active_threads.append(thread)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar cliques contínuos: {e}")
            return False
    
    def stop_continuous_clicking(self) -> bool:
        """Parar cliques contínuos"""
        try:
            if self.continuous_actions['clicking']:
                self.continuous_actions['clicking'] = False
                time.sleep(0.2)  # Aguardar thread parar
                return True
            else:
                _safe_print("⚠️ Cliques contínuos não estão ativos")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao parar cliques contínuos: {e}")
            return False
    
    def capture_initial_position(self) -> Tuple[int, int]:
        """
        Capturar posição inicial do mouse
        
        Baseado em: initial_mouse_pos = pyautogui.position()
        """
        try:
            position = pyautogui.position()
            self.mouse_state['last_position'] = (position.x, position.y)
            _safe_print(f"📍 Posição inicial capturada: {position}")
            return (position.x, position.y)
            
        except Exception as e:
            _safe_print(f"❌ Erro ao capturar posição: {e}")
            return (0, 0)
    
    # ===== MÉTODOS DE TECLADO =====
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """Pressionar tecla por duração específica"""
        try:
            self._focus_game_window()
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao pressionar tecla {key}: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """Pressionar e manter tecla"""
        try:
            log_debug("INPUT_KEY", f"key_down chamado para '{key}'", keys_down_before=list(self.keyboard_state['keys_down']))

            if key not in self.keyboard_state['keys_down']:
                log_info("INPUT_KEY", f"Pressionando tecla '{key}'...")
                self._focus_game_window()
                pyautogui.keyDown(key)
                self.keyboard_state['keys_down'].add(key)

                # Atualizar estados específicos
                if key == 'a':
                    self.keyboard_state['a_pressed'] = True
                elif key == 'd':
                    self.keyboard_state['d_pressed'] = True

                log_state("INPUT_KEY", {
                    "action": "key_down",
                    "key": key,
                    "keys_down": list(self.keyboard_state['keys_down']),
                    "a_pressed": self.keyboard_state['a_pressed'],
                    "d_pressed": self.keyboard_state['d_pressed']
                })
                return True
            else:
                _safe_print(f"⚠️ Tecla {key} já está pressionada")
                log_warning("INPUT_KEY", f"Tecla '{key}' já estava pressionada!", keys_down=list(self.keyboard_state['keys_down']))
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao pressionar tecla {key}: {e}")
            log_error("INPUT_KEY", f"Erro ao pressionar tecla '{key}': {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """Soltar tecla"""
        try:
            log_debug("INPUT_KEY", f"key_up chamado para '{key}'", keys_down_before=list(self.keyboard_state['keys_down']))

            if key in self.keyboard_state['keys_down']:
                log_info("INPUT_KEY", f"Soltando tecla '{key}'...")
                self._focus_game_window()
                pyautogui.keyUp(key)
                self.keyboard_state['keys_down'].discard(key)

                # Atualizar estados específicos
                if key == 'a':
                    self.keyboard_state['a_pressed'] = False
                elif key == 'd':
                    self.keyboard_state['d_pressed'] = False

                log_state("INPUT_KEY", {
                    "action": "key_up",
                    "key": key,
                    "keys_down": list(self.keyboard_state['keys_down']),
                    "a_pressed": self.keyboard_state['a_pressed'],
                    "d_pressed": self.keyboard_state['d_pressed']
                })
                return True
            else:
                _safe_print(f"⚠️ Tecla {key} não está pressionada")
                log_warning("INPUT_KEY", f"Tentou soltar tecla '{key}' que não estava pressionada", keys_down=list(self.keyboard_state['keys_down']))
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao soltar tecla {key}: {e}")
            log_error("INPUT_KEY", f"Erro ao soltar tecla '{key}': {e}")
            return False
    
    def move_camera_a(self, duration: Optional[float] = None) -> bool:
        """
        Mover câmera para esquerda (tecla A)
        
        Baseado na sequência A/D do botpesca
        """
        try:
            if duration is None:
                # Usar duração aleatória baseada na configuração
                import random
                min_dur, max_dur = self.timing_config['movement_a_duration']
                duration = random.uniform(min_dur, max_dur)
            
            _safe_print(f"◀️ Movimento A por {duration:.1f}s")
            
            self.key_down('a')
            time.sleep(duration)
            self.key_up('a')
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro no movimento A: {e}")
            return False
    
    def move_camera_d(self, duration: Optional[float] = None) -> bool:
        """
        Mover câmera para direita (tecla D)
        
        Baseado na sequência A/D do botpesca
        """
        try:
            if duration is None:
                # Usar duração aleatória baseada na configuração
                import random
                min_dur, max_dur = self.timing_config['movement_d_duration']
                duration = random.uniform(min_dur, max_dur)
            
            _safe_print(f"▶️ Movimento D por {duration:.1f}s")
            
            self.key_down('d')
            time.sleep(duration)
            self.key_up('d')
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro no movimento D: {e}")
            return False
    
    def start_camera_movement_cycle(self, stop_callback: Callable[[], bool]) -> bool:
        """
        Iniciar ciclo de movimento A/D em thread separada
        
        Baseado na função mover_camera() do botpesca
        """
        try:
            if self.continuous_actions['moving_camera']:
                _safe_print("⚠️ Movimento de câmera já está ativo")
                return False
            
            self.continuous_actions['moving_camera'] = True
            
            def movement_thread():
                import random
                _safe_print("📹 Movimento de câmera A/D iniciado")
                
                while self.continuous_actions['moving_camera']:
                    try:
                        # Verificar se deve parar (callback)
                        if stop_callback and stop_callback():
                            _safe_print("🛑 Movimento A/D interrompido por callback")
                            break
                        
                        if not self.continuous_actions['moving_camera']:
                            break
                        
                        # Movimento A
                        self.move_camera_a()
                        
                        # Verificar novamente antes da pausa
                        if stop_callback and stop_callback():
                            break
                        if not self.continuous_actions['moving_camera']:
                            break
                        
                        # Pausa entre A e D
                        min_pause, max_pause = self.timing_config['movement_pause']
                        pause_duration = random.uniform(min_pause, max_pause)
                        time.sleep(pause_duration)
                        
                        # Verificar antes do movimento D
                        if stop_callback and stop_callback():
                            break
                        if not self.continuous_actions['moving_camera']:
                            break
                        
                        # Movimento D
                        self.move_camera_d()
                        
                        # Pausa após D
                        time.sleep(pause_duration)
                        
                    except Exception as e:
                        _safe_print(f"❌ Erro em movimento A/D: {e}")
                        break
                
                _safe_print("🛑 Movimento de câmera A/D finalizado")
            
            thread = threading.Thread(target=movement_thread, daemon=True)
            thread.start()
            self.active_threads.append(thread)
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar movimento de câmera: {e}")
            return False
    
    def stop_camera_movement(self) -> bool:
        """Parar movimento de câmera"""
        try:
            if self.continuous_actions['moving_camera']:
                self.continuous_actions['moving_camera'] = False

                # Soltar teclas se estiverem pressionadas
                if 'a' in self.keyboard_state['keys_down']:
                    self.key_up('a')
                if 'd' in self.keyboard_state['keys_down']:
                    self.key_up('d')

                _safe_print("🛑 Parando movimento de câmera...")
                time.sleep(0.2)  # Aguardar thread parar
                return True
            else:
                _safe_print("⚠️ Movimento de câmera não está ativo")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao parar movimento de câmera: {e}")
            return False

    def start_continuous_s_press(self) -> bool:
        """
        Iniciar ciclo contínuo de pressionar tecla S

        Ciclo:
        1. Pressiona S
        2. Segura: 1.5-2.5 segundos
        3. Solta S
        4. Aguarda: 1-2 segundos
        5. Repete...
        """
        try:
            if self.continuous_actions['pressing_s']:
                _safe_print("⚠️ Ciclo de tecla S já está ativo")
                return False

            self.continuous_actions['pressing_s'] = True

            def s_press_thread():
                import random

                # ✅ NOVO: Ler configurações da config se disponível
                hold_min = 1.5
                hold_max = 2.5
                release_min = 1.0
                release_max = 2.0

                if self.config_manager:
                    s_config = self.config_manager.get('anti_detection.s_key_cycle', {})
                    if s_config.get('enabled', True):
                        hold_min = s_config.get('hold_duration_min', 1.5)
                        hold_max = s_config.get('hold_duration_max', 2.5)
                        release_min = s_config.get('release_duration_min', 1.0)
                        release_max = s_config.get('release_duration_max', 2.0)

                # _safe_print(f"🔄 Ciclo de tecla S iniciado ({hold_min}-{hold_max}s pressionado, {release_min}-{release_max}s solto)")  # ← DESABILITADO - polui logs

                while self.continuous_actions['pressing_s']:
                    try:
                        if not self.continuous_actions['pressing_s']:
                            break

                        # PASSO 1: Pressionar S
                        # _safe_print("⬇️ Pressionando S...")  # ← Log verboso desabilitado
                        self.key_down('s')

                        # PASSO 2: Segurar por tempo configurado
                        hold_duration = random.uniform(hold_min, hold_max)
                        # _safe_print(f"⏱️ Segurando S por {hold_duration:.2f}s...")  # ← Log verboso desabilitado
                        time.sleep(hold_duration)

                        if not self.continuous_actions['pressing_s']:
                            break

                        # PASSO 3: Soltar S
                        # _safe_print("⬆️ Soltando S...")  # ← Log verboso desabilitado
                        self.key_up('s')

                        # PASSO 4: Aguardar tempo configurado
                        release_duration = random.uniform(release_min, release_max)
                        # _safe_print(f"⏳ Aguardando {release_duration:.2f}s...")  # ← Log verboso desabilitado
                        time.sleep(release_duration)

                    except Exception as e:
                        _safe_print(f"❌ Erro no ciclo de S: {e}")
                        break

                # Garantir que S está solto ao finalizar
                if 's' in self.keyboard_state['keys_down']:
                    self.key_up('s')

                # _safe_print("🛑 Ciclo de tecla S finalizado")  # ← DESABILITADO - polui logs

            thread = threading.Thread(target=s_press_thread, daemon=True)
            thread.start()
            self.active_threads.append(thread)

            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao iniciar ciclo de S: {e}")
            return False

    def stop_continuous_s_press(self) -> bool:
        """Parar ciclo de tecla S"""
        try:
            if self.continuous_actions['pressing_s']:
                self.continuous_actions['pressing_s'] = False

                # Soltar S se estiver pressionado
                if 's' in self.keyboard_state['keys_down']:
                    self.key_up('s')

                # _safe_print("🛑 Parando ciclo de tecla S...")  # ← DESABILITADO - polui logs
                time.sleep(0.2)  # Aguardar thread parar
                return True
            else:
                # _safe_print("⚠️ Ciclo de tecla S não está ativo")  # ← DESABILITADO - polui logs
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao parar ciclo de S: {e}")
            return False
    
    # ===== MÉTODOS PARA MANUTENÇÃO DE VARAS =====

    def right_click(self, x: int, y: int) -> bool:
        """
        Clique direito em posição específica

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        try:
            self._focus_game_window()
            pyautogui.rightClick(x, y)
            _safe_print(f"🖱️ Clique direito em ({x}, {y})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique direito: {e}")
            return False

    def click(self, x: int, y: int, button: str = 'left') -> bool:
        """
        Clique em posição específica

        Args:
            x: Coordenada X
            y: Coordenada Y
            button: 'left', 'right', ou 'middle'
        """
        try:
            self._focus_game_window()
            pyautogui.click(x, y, button=button)
            _safe_print(f"🖱️ Clique {button} em ({x}, {y})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no clique {button}: {e}")
            return False

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        Arrastar de uma posição para outra - TÉCNICA EXATA DO V3

        ✅ SUPORTE MULTI-MONITOR: Aplica offset configurado

        Args:
            start_x: X inicial (relativo ao monitor do jogo)
            start_y: Y inicial (relativo ao monitor do jogo)
            end_x: X final (relativo ao monitor do jogo)
            end_y: Y final (relativo ao monitor do jogo)
            duration: Duração do movimento
        """
        try:
            # ✅ NOVO: Aplicar offset de multi-monitor
            offset_x = 0
            offset_y = 0
            if self.config_manager:
                offset_x = self.config_manager.get('coordinates.monitor_offset_x', 0)
                offset_y = self.config_manager.get('coordinates.monitor_offset_y', 0)

            # Aplicar offset às coordenadas
            actual_start_x = start_x + offset_x
            actual_start_y = start_y + offset_y
            actual_end_x = end_x + offset_x
            actual_end_y = end_y + offset_y

            log_info("INPUT_DRAG", f"DRAG INICIADO: ({start_x}, {start_y}) → ({end_x}, {end_y}), duration={duration}s")
            if offset_x != 0 or offset_y != 0:
                log_info("INPUT_DRAG", f"  OFFSET APLICADO: +({offset_x}, {offset_y})")
                log_info("INPUT_DRAG", f"  COORDENADAS REAIS: ({actual_start_x}, {actual_start_y}) → ({actual_end_x}, {actual_end_y})")
            log_state("INPUT_DRAG", {"before_drag": self.get_state()})

            self._focus_game_window()

            # Desabilitar fail-safe temporariamente (como no v3)
            original_failsafe = pyautogui.FAILSAFE
            pyautogui.FAILSAFE = False

            try:
                _safe_print(f"🖱️ Drag de ({start_x}, {start_y}) para ({end_x}, {end_y}) em {duration}s")
                if offset_x != 0 or offset_y != 0:
                    _safe_print(f"   📍 Offset: +({offset_x}, {offset_y}) → Real: ({actual_start_x}, {actual_start_y}) → ({actual_end_x}, {actual_end_y})")

                # ✅ TÉCNICA EXATA DO V3 (linha 24733-24750):
                # PASSO 1: Mover para posição inicial SEM segurar
                log_debug("INPUT_DRAG", "PASSO 1: Movendo para posição inicial...")
                pyautogui.moveTo(actual_start_x, actual_start_y)
                time.sleep(0.2)  # ✅ RESTAURADO: V3 usa 0.2s

                # PASSO 2: Segurar botão esquerdo
                log_debug("INPUT_DRAG", "PASSO 2: Segurando botão esquerdo...")
                pyautogui.mouseDown(button='left')
                self.mouse_state['left_button_down'] = True
                time.sleep(0.2)  # ✅ RESTAURADO: V3 usa 0.2s

                # PASSO 3: Mover para destino COM botão pressionado
                log_debug("INPUT_DRAG", "PASSO 3: Movendo para destino com botão pressionado...")
                pyautogui.moveTo(actual_end_x, actual_end_y, duration=duration)
                time.sleep(0.4)  # ✅ RESTAURADO: V3 usa 0.4s (CRÍTICO para item chegar ao destino!)

                # PASSO 4: Soltar botão
                log_debug("INPUT_DRAG", "PASSO 4: Soltando botão esquerdo...")
                self._focus_game_window()  # Garantir foco
                pyautogui.mouseUp(button='left')
                self.mouse_state['left_button_down'] = False
                time.sleep(0.4)  # ✅ RESTAURADO: V3 usa 0.4s (CRÍTICO para garantir que soltou!)

                _safe_print(f"✅ Drag completo: item movido para ({end_x}, {end_y})")
                log_info("INPUT_DRAG", "DRAG CONCLUÍDO COM SUCESSO")
                log_state("INPUT_DRAG", {"after_drag": self.get_state()})
                return True

            finally:
                # CRÍTICO: Garantir que mouse não fique pressionado
                try:
                    log_debug("INPUT_DRAG", "FINALLY: Garantindo release do botão esquerdo...")
                    self._focus_game_window()
                    pyautogui.mouseUp(button='left')
                    self.mouse_state['left_button_down'] = False
                except Exception as e:
                    log_error("INPUT_DRAG", f"Erro no finally ao liberar botão: {e}")
                # Restaurar fail-safe
                pyautogui.FAILSAFE = original_failsafe

        except Exception as e:
            _safe_print(f"❌ Erro no drag: {e}")
            log_error("INPUT_DRAG", f"ERRO CRÍTICO NO DRAG: {e}")
            log_state("INPUT_DRAG", {"error_state": self.get_state()})
            # CRÍTICO: Garantir que mouse não fique pressionado
            try:
                self._focus_game_window()
                pyautogui.mouseUp(button='left')
                self.mouse_state['left_button_down'] = False
            except:
                pass
            return False

    def move_to(self, x: int, y: int) -> bool:
        """
        Mover mouse para posição específica

        Args:
            x: Coordenada X
            y: Coordenada Y
        """
        try:
            pyautogui.moveTo(x, y)
            self.mouse_state['last_position'] = (x, y)
            return True

        except Exception as e:
            _safe_print(f"❌ Erro ao mover mouse: {e}")
            return False

    # ===== MÉTODOS DE UTILIDADE =====

    def _focus_game_window(self):
        """
        Garantir foco na janela do jogo
        
        Baseado em focus_game_window() do botpesca
        """
        try:
            if WIN32_AVAILABLE:
                # Implementação com win32 se disponível
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    win32gui.SetForegroundWindow(hwnd)
            
        except Exception as e:
            # Silencioso - não é crítico
            pass
    
    def stop_all_actions(self) -> bool:
        """
        Parar todas as ações - EMERGENCY STOP

        Baseado na lógica de emergency stop do botpesca
        """
        try:
            _safe_print("🚨 EMERGENCY STOP - Parando todas as ações!")
            log_warning("INPUT_EMERGENCY", "EMERGENCY STOP ACIONADO!")
            log_state("INPUT_EMERGENCY", {
                "before_stop": self.get_state()
            })

            # Parar ações contínuas
            log_info("INPUT_EMERGENCY", "Parando ações contínuas...")
            self.stop_continuous_clicking()
            self.stop_camera_movement()
            self.stop_continuous_s_press()

            # Soltar botão direito
            log_info("INPUT_EMERGENCY", "Soltando botão direito...")
            self.stop_fishing()

            # Soltar todas as teclas
            log_info("INPUT_EMERGENCY", f"Soltando {len(self.keyboard_state['keys_down'])} teclas pressionadas...")
            keys_to_release = list(self.keyboard_state['keys_down'])
            for key in keys_to_release:
                log_debug("INPUT_EMERGENCY", f"Liberando tecla '{key}'...")
                try:
                    pyautogui.keyUp(key)  # Forçar release direto via pyautogui
                except Exception as e:
                    log_error("INPUT_EMERGENCY", f"Erro ao liberar tecla '{key}': {e}")

            # CRÍTICO: Liberar ALT especificamente (pode estar travado!)
            log_info("INPUT_EMERGENCY", "Liberando ALT, CTRL, SHIFT explicitamente...")
            for special_key in ['alt', 'ctrl', 'shift', 'altleft', 'altright']:
                try:
                    pyautogui.keyUp(special_key)
                    log_debug("INPUT_EMERGENCY", f"'{special_key}' liberado")
                except:
                    pass

            # Soltar botão esquerdo também
            log_info("INPUT_EMERGENCY", "Soltando botão esquerdo...")
            try:
                self._focus_game_window()
                pyautogui.mouseUp(button='left')
                pyautogui.mouseUp(button='right')
            except:
                pass

            # Limpar estado
            log_info("INPUT_EMERGENCY", "Limpando estados internos...")
            self.mouse_state['right_button_down'] = False
            self.mouse_state['left_button_down'] = False
            self.keyboard_state['keys_down'].clear()
            self.keyboard_state['a_pressed'] = False
            self.keyboard_state['d_pressed'] = False

            log_state("INPUT_EMERGENCY", {
                "after_stop": self.get_state()
            })
            _safe_print("✅ Emergency stop concluído - todos os controles liberados")
            log_info("INPUT_EMERGENCY", "Emergency stop concluído com sucesso")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no emergency stop: {e}")
            log_error("INPUT_EMERGENCY", f"ERRO CRÍTICO no emergency stop: {e}")
            return False
    
    def get_state(self) -> dict:
        """Obter estado atual do InputManager"""
        return {
            'mouse': self.mouse_state.copy(),
            'keyboard': {
                'a_pressed': self.keyboard_state['a_pressed'],
                'd_pressed': self.keyboard_state['d_pressed'],
                'keys_down': list(self.keyboard_state['keys_down'])
            },
            'continuous_actions': self.continuous_actions.copy(),
            'active_threads': len(self.active_threads)
        }
    
    def set_callbacks(self, on_mouse_action: Optional[Callable] = None, 
                     on_keyboard_action: Optional[Callable] = None):
        """Configurar callbacks para eventos"""
        self.on_mouse_action = on_mouse_action
        self.on_keyboard_action = on_keyboard_action
        _safe_print("✅ Callbacks configurados")
    
    def camera_turn_in_game(self, dx: int, dy: int) -> bool:
        """
        🎮 Movimento de câmera usando SendInput (EXATO DO V3)

        Move a câmera do jogo de forma RELATIVA enquanto ALT está pressionado.
        Usa Windows SendInput API para movimento nativo que o jogo reconhece.

        Args:
            dx: Deslocamento horizontal (-= esquerda, += direita)
            dy: Deslocamento vertical (+= baixo, -= cima)

        Returns:
            True se sucesso, False se erro
        """
        try:
            _safe_print(f"   🎮 Movimento de câmera: DX={dx}, DY={dy}")

            # Estruturas Windows para SendInput
            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [("dx", ctypes.wintypes.LONG),
                           ("dy", ctypes.wintypes.LONG),
                           ("mouseData", ctypes.wintypes.DWORD),
                           ("dwFlags", ctypes.wintypes.DWORD),
                           ("time", ctypes.wintypes.DWORD),
                           ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    _fields_ = [("mi", MOUSEINPUT)]
                _fields_ = [("type", ctypes.wintypes.DWORD),
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

            _safe_print(f"   ✅ Movimento de câmera executado!")
            return True

        except Exception as e:
            _safe_print(f"   ❌ Erro no movimento de câmera: {e}")
            return False

    def center_camera(self, initial_pos: Tuple[int, int] = None) -> bool:
        """
        🎯 Centralizar câmera antes de executar macro (EXATO DO V3)

        Reseta a câmera para posição inicial usando movimentos em cruz
        para "cancelar" qualquer posição anterior.

        Args:
            initial_pos: Tupla (x, y) da posição inicial, ou None para centro da tela

        Returns:
            True se sucesso, False se erro
        """
        try:
            _safe_print("   🎯 Resetando câmera para posição inicial...")

            # Usar posição inicial capturada no F9, ou centro da tela como fallback
            if initial_pos:
                center_x, center_y = initial_pos
                _safe_print(f"   📍 Usando posição inicial: ({center_x}, {center_y})")
            else:
                screen_width, screen_height = pyautogui.size()
                center_x = screen_width // 2
                center_y = screen_height // 2
                _safe_print(f"   📍 Fallback - centro da tela: ({center_x}, {center_y})")

            pyautogui.moveTo(center_x, center_y)
            time.sleep(0.1)

            # Método 2: Reset de câmera por movimento
            # Fazer movimentos em cruz para "cancelar" posição anterior
            pyautogui.moveRel(200, 0)    # Direita
            time.sleep(0.05)
            pyautogui.moveRel(-400, 0)   # Esquerda forte
            time.sleep(0.05)
            pyautogui.moveRel(200, 0)    # Volta centro
            time.sleep(0.05)

            pyautogui.moveRel(0, 200)    # Baixo
            time.sleep(0.05)
            pyautogui.moveRel(0, -400)   # Cima forte
            time.sleep(0.05)
            pyautogui.moveRel(0, 200)    # Volta centro
            time.sleep(0.05)

            # Voltar para centro absoluto novamente
            pyautogui.moveTo(center_x, center_y)
            time.sleep(0.2)

            _safe_print("   ✅ Câmera resetada - posição zero garantida!")
            return True

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao resetar câmera: {e}")
            return False

    def release_mouse_buttons(self, preserve_right_click: bool = False) -> bool:
        """
        🖱️ Liberar todos os botões do mouse (EXATO DO V3)

        Args:
            preserve_right_click: Se True, mantém botão direito pressionado

        Returns:
            True se sucesso, False se erro
        """
        try:
            _safe_print("   🖱️ Liberando botões do mouse...")

            # Liberar botão esquerdo sempre
            pyautogui.mouseUp('left')
            self.mouse_state['left_button_down'] = False

            # Liberar botão direito apenas se não for para preservar
            if not preserve_right_click:
                pyautogui.mouseUp('right')
                self.mouse_state['right_button_down'] = False
            else:
                _safe_print("   ℹ️ Botão direito preservado (pescando)")

            return True

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao liberar mouse: {e}")
            return False

    def __del__(self):
        """Cleanup ao destruir objeto"""
        try:
            self.stop_all_actions()
        except:
            pass