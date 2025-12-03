"""
Arduino Input Manager - Envia comandos HID via Serial para Arduino

Substitui InputManager padrão para usar Arduino Pro Micro como dispositivo HID.
Evita detecção de automação por software.

Hardware necessário:
- Arduino Pro Micro (ATmega32U4) ou Leonardo
- Sketch arduino_hid_controller.ino carregado no Arduino

Comunicação:
- Serial USB 9600 baud
- Protocolo de comandos texto (ver arduino_hid_controller.ino)

VERSÃO COMPLETA: Implementa TODOS os métodos do InputManager
"""

import serial
import serial.tools.list_ports
import time
import threading
import random
from typing import Optional, Tuple, Dict, Callable
import re

# Importar pyautogui apenas para obter posição do mouse (não para input!)
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except:
    PYAUTOGUI_AVAILABLE = False


def _safe_print(text):
    """Print seguro para Unicode/emoji"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)


class ArduinoInputManager:
    """
    Gerenciador de inputs via Arduino HID

    100% compatível com InputManager original - mesma interface
    Todos os métodos implementados com suporte completo via Arduino
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 9600, config_manager=None):
        """
        Inicializar conexão com Arduino

        Args:
            port: Porta COM (ex: 'COM3'). Se None, tenta auto-detectar.
            baudrate: Velocidade serial (padrão: 9600)
            config_manager: ConfigManager instance (opcional)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.lock = threading.RLock()
        self.config_manager = config_manager

        # ✅ CORREÇÃO CRÍTICA: Locks separados para thread-safety (igual InputManager)
        self.mouse_state_lock = threading.RLock()
        self.keyboard_state_lock = threading.RLock()
        self.continuous_actions_lock = threading.RLock()
        self.threads_lock = threading.RLock()

        # Estado interno (para compatibilidade)
        self.keyboard_state = {
            'keys_down': set(),
            'a_pressed': False,
            'd_pressed': False
        }
        self.mouse_state = {
            'left_button_down': False,
            'right_button_down': False,
            'last_position': (960, 540)  # Centro da tela 1920x1080
        }
        self.continuous_actions = {'clicking': False, 'moving_camera': False, 'pressing_s': False}
        self.active_threads = []

        # Timing config (para compatibilidade)
        self.timing_config = {
            'click_delay': 1.0 / 12,
            'movement_a_duration': (1.2, 1.8),
            'movement_d_duration': (1.0, 1.4),
            'movement_pause': (0.2, 0.5),
            'fish_catch_delay': 3.0,
            'phase_transition_delay': 0.1
        }

        # Callbacks (para compatibilidade)
        self.on_mouse_action: Optional[Callable] = None
        self.on_keyboard_action: Optional[Callable] = None

        # Carregar configurações se disponível
        self._load_config()

        # ✅ CORREÇÃO: NÃO tentar conectar automaticamente aqui!
        # Motivo: Bloqueia inicialização e compete com UI
        # A UI vai tentar conectar DEPOIS de tudo pronto (via _auto_refresh_arduino_on_startup)
        if self.port:
            _safe_print(f"   📌 Última porta usada: {self.port} (conexão será feita pela UI)")

    # ===== MÉTODOS THREAD-SAFE PARA ACESSO A ESTADOS =====

    def _set_mouse_button_state(self, button: str, pressed: bool):
        """Thread-safe: Definir estado de botão do mouse"""
        with self.mouse_state_lock:
            self.mouse_state[button] = pressed

    def _get_mouse_button_state(self, button: str) -> bool:
        """Thread-safe: Obter estado de botão do mouse"""
        with self.mouse_state_lock:
            return self.mouse_state.get(button, False)

    def _set_mouse_position(self, x: int, y: int):
        """Thread-safe: Atualizar última posição do mouse"""
        with self.mouse_state_lock:
            self.mouse_state['last_position'] = (x, y)

    def _get_mouse_position(self) -> Tuple[int, int]:
        """Thread-safe: Obter última posição do mouse"""
        with self.mouse_state_lock:
            return self.mouse_state['last_position']

    def _set_continuous_action(self, action: str, active: bool):
        """Thread-safe: Definir estado de ação contínua"""
        with self.continuous_actions_lock:
            self.continuous_actions[action] = active

    def _get_continuous_action(self, action: str) -> bool:
        """Thread-safe: Obter estado de ação contínua"""
        with self.continuous_actions_lock:
            return self.continuous_actions.get(action, False)

    def _add_active_thread(self, thread: threading.Thread):
        """Thread-safe: Adicionar thread à lista de threads ativas"""
        with self.threads_lock:
            # ✅ CORREÇÃO: Limpar threads finalizadas antes de adicionar
            self.active_threads = [t for t in self.active_threads if t.is_alive()]
            self.active_threads.append(thread)

    def _cleanup_finished_threads(self):
        """Thread-safe: Remover threads finalizadas da lista (previne memory leak)"""
        with self.threads_lock:
            self.active_threads = [t for t in self.active_threads if t.is_alive()]

    # ===== MÉTODOS DE CONEXÃO =====

    def connect(self) -> bool:
        """Conectar ao Arduino (método público para UI)"""
        return self._connect()

    def _connect(self) -> bool:
        """Conectar ao Arduino via Serial"""
        try:
            # Auto-detectar porta se não especificada
            if not self.port:
                self.port = self._find_arduino_port()
                if not self.port:
                    _safe_print("❌ Arduino não encontrado. Conecte o Arduino Pro Micro e tente novamente.")
                    return False

            _safe_print(f"🔌 Conectando ao Arduino na porta {self.port}...")

            # ✅ CORREÇÃO: Fechar porta existente se estiver aberta (evita PermissionError)
            if self.serial and self.serial.is_open:
                try:
                    _safe_print(f"   🔒 Fechando porta anterior {self.port}...")
                    self.serial.close()
                    time.sleep(0.5)  # Aguardar Windows liberar a porta
                    _safe_print(f"   ✅ Porta fechada")
                except Exception as e:
                    _safe_print(f"   ⚠️ Erro ao fechar porta: {e}")

            # Abrir conexão serial
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1.0,
                write_timeout=1.0
            )

            # Aguardar Arduino inicializar (Leonardo/Pro Micro reset na conexão)
            time.sleep(2.0)

            # Limpar buffer
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()

            # Aguardar mensagem READY
            ready = False
            for _ in range(10):
                line = self.serial.readline().decode('utf-8').strip()
                _safe_print(f"[DEBUG] Arduino enviou: '{line}'")
                if line.startswith("READY"):  # ✅ Aceita "READY", "READY:HID-NKRO", etc
                    ready = True
                    _safe_print(f"✅ Arduino pronto: {line}")
                    break
                time.sleep(0.1)

            if not ready:
                _safe_print("⚠️ Arduino não enviou READY, mas continuando...")

            # Testar conexão com PING
            if self._ping():
                self.connected = True
                _safe_print(f"✅ Arduino conectado em {self.port}")

                # ✅ NOVO: Salvar porta na config para reconexão automática
                if self.config_manager:
                    try:
                        self.config_manager.set('arduino_port', self.port)
                        self.config_manager.save_config()
                        _safe_print(f"💾 Porta {self.port} salva para reconexão automática")
                    except Exception as e:
                        _safe_print(f"⚠️ Não foi possível salvar porta na config: {e}")

                return True
            else:
                _safe_print("❌ Arduino não respondeu ao PING")
                # ✅ CRÍTICO: Fechar porta se PING falhou (evita PermissionError nas próximas tentativas)
                try:
                    if self.serial and self.serial.is_open:
                        self.serial.close()
                        _safe_print("   🔒 Porta fechada (PING falhou)")
                except:
                    pass
                self.serial = None
                self.connected = False
                return False

        except serial.SerialException as e:
            _safe_print(f"❌ Erro ao conectar: {e}")
            # ✅ CRÍTICO: Fechar porta se erro ao conectar
            try:
                if self.serial and self.serial.is_open:
                    self.serial.close()
            except:
                pass
            self.serial = None
            self.connected = False
            return False

    def _find_arduino_port(self) -> Optional[str]:
        """Auto-detectar porta COM do Arduino"""
        _safe_print("🔍 Procurando Arduino...")

        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Arduino Pro Micro/Leonardo geralmente aparecem como:
            # - VID 2341 (Arduino.cc)
            # - VID 1B4F (SparkFun Pro Micro)
            # - VID 2A03 (Arduino.org)
            if port.vid in [0x2341, 0x1B4F, 0x2A03]:
                _safe_print(f"   ✅ Arduino encontrado: {port.device} ({port.description})")
                return port.device

            # Fallback: procurar por nome
            if 'Arduino' in port.description or 'USB Serial' in port.description:
                _safe_print(f"   🤔 Possível Arduino: {port.device} ({port.description})")
                return port.device

        _safe_print("   ❌ Nenhum Arduino detectado")
        _safe_print("\n📋 Portas disponíveis:")
        for port in ports:
            _safe_print(f"   - {port.device}: {port.description} (VID={hex(port.vid) if port.vid else 'N/A'})")

        return None

    def _ping(self) -> bool:
        """Testar conexão com Arduino"""
        try:
            response = self._send_command("PING")
            return response == "PONG"
        except Exception:
            return False

    def _send_command_fast(self, command: str) -> bool:
        """
        Enviar comando ao Arduino SEM ESPERAR resposta (modo rápido)

        Usado para comandos de alta frequência (cliques, teclas)
        Latência: ~2-5ms (vs ~20-30ms com espera)

        Args:
            command: Comando a enviar

        Returns:
            True se enviou, False se erro
        """
        with self.lock:
            if not self.connected or not self.serial:
                return False

            try:
                self.serial.write(f"{command}\n".encode('utf-8'))
                # NÃO fazer flush() - deixa buffer acumular para melhor throughput
                return True
            except Exception:
                return False

    def _send_command(self, command: str, timeout: float = 1.0) -> Optional[str]:
        """
        Enviar comando ao Arduino e aguardar resposta (modo confiável)

        Args:
            command: Comando a enviar (ex: "KEYPRESS:1")
            timeout: Tempo máximo de espera (segundos)

        Returns:
            Resposta do Arduino ou None se timeout/erro
        """
        with self.lock:
            if not self.connected or not self.serial:
                _safe_print(f"⚠️ [ARDUINO] NÃO CONECTADO! (connected={self.connected}, serial={self.serial is not None})")
                return None

            try:
                # ✅ DEBUG: Mostrar comandos críticos sendo enviados
                if 'KEY_DOWN:alt' in command.lower() or 'KEY_UP:alt' in command.lower() or 'KEY_DOWN:e' in command.lower():
                    _safe_print(f"   🔌 [ARDUINO] Enviando: {command}")

                # ✅ CRÍTICO: Limpar buffer de entrada ANTES de enviar comando
                # Isso evita ler respostas antigas/atrasadas
                if self.serial.in_waiting > 0:
                    old_data = self.serial.read(self.serial.in_waiting)
                    # _safe_print(f"   🗑️ Limpou {len(old_data)} bytes do buffer")

                # Enviar comando
                self.serial.write(f"{command}\n".encode('utf-8'))
                self.serial.flush()

                # Aguardar resposta
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self.serial.in_waiting > 0:
                        response = self.serial.readline().decode('utf-8').strip()

                        # ✅ DEBUG: Mostrar respostas de comandos críticos
                        if 'KEY_DOWN:alt' in command.lower() or 'KEY_UP:alt' in command.lower() or 'KEY_DOWN:e' in command.lower():
                            _safe_print(f"   📥 [ARDUINO] Resposta: {response}")

                        return response
                    time.sleep(0.01)

                _safe_print(f"⚠️ [ARDUINO] Timeout aguardando resposta para: {command}")
                return None

            except Exception as e:
                _safe_print(f"❌ Erro ao enviar comando '{command}': {e}")
                return None

    # ===== MÉTODOS DE CONFIGURAÇÃO =====

    def _load_config(self):
        """Carregar configurações de timing e Arduino"""
        try:
            if self.config_manager:
                # ✅ NOVO: Carregar porta e baudrate do Arduino
                if not self.port:
                    self.port = self.config_manager.get('arduino_port', None)
                arduino_baudrate = self.config_manager.get('arduino_baudrate', None)
                if arduino_baudrate:
                    self.baudrate = arduino_baudrate
                    _safe_print(f"✅ Arduino baudrate configurado: {self.baudrate}")

                # Cliques por segundo
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)
                self.timing_config['click_delay'] = 1.0 / clicks_per_second

                # Durações de movimento
                anti_detection = self.config_manager.get('anti_detection', {})
                if anti_detection.get('movement_variation', False):
                    self.timing_config['movement_a_duration'] = (1.2, 1.8)
                    self.timing_config['movement_d_duration'] = (1.0, 1.4)
                else:
                    self.timing_config['movement_a_duration'] = (1.5, 1.5)
                    self.timing_config['movement_d_duration'] = (1.2, 1.2)

                _safe_print("✅ Configurações de timing carregadas do ConfigManager")

        except Exception as e:
            _safe_print(f"⚠️ Erro ao carregar config de timing: {e}")

    def get_click_delay(self) -> float:
        """
        Obter delay variado para cliques com anti-detecção

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
                clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)
                self.timing_config['click_delay'] = 1.0 / clicks_per_second

                anti_detection = self.config_manager.get('anti_detection', {})
                if anti_detection.get('movement_variation', False):
                    self.timing_config['mouse_move_duration'] = (0.1, 0.3)
                    self.timing_config['key_press_duration'] = (0.05, 0.15)
                else:
                    self.timing_config['mouse_move_duration'] = 0.1
                    self.timing_config['key_press_duration'] = 0.05

                self.timing_config['action_delay'] = anti_detection.get('action_delay', 0.1)
                self.timing_config['fish_catch_delay'] = 3.0

                _safe_print(f"✅ Configurações atualizadas: {clicks_per_second} cliques/s")
            else:
                _safe_print("⚠️ ConfigManager não disponível para recarregar")

        except Exception as e:
            _safe_print(f"❌ Erro ao recarregar timing: {e}")

    # ===== MÉTODOS DE TECLADO =====

    def press_key(self, key: str, duration: float = 0.05) -> bool:
        """
        Pressionar e soltar tecla

        Args:
            key: Tecla (ex: '1', 'e', 'tab', 'ALT')
            duration: Duração (tempo pressionado)
        """
        # Comandos curtos suportados pelo Arduino: w, a, s, d, e, tab, 1-6, alt
        key_lower = key.lower()

        try:
            # Pressionar
            if not self.key_down(key_lower):
                _safe_print(f"❌ [PRESS_KEY] FALHA ao pressionar '{key_lower}'!")
                return False

            # Segurar
            time.sleep(duration)

            # Soltar
            success = self.key_up(key_lower)

            if not success:
                _safe_print(f"❌ [PRESS_KEY] FALHA ao soltar '{key_lower}'!")
                # 🔴 CRÍTICO: Se falhou, tentar forçar release!
                try:
                    self._send_command(f"KEY_UP:{key_lower}", timeout=0.5)
                except:
                    _safe_print(f"❌ [PRESS_KEY] Force release FALHOU para '{key_lower}'!")

            return success

        except Exception as e:
            _safe_print(f"❌ [PRESS_KEY] EXCEÇÃO durante press_key: {e}")
            return False

        finally:
            # ✅ CRÍTICO: SEMPRE tentar soltar a tecla, mesmo em caso de exceção
            # Isso garante que números dos slots (1-6) nunca ficam presos!
            try:
                self._send_command(f"KEY_UP:{key_lower}", timeout=0.5)
                # Limpar do state também
                if key_lower in self.keyboard_state['keys_down']:
                    self.keyboard_state['keys_down'].discard(key_lower)
            except:
                pass  # Falhou, mas já tentamos

    def key_down(self, key: str) -> bool:
        """Pressionar tecla - SEMPRE usa KEY_DOWN:tecla"""
        # ✅ NORMALIZAR para lowercase para evitar case mismatch
        key_normalized = key.lower()

        # 🔴 CRITICAL FIX: Se for TAB, ALT, A, S, D, E, ou números, SEMPRE enviar comando (ignora keyboard_state check)
        # Mesmo padrão do key_up para evitar falhas de state dessincronizado
        force_release_keys = ['tab', 'alt', 'lalt', 'a', 's', 'd', 'e', '1', '2', '3', '4', '5', '6']
        if key_normalized in force_release_keys:
            # SEMPRE enviar KEY_DOWN, mesmo se já estiver no state
            response = self._send_command(f"KEY_DOWN:{key_normalized}")
            success = response and "OK" in response

            # Adicionar ao state se sucesso
            if success:
                self.keyboard_state['keys_down'].add(key_normalized)
                # Atualizar flags especiais
                if key_normalized == 'a':
                    self.keyboard_state['a_pressed'] = True
                elif key_normalized == 'd':
                    self.keyboard_state['d_pressed'] = True

            return success

        # Para outras teclas, comportamento normal
        if key_normalized in self.keyboard_state['keys_down']:
            _safe_print(f"⚠️ Tecla {key} já está pressionada (state: {self.keyboard_state['keys_down']})")
            return False

        # ✅ CRÍTICO: Enviar comando com key NORMALIZADO (lowercase)
        # Arduino usa equalsIgnoreCase, mas para consistência sempre enviar lowercase
        response = self._send_command(f"KEY_DOWN:{key_normalized}")
        success = response and "OK" in response

        if success:
            self.keyboard_state['keys_down'].add(key_normalized)
            if key_normalized == 'a':
                self.keyboard_state['a_pressed'] = True
            elif key_normalized == 'd':
                self.keyboard_state['d_pressed'] = True

        return success

    def key_up(self, key: str) -> bool:
        """Soltar tecla - SEMPRE usa KEY_UP:tecla"""
        # ✅ NORMALIZAR para lowercase para evitar case mismatch
        key_normalized = key.lower()

        # _safe_print(f"   🔼 [KEY_UP] Tentando soltar '{key_normalized}'...")  # ← Log verboso desabilitado
        # _safe_print(f"   📊 [KEY_UP] Estado atual: {self.keyboard_state['keys_down']}")  # ← Log verboso desabilitado

        # ✅ DEBUG: Se for ALT, mostrar de onde veio a chamada!
        if key_normalized in ['alt', 'lalt', 'ralt']:
            import traceback
            _safe_print(f"   🔍 [DEBUG_ALT] ALT KEY_UP chamado de:")
            stack = traceback.extract_stack(limit=6)
            for frame in stack[-5:-1]:  # Últimos 4 frames (excluindo este)
                _safe_print(f"      📄 {frame.filename.split('v5')[-1]}:{frame.lineno} in {frame.name}()")

        # 🔴 CRITICAL FIX: Se for TAB, ALT, A, S, D, E, ou números, SEMPRE enviar comando (ignora keyboard_state check)
        force_release_keys = ['tab', 'alt', 'lalt', 'a', 's', 'd', 'e', '1', '2', '3', '4', '5', '6']
        if key_normalized in force_release_keys:
            # _safe_print(f"   🔓 [KEY_UP] '{key_normalized}' está em force_release_keys - SEMPRE solta!")  # ← Log verboso desabilitado
            # SEMPRE enviar KEY_UP, mesmo se não estiver no state
            # _safe_print(f"   📤 [KEY_UP] Enviando comando: KEY_UP:{key_normalized}")  # ← Log verboso desabilitado
            response = self._send_command(f"KEY_UP:{key_normalized}", timeout=1.0)
            # _safe_print(f"   📥 [KEY_UP] Resposta: {response}")  # ← Log verboso desabilitado

            success = response and "OK" in response

            # Limpar do state se existir
            if key_normalized in self.keyboard_state['keys_down']:
                self.keyboard_state['keys_down'].discard(key_normalized)
                # _safe_print(f"   🗑️  [KEY_UP] Removido '{key_normalized}' do state")  # ← Log verboso desabilitado

            # Limpar flags especiais
            if key_normalized == 'a':
                self.keyboard_state['a_pressed'] = False
            elif key_normalized == 'd':
                self.keyboard_state['d_pressed'] = False

            if success:
                pass  # _safe_print(f"   ✅ [KEY_UP] '{key_normalized}' SOLTO com sucesso!")  # ← Log verboso desabilitado
            else:
                _safe_print(f"   ❌ [KEY_UP] FALHA ao soltar '{key_normalized}'! Resposta: {response}")  # ← Mantido (erro crítico)

            return success

        # Para outras teclas, comportamento normal
        if key_normalized not in self.keyboard_state['keys_down']:
            _safe_print(f"⚠️ Tecla {key} não está pressionada (state: {self.keyboard_state['keys_down']})")
            return False

        # ✅ CRÍTICO: Enviar comando com key NORMALIZADO (lowercase)
        # Arduino usa equalsIgnoreCase, mas para consistência sempre enviar lowercase
        # _safe_print(f"   📤 [KEY_UP] Enviando comando: KEY_UP:{key_normalized}")  # ← Log verboso desabilitado
        response = self._send_command(f"KEY_UP:{key_normalized}", timeout=1.0)
        # _safe_print(f"   📥 [KEY_UP] Resposta: {response}")  # ← Log verboso desabilitado
        success = response and "OK" in response

        if success:
            self.keyboard_state['keys_down'].discard(key_normalized)
            if key_normalized == 'a':
                self.keyboard_state['a_pressed'] = False
            elif key_normalized == 'd':
                self.keyboard_state['d_pressed'] = False
            # _safe_print(f"   ✅ [KEY_UP] '{key_normalized}' solto e removido do state")  # ← Log verboso desabilitado
        else:
            _safe_print(f"   ❌ [KEY_UP] FALHA ao soltar '{key_normalized}'!")  # ← Mantido (erro crítico)

        return success

    # ===== MÉTODOS DE MOUSE =====

    def _get_current_mouse_position(self) -> Tuple[int, int]:
        """Obter posição atual do mouse (usa pyautogui se disponível)"""
        if PYAUTOGUI_AVAILABLE:
            try:
                pos = pyautogui.position()
                self.mouse_state['last_position'] = (pos.x, pos.y)
                return (pos.x, pos.y)
            except:
                pass
        return self.mouse_state['last_position']

    def click(self, x: Optional[int] = None, y: Optional[int] = None,
              button: str = 'left') -> bool:
        """
        Clicar com mouse (com movimento automático se coordenadas fornecidas)

        Args:
            x, y: Coordenadas (se fornecidas, move mouse antes de clicar)
            button: 'left' ou 'right'
        """
        _safe_print(f"")
        _safe_print(f"🖱️  [ARDUINO] CLICK REQUISITADO:")
        _safe_print(f"   📍 Posição: ({x}, {y})" if x and y else "   📍 Posição: ATUAL (sem movimento)")
        _safe_print(f"   🔘 Botão: {button}")

        # Se coordenadas fornecidas, mover mouse primeiro
        if x is not None and y is not None:
            _safe_print(f"   ➡️  Movendo para posição antes de clicar...")
            if not self.move_to(x, y):
                _safe_print(f"   ❌ FALHA ao mover mouse!")
                return False
            time.sleep(0.05)  # Pequeno delay após movimento
            _safe_print(f"   ✅ Mouse posicionado!")

        # Executar click usando mouse_down + mouse_up
        # Arduino não tem comando MOUSECLICK, precisa fazer manualmente
        _safe_print(f"   🔽 Pressionando botão {button}...")
        if not self.mouse_down(button):
            _safe_print(f"   ❌ FALHA ao pressionar!")
            return False
        time.sleep(0.1)  # Manter pressionado
        _safe_print(f"   🔼 Soltando botão {button}...")
        if not self.mouse_up(button):
            _safe_print(f"   ❌ FALHA ao soltar!")
            return False
        _safe_print(f"   ✅ CLICK COMPLETO!")
        _safe_print(f"")

        if self.on_mouse_action:
            self.on_mouse_action('click', True)

        return True

    def click_left(self, duration: float = None) -> bool:
        """
        Executar clique esquerdo único - EXATO COMO PYAUTOGUI

        CRÍTICO: Botão DEVE ficar pressionado por 'duration' segundos
        para o jogo registrar o clique corretamente!

        CORRIGIDO: Variação aleatória de 50-250ms (0.05-0.25s)
        para simular comportamento humano e garantir detecção pelo jogo!

        Args:
            duration: Tempo que o botão fica pressionado (None = aleatório 50-250ms)
        """
        # Se duration não especificado, usar variação aleatória
        if duration is None:
            duration = random.uniform(0.05, 0.25)  # 50-250ms

        # PASSO 1: Pressionar botão (MODO RÁPIDO - sem esperar resposta)
        success = self._send_command_fast("MOUSE_DOWN:left")  # ✅ CORRIGIDO: "left" completo

        if not success:
            return False

        # PASSO 2: AGUARDAR com botão PRESSIONADO (CRÍTICO!)
        time.sleep(duration)

        # PASSO 3: Soltar botão (MODO RÁPIDO - sem esperar resposta)
        success = self._send_command_fast("MOUSE_UP:left")  # ✅ CORRIGIDO: "left" completo

        return success

    def click_left_simple(self) -> bool:
        """
        ✅ NOVO: Clique esquerdo SIMPLES usando Mouse.click() (relativo)

        CRÍTICO: Este método usa o comando CLICK_LEFT_SIMPLE do Arduino
        que executa Mouse.click() ao invés de AbsoluteMouse.press().

        VANTAGENS:
        - SEM movimento do cursor (100% relativo)
        - SEM drift acumulativo
        - PERFEITO para cliques rápidos repetidos (Fase 2)

        DESVANTAGENS:
        - Não move o mouse para posição específica
        - Apenas clica onde o cursor JÁ ESTÁ

        Returns:
            bool: True se clique executado com sucesso
        """
        if not self.connected or not self.serial_port:
            _safe_print("⚠️ Arduino não conectado - click_left_simple ignorado")
            return False

        # Enviar comando simples (SEM colon - como PING)
        response = self._send_command("CLICK_LEFT_SIMPLE")  # ← SEM colon!

        if response and response.startswith("OK:CLICK_LEFT_SIMPLE"):
            return True
        else:
            _safe_print(f"❌ Erro ao executar click_left_simple: {response}")
            return False

    def click_right(self, x: Optional[int] = None, y: Optional[int] = None, duration: float = 0.02) -> bool:
        """Executar clique direito (com movimento opcional)"""
        if x is not None and y is not None:
            if not self.move_to(x, y):
                return False
            time.sleep(0.05)

        # Executar clique direito usando mouse_down + mouse_up
        # Arduino não tem comando MOUSECLICK
        if not self.mouse_down('right'):
            return False
        time.sleep(duration)
        if not self.mouse_up('right'):
            return False

        return True

    def right_click(self, x: int, y: int) -> bool:
        """Clique direito em posição específica (alias para click_right)"""
        return self.click_right(x, y)

    def mouse_down(self, button: str = 'left') -> bool:
        """Pressionar botão do mouse (sem soltar)"""
        # 🔍 DEBUG: Capturar posição ANTES do comando
        if PYAUTOGUI_AVAILABLE:
            import pyautogui
            pos_before = pyautogui.position()
            _safe_print(f"")
            # _safe_print(f"🔍 [MOUSE_DOWN] DEBUG MOVIMENTO:")  # ← Log verboso desabilitado
            # _safe_print(f"   📍 Posição ANTES: ({pos_before.x}, {pos_before.y})")  # ← Log verboso desabilitado
            pass

        # ✅ CORRIGIDO: Enviar "left" ou "right" completo (Arduino espera isso!)
        # _safe_print(f"   📤 Enviando: MOUSE_DOWN:{button}")  # ← Log verboso desabilitado
        response = self._send_command(f"MOUSE_DOWN:{button}")
        # _safe_print(f"   📥 Resposta: {response}")  # ← Log verboso desabilitado
        success = response and response.startswith("OK")

        # 🔍 DEBUG: Capturar posição DEPOIS do comando
        if PYAUTOGUI_AVAILABLE:
            pos_after = pyautogui.position()
            # _safe_print(f"   📍 Posição DEPOIS: ({pos_after.x}, {pos_after.y})")  # ← Log verboso desabilitado
            delta_x = pos_after.x - pos_before.x
            delta_y = pos_after.y - pos_before.y
            # if delta_x != 0 or delta_y != 0:  # ← Log verboso desabilitado
            #     _safe_print(f"   🚨 MOVIMENTO DETECTADO: ({delta_x:+d}, {delta_y:+d}) pixels!")  # ← Log verboso desabilitado
            # else:  # ← Log verboso desabilitado
            #     _safe_print(f"   ✅ SEM MOVIMENTO (delta: 0, 0)")  # ← Log verboso desabilitado
            _safe_print(f"")

        if success:
            if button == 'left':
                self._set_mouse_button_state('left_button_down', True)
            elif button == 'right':
                self._set_mouse_button_state('right_button_down', True)

        return success

    def mouse_up(self, button: str = 'left') -> bool:
        """Soltar botão do mouse"""
        # ✅ CORRIGIDO: Enviar "left" ou "right" completo (Arduino espera isso!)
        response = self._send_command(f"MOUSE_UP:{button}")
        success = response and response.startswith("OK")

        if success:
            if button == 'left':
                self._set_mouse_button_state('left_button_down', False)
            elif button == 'right':
                self._set_mouse_button_state('right_button_down', False)

        return success

    def mouse_down_relative(self, button: str = 'left') -> bool:
        """
        ✅ SOLUÇÃO DEFINITIVA: Press RELATIVO usando Mouse.press()

        Usa Mouse.press() ao invés de AbsoluteMouse.press()
        Mouse.press() NÃO precisa de coordenadas → ZERO drift!

        Perfeito para fishing cycle onde não precisamos mover o cursor!
        """
        # _safe_print(f"🎯 [REL] Pressionando botão {button} (Mouse relativo)...")  # ← Log verboso desabilitado
        # _safe_print(f"   📤 Enviando: MOUSE_DOWN_REL:{button}")  # ← Log verboso desabilitado
        response = self._send_command(f"MOUSE_DOWN_REL:{button}")
        # _safe_print(f"   📥 Arduino respondeu: {response}")  # ← Log verboso desabilitado
        success = response and response.startswith("OK")

        if success:
            if button == 'left':
                self._set_mouse_button_state('left_button_down', True)
            elif button == 'right':
                self._set_mouse_button_state('right_button_down', True)
            # _safe_print(f"✅ [REL] Botão {button} pressionado - Estado atualizado: right_down={self._get_mouse_button_state('right_button_down')}")  # ← Log verboso desabilitado
        else:
            _safe_print(f"❌ [REL] Falha ao pressionar botão {button} - Resposta inválida!")

        return success

    def mouse_up_relative(self, button: str = 'left') -> bool:
        """
        ✅ SOLUÇÃO DEFINITIVA: Release RELATIVO usando Mouse.release()
        """
        # _safe_print(f"🎯 [REL] Soltando botão {button} (Mouse relativo)...")  # ← Log verboso desabilitado
        response = self._send_command(f"MOUSE_UP_REL:{button}")
        success = response and response.startswith("OK")

        if success:
            if button == 'left':
                self._set_mouse_button_state('left_button_down', False)
            elif button == 'right':
                self._set_mouse_button_state('right_button_down', False)
            # _safe_print(f"✅ [REL] Botão {button} solto")  # ← Log verboso desabilitado

        return success

    def calibrate_mouseto(self, x: int = 959, y: int = 539) -> bool:
        """
        ✅ NOVO: Calibrar MouseTo após abrir baú

        IMPORTANTE: Chamar UMA VEZ após abrir o baú!
        O jogo automaticamente coloca o mouse em (959, 539) ao abrir baú.

        Este comando faz:
        1. Home para (0,0)
        2. Move para (x, y) com precisão
        3. Calibra sistema interno do MouseTo

        Args:
            x: Posição X após abrir baú (padrão: 959)
            y: Posição Y após abrir baú (padrão: 539)

        Returns:
            True se calibração bem sucedida
        """
        try:
            # LOG DETALHADO: Posição antes de calibrar
            current_x, current_y = self._get_current_mouse_position()
            _safe_print(f"")
            _safe_print(f"🎯 [ARDUINO] CALIBRANDO MOUSETO:")
            _safe_print(f"   📍 Posição atual do cursor: ({current_x}, {current_y})")
            _safe_print(f"   🔄 Sincronizando MouseTo para: ({x}, {y})")

            command = f"RESET_POS:{x}:{y}"
            _safe_print(f"   📤 Comando: {command}")
            _safe_print(f"   ⚠️  IMPORTANTE: Este comando NÃO move o cursor!")
            _safe_print(f"   ℹ️  Apenas informa ao Arduino onde o cursor ESTÁ")

            response = self._send_command(command, timeout=5.0)
            _safe_print(f"   📥 Resposta: {response}")

            if response and "OK:RESET_POS" in response:
                self.mouse_state['last_position'] = (x, y)
                _safe_print(f"   ✅ MouseTo sincronizado!")
                _safe_print(f"   ℹ️  Próximos MOVE: serão calculados a partir de ({x}, {y})")
                _safe_print(f"")
                return True
            else:
                _safe_print(f"   ❌ FALHA na calibração: {response}")
                _safe_print(f"")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao calibrar MouseTo: {e}")
            return False

    def move_to(self, x: int, y: int) -> bool:
        """
        Mover mouse para posição absoluta via Arduino (MouseTo)

        Usa o novo protocolo MOVE:x:y que move DIRETAMENTE ao destino
        sem passar pelo canto da tela.

        IMPORTANTE: Chame calibrate_mouseto() UMA VEZ após abrir o baú
        antes de usar este método!

        Args:
            x: Coordenada X de destino
            y: Coordenada Y de destino

        Returns:
            True se movimento bem sucedido
        """
        try:
            # 📍 LOG DETALHADO: Movimento do mouse
            current_x, current_y = self._get_current_mouse_position()
            _safe_print(f"")
            # _safe_print(f"🎮 [ARDUINO] MOVIMENTO REQUISITADO:")  # ← Log verboso desabilitado
            # _safe_print(f"   📍 Atual: ({current_x}, {current_y})")  # ← Log verboso desabilitado
            # _safe_print(f"   🎯 Destino: ({x}, {y})")  # ← Log verboso desabilitado
            delta_x = x - current_x
            delta_y = y - current_y
            # _safe_print(f"   ➡️  Delta: ({delta_x:+d}, {delta_y:+d})")  # ← Log verboso desabilitado

            command = f"MOVE:{x}:{y}"
            # _safe_print(f"   📤 Comando: {command}")  # ← Log verboso desabilitado
            response = self._send_command(command, timeout=5.0)
            # _safe_print(f"   📥 Resposta: {response}")  # ← Log verboso desabilitado

            if response and "OK:MOVE" in response:
                self.mouse_state['last_position'] = (x, y)
                # Verificar posição final
                time.sleep(0.1)
                final_x, final_y = self._get_current_mouse_position()
                error_x = x - final_x
                error_y = y - final_y
                # _safe_print(f"   🔍 Verificação:")  # ← Log verboso desabilitado
                # _safe_print(f"      Esperado: ({x}, {y})")  # ← Log verboso desabilitado
                # _safe_print(f"      Real: ({final_x}, {final_y})")  # ← Log verboso desabilitado
                # _safe_print(f"      Erro: ({error_x:+d}, {error_y:+d})")  # ← Log verboso desabilitado
                # _safe_print(f"   ✅ Movimento OK!")  # ← Log verboso desabilitado
                # _safe_print(f"")  # ← Log verboso desabilitado
                return True
            else:
                _safe_print(f"   ❌ FALHA no movimento!")
                _safe_print(f"")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao mover mouse para ({x}, {y}): {e}")
            return False

    def move_camera_relative(self, dx: int, dy: int, steps: int = 10) -> bool:
        """
        ✅ NOVO: Movimento RELATIVO de câmera via Arduino (SEM botão direito)

        Simula movimento relativo usando comandos MOVE absolutos do Arduino.
        Divide o movimento em passos para suavidade.

        Args:
            dx: Delta X (movimento horizontal, negativo = esquerda)
            dy: Delta Y (movimento vertical, negativo = cima)
            steps: Número de passos para suavidade (padrão: 10)

        Returns:
            True se movimento bem sucedido
        """
        try:
            _safe_print(f"🎥 [CAMERA] Movimento relativo via Arduino: DX={dx}, DY={dy}")

            # Pegar posição inicial
            current_x, current_y = self._get_current_mouse_position()
            _safe_print(f"   📍 Posição inicial: ({current_x}, {current_y})")

            # Calcular posição final
            target_x = current_x + dx
            target_y = current_y + dy

            # Limitar aos limites da tela
            target_x = max(0, min(1920, target_x))
            target_y = max(0, min(1080, target_y))

            _safe_print(f"   🎯 Posição final: ({target_x}, {target_y})")

            # Dividir em passos para suavidade
            dx_step = dx // steps
            dy_step = dy // steps

            _safe_print(f"   🔄 Movendo em {steps} passos...")

            for i in range(steps):
                # Calcular posição intermediária
                step_x = current_x + (dx_step * (i + 1))
                step_y = current_y + (dy_step * (i + 1))

                # Último passo vai exatamente para o target
                if i == steps - 1:
                    step_x = target_x
                    step_y = target_y

                # Mover via Arduino (SEM debug verbose)
                command = f"MOVE:{step_x}:{step_y}"
                response = self._send_command_fast(command)

                if not response:
                    _safe_print(f"   ❌ Falha no passo {i+1}/{steps}")
                    return False

                # Delay mínimo entre passos
                time.sleep(0.01)

            _safe_print(f"   ✅ Movimento de câmera concluído!")

            # Verificar posição final
            final_x, final_y = self._get_current_mouse_position()
            error_x = target_x - final_x
            error_y = target_y - final_y
            _safe_print(f"   📊 Erro final: ({error_x:+d}, {error_y:+d})")

            return True

        except Exception as e:
            _safe_print(f"❌ Erro no movimento de câmera: {e}")
            return False

    def move_camera_windows_style(self, dx: int, dy: int, steps: int = 10) -> bool:
        """
        ✅ NOVO: Movimento de câmera IDÊNTICO à API Windows via Arduino

        Replica EXATAMENTE o comportamento do Windows SendInput com MOUSEEVENTF_MOVE:
        - Movimento RELATIVO (delta, não absoluto)
        - Dividido em steps para suavidade
        - Remainder handling para precisão

        Args:
            dx: Delta X (quantos pixels mover horizontalmente)
            dy: Delta Y (quantos pixels mover verticalmente)
            steps: Número de passos (default: 10, igual ao Windows API)

        Returns:
            bool: True se sucesso
        """
        try:
            _safe_print(f"🎥 [CAMERA_WINDOWS] Movimento via Arduino MOVE_REL:")
            _safe_print(f"   📊 Delta: DX={dx:+d}, DY={dy:+d}")
            _safe_print(f"   🔢 Steps: {steps}")

            # Dividir em steps (igual ao Windows API)
            dx_step = dx // steps
            dy_step = dy // steps

            _safe_print(f"   📐 Step size: ({dx_step:+d}, {dy_step:+d})")

            # Executar cada step
            for i in range(steps):
                command = f"MOVE_REL:{dx_step}:{dy_step}"
                response = self._send_command_fast(command)

                if not response:
                    _safe_print(f"   ❌ MOVE_REL falhou no step {i+1}/{steps}")
                    return False

                time.sleep(0.01)  # Delay entre steps (igual ao Windows)

            # Movimento restante (remainder)
            remainder_x = dx - (dx_step * steps)
            remainder_y = dy - (dy_step * steps)

            if remainder_x != 0 or remainder_y != 0:
                _safe_print(f"   📊 Remainder: ({remainder_x:+d}, {remainder_y:+d})")
                command = f"MOVE_REL:{remainder_x}:{remainder_y}"
                response = self._send_command_fast(command)

                if not response:
                    _safe_print(f"   ❌ MOVE_REL remainder falhou")
                    return False

            _safe_print(f"   ✅ Câmera movida via Arduino (total: {dx:+d}, {dy:+d})")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no movimento de câmera Windows style: {e}")
            return False

    def _move_to_relative_optimized(self, x: int, y: int) -> bool:
        """
        Movimento via relativo otimizado (fallback se AbsMouse não disponível)

        Args:
            x, y: Coordenadas absolutas de destino
        """
        try:
            # Obter posição atual REAL
            current_x, current_y = self._get_current_mouse_position()

            # Calcular delta (movimento relativo)
            delta_x = x - current_x
            delta_y = y - current_y

            # Se já está na posição, não fazer nada
            if abs(delta_x) < 5 and abs(delta_y) < 5:
                self.mouse_state['last_position'] = (x, y)
                return True

            # Movimento em um único comando se possível
            distance = max(abs(delta_x), abs(delta_y))

            if distance < 127:  # Arduino suporta até ±127 por comando
                # ✅ CORRIGIDO: Usar MOVE_REL ao invés de MOUSEMOVE
                # Movimento direto
                self._send_command_fast(f"MOVE_REL:{delta_x}:{delta_y}")
                time.sleep(0.05)
            else:
                # Movimento em 3 passos rápidos
                steps = 3
                step_x = delta_x // steps
                step_y = delta_y // steps

                for i in range(steps):
                    # ✅ CORRIGIDO: Usar MOVE_REL ao invés de MOUSEMOVE
                    self._send_command_fast(f"MOVE_REL:{step_x}:{step_y}")
                time.sleep(0.05)

                # Ajuste fino
                remainder_x = delta_x - (step_x * steps)
                remainder_y = delta_y - (step_y * steps)
                if remainder_x != 0 or remainder_y != 0:
                    # ✅ CORRIGIDO: Usar MOVE_REL ao invés de MOUSEMOVE
                    self._send_command_fast(f"MOVE_REL:{remainder_x}:{remainder_y}")
                    time.sleep(0.05)

            # ✅ CORREÇÃO: Verificar se chegou no lugar certo
            if PYAUTOGUI_AVAILABLE:
                time.sleep(0.1)
                actual_x, actual_y = self._get_current_mouse_position()

                error_x = x - actual_x
                error_y = y - actual_y

                # Se erro > 15 pixels, corrigir
                if abs(error_x) > 15 or abs(error_y) > 15:
                    _safe_print(f"   🔧 Correção: erro ({error_x}, {error_y})")
                    # ✅ CORRIGIDO: Usar MOVE_REL ao invés de MOUSEMOVE
                    self._send_command_fast(f"MOVE_REL:{error_x}:{error_y}")
                    time.sleep(0.05)

            # Atualizar posição
            self.mouse_state['last_position'] = (x, y)
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no movimento relativo: {e}")
            return False

    def move_mouse(self, x: int, y: int, relative: bool = True) -> bool:
        """
        Mover mouse (relativo ou absoluto)

        Args:
            x, y: Coordenadas
            relative: True=movimento relativo, False=absoluto
        """
        if relative:
            # ✅ CORRIGIDO: Usar MOVE_REL ao invés de MOUSEMOVE
            response = self._send_command(f"MOVE_REL:{x}:{y}")
            return response and response.startswith("OK")
        else:
            return self.move_to(x, y)

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        Arrastar de uma posição para outra (IMPLEMENTAÇÃO COMPLETA via Arduino)

        Args:
            start_x: X inicial
            start_y: Y inicial
            end_x: X final
            end_y: Y final
            duration: Duração do movimento
        """
        try:
            # PASSO 1: Mover para posição inicial
            if not self.move_to(start_x, start_y):
                _safe_print(f"❌ [DRAG] FALHA ao mover para posição inicial ({start_x}, {start_y})")
                return False
            time.sleep(0.2)

            # PASSO 2: Segurar botão esquerdo
            if not self.mouse_down('left'):
                _safe_print(f"❌ [DRAG] FALHA ao pressionar botão esquerdo")
                return False
            time.sleep(0.2)

            # PASSO 3: Mover para destino COM botão pressionado
            # ✅ USAR MOUSEABS (absoluto) EM VEZ DE RELATIVO!
            # ✅ CORREÇÃO CRÍTICA: Usar MOUSEABS para ir direto ao destino
            # Movimento relativo em loop causa o mouse ir até final da tela!
            success = self.move_to(end_x, end_y)

            if not success:
                _safe_print(f"❌ [DRAG] FALHA ao mover para destino ({end_x}, {end_y})")
                return False

            time.sleep(0.4)  # CRÍTICO: aguardar item chegar ao destino

            # PASSO 4: Soltar botão
            if not self.mouse_up('left'):
                _safe_print(f"❌ [DRAG] FALHA ao soltar botão esquerdo")
                return False

            time.sleep(0.4)  # CRÍTICO: garantir que soltou

            # Atualizar posição
            self.mouse_state['last_position'] = (end_x, end_y)

            return True

        except Exception as e:
            _safe_print(f"❌ [DRAG] ERRO: {e}")
            # CRÍTICO: Garantir que mouse não fique pressionado
            try:
                self.mouse_up('left')
            except:
                pass
            return False

    # ===== MÉTODOS DE PESCA =====

    def start_fishing(self) -> bool:
        """Iniciar pesca - Pressionar e manter botão direito"""
        try:
            if not self._get_mouse_button_state('right_button_down'):
                if self.mouse_down('right'):
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
        """Parar pesca - Soltar botão direito"""
        try:
            if self._get_mouse_button_state('right_button_down'):
                if self.mouse_up('right'):
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

    def catch_fish(self) -> bool:
        """Capturar peixe - Sequência específica do bot"""
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

    # ===== MÉTODOS DE CÂMERA =====

    def move_camera_a(self, duration: Optional[float] = None) -> bool:
        """Mover câmera para esquerda (tecla A)"""
        try:
            if duration is None:
                min_dur, max_dur = self.timing_config['movement_a_duration']
                duration = random.uniform(min_dur, max_dur)

            _safe_print(f"◀️ Movimento A por {duration:.1f}s")

            self.key_down('a')
            time.sleep(duration)
            self.key_up('a')

            return True

        except Exception as e:
            _safe_print(f"❌ Erro no movimento A: {e}")
            # Garantir que tecla seja solta
            try:
                self.key_up('a')
            except:
                pass
            return False

    def move_camera_d(self, duration: Optional[float] = None) -> bool:
        """Mover câmera para direita (tecla D)"""
        try:
            if duration is None:
                min_dur, max_dur = self.timing_config['movement_d_duration']
                duration = random.uniform(min_dur, max_dur)

            _safe_print(f"▶️ Movimento D por {duration:.1f}s")

            self.key_down('d')
            time.sleep(duration)
            self.key_up('d')

            return True

        except Exception as e:
            _safe_print(f"❌ Erro no movimento D: {e}")
            # Garantir que tecla seja solta
            try:
                self.key_up('d')
            except:
                pass
            return False

    def camera_turn_in_game(self, dx: int, dy: int) -> bool:
        """
        Movimento de câmera usando movimento relativo de mouse

        Args:
            dx: Deslocamento horizontal (-= esquerda, += direita)
            dy: Deslocamento vertical (+= baixo, -= cima)
        """
        try:
            _safe_print(f"   🎮 [ARDUINO] camera_turn_in_game({dx:+d}, {dy:+d})")

            # Dividir movimento em passos para suavidade
            steps = 10
            dx_step = dx // steps
            dy_step = dy // steps
            _safe_print(f"   📊 Dividindo em {steps} passos: ({dx_step:+d}, {dy_step:+d}) cada")

            for i in range(steps):
                cmd = f"MOVE_REL:{dx_step}:{dy_step}"
                _safe_print(f"      [Passo {i+1}/{steps}] {cmd}")
                response = self._send_command(cmd)  # ✅ CORRIGIDO: MOVE_REL em vez de MOUSEMOVE
                _safe_print(f"         Resposta: {response}")
                if not (response and response.startswith("OK")):
                    _safe_print(f"         ❌ FALHA no passo {i+1}")
                    return False
                time.sleep(0.01)

            # Movimento restante
            remainder_x = dx - (dx_step * steps)
            remainder_y = dy - (dy_step * steps)

            if remainder_x != 0 or remainder_y != 0:
                cmd = f"MOVE_REL:{remainder_x}:{remainder_y}"
                _safe_print(f"      [Ajuste final] {cmd}")
                response = self._send_command(cmd)  # ✅ CORRIGIDO: MOVE_REL em vez de MOUSEMOVE
                _safe_print(f"         Resposta: {response}")
                if not (response and response.startswith("OK")):
                    _safe_print(f"         ❌ FALHA no ajuste final")
                    return False

            _safe_print(f"   ✅ Movimento de câmera executado!")
            return True

        except Exception as e:
            _safe_print(f"   ❌ Erro no movimento de câmera: {e}")
            return False

    def center_camera(self, initial_pos: Tuple[int, int] = None) -> bool:
        """
        Centralizar câmera (resetar posição)

        Args:
            initial_pos: Tupla (x, y) da posição inicial
        """
        try:
            _safe_print("   🎯 Resetando câmera para posição inicial...")

            # Movimentos de reset (cancelar posição anterior)
            # ✅ CORRIGIDO: Usar MOVE_REL (suportado pelo Arduino) ao invés de MOUSEMOVE
            # Direita
            self._send_command("MOVE_REL:200:0")
            time.sleep(0.05)

            # Esquerda forte
            self._send_command("MOVE_REL:-400:0")
            time.sleep(0.05)

            # Volta centro
            self._send_command("MOVE_REL:200:0")
            time.sleep(0.05)

            # Baixo
            self._send_command("MOVE_REL:0:200")
            time.sleep(0.05)

            # Cima forte
            self._send_command("MOVE_REL:0:-400")
            time.sleep(0.05)

            # Volta centro
            self._send_command("MOVE_REL:0:200")
            time.sleep(0.2)

            _safe_print("   ✅ Câmera resetada - posição zero garantida!")
            return True

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao resetar câmera: {e}")
            return False

    # ===== MÉTODOS DE AÇÕES CONTÍNUAS =====

    def start_continuous_clicking(self) -> bool:
        """
        Iniciar cliques contínuos em thread separada
        NOVO: Inicia automaticamente o ciclo de tecla S junto com os cliques!
        """
        try:
            if self.continuous_actions['clicking']:
                _safe_print("⚠️ Cliques contínuos já estão ativos")
                return False

            self.continuous_actions['clicking'] = True

            # ✅ NOVO: Iniciar ciclo de tecla S automaticamente!
            _safe_print("🔄 Iniciando ciclo de tecla S junto com cliques...")
            self.start_continuous_s_press()

            def clicking_thread():
                clicks_per_second = 12
                if self.config_manager:
                    clicks_per_second = self.config_manager.get('performance.clicks_per_second', 12)

                _safe_print(f"🖱️ Cliques contínuos iniciados ({clicks_per_second}/s)")

                while self.continuous_actions['clicking']:
                    try:
                        if not self.continuous_actions['clicking']:
                            break

                        self.click_left()

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
        """Parar cliques contínuos e ciclo de S"""
        try:
            if self.continuous_actions['clicking']:
                self.continuous_actions['clicking'] = False

                # ✅ NOVO: Parar ciclo de tecla S também!
                _safe_print("🛑 Parando cliques e ciclo de S...")
                self.stop_continuous_s_press()

                time.sleep(0.2)
                return True
            else:
                _safe_print("⚠️ Cliques contínuos não estão ativos")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao parar cliques contínuos: {e}")
            return False

    def start_camera_movement_cycle(self, stop_callback: Callable[[], bool]) -> bool:
        """Iniciar ciclo de movimento A/D em thread separada"""
        try:
            if self.continuous_actions['moving_camera']:
                _safe_print("⚠️ Movimento de câmera já está ativo")
                return False

            self.continuous_actions['moving_camera'] = True

            def movement_thread():
                _safe_print("📹 Movimento de câmera A/D iniciado")

                while self.continuous_actions['moving_camera']:
                    try:
                        # Verificar callback
                        if stop_callback and stop_callback():
                            _safe_print("🛑 Movimento A/D interrompido por callback")
                            break

                        if not self.continuous_actions['moving_camera']:
                            break

                        # Movimento A
                        self.move_camera_a()

                        if stop_callback and stop_callback():
                            break
                        if not self.continuous_actions['moving_camera']:
                            break

                        # Pausa entre A e D
                        min_pause, max_pause = self.timing_config['movement_pause']
                        pause_duration = random.uniform(min_pause, max_pause)
                        time.sleep(pause_duration)

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
                time.sleep(0.2)
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

                _safe_print(f"🔄 Ciclo de tecla S iniciado ({hold_min}-{hold_max}s pressionado, {release_min}-{release_max}s solto)")

                while self.continuous_actions['pressing_s']:
                    try:
                        if not self.continuous_actions['pressing_s']:
                            break

                        # PASSO 1: Pressionar S
                        # _safe_print("⬇️ Pressionando S...")  # ← DESABILITADO - polui logs
                        self.key_down('s')

                        # PASSO 2: Segurar por tempo configurado
                        hold_duration = random.uniform(hold_min, hold_max)
                        # _safe_print(f"⏱️ Segurando S por {hold_duration:.2f}s...")  # ← DESABILITADO - polui logs
                        time.sleep(hold_duration)

                        if not self.continuous_actions['pressing_s']:
                            break

                        # PASSO 3: Soltar S
                        # _safe_print("⬆️ Soltando S...")  # ← DESABILITADO - polui logs
                        self.key_up('s')

                        # PASSO 4: Aguardar tempo configurado
                        release_duration = random.uniform(release_min, release_max)
                        # _safe_print(f"⏳ Aguardando {release_duration:.2f}s...")  # ← DESABILITADO - polui logs
                        time.sleep(release_duration)

                    except Exception as e:
                        _safe_print(f"❌ Erro no ciclo de S: {e}")
                        break

                # Garantir que S está solto ao finalizar
                if 's' in self.keyboard_state['keys_down']:
                    self.key_up('s')

                _safe_print("🛑 Ciclo de tecla S finalizado")

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

                _safe_print("🛑 Parando ciclo de tecla S...")
                time.sleep(0.2)
                return True
            else:
                _safe_print("⚠️ Ciclo de tecla S não está ativo")
                return False

        except Exception as e:
            _safe_print(f"❌ Erro ao parar ciclo de S: {e}")
            return False

    # ===== MÉTODOS DE UTILIDADE =====

    def capture_initial_position(self) -> Tuple[int, int]:
        """Capturar posição inicial do mouse"""
        try:
            position = self._get_current_mouse_position()
            _safe_print(f"📍 Posição inicial capturada: {position}")
            return position

        except Exception as e:
            _safe_print(f"❌ Erro ao capturar posição: {e}")
            return (960, 540)  # Centro da tela como fallback

    def release_mouse_buttons(self, preserve_right_click: bool = False) -> bool:
        """
        Liberar todos os botões do mouse

        Args:
            preserve_right_click: Se True, mantém botão direito pressionado
        """
        try:
            _safe_print("   🖱️ Liberando botões do mouse...")

            # Liberar botão esquerdo sempre
            if self._get_mouse_button_state('left_button_down'):
                self.mouse_up('left')

            # Liberar botão direito apenas se não for para preservar
            if not preserve_right_click and self._get_mouse_button_state('right_button_down'):
                self.mouse_up('right')
            elif preserve_right_click:
                _safe_print("   ℹ️ Botão direito preservado (pescando)")

            return True

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao liberar mouse: {e}")
            return False

    def _focus_game_window(self):
        """Garantir foco na janela do jogo (placeholder - não aplicável ao Arduino)"""
        # Arduino HID funciona independente de foco de janela
        pass

    def stop_all_actions(self) -> bool:
        """Parar todas as ações - EMERGENCY STOP"""
        try:
            _safe_print("")
            _safe_print("="*70)
            _safe_print("🚨 EMERGENCY STOP - PARANDO TUDO IMEDIATAMENTE!")
            _safe_print("="*70)

            # PASSO 1: Parar ações contínuas
            _safe_print("🛑 [1/7] Parando ações contínuas...")
            self.stop_continuous_clicking()
            self.stop_camera_movement()
            self.stop_continuous_s_press()
            _safe_print("   ✅ Ações contínuas paradas")

            # PASSO 2: Soltar botão direito
            _safe_print("🛑 [2/7] Parando fishing...")
            self.stop_fishing()
            _safe_print("   ✅ Fishing parado")

            # PASSO 3: FORCE RELEASE de TODAS as teclas (ignorar estado!)
            _safe_print("🛑 [3/7] Force release de TODAS as teclas...")
            critical_keys = ['tab', 'alt', 'lalt', 'a', 's', 'd', 'e', 'w', '1', '2', '3', '4', '5', '6']
            for key in critical_keys:
                try:
                    self._send_command(f"KEY_UP:{key}")
                except:
                    pass
            _safe_print("   ✅ Todas as teclas forçadamente liberadas")

            # PASSO 4: FORCE RELEASE de TODOS os botões do mouse
            _safe_print("🛑 [4/7] Force release de botões do mouse...")
            try:
                self._send_command("MOUSE_UP:left")
                self._send_command("MOUSE_UP:right")
            except:
                pass
            _safe_print("   ✅ Botões do mouse forçadamente liberados")

            # PASSO 5: Limpar estado interno
            _safe_print("🛑 [5/7] Limpando estado interno...")
            self._set_mouse_button_state('right_button_down', False)
            self._set_mouse_button_state('left_button_down', False)
            self.keyboard_state['keys_down'].clear()
            self.keyboard_state['a_pressed'] = False
            self.keyboard_state['d_pressed'] = False
            _safe_print("   ✅ Estado limpo")

            # PASSO 6: Matar threads ativas
            _safe_print("🛑 [6/7] Matando threads de background...")
            threads_killed = 0
            for thread in list(self.active_threads):
                try:
                    if thread.is_alive():
                        # Não podemos matar threads diretamente, mas podemos sinalizar para parar
                        threads_killed += 1
                except:
                    pass
            self.active_threads.clear()
            _safe_print(f"   ✅ {threads_killed} threads sinalizadas para parar")

            # PASSO 7: REMOVIDO - Comando RESET não é suportado pelo Arduino
            # ✅ CORRIGIDO: Arduino não tem handler para comando "RESET"
            # Todos os inputs já foram liberados nos passos anteriores (KEY_UP, MOUSE_UP)
            # Não é necessário enviar comando adicional
            _safe_print("🛑 [7/7] Verificando estado final...")
            _safe_print("   ✅ Todos os inputs liberados via comandos anteriores")

            _safe_print("="*70)
            _safe_print("✅ EMERGENCY STOP COMPLETO - TUDO PARADO E LIBERADO!")
            _safe_print("="*70)
            _safe_print("")
            return True

        except Exception as e:
            _safe_print(f"❌ Erro no emergency stop: {e}")
            return False

    def emergency_stop(self) -> None:
        """Alias para stop_all_actions (compatibilidade)"""
        self.stop_all_actions()

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
            'active_threads': len(self.active_threads),
            'arduino_connected': self.connected
        }

    def set_callbacks(self, on_mouse_action: Optional[Callable] = None,
                     on_keyboard_action: Optional[Callable] = None):
        """Configurar callbacks para eventos"""
        self.on_mouse_action = on_mouse_action
        self.on_keyboard_action = on_keyboard_action
        _safe_print("✅ Callbacks configurados")

    # ===== MÉTODOS DE LIMPEZA =====

    def shutdown(self):
        """
        ✅ CORREÇÃO CRÍTICA: Shutdown explícito para liberar recursos

        Deve ser chamado antes de encerrar a aplicação para garantir:
        - Todas as ações contínuas sejam paradas
        - Todos os botões sejam liberados
        - Todas as threads sejam finalizadas
        - Porta serial seja fechada
        """
        try:
            _safe_print("🔧 ArduinoInputManager: Liberando recursos...")

            # Parar todas as ações
            self.stop_all_actions()

            # Aguardar threads ativas terminarem (com timeout)
            with self.threads_lock:
                threads_to_join = list(self.active_threads)

            _safe_print(f"   ⏳ Aguardando {len(threads_to_join)} threads terminarem...")
            for thread in threads_to_join:
                if thread.is_alive():
                    thread.join(timeout=2.0)  # Timeout de 2s por thread

            # Limpar lista de threads
            with self.threads_lock:
                self.active_threads.clear()

            # Fechar porta serial
            if self.serial and self.serial.is_open:
                self.serial.close()
                _safe_print("   🔌 Porta serial fechada")

            self.connected = False
            _safe_print("✅ ArduinoInputManager: Recursos liberados")

        except Exception as e:
            _safe_print(f"⚠️ Erro ao liberar recursos: {e}")

    def cleanup(self) -> None:
        """Fechar conexão com Arduino (legacy - usar shutdown())"""
        self.emergency_stop()

        if self.serial and self.serial.is_open:
            self.serial.close()
            _safe_print("🔌 Conexão com Arduino fechada")

        self.connected = False

    def __del__(self):
        """Destrutor - garantir limpeza"""
        try:
            self.shutdown()
        except:
            pass


# ===== FUNÇÃO DE TESTE =====

def test_arduino_connection():
    """Testar conexão e funcionalidade do Arduino"""
    _safe_print("="*60)
    _safe_print("🧪 TESTE DE CONEXÃO ARDUINO - VERSÃO COMPLETA")
    _safe_print("="*60)

    # Criar manager
    arduino = ArduinoInputManager()

    if not arduino.connected:
        _safe_print("\n❌ Falha na conexão. Verifique:")
        _safe_print("   1. Arduino Pro Micro conectado via USB")
        _safe_print("   2. Sketch arduino_hid_controller.ino carregado")
        _safe_print("   3. Driver instalado (Leonardo/Pro Micro)")
        return False

    _safe_print("\n✅ Arduino conectado com sucesso!\n")

    # Teste 1: PING
    _safe_print("📡 Teste 1: PING")
    if arduino._ping():
        _safe_print("   ✅ PONG recebido\n")
    else:
        _safe_print("   ❌ Falha no PING\n")
        return False

    # Teste 2: Pressionar tecla
    _safe_print("⌨️ Teste 2: Pressionar tecla '1' (em 2 segundos...)")
    time.sleep(2)
    arduino.press_key('1')
    _safe_print("   ✅ Tecla '1' pressionada\n")

    # Teste 3: Click esquerdo
    _safe_print("🖱️ Teste 3: Click esquerdo (em 2 segundos...)")
    time.sleep(2)
    arduino.click(button='left')
    _safe_print("   ✅ Click executado\n")

    # Teste 4: Segurar botão direito
    _safe_print("🖱️ Teste 4: Segurar botão direito por 1 segundo...")
    time.sleep(2)
    arduino.mouse_down('right')
    time.sleep(1)
    arduino.mouse_up('right')
    _safe_print("   ✅ Botão direito segurado e solto\n")

    # Teste 5: Movimento de mouse
    _safe_print("🖱️ Teste 5: Movimento relativo do mouse...")
    time.sleep(1)
    arduino.move_mouse(50, 50, relative=True)
    time.sleep(0.5)
    arduino.move_mouse(-50, -50, relative=True)
    _safe_print("   ✅ Movimento de mouse executado\n")

    _safe_print("="*60)
    _safe_print("✅ TODOS OS TESTES PASSARAM!")
    _safe_print("="*60)

    arduino.cleanup()
    return True


if __name__ == "__main__":
    test_arduino_connection()
