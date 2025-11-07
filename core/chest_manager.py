#!/usr/bin/env python3
"""
🔧 ChestManager - Sistema Unificado de Abertura de Baú
Reutilizado por: Alimentação, Manutenção de Varas, Limpeza Automática
"""

import os
import time
import pickle
import pyautogui
from typing import Optional, Dict, Any, Callable, Tuple
from enum import Enum
import threading
import re

# Wrapper de print seguro para encoding
def _safe_print(text):
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re as _re
        clean = _re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)



class ChestSide(Enum):
    LEFT = "left"
    RIGHT = "right"


class MacroType(Enum):
    STANDARD = "standard"  # Macro padrão
    CUSTOM = "custom"      # Macro personalizado


class ChestOperation(Enum):
    FEEDING = "feeding"
    MAINTENANCE = "maintenance" 
    CLEANING = "cleaning"


class ChestManager:
    """
    🏪 Gerenciador Unificado de Baú
    
    Sistema centralizado para abertura/fechamento de baú usado por:
    - Sistema de Alimentação (F6)
    - Manutenção de Varas (Tecla 0)  
    - Limpeza Automática
    """
    
    def __init__(self, config_manager, input_manager=None, game_state=None):
        self.config_manager = config_manager
        self.input_manager = input_manager
        self.game_state = game_state or {}
        self.chest_lock = threading.RLock()
        
        # Estado do baú
        self.is_chest_open = False
        self.current_operation = None
        self.operation_context = ""
        
        # Configurações de macro
        self.macro_files = {
            ChestSide.LEFT: {
                MacroType.STANDARD: "left_macro.pkl",
                MacroType.CUSTOM: "custom_left_macro.pkl"
            },
            ChestSide.RIGHT: {
                MacroType.STANDARD: "right_macro.pkl", 
                MacroType.CUSTOM: "custom_right_macro.pkl"
            }
        }
        
        # Callbacks para diferentes operações
        self.operation_callbacks = {}
        
    def register_operation_callback(self, operation: ChestOperation, callback: Callable):
        """Registrar callback para operação específica"""
        self.operation_callbacks[operation] = callback
        
    def get_chest_config(self) -> Dict[str, Any]:
        """Obter configurações atuais do baú"""
        return {
            'side': self.config_manager.get('chest_side', 'left'),
            'distance': self.config_manager.get('chest_distance', 300),
            'vertical_offset': self.config_manager.get('chest_vertical_offset', 200),
            'macro_type': self.config_manager.get('macro_type', 'standard')
        }
    
    def ensure_initial_camera_position(self) -> bool:
        """Garantir que posição inicial da câmera está definida"""
        try:
            initial_pos = self.config_manager.get('initial_camera_pos')
            if not initial_pos:
                _safe_print("🔧 [CHEST] Definindo posição inicial da câmera...")
                current_pos = pyautogui.position()
                self.config_manager.set('initial_camera_pos', {
                    'x': current_pos.x,
                    'y': current_pos.y
                })
                self.config_manager.save_config()
                _safe_print(f"✅ [CHEST] Posição inicial definida: ({current_pos.x}, {current_pos.y})")
                
            return True
            
        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao definir posição inicial: {e}")
            return False
    
    def release_mouse_buttons(self):
        """Liberar todos os botões do mouse (segurança)"""
        try:
            # ✅ CRÍTICO: Usar InputManager se disponível para atualizar estado interno
            if self.input_manager:
                # Liberar botão direito via InputManager (atualiza state)
                if hasattr(self.input_manager, 'mouse_up'):
                    self.input_manager.mouse_up('right')
                if hasattr(self.input_manager, 'mouse_up'):
                    self.input_manager.mouse_up('left')
                _safe_print("🛡️ [SAFETY] Botões do mouse liberados via InputManager")
            else:
                # Fallback para pyautogui (não atualiza state, mas libera fisicamente)
                pyautogui.mouseUp(button='left')
                pyautogui.mouseUp(button='right')
                pyautogui.mouseUp(button='middle')
                _safe_print("⚠️ [SAFETY] Botões liberados via pyautogui (InputManager não disponível)")

            time.sleep(0.1)
        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao liberar botões: {e}")
    
    def center_camera(self, position: Optional[Tuple[int, int]] = None):
        """Centralizar câmera na posição inicial"""
        try:
            if position:
                target_x, target_y = position
            else:
                initial_pos = self.config_manager.get('initial_camera_pos')
                if initial_pos:
                    target_x = initial_pos['x']
                    target_y = initial_pos['y']
                else:
                    # Fallback para centro da tela
                    screen_width, screen_height = pyautogui.size()
                    target_x = screen_width // 2
                    target_y = screen_height // 2

            _safe_print(f"📍 [CHEST] Centralizando câmera em ({target_x}, {target_y})")

            # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
            if self.input_manager and hasattr(self.input_manager, 'move_to'):
                self.input_manager.move_to(target_x, target_y)
                _safe_print("✅ [CHEST] Câmera centralizada via Arduino")
            else:
                # Fallback para pyautogui se InputManager não disponível
                pyautogui.moveTo(target_x, target_y, duration=0.3)
                _safe_print("⚠️ [CHEST] Câmera centralizada via pyautogui (fallback)")

            time.sleep(0.2)
            return True

        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao centralizar câmera: {e}")
            return False
    
    def execute_camera_movement(self, chest_config: Dict[str, Any]) -> bool:
        """Executar movimento da câmera para o baú"""
        try:
            side = chest_config['side']
            distance = chest_config['distance']
            vertical_offset = chest_config['vertical_offset']

            # Calcular movimento
            # ✅ CORREÇÃO: Windows SendInput com ALT (freelook) tem eixo X invertido!
            # Movimento POSITIVO = esquerda | Movimento NEGATIVO = direita
            if side == 'left':
                dx = distance  # Positivo = esquerda
            elif side == 'right':
                dx = -distance  # Negativo = direita
            else:
                dx = 0

            dy = abs(vertical_offset)  # Sempre positivo (para baixo)

            _safe_print(f"📐 [CHEST] Movimento calculado: DX={dx}, DY={dy}")

            if dx != 0 or dy != 0:
                # ✅ CORREÇÃO: Usar movimento RELATIVO para câmera (não absoluto!)
                # Durante ALT (freelook), cursor fica invisível - precisa mover RELATIVO

                # 📍 LOG DETALHADO: Movimento da câmera
                _safe_print(f"")
                _safe_print(f"📹 [CHEST] MOVIMENTO DA CÂMERA (FREELOOK):")
                _safe_print(f"   🎮 Modo: ALT + Movimento Relativo")
                _safe_print(f"   ➡️  Deslocamento: DX={dx:+d}, DY={dy:+d}")
                _safe_print(f"   ⚠️  Cursor invisível durante ALT!")
                _safe_print(f"")

                if self.input_manager and hasattr(self.input_manager, 'camera_turn_in_game'):
                    # Usar movimento relativo via Arduino (MOVE_REL ou loop suave)
                    _safe_print(f"   🚀 Executando camera_turn_in_game({dx}, {dy}) via {type(self.input_manager).__name__}...")
                    result = self.input_manager.camera_turn_in_game(dx, dy)
                    _safe_print(f"   📥 Resultado movimento: {result}")
                    _safe_print(f"   ✅ Câmera movida via InputManager!")
                    _safe_print(f"")
                else:
                    # Fallback para pyautogui se InputManager não disponível
                    _safe_print("   ⚠️ InputManager não tem camera_turn_in_game - usando pyautogui")
                    current_pos = pyautogui.position()
                    target_x = current_pos.x + dx
                    target_y = current_pos.y + dy
                    pyautogui.moveTo(target_x, target_y, duration=0.5)
                    _safe_print("⚠️ [CHEST] Câmera movida via pyautogui (fallback)")

                time.sleep(0.3)

            return True

        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro no movimento da câmera: {e}")
            return False
    
    def execute_standard_macro(self, chest_config: Dict[str, Any]) -> bool:
        """Executar macro padrão de abertura de baú"""
        _safe_print("🔧 [CHEST] Executando macro PADRÃO...")

        try:
            # 0. ✅ CRÍTICO: SEMPRE liberar ALT ANTES (prevenção de ALT preso)
            try:
                _safe_print("🛡️ [SAFETY] Liberando ALT preventivamente...")
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                else:
                    pyautogui.keyUp('alt')
                time.sleep(0.1)
            except:
                pass

            # 1. Centralizar câmera
            # ✅ DESABILITADO: center_camera() não funciona com HID-Project (MOVE_REL não implementado)
            # O HID-Project usa movimento absoluto, não precisa de reset de câmera
            # if not self.center_camera():
            #     return False

            # 2. ✅ CRÍTICO: Liberar botões do mouse ANTES de ALT
            self.release_mouse_buttons()

            # 3. ALT Down (freelook) - ✅ USAR ARDUINO
            _safe_print("\n🔑 [CHEST] === INICIANDO SEQUÊNCIA ALT DOWN ===")
            _safe_print(f"   📊 InputManager disponível? {self.input_manager is not None}")
            _safe_print(f"   📊 InputManager tipo: {type(self.input_manager).__name__ if self.input_manager else 'None'}")
            _safe_print(f"   📊 Tem key_down? {hasattr(self.input_manager, 'key_down') if self.input_manager else False}")

            if self.input_manager and hasattr(self.input_manager, 'key_down'):
                _safe_print(f"   🚀 Enviando ALT Down via {type(self.input_manager).__name__}...")
                result = self.input_manager.key_down('ALT')
                _safe_print(f"   📥 Resultado: {result}")
                _safe_print("✅ [CHEST] ALT Down via InputManager")
            else:
                _safe_print("   ⚠️ InputManager não disponível - usando pyautogui")
                pyautogui.keyDown('alt')
                _safe_print("⚠️ [CHEST] ALT Down via pyautogui (fallback)")

            _safe_print("   ⏳ Aguardando 0.5s após ALT...")
            time.sleep(0.5)
            _safe_print("   ✅ Delay concluído\n")

            # 4. Movimento da câmera
            if not self.execute_camera_movement(chest_config):
                # Garantir que ALT seja solto
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                else:
                    pyautogui.keyUp('alt')
                return False

            # 5. Pressionar E (interagir) - ✅ USAR ARDUINO
            _safe_print("\n⌨️ [CHEST] === PRESSIONANDO TECLA E ===")
            _safe_print(f"   📊 InputManager disponível? {self.input_manager is not None}")
            _safe_print(f"   📊 Tem press_key? {hasattr(self.input_manager, 'press_key') if self.input_manager else False}")

            if self.input_manager and hasattr(self.input_manager, 'press_key'):
                _safe_print(f"   🚀 Enviando press_key('E') via {type(self.input_manager).__name__}...")
                result = self.input_manager.press_key('E')
                _safe_print(f"   📥 Resultado: {result}")
                _safe_print("✅ [CHEST] E pressionado via InputManager")
            else:
                # Fallback para pyautogui
                _safe_print("   ⚠️ InputManager não disponível - usando pyautogui")
                pyautogui.press('e')
                _safe_print("⚠️ [CHEST] E via pyautogui (fallback)")

            _safe_print("   ⏳ Aguardando 0.5s após E...")
            time.sleep(0.5)
            _safe_print("   ✅ Delay concluído\n")

            # ✅ CORREÇÃO: ALT permanece pressionado durante TODA a operação de baú!
            # Será solto APENAS em _close_chest(), antes do TAB
            _safe_print("   ⚠️ ALT permanece pressionado durante operações...")

            return True

        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro no macro padrão: {e}")
            # Garantir que ALT seja solto
            try:
                if self.input_manager and hasattr(self.input_manager, 'key_up'):
                    self.input_manager.key_up('ALT')
                else:
                    pyautogui.keyUp('alt')
            except:
                pass
            return False
    
    def load_custom_macro(self, chest_side: ChestSide) -> Optional[list]:
        """Carregar macro personalizado do arquivo"""
        try:
            macro_file = self.macro_files[chest_side][MacroType.CUSTOM]
            
            if os.path.exists(macro_file):
                with open(macro_file, 'rb') as f:
                    macro_data = pickle.load(f)
                _safe_print(f"✅ [CHEST] Macro personalizado carregado: {macro_file}")
                return macro_data
            else:
                _safe_print(f"⚠️ [CHEST] Macro personalizado não encontrado: {macro_file}")
                return None
                
        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao carregar macro personalizado: {e}")
            return None
    
    def execute_custom_macro(self, chest_side: ChestSide) -> bool:
        """Executar macro personalizado"""
        _safe_print("🎯 [CHEST] Executando macro PERSONALIZADO...")

        try:
            macro_data = self.load_custom_macro(chest_side)
            if not macro_data:
                _safe_print("❌ [CHEST] Macro personalizado não disponível, usando padrão")
                return False

            # Executar comandos do macro
            for command in macro_data:
                action = command.get('action')

                if action == 'move':
                    x, y = command['x'], command['y']
                    # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
                    if self.input_manager and hasattr(self.input_manager, 'move_to'):
                        self.input_manager.move_to(x, y)
                    else:
                        duration = command.get('duration', 0.1)
                        pyautogui.moveTo(x, y, duration=duration)

                elif action == 'click':
                    button = command.get('button', 'left')
                    # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
                    if self.input_manager and hasattr(self.input_manager, 'click'):
                        self.input_manager.click(x=None, y=None, button=button)
                    else:
                        pyautogui.click(button=button)

                elif action == 'key':
                    key = command['key']
                    # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
                    if self.input_manager and hasattr(self.input_manager, 'press_key'):
                        self.input_manager.press_key(key)
                    else:
                        pyautogui.press(key)

                elif action == 'key_down':
                    key = command['key']
                    # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
                    if self.input_manager and hasattr(self.input_manager, 'key_down'):
                        self.input_manager.key_down(key)
                    else:
                        pyautogui.keyDown(key)

                elif action == 'key_up':
                    key = command['key']
                    # ✅ USAR ARDUINO via InputManager ao invés de pyautogui
                    if self.input_manager and hasattr(self.input_manager, 'key_up'):
                        self.input_manager.key_up(key)
                    else:
                        pyautogui.keyUp(key)

                elif action == 'sleep':
                    duration = command['duration']
                    time.sleep(duration)

                # Pequena pausa entre comandos
                time.sleep(0.05)

            _safe_print("✅ [CHEST] Macro personalizado executado!")
            return True

        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro no macro personalizado: {e}")
            return False
    
    def open_chest(self, operation: ChestOperation, context: str = "") -> bool:
        """
        🏪 Abertura Unificada de Baú
        
        Usado por todos os sistemas:
        - Alimentação (F6)
        - Manutenção de Varas (Tecla 0)
        - Limpeza Automática
        """
        with self.chest_lock:
            if self.is_chest_open:
                _safe_print(f"📦 [CHEST] Baú já está aberto para: {self.operation_context}")
                return True
            
            _safe_print(f"\n📦 [CHEST] Abrindo baú para: {operation.value}")
            if context:
                _safe_print(f"📋 [CHEST] Contexto: {context}")

            # ✅ CRÍTICO: Parar TODOS os inputs antes de abrir baú
            # Durante pesca: cliques contínuos, movimento A/D, tecla S estão ativos
            # DEVEM ser parados antes de abrir baú!
            if self.input_manager and hasattr(self.input_manager, 'stop_all_actions'):
                _safe_print("🛑 [CHEST] Parando todos os inputs (cliques, A/D, S)...")
                self.input_manager.stop_all_actions()
                time.sleep(0.3)  # Aguardar inputs pararem completamente
                _safe_print("✅ [CHEST] Inputs parados com sucesso")
            else:
                _safe_print("⚠️ [CHEST] InputManager.stop_all_actions() não disponível!")

            # Garantir posição inicial
            if not self.ensure_initial_camera_position():
                return False

            # Obter configurações
            chest_config = self.get_chest_config()
            _safe_print(f"⚙️ [CHEST] Config: {chest_config['side']} side, {chest_config['distance']}px, macro {chest_config['macro_type']}")
            
            # Decidir qual macro usar
            success = False
            if chest_config['macro_type'] == 'custom':
                chest_side = ChestSide.LEFT if chest_config['side'] == 'left' else ChestSide.RIGHT
                success = self.execute_custom_macro(chest_side)
                
                # Fallback para padrão se personalizado falhar
                if not success:
                    _safe_print("🔄 [CHEST] Fallback para macro padrão...")
                    success = self.execute_standard_macro(chest_config)
            else:
                success = self.execute_standard_macro(chest_config)
            
            if success:
                self.is_chest_open = True
                self.current_operation = operation
                self.operation_context = context

                # Atualizar game state se disponível
                if self.game_state is not None:
                    if hasattr(self.game_state, 'set_chest_open'):
                        self.game_state.set_chest_open(True)
                    elif isinstance(self.game_state, dict):
                        self.game_state['chest_open'] = True

                # ✅ CORREÇÃO: NÃO chamar calibrate_mouseto() porque causa movimento!
                # O jogo coloca o mouse em (959, 539) automaticamente
                # O primeiro move_to() já sincroniza naturalmente
                time.sleep(0.5)  # Aguardar o jogo posicionar mouse

                # Chamar callback se registrado
                if operation in self.operation_callbacks:
                    try:
                        self.operation_callbacks[operation](opened=True, context=context)
                    except Exception as e:
                        _safe_print(f"⚠️ [CHEST] Erro no callback: {e}")

                _safe_print(f"✅ [CHEST] Baú aberto com sucesso para: {operation.value}")

                # Aguardar estabilização
                time.sleep(1.0)

                return True
            else:
                _safe_print(f"❌ [CHEST] Falha ao abrir baú para: {operation.value}")
                return False
    
    def close_chest(self, context: str = "") -> bool:
        """Fechar baú e limpar estado"""
        with self.chest_lock:
            if not self.is_chest_open:
                _safe_print("📦 [CHEST] Baú já está fechado")
                return True

            _safe_print(f"📦 [CHEST] Fechando baú após: {self.operation_context}")
            if context:
                _safe_print(f"📋 [CHEST] Contexto: {context}")

            try:
                # ✅ CRÍTICO: SEMPRE liberar ALT ANTES de fechar baú (bug do loop infinito)
                try:
                    _safe_print("🛡️ [SAFETY] Liberando ALT antes de fechar baú...")
                    if self.input_manager and hasattr(self.input_manager, 'key_up'):
                        self.input_manager.key_up('ALT')
                    else:
                        pyautogui.keyUp('alt')
                    time.sleep(0.1)
                except:
                    pass

                # Fechar com TAB - ✅ USAR ARDUINO
                _safe_print("⌨️ [CHEST] Pressionando TAB para fechar")
                if self.input_manager and hasattr(self.input_manager, 'press_key'):
                    self.input_manager.press_key('TAB')
                    _safe_print("✅ [CHEST] TAB via Arduino")
                else:
                    # Fallback para Windows API
                    import win32api, win32con
                    win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)  # TAB down
                    time.sleep(0.02)
                    win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)  # TAB up
                    _safe_print("⚠️ [CHEST] TAB via Windows API (fallback)")
                time.sleep(0.5)
                
                # Limpar estado
                operation = self.current_operation
                old_context = self.operation_context
                
                self.is_chest_open = False
                self.current_operation = None
                self.operation_context = ""
                
                # Atualizar game state se disponível
                if self.game_state is not None:
                    if hasattr(self.game_state, 'set_chest_open'):
                        self.game_state.set_chest_open(False)
                        self.game_state.set_inventory_open(False)
                    elif isinstance(self.game_state, dict):
                        self.game_state['chest_open'] = False
                        self.game_state['inventory_open'] = False
                
                # Chamar callback se registrado
                if operation and operation in self.operation_callbacks:
                    try:
                        self.operation_callbacks[operation](opened=False, context=old_context)
                    except Exception as e:
                        _safe_print(f"⚠️ [CHEST] Erro no callback: {e}")
                
                _safe_print("✅ [CHEST] Baú fechado com sucesso")
                return True
                
            except Exception as e:
                _safe_print(f"❌ [CHEST] Erro ao fechar baú: {e}")
                return False
    
    def is_open(self) -> bool:
        """Verificar se baú está aberto"""
        return self.is_chest_open
    
    def get_current_operation(self) -> Optional[ChestOperation]:
        """Obter operação atual do baú"""
        return self.current_operation
    
    def force_close(self):
        """Forçar fechamento do baú (emergência)"""
        with self.chest_lock:
            _safe_print("🚨 [CHEST] Fechamento forçado!")
            try:
                # ✅ USAR ARDUINO primeiro
                if self.input_manager and hasattr(self.input_manager, 'press_key'):
                    self.input_manager.press_key('TAB')
                    _safe_print("✅ [CHEST] TAB forçado via Arduino")
                else:
                    # Fallback para Windows API
                    import win32api, win32con
                    win32api.keybd_event(win32con.VK_TAB, 0, 0, 0)  # TAB down
                    time.sleep(0.02)
                    win32api.keybd_event(win32con.VK_TAB, 0, win32con.KEYEVENTF_KEYUP, 0)  # TAB up
                    _safe_print("⚠️ [CHEST] TAB forçado via Windows API (fallback)")
                time.sleep(0.3)
            except:
                try:
                    pyautogui.press('tab')
                    time.sleep(0.3)
                except:
                    pass
            
            self.is_chest_open = False
            self.current_operation = None
            self.operation_context = ""
            
            if self.game_state is not None:
                if hasattr(self.game_state, 'set_chest_open'):
                    self.game_state.set_chest_open(False)
                    self.game_state.set_inventory_open(False)
                elif isinstance(self.game_state, dict):
                    self.game_state['chest_open'] = False
                    self.game_state['inventory_open'] = False
    
    def create_custom_macro(self, chest_side: ChestSide, commands: list) -> bool:
        """Criar macro personalizado"""
        try:
            macro_file = self.macro_files[chest_side][MacroType.CUSTOM]
            
            with open(macro_file, 'wb') as f:
                pickle.dump(commands, f)
            
            _safe_print(f"✅ [CHEST] Macro personalizado criado: {macro_file}")
            return True
            
        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao criar macro personalizado: {e}")
            return False
    
    def setup_default_macros(self) -> bool:
        """Configurar macros padrão se não existirem"""
        try:
            for side in ChestSide:
                standard_file = self.macro_files[side][MacroType.STANDARD]
                
                if not os.path.exists(standard_file):
                    _safe_print(f"🔧 [CHEST] Criando macro padrão: {standard_file}")
                    
                    # Macro padrão simples baseado na análise do código original
                    default_commands = [
                        {'action': 'key_down', 'key': 'alt'},
                        {'action': 'sleep', 'duration': 0.5},
                        {'action': 'move', 'x': 960 + (300 if side == ChestSide.RIGHT else -300), 'y': 540, 'duration': 0.5},
                        {'action': 'sleep', 'duration': 0.3},
                        {'action': 'key', 'key': 'e'},
                        {'action': 'sleep', 'duration': 0.5},
                        {'action': 'key_up', 'key': 'alt'}
                    ]
                    
                    with open(standard_file, 'wb') as f:
                        pickle.dump(default_commands, f)
                    
                    _safe_print(f"✅ [CHEST] Macro padrão criado: {standard_file}")
            
            return True
            
        except Exception as e:
            _safe_print(f"❌ [CHEST] Erro ao configurar macros padrão: {e}")
            return False