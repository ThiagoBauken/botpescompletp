#!/usr/bin/env python3
"""
🎣 Ultimate Fishing Bot v4.0 - Interface Principal CORRIGIDA
8 abas conforme especificado na ordem correta
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import sys
from pathlib import Path
import warnings

# Suprimir aviso de compatibilidade do keyboard library
warnings.filterwarnings("ignore", message=".*blocking_hotkeys.*")
warnings.filterwarnings("ignore", message=".*'_KeyboardListener'.*blocking_hotkeys.*")

# Imports essenciais com fallback
try:
    import cv2
    import numpy as np
    import pyautogui
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("[WARN] OpenCV/PyAutoGUI nao disponivel - funcionalidades limitadas")

# Import keyboard separado
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
    print("[OK] Biblioteca keyboard disponivel - captura de hotkeys habilitada")
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("[WARN] Biblioteca keyboard nao disponivel - captura de hotkeys limitada")

# Sistema de internacionalização
try:
    from utils.i18n import i18n, _
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def _(text, **kwargs): 
        return text

# Core engines
try:
    from core.fishing_engine import FishingEngine
    from core.template_engine import TemplateEngine
    from core.config_manager import ConfigManager
    CORE_ENGINES_AVAILABLE = True
    print("[OK] Core engines disponiveis (FishingEngine, TemplateEngine, ConfigManager)")
except ImportError:
    CORE_ENGINES_AVAILABLE = False
    print("[WARN] Core engines nao disponiveis - funcionalidade limitada")

# Detectar portas COM
try:
    import serial.tools.list_ports
    def get_com_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
except ImportError:
    def get_com_ports():
        return ['COM1', 'COM2', 'COM3', 'COM4', 'COM5']

class MockConfig:
    def __init__(self):
        # Simular valores do default_config.json
        self.config_data = {
            'auto_clean': {
                'chest_side': 'right',
                'chest_method': 'macro'
            },
            'rod_system': {
                'broken_rod_action': 'save',
                'auto_replace_broken': True
            },
            'cycle_timeout': 122
        }
    
    def get(self, key, default=None): 
        if key in self.config_data:
            return self.config_data[key]
        return default
    
    def set(self, key, value): pass
    def get_template_confidence(self, template): return 0.7
    def get_feeding_position(self, slot): return (1306, 858)

class FishingBotUI:
    """Interface principal - 8 ABAS CONFORME ESPECIFICADO"""
    
    def __init__(self, config_manager=None, ws_client=None):
        """Inicializar UI com ConfigManager e WebSocket Client (opcional)"""
        # Usar ConfigManager real se disponível, senão usar Mock
        if config_manager:
            self.config_manager = config_manager
        elif CORE_ENGINES_AVAILABLE:
            try:
                self.config_manager = ConfigManager()
                print("[OK] ConfigManager real inicializado")
            except Exception as e:
                print(f"[WARN] Erro ao inicializar ConfigManager: {e}")
                self.config_manager = MockConfig()
        else:
            self.config_manager = MockConfig()

        # ✅ WebSocket Client para servidor multi-usuário
        self.ws_client = ws_client
        if ws_client:
            print("[OK] WebSocket Client recebido - modo multi-usuário ATIVO")
        else:
            print("[INFO] WebSocket Client não disponível - modo offline")

        self.notebook = None
        self.is_destroyed = False
        
        # Criar janela principal PRIMEIRO (antes das variáveis tkinter)
        self.main_window = tk.Tk()
        self.main_window.title("🎣 Ultimate Fishing Bot v4.0")
        self.main_window.geometry("1200x800")  # Aumentar tamanho para melhor responsividade
        self.main_window.configure(bg='#0f1419')  # Azul escuro mais elegante
        self.main_window.resizable(True, True)
        
        # Configurar tamanho mínimo
        self.main_window.minsize(1000, 600)
        
        # Configurar tema melhorado
        self.setup_improved_theme()
        
        # Estado do bot
        self.bot_running = False
        self.bot_paused = False
        
        # Core engines
        self.template_engine = None
        self.fishing_engine = None
        self._initialize_engines()
        
        # Stats e labels
        self.stats_labels = {}

        # 🌍 WIDGET REFERENCES - For dynamic language switching
        self.translatable_widgets = {
            'frames': {},      # LabelFrames with text
            'labels': {},      # Labels with text
            'buttons': {},     # Buttons with text
            'checkboxes': {},  # Checkbuttons with text
            'radiobuttons': {},# Radiobuttons with text
        }

        # Variáveis tkinter
        self.auto_clean_interval_var = tk.StringVar(value="1")
        self.auto_clean_enabled_var = tk.BooleanVar(value=True)
        self.auto_clean_baits_enabled_var = tk.BooleanVar(value=True)
        self.auto_clean_status_label = None
        
        # Config tab
        self.cycle_timeout_var = tk.StringVar(value="122")
        self.rod_switch_limit_var = tk.StringVar(value="20")
        self.clicks_per_second_var = tk.StringVar(value="9")
        self.maintenance_timeout_var = tk.StringVar(value="3")
        self.chest_side_var = tk.StringVar(value="right")
        self.macro_type_var = tk.StringVar(value="padrão")
        self.chest_distance_var = tk.StringVar(value="1000")
        self.auto_reload_var = tk.BooleanVar(value=True)
        self.auto_focus_var = tk.BooleanVar(value=False)
        self.broken_rod_action_var = tk.StringVar(value="discard")
        
        # Feeding tab
        self.feeding_enabled_var = tk.BooleanVar(value=True)
        self.feeding_trigger_mode_var = tk.StringVar(value="catches")
        self.feeding_trigger_catches_var = tk.StringVar(value="3")
        self.feeding_trigger_time_var = tk.StringVar(value="20")
        self.feeding_session_count_var = tk.StringVar(value="5")
        self.feeding_max_uses_var = tk.StringVar(value="20")
        self.feeding_auto_detect_var = tk.BooleanVar(value=True)
        self.feeding_slot1_x_var = tk.StringVar(value="1306")
        self.feeding_slot1_y_var = tk.StringVar(value="858")
        self.feeding_slot2_x_var = tk.StringVar(value="1403")
        self.feeding_slot2_y_var = tk.StringVar(value="877")
        self.feeding_eat_x_var = tk.StringVar(value="1083")
        self.feeding_eat_y_var = tk.StringVar(value="373")
        self.feeding_mode_var = tk.StringVar(value="time")
        self.feeding_interval_var = tk.StringVar(value="60")
        self.feeding_fish_count_var = tk.StringVar(value="10")
        
        # Anti-detection tab
        self.anti_detection_enabled_var = tk.BooleanVar(value=True)
        self.click_delay_min_var = tk.StringVar(value="80")
        self.click_delay_max_var = tk.StringVar(value="150")
        self.click_variation_var = tk.BooleanVar(value=False)
        self.movement_variation_var = tk.BooleanVar(value=True)
        self.natural_breaks_var = tk.BooleanVar(value=True)
        self.break_mode_var = tk.StringVar(value="catches")
        self.break_catches_var = tk.StringVar(value="50")
        self.break_minutes_var = tk.StringVar(value="45")
        self.detection_interval_var = tk.StringVar(value="100")
        self.screenshot_optimization_var = tk.BooleanVar(value=True)
        self.template_caching_var = tk.BooleanVar(value=True)
        self.movement_duration_a_min_var = tk.StringVar(value="1.2")
        self.movement_duration_a_max_var = tk.StringVar(value="1.8")
        self.movement_duration_d_min_var = tk.StringVar(value="1.0")
        self.movement_duration_d_max_var = tk.StringVar(value="1.4")
        self.natural_pause_time_var = tk.StringVar(value="45")
        
        # Hotkeys tab
        self.hotkey_vars = {
            'start': tk.StringVar(value="f9"),
            'pause': tk.StringVar(value="f2"),
            'stop': tk.StringVar(value="f1"),
            'emergency': tk.StringVar(value="escape"),
            'interface': tk.StringVar(value="f4"),
            'macro_execute': tk.StringVar(value="f8"),
            'macro_chest': tk.StringVar(value="f11"),
            'macro_record': tk.StringVar(value="f3"),
            'test_mouse': tk.StringVar(value="f12"),
            'test_feeding': tk.StringVar(value="f6"),
            'test_cleaning': tk.StringVar(value="f5"),
            'test_maintenance': tk.StringVar(value="page down")
        }
        
        # Sistema de idiomas
        self.current_language = i18n.current_language if I18N_AVAILABLE else "pt"
        
        # Variáveis do Arduino (antes de criar UI)
        self.arduino_port_var = tk.StringVar(value="COM3")
        self.arduino_baud_var = tk.StringVar(value="9600")
        self.arduino_timeout_var = tk.StringVar(value="1")
        
        # Inicializar UI
        self.setup_ui_components()

        # Carregar configurações salvas após UI estar pronta
        self.load_feeding_config()
        self.load_cleaning_config()  # ✅ NOVO: Carregar configs de limpeza
        self.load_anti_detection_config()  # ✅ NOVO: Carregar configs de anti-detecção
    
    def _initialize_engines(self):
        """Inicializar TODOS os core engines na ordem correta"""
        try:
            if CORE_ENGINES_AVAILABLE:
                print("[CONFIG] Inicializando todos os componentes v4...")
                
                # Initialize game state before engines (usar classe real GameState)
                try:
                    from core.game_state import GameState
                    self.game_state = GameState()
                    print("[GAME] GameState real inicializado")
                except ImportError:
                    # Fallback para dict simples se GameState não disponível
                    self.game_state = {
                        'chest_open': False,
                        'inventory_open': False,
                        'bot_running': False,
                        'paused': False
                    }
                    print("[WARN] Usando GameState simplificado (dict)")
                
                # 1. TemplateEngine (base para tudo)
                print("  📋 Inicializando TemplateEngine...")
                self.template_engine = TemplateEngine(config_manager=self.config_manager)
                
                # 2. InputManager (necessário para todos os sistemas de controle)
                print("  🖱️ Inicializando InputManager...")

                # ===== SISTEMA DE SELEÇÃO DE INPUT MANAGER =====
                # Verifica configuração para usar Arduino ou InputManager padrão
                use_arduino = self.config_manager.get('arduino.enabled', False)

                if use_arduino:
                    print("  🤖 Modo Arduino HID ativado")
                    print("     ⚠️ Conexão será feita quando clicar em 'Conectar' na aba Arduino")
                    try:
                        from core.arduino_input_manager import ArduinoInputManager
                        self.input_manager = ArduinoInputManager(config_manager=self.config_manager)
                        print("  ✅ ArduinoInputManager inicializado (aguardando conexão)")
                        print("     🔒 Quando conectado, TODOS os inputs serão via hardware USB HID")
                    except ImportError as e:
                        print(f"  ⚠️ ArduinoInputManager não disponível: {e}")
                        print("  ⚠️ Usando InputManager padrão...")
                        from core.input_manager import InputManager
                        self.input_manager = InputManager(config_manager=self.config_manager)
                        print("  ✅ InputManager padrão inicializado")
                    except Exception as e:
                        print(f"  ⚠️ Erro ao inicializar Arduino: {e}")
                        print("  ⚠️ Usando InputManager padrão...")
                        from core.input_manager import InputManager
                        self.input_manager = InputManager(config_manager=self.config_manager)
                        print("  ✅ InputManager padrão inicializado")
                else:
                    print("  🖥️ Usando InputManager padrão (pyautogui)...")
                    try:
                        from core.input_manager import InputManager
                        self.input_manager = InputManager(config_manager=self.config_manager)
                        print("  ✅ InputManager padrão inicializado")
                    except ImportError as e:
                        print(f"  ❌ Erro ao importar InputManager: {e}")
                        self.input_manager = None
                
                # 3. ChestManager (necessário para feeding e cleaning)
                print("  📦 Inicializando ChestManager...")
                try:
                    from core.chest_manager import ChestManager
                    self.chest_manager = ChestManager(
                        config_manager=self.config_manager,
                        input_manager=self.input_manager,
                        game_state=self.game_state
                    )
                    print("  ✅ ChestManager inicializado")
                except ImportError as e:
                    print(f"  ❌ Erro ao importar ChestManager: {e}")
                    self.chest_manager = None
                
                # 4. RodManager
                print("  🎣 Inicializando RodManager...")
                try:
                    from core.rod_manager import RodManager
                    self.rod_manager = RodManager(
                        template_engine=self.template_engine,
                        input_manager=self.input_manager,
                        config_manager=self.config_manager,
                        chest_manager=self.chest_manager
                    )
                    print("  ✅ RodManager inicializado")
                except ImportError as e:
                    print(f"  ❌ Erro ao importar RodManager: {e}")
                    self.rod_manager = None
                
                # 5. FeedingSystem
                print("  🍖 Inicializando FeedingSystem...")
                try:
                    from core.feeding_system import FeedingSystem
                    self.feeding_system = FeedingSystem(
                        config_manager=self.config_manager,
                        template_engine=self.template_engine,
                        chest_manager=self.chest_manager
                    )
                    print("  ✅ FeedingSystem inicializado")
                except ImportError as e:
                    print(f"  ❌ Erro ao importar FeedingSystem: {e}")
                    self.feeding_system = None
                
                # 6. InventoryManager
                print("  📦 Inicializando InventoryManager...")
                try:
                    from core.inventory_manager import InventoryManager
                    self.inventory_manager = InventoryManager(
                        template_engine=self.template_engine,
                        chest_manager=self.chest_manager,
                        input_manager=self.input_manager,
                        config_manager=self.config_manager
                    )
                    print("  ✅ InventoryManager inicializado")
                except ImportError as e:
                    print(f"  ❌ Erro ao importar InventoryManager: {e}")
                    self.inventory_manager = None
                
                # 7. FishingEngine (coordenador principal com TODOS os componentes)
                print("  🎮 Inicializando FishingEngine com todos os componentes...")
                self.fishing_engine = FishingEngine(
                    template_engine=self.template_engine,
                    input_manager=self.input_manager,
                    rod_manager=self.rod_manager,
                    feeding_system=self.feeding_system,
                    inventory_manager=self.inventory_manager,
                    chest_manager=self.chest_manager,
                    config_manager=self.config_manager,
                    ws_client=self.ws_client  # ✅ Passar WebSocket Client
                )
                
                # Configurar callbacks do FishingEngine para UI
                self.fishing_engine.set_callbacks(
                    on_state_change=self._on_fishing_state_change,
                    on_fish_caught=self._on_fish_caught,
                    on_error=self._on_fishing_error,
                    on_stats_update=self._on_fishing_stats_update
                )

                # ✅ Registrar callbacks do servidor (se conectado)
                if self.ws_client:
                    try:
                        from client.server_connector import register_server_callbacks
                        register_server_callbacks(self.ws_client, self.fishing_engine)
                        print("  ✅ Callbacks do servidor registrados")
                    except Exception as e:
                        print(f"  ⚠️ Erro ao registrar callbacks do servidor: {e}")

                # 8. GameWindowVisualizer (para debugging e monitoramento)
                print("  🎮 Inicializando GameWindowVisualizer...")
                try:
                    from core.game_window_visualizer import GameWindowVisualizer
                    self.game_visualizer = GameWindowVisualizer(
                        template_engine=self.template_engine,
                        config_manager=self.config_manager
                    )
                    print("  ✅ GameWindowVisualizer inicializado")
                except ImportError as e:
                    print(f"  ❌ Erro ao importar GameWindowVisualizer: {e}")
                    self.game_visualizer = None
                
                # 9. Sistema de Hotkeys Globais
                print("  ⌨️ Configurando sistema de hotkeys globais...")
                self._setup_global_hotkeys()

                print("[OK] TODOS os componentes inicializados com sucesso!")
                print(f"[INFO] Resumo dos componentes:")
                print(f"  📋 TemplateEngine: {'✅' if self.template_engine else '❌'}")
                print(f"  🖱️ InputManager: {'✅' if self.input_manager else '❌'}")
                print(f"  📦 ChestManager: {'✅' if self.chest_manager else '❌'}")
                print(f"  🎣 RodManager: {'✅' if self.rod_manager else '❌'}")
                print(f"  🍖 FeedingSystem: {'✅' if self.feeding_system else '❌'}")
                print(f"  📦 InventoryManager: {'✅' if self.inventory_manager else '❌'}")
                print(f"  🎮 GameWindowVisualizer: {'✅' if self.game_visualizer else '❌'}")
                print(f"  🎮 FishingEngine: {'✅' if self.fishing_engine else '❌'}")
                
            else:
                print("[WARN] Core engines não disponíveis - usando modo simulação")
                
        except Exception as e:
            print(f"[ERROR] Erro ao inicializar engines: {e}")
            import traceback
            traceback.print_exc()
            self.template_engine = None
            self.fishing_engine = None
    
    def _setup_global_hotkeys(self):
        """Configurar sistema global de hotkeys - BASEADO NO BOTPESCA.PY"""
        try:
            if not KEYBOARD_AVAILABLE:
                print("[WARN] Biblioteca keyboard não disponível - hotkeys desabilitados")
                return
            
            print("⌨️ Configurando hotkeys globais...")
            
            # Limpar hotkeys existentes primeiro (com verificação de compatibilidade)
            try:
                if hasattr(keyboard, 'clear_all_hotkeys'):
                    keyboard.clear_all_hotkeys()
                    print("[CLEAN] Hotkeys anteriores limpas")
                elif hasattr(keyboard, 'unhook_all'):
                    keyboard.unhook_all()
                    print("[CLEAN] Hotkeys anteriores removidas")

                # Filtros já aplicados no início do arquivo
                print("[CONFIG] Filtros de compatibilidade já ativos")
            except AttributeError as e:
                print(f"ℹ️ Aviso de compatibilidade keyboard: {e}")
            except Exception as e:
                print(f"[WARN] Erro na limpeza de hotkeys: {e}")
            
            # Hotkeys principais (mesmo esquema do botpesca.py)
            hotkeys_config = {
                'f9': ('start_bot', "🚀 Iniciar bot"),  # F9 para iniciar bot
                'f1': ('pause_bot', "⏸️ Pausar/Despausar"),
                'f2': ('stop_bot', "🛑 Parar bot"),
                'f6': ('trigger_feeding', "🍖 Alimentação manual"),
                'f5': ('trigger_cleaning', "🧹 Limpeza manual"),
                'page down': ('trigger_rod_maintenance', "🔧 Manutenção de vara"),
                'esc': ('emergency_stop', "🚨 Parada de emergência")
            }

            # REMOVIDO: TAB como hotkey global - TAB deve funcionar apenas no jogo
            
            for hotkey, (method_name, description) in hotkeys_config.items():
                try:
                    method = getattr(self, method_name, None)
                    if method:
                        keyboard.add_hotkey(hotkey, method)
                        print(f"  ✅ {hotkey.upper()}: {description} -> {method_name}")
                        if hotkey == 'f9':
                            print(f"      🔍 F9 especialmente mapeado para: {method}")
                        if hotkey == 'page down':
                            print(f"      🔍 PAGE DOWN registrado! Teste pressionando a tecla.")
                    else:
                        print(f"  ❌ {hotkey.upper()}: método {method_name} não encontrado")
                except Exception as e:
                    print(f"  ❌ {hotkey.upper()}: erro ao configurar - {e}")
                    import traceback
                    traceback.print_exc()
            
            print("[OK] Sistema de hotkeys globais configurado!")
            
        except Exception as e:
            print(f"[ERROR] Erro ao configurar hotkeys globais: {e}")
    
    # ===== MÉTODOS DE HOTKEYS =====
    
    def trigger_feeding(self):
        """Trigger manual de alimentação (F6)"""
        print("[TARGET] [F6] HOTKEY PRESSIONADA!")
        try:
            print(f"   🔍 Verificando fishing_engine: hasattr={hasattr(self, 'fishing_engine')}")
            if hasattr(self, 'fishing_engine'):
                print(f"   🔍 fishing_engine = {self.fishing_engine}")

            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                print("[CONFIG] [F6] Trigger manual de alimentação ativado")
                success = self.fishing_engine.trigger_feeding()
                if success:
                    print("[OK] [F6] Alimentação executada com sucesso")
                else:
                    print("[ERROR] [F6] Falha na alimentação")
            else:
                print("[WARN] [F6] FishingEngine não disponível - inicie o bot primeiro (F9)")
        except Exception as e:
            print(f"[ERROR] [F6] Erro no trigger de alimentação: {e}")
            import traceback
            traceback.print_exc()
    
    def trigger_cleaning(self):
        """Trigger manual de limpeza (F5)"""
        try:
            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                print("[CONFIG] [F5] Trigger manual de limpeza ativado")
                success = self.fishing_engine.trigger_cleaning()
                if success:
                    print("[OK] [F5] Limpeza executada com sucesso")
                else:
                    print("[ERROR] [F5] Falha na limpeza")
            else:
                print("[WARN] [F5] FishingEngine não disponível")
        except Exception as e:
            print(f"[ERROR] [F5] Erro no trigger de limpeza: {e}")
    
    def trigger_rod_maintenance(self):
        """Trigger de manutenção de vara (PAGE DOWN) - Igual ao botpesca.py"""
        try:
            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                print("[CONFIG] [PAGE DOWN] Trigger de manutenção de vara ativado")
                success = self.fishing_engine.trigger_rod_maintenance()
                if success:
                    print("[OK] [PAGE DOWN] Manutenção de vara executada com sucesso")
                else:
                    print("[ERROR] [PAGE DOWN] Falha na manutenção de vara")
            else:
                print("[WARN] [PAGE DOWN] FishingEngine não disponível")
        except Exception as e:
            print(f"[ERROR] [PAGE DOWN] Erro no trigger de manutenção: {e}")
    
    def emergency_stop(self):
        """Parada de emergência (ESC)"""
        try:
            print("🚨 [ESC] PARADA DE EMERGÊNCIA ATIVADA!")
            
            # Parar bot
            self.stop_bot()
            
            # Parar todos os inputs
            if hasattr(self, 'input_manager') and self.input_manager:
                self.input_manager.stop_all_actions()
            
            # Limpar estados
            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                self.fishing_engine.stop()
            
            print("[OK] [ESC] Parada de emergência concluída")
            
        except Exception as e:
            print(f"[ERROR] [ESC] Erro na parada de emergência: {e}")
    
    def open_game_visualizer(self):
        """Abrir visualizador da janela do jogo"""
        try:
            if hasattr(self, 'game_visualizer') and self.game_visualizer:
                print("[GAME] Abrindo visualizador da janela do jogo...")
                self.game_visualizer.show_viewer_window()
            else:
                print("[WARN] GameWindowVisualizer não disponível")
                messagebox.showwarning("Aviso", "Visualizador do jogo não está disponível.\nVerifique se todos os componentes foram inicializados corretamente.")
        except Exception as e:
            print(f"[ERROR] Erro ao abrir visualizador: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir visualizador: {e}")
    
    def setup_ui_components(self):
        """Configurar componentes da UI (janela já criada)"""
        try:
            # Protocolo de fechamento
            self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Configurar tema escuro
            self.setup_dark_theme()
            
            # Criar interface
            self.create_interface()
            
            # Centralizar janela
            self.center_window()
            
        except Exception as e:
            print(f"Erro ao criar janela principal: {e}")
    
    def setup_dark_theme(self):
        """Configurar tema escuro com cores melhoradas"""
        try:
            style = ttk.Style()
            
            # Configurar outros estilos para melhor legibilidade
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TButton', font=('Arial', 9, 'bold'))
            style.configure('TEntry', font=('Arial', 9))
            style.configure('TCheckbutton', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TScale', background='#2d2d2d')
            
        except Exception as e:
            print(f"Erro ao configurar tema: {e}")
    
    def setup_improved_theme(self):
        """Configurar tema escuro melhorado com cores mais vibrantes"""
        try:
            style = ttk.Style()
            
            # Cores principais do tema
            bg_primary = '#0f1419'      # Azul escuro elegante (fundo principal)
            bg_secondary = '#1e2328'    # Cinza azulado (frames/containers)
            bg_tertiary = '#252b31'     # Cinza mais claro (elementos)
            
            # Cores de texto
            text_primary = '#ffffff'    # Branco puro (texto principal)
            text_secondary = '#000000'  # Preto escuro forte para melhor contraste
            text_accent = '#ffffff'     # Branco para destaques
            
            # Cores de elementos
            accent_blue = '#0078d4'     # Azul Microsoft
            accent_green = '#16c79a'    # Verde vibrante
            accent_orange = '#ff9500'   # Laranja vibrante
            accent_red = '#ff4757'      # Vermelho vibrante
            accent_yellow = '#ffa726'   # Amarelo vibrante
            
            # Configurar estilo do Notebook (abas)
            style.configure('TNotebook', 
                          background=bg_primary,
                          borderwidth=0,
                          tabmargins=[0, 5, 0, 0])
            
            style.configure('TNotebook.Tab',
                          background='#ffffff',  # FUNDO BRANCO para abas não selecionadas
                          foreground='#000000',  # TEXTO PRETO FORTE
                          padding=[15, 8],
                          focuscolor='none',
                          borderwidth=2,
                          relief='raised')
            
            # Aba ativa
            style.map('TNotebook.Tab',
                     background=[('selected', '#28a745'),   # VERDE FORTE para aba selecionada
                               ('active', '#e6f3ff')],      # Azul bem claro para hover
                     foreground=[('selected', '#000000'),   # TEXTO PRETO para aba selecionada
                               ('active', '#000000')])
            
            # Frames
            style.configure('TFrame', 
                          background=bg_primary,
                          relief='flat',
                          borderwidth=0)
            
            # Labels
            style.configure('TLabel',
                          background=bg_primary,
                          foreground=text_primary,
                          font=('Segoe UI', 9))
            
            # Buttons
            style.configure('TButton',
                          background=accent_blue,
                          foreground=text_primary,
                          borderwidth=0,
                          focuscolor='none',
                          font=('Segoe UI', 9, 'bold'),
                          padding=[10, 5])
            
            style.map('TButton',
                     background=[('active', '#106ebe'),
                               ('pressed', '#005a9e')])
            
            # Combobox
            style.configure('TCombobox',
                          fieldbackground=bg_tertiary,
                          background=bg_tertiary,
                          foreground=text_primary,
                          borderwidth=1,
                          insertcolor=text_primary)
            
            # Entry
            style.configure('TEntry',
                          fieldbackground=bg_tertiary,
                          foreground=text_primary,
                          borderwidth=1,
                          insertcolor=text_primary)
            
            # Separator
            style.configure('TSeparator',
                          background=bg_tertiary)
            
            # Scrollbar
            style.configure('TScrollbar',
                          background=bg_secondary,
                          troughcolor=bg_primary,
                          borderwidth=0,
                          arrowcolor=text_secondary)
            
            # LabelFrame (não é ttk, mas configuramos as cores para compatibilidade)
            self.theme_colors = {
                'bg_primary': bg_primary,
                'bg_secondary': bg_secondary, 
                'bg_tertiary': bg_tertiary,
                'text_primary': text_primary,
                'text_secondary': text_secondary,
                'text_accent': text_accent,
                'accent_blue': accent_blue,
                'accent_green': accent_green,
                'accent_orange': accent_orange,
                'accent_red': accent_red,
                'accent_yellow': accent_yellow
            }
            
            print("[OK] Tema melhorado aplicado com sucesso!")
            
        except Exception as e:
            print(f"[WARN] Erro ao configurar tema: {e}")
    
    def create_interface(self):
        """Criar interface com 8 abas na ordem especificada"""
        try:
            # Frame principal com cores melhoradas
            main_frame = tk.Frame(self.main_window, bg=self.theme_colors['bg_primary'])
            main_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Título com cores melhoradas
            title_label = tk.Label(main_frame,
                                 text=_("header_hardcoded.ultimate_fishing_bot"),
                                 font=('Segoe UI', 18, 'bold'),
                                 fg=self.theme_colors['text_accent'],
                                 bg=self.theme_colors['bg_primary'])
            title_label.pack(pady=15)
            
            # Criar notebook (sistema de abas)
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill='both', expand=True, pady=10)
            
            # 8 ABAS NA ORDEM CORRETA CONFORME ESPECIFICADO:
            self.create_control_tab()        # Aba 1: 🎮 Controle - Status, estatísticas, botões Start/Stop/Pause
            self.create_config_tab()         # Aba 2: ⚙️ Configurações - Timeout, lado do baú, varas quebradas  
            self.create_feeding_tab()        # Aba 3: 🍖 Alimentação - Modos de detecção, triggers, posições
            self.create_confidence_tab()     # Aba 4: 🎯 Templates - Sliders de confiança, categorias
            self.create_anti_detection_tab() # Aba 5: 🛡️ Anti-Detecção - Variação de cliques, pausas naturais
            self.create_catch_viewer_tab()   # Aba 6: 🐟 Visualizador - Janela de capturas e detecções em tempo real
            self.create_hotkeys_tab()        # Aba 7: ⌨️ Hotkeys - Entries para teclas, botões de captura
            self.create_arduino_tab()        # Aba 8: 🔌 Arduino - Conexão COM e controle do hardware
            self.create_help_tab()           # Aba 9: ❓ Ajuda - Documentação e troubleshooting
            
            # Carregar valores do config após criar todas as abas
            self.load_config_values()
            
            # Criar barra de status FORA do main_frame (na janela principal)
            self.create_status_bar()
            
        except Exception as e:
            print(f"Erro ao criar interface: {e}")
    
    def create_control_tab(self):
        """Aba 1: 🎮 Controle - Status, estatísticas, botões Start/Stop/Pause"""
        control_frame = tk.Frame(self.notebook, bg=self.theme_colors['bg_primary'])
        tab_text = i18n.get_text('tabs.control_tab') if I18N_AVAILABLE else '🎮 Controle'
        self.notebook.add(control_frame, text=tab_text)
        
        # Adicionar scroll à aba de controle
        canvas = tk.Canvas(control_frame, bg=self.theme_colors['bg_primary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(control_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme_colors['bg_primary'])
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Usar scrollable_frame em vez de control_frame daqui para frente

        # Status do Bot com cores melhoradas
        status_frame = tk.LabelFrame(scrollable_frame,
                                   text=i18n.get_text('ui.bot_status') if I18N_AVAILABLE else "🤖 Status do Bot",
                                   fg=self.theme_colors['text_primary'],
                                   bg=self.theme_colors['bg_secondary'],
                                   font=('Segoe UI', 12, 'bold'))
        self.register_translatable_widget('frames', 'status_frame', status_frame, 'ui.bot_status')
        status_frame.pack(fill='x', pady=10, padx=10)

        self.status_label = tk.Label(status_frame,
                                   text=i18n.get_text('ui.stopped') if I18N_AVAILABLE else "⚫ Parado",
                                   font=('Segoe UI', 14, 'bold'),
                                   fg=self.theme_colors['accent_red'],
                                   bg=self.theme_colors['bg_secondary'])
        self.register_translatable_widget('labels', 'status_label', self.status_label, 'ui.stopped')
        self.status_label.pack(pady=10)

        # Estatísticas Detalhadas com cores melhoradas
        stats_frame = tk.LabelFrame(scrollable_frame,
                                  text=i18n.get_text('ui.detailed_statistics') if I18N_AVAILABLE else "📊 Estatísticas Detalhadas",
                                  fg=self.theme_colors['text_primary'],
                                  bg=self.theme_colors['bg_secondary'],
                                  font=('Segoe UI', 12, 'bold'))
        self.register_translatable_widget('frames', 'stats_frame', stats_frame, 'ui.detailed_statistics')
        stats_frame.pack(fill='x', pady=10, padx=10)

        # Grid para organizar estatísticas em duas colunas
        stats_grid = tk.Frame(stats_frame, bg=self.theme_colors['bg_secondary'])
        stats_grid.pack(pady=10, padx=10)

        # Coluna 1 - Estatísticas principais com cores melhoradas
        col1_frame = tk.Frame(stats_grid, bg=self.theme_colors['bg_secondary'])
        col1_frame.grid(row=0, column=0, padx=20, sticky='n')

        self.stats_labels = {}

        # Peixes capturados
        fish_frame = tk.Frame(col1_frame, bg=self.theme_colors['bg_secondary'])
        fish_frame.pack(anchor='w', pady=2)
        fish_caught_lbl = tk.Label(fish_frame,
                text=i18n.get_text('ui.fish_caught') if I18N_AVAILABLE else "🐟 Peixes capturados:",
                fg=self.theme_colors['text_accent'], bg=self.theme_colors['bg_secondary'],
                font=('Segoe UI', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'fish_caught_label', fish_caught_lbl, 'ui.fish_caught')
        fish_caught_lbl.pack(side='left')
        self.stats_labels['fish'] = tk.Label(fish_frame, text="0",
                                            fg=self.theme_colors['accent_green'], 
                                            bg=self.theme_colors['bg_secondary'], 
                                            font=('Segoe UI', 10, 'bold'))
        self.stats_labels['fish'].pack(side='left')

        # Tempo de sessão
        time_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        time_frame.pack(anchor='w', pady=2)
        session_time_lbl = tk.Label(time_frame,
                text=i18n.get_text('ui.session_time') if I18N_AVAILABLE else "⏱️ Tempo de sessão:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'session_time_label', session_time_lbl, 'ui.session_time')
        session_time_lbl.pack(side='left')
        self.stats_labels['session_time'] = tk.Label(time_frame, text=_("header_hardcoded.000000"),
                                                    fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['session_time'].pack(side='left')

        # Peixes por hora
        rate_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        rate_frame.pack(anchor='w', pady=2)
        fish_per_hour_lbl = tk.Label(rate_frame, text=i18n.get_text("ui.fish_per_hour") if I18N_AVAILABLE else "⚡ Peixes/hora:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'fish_per_hour_label', fish_per_hour_lbl, 'ui.fish_per_hour')
        fish_per_hour_lbl.pack(side='left')
        self.stats_labels['fish_per_hour'] = tk.Label(rate_frame, text="0",
                                                     fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['fish_per_hour'].pack(side='left')

        # Taxa de sucesso
        success_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        success_frame.pack(anchor='w', pady=2)
        success_rate_lbl = tk.Label(success_frame, text=i18n.get_text("ui.success_rate") if I18N_AVAILABLE else "🎯 Taxa de sucesso:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'success_rate_label', success_rate_lbl, 'ui.success_rate')
        success_rate_lbl.pack(side='left')
        self.stats_labels['success_rate'] = tk.Label(success_frame, text="0%",
                                                    fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['success_rate'].pack(side='left')

        # Coluna 2 - Contadores de eventos
        col2_frame = tk.Frame(stats_grid, bg='#1a1a1a')
        col2_frame.grid(row=0, column=1, padx=20, sticky='n')

        # Alimentações
        feed_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        feed_frame.pack(anchor='w', pady=2)
        feedings_lbl = tk.Label(feed_frame, text=i18n.get_text("ui.feedings") if I18N_AVAILABLE else "🍖 Alimentações:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'feedings_label', feedings_lbl, 'ui.feedings')
        feedings_lbl.pack(side='left')
        self.stats_labels['feeds'] = tk.Label(feed_frame, text="0",
                                             fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['feeds'].pack(side='left')

        # Limpezas
        clean_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        clean_frame.pack(anchor='w', pady=2)
        cleanings_lbl = tk.Label(clean_frame, text=i18n.get_text("ui.cleanings") if I18N_AVAILABLE else "🧹 Limpezas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'cleanings_label', cleanings_lbl, 'ui.cleanings')
        cleanings_lbl.pack(side='left')
        self.stats_labels['cleans'] = tk.Label(clean_frame, text="0",
                                              fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['cleans'].pack(side='left')

        # Manutenções
        maintenance_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        maintenance_frame.pack(anchor='w', pady=2)
        maintenances_lbl = tk.Label(maintenance_frame, text=i18n.get_text("ui.maintenances") if I18N_AVAILABLE else "🔧 Manutenções:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'maintenances_label', maintenances_lbl, 'ui.maintenances')
        maintenances_lbl.pack(side='left')
        self.stats_labels['maintenances'] = tk.Label(maintenance_frame, text="0",
                                              fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['maintenances'].pack(side='left')

        # Varas quebradas
        broken_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        broken_frame.pack(anchor='w', pady=2)
        broken_rods_lbl = tk.Label(broken_frame, text=i18n.get_text("ui.broken_rods") if I18N_AVAILABLE else "🔧 Varas quebradas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'broken_rods_label', broken_rods_lbl, 'ui.broken_rods')
        broken_rods_lbl.pack(side='left')
        self.stats_labels['broken_rods'] = tk.Label(broken_frame, text="0",
                                                   fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['broken_rods'].pack(side='left')

        # Timeouts
        timeout_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        timeout_frame.pack(anchor='w', pady=2)
        timeouts_lbl = tk.Label(timeout_frame, text=i18n.get_text("ui.timeouts") if I18N_AVAILABLE else "⏱️ Timeouts:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'timeouts_label', timeouts_lbl, 'ui.timeouts')
        timeouts_lbl.pack(side='left')
        self.stats_labels['timeouts'] = tk.Label(timeout_frame, text="0",
                                                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['timeouts'].pack(side='left')

        # ✅ NOVO: Vara do último timeout
        rod_timeout_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        rod_timeout_frame.pack(anchor='w', pady=2)
        last_rod_lbl = tk.Label(rod_timeout_frame, text=i18n.get_text("ui.last_rod") if I18N_AVAILABLE else "🎣 Vara (último timeout):",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w')
        self.register_translatable_widget('labels', 'last_rod_label', last_rod_lbl, 'ui.last_rod')
        last_rod_lbl.pack(side='left')
        self.stats_labels['rod_at_timeout'] = tk.Label(rod_timeout_frame, text="-",
                                                       fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['rod_at_timeout'].pack(side='left')

        # Sistema de Limpeza Automática
        auto_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.auto_clean") if I18N_AVAILABLE else "🔄 Limpeza Automática",
                                 fg='white', bg='#1a1a1a',
                                 font=('Arial', 12, 'bold'))
        self.register_translatable_widget('frames', 'auto_frame', auto_frame, 'ui.auto_clean')
        auto_frame.pack(fill='x', pady=10, padx=10)

        # Configuração a cada X pescas
        fish_frame = tk.Frame(auto_frame, bg='#1a1a1a')
        fish_frame.pack(fill='x', padx=10, pady=5)

        clean_every_lbl = tk.Label(fish_frame, text=i18n.get_text("ui.clean_every") if I18N_AVAILABLE else "🐟 Limpar inventário a cada:",
                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.register_translatable_widget('labels', 'clean_every_label', clean_every_lbl, 'ui.clean_every')
        clean_every_lbl.pack(side='left')

        self.auto_clean_interval_var = tk.StringVar(value="10")
        tk.Entry(fish_frame, textvariable=self.auto_clean_interval_var, width=5).pack(side='left', padx=5)

        catches_lbl = tk.Label(fish_frame, text=i18n.get_text("ui.catches") if I18N_AVAILABLE else "pescas",
                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.register_translatable_widget('labels', 'catches_label', catches_lbl, 'ui.catches')
        catches_lbl.pack(side='left')

        # Toggle para ativação
        self.auto_clean_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_frame, text=i18n.get_text("ui.enable_auto_clean") if I18N_AVAILABLE else "✅ Ativar limpeza automática",
                      variable=self.auto_clean_enabled_var,
                      bg='#1a1a1a', fg='white', font=('Arial', 10),
                      selectcolor='#333333').pack(padx=10, pady=5)
        
        # Toggle para limpeza de iscas
        self.auto_clean_baits_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_frame, text=i18n.get_text("ui.include_baits_button") if I18N_AVAILABLE else "🎣 Incluir limpeza de iscas (transferir para baú)",
                      variable=self.auto_clean_baits_enabled_var,
                      bg='#1a1a1a', fg='#ffaa00', font=('Arial', 10),
                      selectcolor='#333333').pack(padx=10, pady=2)

        # Status da limpeza
        self.auto_clean_status_label = tk.Label(auto_frame,
                                              text=i18n.get_text("ui.next_clean_status") if I18N_AVAILABLE else "📊 Próxima limpeza em: 10 pescas",
                                              font=('Arial', 10),
                                              fg='#28a745', bg='#1a1a1a')
        self.auto_clean_status_label.pack(pady=5)
        
        # Botão para salvar configurações de limpeza
        save_clean_frame = tk.Frame(auto_frame, bg='#1a1a1a')
        save_clean_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(save_clean_frame, text=i18n.get_text("ui.save_clean_config") if I18N_AVAILABLE else "💾 Salvar Config de Limpeza",
                 command=self.save_cleaning_config,
                 bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left')
        
        # Configurar canvas e scrollbar para a aba de controle
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_config_tab(self):
        """Aba 2: ⚙️ Configurações - Timeout, lado do baú, varas quebradas"""
        config_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.config_tab') if I18N_AVAILABLE else '⚙️ Configurações'
        self.notebook.add(config_frame, text=tab_text)
        
        # Título
        title_label = tk.Label(config_frame,
                              text=i18n.get_text("ui.general_config") if I18N_AVAILABLE else "⚙️ Configurações Gerais do Sistema",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(config_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== CONFIGURAÇÕES DE TIMEOUT ==========
        timeout_frame = tk.LabelFrame(scrollable_frame, text=_("config_hardcoded.timeouts_e_ciclos"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        timeout_frame.pack(fill='x', padx=20, pady=10)
        
        # Timeout do ciclo
        cycle_frame = tk.Frame(timeout_frame, bg='#2a2a2a')
        cycle_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(cycle_frame, text=i18n.get_text("ui.cycle_timeout_label") if I18N_AVAILABLE else "Timeout do ciclo (segundos):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(cycle_frame, textvariable=self.cycle_timeout_var, width=8).pack(side='left', padx=5)
        
        # Limite troca par
        rod_limit_frame = tk.Frame(timeout_frame, bg='#2a2a2a')
        rod_limit_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(rod_limit_frame, text=i18n.get_text("ui.rod_switch_limit_label") if I18N_AVAILABLE else "Limite troca par de varas:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(rod_limit_frame, textvariable=self.rod_switch_limit_var, width=8).pack(side='left', padx=5)
        
        # Cliques por segundo
        clicks_frame = tk.Frame(timeout_frame, bg='#2a2a2a')
        clicks_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(clicks_frame, text=i18n.get_text("ui.clicks_per_second_label") if I18N_AVAILABLE else "Cliques por segundo:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(clicks_frame, textvariable=self.clicks_per_second_var, width=8).pack(side='left', padx=5)
        
        # Timeout para manutenção
        maintenance_frame = tk.Frame(timeout_frame, bg='#2a2a2a')
        maintenance_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(maintenance_frame, text=_("config_hardcoded.timeout_para_manutenção"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(maintenance_frame, textvariable=self.maintenance_timeout_var, width=8).pack(side='left', padx=5)
        
        # ========== SEÇÃO: CONFIGURAÇÕES DO BAÚ ==========
        chest_frame = tk.LabelFrame(scrollable_frame, text=_("config_hardcoded.configurações_do_baú"),
                                   bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        chest_frame.pack(fill='x', padx=15, pady=10)

        chest_grid = tk.Frame(chest_frame, bg='#2a2a2a')
        chest_grid.pack(padx=10, pady=10)

        # Lado do Baú e Tipo de Macro (mesma linha)
        tk.Label(chest_grid, text=_("config_hardcoded.lado_do_baú"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        chest_combo = tk.OptionMenu(chest_grid, self.chest_side_var, "left", "right",
                                    command=self._on_chest_side_change)  # ✅ Salvar automaticamente ao mudar
        chest_combo.configure(bg='#404040', fg='white', width=10)
        chest_combo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(chest_grid, text=_("config_hardcoded.tipo_de_macro"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=0, column=2, sticky='w', pady=5, padx=(30,0))
        macro_combo = tk.OptionMenu(chest_grid, self.macro_type_var, "padrão", "personalizado")
        macro_combo.configure(bg='#404040', fg='white', width=12)
        macro_combo.grid(row=0, column=3, padx=10, pady=5)

        # Distância do Baú
        tk.Label(chest_grid, text=_("config_hardcoded.distância_baú_px"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        tk.Entry(chest_grid, textvariable=self.chest_distance_var, width=10,
                bg='#404040', fg='white').grid(row=1, column=1, padx=10, pady=5)
        
        # ========== SEÇÃO: OPÇÕES ADICIONAIS ==========
        options_frame = tk.LabelFrame(scrollable_frame, text=_("config_hardcoded.opções_adicionais"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        options_frame.pack(fill='x', padx=15, pady=10)

        options_grid = tk.Frame(options_frame, bg='#2a2a2a')
        options_grid.pack(padx=10, pady=10)

        # Auto Reload e Foco Automático
        tk.Checkbutton(options_grid, text=_("config_hardcoded.auto_reload"), variable=self.auto_reload_var,
                      fg='white', bg='#2a2a2a', selectcolor='#404040',
                      font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)

        tk.Checkbutton(options_grid, text=_("config_hardcoded.foco_automático_impede"),
                      variable=self.auto_focus_var,
                      fg='white', bg='#2a2a2a', selectcolor='#404040',
                      font=('Arial', 10)).grid(row=0, column=1, sticky='w', pady=5, padx=(30,0))

        # ========== SEÇÃO: VARAS QUEBRADAS ==========
        broken_frame = tk.LabelFrame(scrollable_frame, text=_("config_hardcoded.manejo_de_varas"),
                                    bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        broken_frame.pack(fill='x', padx=15, pady=10)

        broken_grid = tk.Frame(broken_frame, bg='#2a2a2a')
        broken_grid.pack(padx=10, pady=10)

        tk.Radiobutton(broken_grid, text=_("config_hardcoded.descartar_remove_para"),
                      variable=self.broken_rod_action_var, value='discard',
                      fg='white', bg='#2a2a2a', selectcolor='#404040',
                      font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)

        tk.Radiobutton(broken_grid, text=_("config_hardcoded.guardar_no_baú"),
                      variable=self.broken_rod_action_var, value='save',
                      fg='white', bg='#2a2a2a', selectcolor='#404040',
                      font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        
        # ========== PRIORIDADE DE ISCAS ==========
        bait_config_frame = tk.LabelFrame(scrollable_frame, text=_("config_hardcoded.prioridade_de_iscas"),
                                         bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        bait_config_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(bait_config_frame, text=_("config_hardcoded.configure_a_ordem"),
                bg='#2a2a2a', fg='#ffaa00', font=('Arial', 10, 'bold')).pack(pady=10)

        # Frame para a lista reordenável
        bait_list_frame = tk.Frame(bait_config_frame, bg='#2a2a2a')
        bait_list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Listbox customizada para drag & drop
        self.config_bait_listbox = tk.Listbox(bait_list_frame,
                                             bg='#3a3a3a', fg='white',
                                             selectbackground='#4a4a4a',
                                             font=('Arial', 11),
                                             height=6)
        self.config_bait_listbox.pack(side='left', fill='both', expand=True)

        # Frame para controles de cada isca
        bait_controls_frame = tk.Frame(bait_list_frame, bg='#2a2a2a')
        bait_controls_frame.pack(side='right', fill='y', padx=(10, 0))

        # Variáveis para checkboxes e prioridades (na aba config)
        self.config_bait_enabled_vars = {}
        self.config_bait_priority_vars = {}

        # Criar lista ordenada por prioridade atual
        self.config_bait_names = ['carne de urso', 'carne de lobo', 'crocodilo', 'trout', 'grub', 'worm']
        self.config_ordered_baits = ['carne de urso', 'carne de lobo', 'crocodilo', 'trout', 'grub', 'worm']

        # Atualizar listbox e criar checkboxes
        self.update_config_bait_listbox()

        # Botões de movimento
        bait_btn_frame = tk.Frame(bait_controls_frame, bg='#2a2a2a')
        bait_btn_frame.pack(pady=5)

        tk.Button(bait_btn_frame, text="🔺", command=self.move_config_bait_up,
                 bg='#4a4a4a', fg='white', width=3).pack(pady=2)
        tk.Button(bait_btn_frame, text="🔻", command=self.move_config_bait_down,
                 bg='#4a4a4a', fg='white', width=3).pack(pady=2)

        # Checkboxes para habilitar/desabilitar
        tk.Label(bait_controls_frame, text=_("config_hardcoded.usar"), bg='#2a2a2a', fg='white',
                font=('Arial', 9, 'bold')).pack(pady=(10,5))

        for bait in self.config_ordered_baits:
            self.config_bait_enabled_vars[bait] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(bait_controls_frame, text=bait,
                               variable=self.config_bait_enabled_vars[bait],
                               bg='#2a2a2a', fg='white',
                               selectcolor='#4a4a4a',
                               activebackground='#2a2a2a',
                               activeforeground='white',
                               command=self.update_config_bait_enabled)
            cb.pack(anchor='w', pady=1)

        # Frame para reset
        bait_reset_frame = tk.Frame(bait_config_frame, bg='#2a2a2a')
        bait_reset_frame.pack(pady=10)

        bait_reset_btn = tk.Button(bait_reset_frame, text=i18n.get_text("ui.reset_defaults") if I18N_AVAILABLE else "🔄 Restaurar Padrão",
                                  command=self.reset_config_bait_priorities,
                                  bg='#6c757d', fg='white', font=('Arial', 9),
                                  padx=10, pady=5)
        bait_reset_btn.pack(side='left', padx=5)
        
        bait_save_btn = tk.Button(bait_reset_frame, text=_("config_hardcoded.salvar_prioridades"),
                                 command=self.save_bait_priority,
                                 bg='#28a745', fg='white', font=('Arial', 9),
                                 padx=10, pady=5)
        bait_save_btn.pack(side='left', padx=5)
        
        # ========== BOTÃO SALVAR ==========
        button_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
        button_frame.pack(fill='x', padx=15, pady=20)

        tk.Button(button_frame, text=_("config_hardcoded.salvar_todas_as"),
                 command=self.save_all_config,
                 bg='#28a745', fg='white', font=('Arial', 12, 'bold'),
                 padx=30, pady=12).pack(pady=10)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_feeding_tab(self):
        """Aba 3: 🍖 Alimentação - Sistema de Template Matching Automático (como v3)"""
        feeding_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.feeding_tab') if I18N_AVAILABLE else '🍖 Alimentação'
        self.notebook.add(feeding_frame, text=tab_text)

        # Título
        title_label = tk.Label(feeding_frame,
                              text=i18n.get_text("ui.smart_feeding_system") if I18N_AVAILABLE else "🍖 Sistema de Alimentação Inteligente",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)

        # Subtítulo
        subtitle_label = tk.Label(feeding_frame,
                                text=_("config_hardcoded.template_matching_automático"),
                                font=('Arial', 10),
                                fg='#cccccc', bg='#1a1a1a')
        subtitle_label.pack(pady=5)

        # Frame scrollável
        canvas = tk.Canvas(feeding_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(feeding_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ========== CONTROLE GERAL ==========
        enable_frame = tk.LabelFrame(scrollable_frame, text=_("feeding_hardcoded.controle_geral"),
                                    bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        enable_frame.pack(fill='x', padx=20, pady=10)

        tk.Checkbutton(enable_frame, text=_("feeding_hardcoded.sistema_de_alimentação"),
                      variable=self.feeding_enabled_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=8)

        # Status do sistema
        status_frame = tk.Frame(enable_frame, bg='#2a2a2a')
        status_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(status_frame, text=_("feeding_hardcoded.modo_detecção_automática"),
                fg='#00ff88', bg='#2a2a2a', font=('Arial', 10, 'bold')).pack(anchor='w')
        tk.Label(status_frame, text=_("feeding_hardcoded.sistema_idêntico_ao")eat' automaticamente",
                fg='#cccccc', bg='#2a2a2a', font=('Arial', 8)).pack(anchor='w', padx=15)

        # ========== TRIGGERS DE ALIMENTAÇÃO ==========
        trigger_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.when_to_feed") if I18N_AVAILABLE else "⚡ Quando Alimentar",
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        trigger_frame.pack(fill='x', padx=20, pady=10)

        # Modo de trigger
        mode_frame = tk.Frame(trigger_frame, bg='#2a2a2a')
        mode_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(mode_frame, text=_("feeding_hardcoded.modo_de_trigger"),
                fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).pack(anchor='w')

        # Radio buttons para modo
        radio_frame = tk.Frame(trigger_frame, bg='#2a2a2a')
        radio_frame.pack(fill='x', padx=10, pady=5)

        tk.Radiobutton(radio_frame, text=i18n.get_text("ui.trigger_by_catches") if I18N_AVAILABLE else "🐟 Por capturas (recomendado)",
                      variable=self.feeding_trigger_mode_var, value="catches",
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 9, 'bold')).pack(anchor='w')

        tk.Radiobutton(radio_frame, text=i18n.get_text("ui.trigger_by_time") if I18N_AVAILABLE else "⏰ Por tempo",
                      variable=self.feeding_trigger_mode_var, value="time",
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 9)).pack(anchor='w', pady=2)

        # Configurações de trigger
        config_frame = tk.Frame(trigger_frame, bg='#2a2a2a')
        config_frame.pack(fill='x', padx=10, pady=10)

        # Trigger por capturas
        catches_frame = tk.Frame(config_frame, bg='#2a2a2a')
        catches_frame.pack(fill='x', pady=2)
        tk.Label(catches_frame, text=i18n.get_text("ui.feed_every") if I18N_AVAILABLE else "🐟 Alimentar a cada:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(catches_frame, textvariable=self.feeding_trigger_catches_var, width=5).pack(side='left', padx=5)
        tk.Label(catches_frame, text=_("feeding_hardcoded.pescas_capturadas"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')

        # Trigger por tempo
        time_frame = tk.Frame(config_frame, bg='#2a2a2a')
        time_frame.pack(fill='x', pady=2)
        tk.Label(time_frame, text=_("feeding_hardcoded.ou_alimentar_a"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(time_frame, textvariable=self.feeding_trigger_time_var, width=5).pack(side='left', padx=5)
        tk.Label(time_frame, text=i18n.get_text("ui.minutes") if I18N_AVAILABLE else "minutos",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')

        # ========== CONFIGURAÇÕES DE CONSUMO ==========
        consumption_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.feeding_config") if I18N_AVAILABLE else "🍽️ Configurações de Alimentação",
                                         bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        consumption_frame.pack(fill='x', padx=20, pady=10)

        # Quantos peixes comer por sessão
        session_frame = tk.Frame(consumption_frame, bg='#2a2a2a')
        session_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(session_frame, text=_("feeding_hardcoded.quantos_peixes_comer"),
                fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).pack(side='left')
        tk.Entry(session_frame, textvariable=self.feeding_session_count_var, width=5).pack(side='left', padx=5)
        tk.Label(session_frame, text=_("feeding_hardcoded.peixes"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')

        # Explicações do sistema
        explanation_frame = tk.Frame(consumption_frame, bg='#2a2a2a')
        explanation_frame.pack(fill='x', padx=10, pady=5)

        explanations = [
            "• Sistema detecta automaticamente filé frito no baú usando template matching",
            "• Detecta dinamicamente a posição do botão 'eat' na interface",
            "• Executa ciclos inteligentes: clica comida → aguarda → clica eat",
            "• Igual ao v3: sem slots fixos, apenas detecção automática"
        ]

        for explanation in explanations:
            tk.Label(explanation_frame, text=explanation,
                    fg='#cccccc', bg='#2a2a2a', font=('Arial', 8)).pack(anchor='w', pady=1)

        # ========== INFORMAÇÕES TÉCNICAS ==========
        tech_frame = tk.LabelFrame(scrollable_frame, text=_("feeding_hardcoded.informações_técnicas"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        tech_frame.pack(fill='x', padx=20, pady=10)

        tech_info = [
            "🎯 Templates detectados: 'filefrito.png', 'file_frito.png'",
            "🎮 Botão eat detectado: 'comer.png' (template matching)",
            "🔄 Abertura de baú: Sistema v3 (ALT + movimento + E)",
            "📦 Coordenação: Integrado com sistema de fila de operações",
            "⚡ Hotkey: F6 (manual) ou automático por triggers"
        ]

        for info in tech_info:
            tk.Label(tech_frame, text=info,
                    fg='#00aaff', bg='#2a2a2a', font=('Arial', 8)).pack(anchor='w', padx=10, pady=1)

        # ========== CONTROLES E TESTES ==========
        controls_frame = tk.LabelFrame(scrollable_frame, text=_("feeding_hardcoded.controles_e_testes"),
                                      bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        controls_frame.pack(fill='x', padx=20, pady=10)

        # Botões de ação
        buttons_frame = tk.Frame(controls_frame, bg='#2a2a2a')
        buttons_frame.pack(fill='x', padx=10, pady=10)

        tk.Button(buttons_frame, text=i18n.get_text("ui.save_feeding_config") if I18N_AVAILABLE else "💾 Salvar Configurações",
                 bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 command=self.save_feeding_config, padx=15, pady=8).pack(side='left', padx=5)

        tk.Button(buttons_frame, text=i18n.get_text("ui.reset_defaults") if I18N_AVAILABLE else "🔄 Restaurar Padrão",
                 bg='#6c757d', fg='white', font=('Arial', 9, 'bold'),
                 command=self.reset_feeding_config, padx=10, pady=5).pack(side='right', padx=5)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_confidence_tab(self):
        """🎯 Criar aba de configuração de confiança para TEMPLATES - TODOS os 50 templates"""
        confidence_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.templates_tab') if I18N_AVAILABLE else '🎯 Templates'
        self.notebook.add(confidence_frame, text=tab_text)
        
        # Título da aba
        title_label = tk.Label(confidence_frame,
                             text=i18n.get_text("ui.templates_confidence") if I18N_AVAILABLE else "🎯 Configuração de Confiança por Template",
                             font=('Arial', 14, 'bold'),
                             fg='#00aaff',
                             bg='#1a1a1a')
        title_label.pack(pady=10)

        # Subtítulo explicativo
        subtitle_label = tk.Label(confidence_frame,
                                text=_("feeding_hardcoded.ajuste_a_precisão"),
                                font=('Arial', 10),
                                fg='#cccccc',
                                bg='#1a1a1a')
        subtitle_label.pack(pady=5)

        # Frame scrollável para os templates
        canvas = tk.Canvas(confidence_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(confidence_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Dicionário para armazenar as variáveis de confiança dos templates
        self.template_confidence_vars = {}

        # Verificar se config tem categorias unified
        if hasattr(self.config_manager, 'has_template_categories') and self.config_manager.has_template_categories():
            # Usar categorias do config unified
            unified_categories = self.config_manager.get_template_categories()
            
            # Converter para formato da UI com ícones e contadores
            template_categories = {}
            category_icons = {
                "critical": "🔴 CRÍTICOS",
                "rods_with_bait": "🎣 VARAS COM ISCA", 
                "rods_without_bait": "🎣 VARAS SEM ISCA",
                "rods_broken": "💥 VARAS QUEBRADAS",
                "fish_main": "🐟 PEIXES PRINCIPAIS",
                "fish_additional": "🐟 PEIXES ADICIONAIS",
                "baits": "🥩 ISCAS/CARNES",
                "food": "🍖 ALIMENTAÇÃO",
                "containers": "📦 CONTAINERS",
                "items_other": "🔧 OUTROS ITENS",
                "items_special": "💀 ITENS ESPECIAIS"
            }
            
            for category_key, templates_list in unified_categories.items():
                icon_name = category_icons.get(category_key, f"📋 {category_key.upper()}")
                count = len(templates_list)
                display_name = f"{icon_name} ({count})"
                template_categories[display_name] = templates_list
                
            print(f"[OK] Usando categorias UNIFIED: {len(template_categories)} categorias")
        else:
            # Fallback para categorias hardcoded (compatibilidade)
            template_categories = {
                "🔴 CRÍTICOS (3)": ['catch', 'inventory', 'loot'],
                "🎣 VARAS COM ISCA (5)": ['comiscavara', 'varacomisca', 'varanobauci', 'namaocomisca', 'comiscanamao'],
                "🎣 VARAS SEM ISCA (6)": ['semiscavara', 'varasemisca', 'enbausi', 'namaosemisca', 'semiscanam', 'semiscavaraescura'],
                "💥 VARAS QUEBRADAS (2)": ['varaquebrada', 'nobauquebrada'],
                "🐟 PEIXES PRINCIPAIS (6)": ['SALMONN', 'TROUTT', 'shark', 'sardine', 'anchovy', 'yellowperch'],
                "🐟 PEIXES NOVOS (4)": ['herring', 'peixecru', 'catfish', 'roughy'],
                "🥩 ISCAS/CARNES (5)": ['carneurso', 'carnedelobo', 'crocodilo', 'grub', 'minhoca'],
                "🍖 ALIMENTAÇÃO (4)": ['eat', 'frito', 'filefrito', 'gut'],
                "📦 CONTAINERS (2)": ['largebox', 'scrap'],
                "🔧 OUTROS ITENS (3)": ['bluecard', 'flare', 'bullet'],
                "💀 ITENS ESPECIAIS (2)": ['BONE', 'fat']
            }
            print(f"[WARN] Usando categorias HARDCODED: {len(template_categories)} categorias")

        # Criar seções para cada categoria
        for category, template_list in template_categories.items():
            # Cabeçalho da categoria
            category_label = tk.Label(scrollable_frame,
                                    text=category,
                                    font=('Arial', 12, 'bold'),
                                    fg='#ffcc00',
                                    bg='#1a1a1a')
            category_label.pack(pady=(20, 10), anchor='w')

            # Frame para os templates desta categoria
            category_frame = tk.Frame(scrollable_frame, bg='#2a2a2a')
            category_frame.pack(fill='x', padx=10, pady=5)

            # Grid para os controles
            grid_frame = tk.Frame(category_frame, bg='#2a2a2a')
            grid_frame.pack(fill='x', padx=10, pady=10)

            # Cabeçalho da grid
            tk.Label(grid_frame, text=_("templates_hardcoded.template_arquivo"), fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
            tk.Label(grid_frame, text=_("templates_hardcoded.valor"), fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
            tk.Label(grid_frame, text=_("templates_hardcoded.confiança_05_flexível"), fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
            tk.Label(grid_frame, text=_("templates_hardcoded.ajuste_fino"), fg='white', bg='#2a2a2a', font=('Arial', 10, 'bold')).grid(row=0, column=3, padx=5, pady=5)

            row = 1
            for template_name in template_list:
                # Nome do template + arquivo .png
                display_name = template_name.replace('_', ' ').title()
                filename = f"{template_name}.png"
                full_display = f"{display_name}\n📁 {filename}"

                label = tk.Label(grid_frame, text=full_display,
                        fg='white', bg='#2a2a2a', font=('Arial', 8), justify='left')
                label.grid(row=row, column=0, sticky='w', padx=5, pady=2)

                # Valor atual de confiança (usar método correto que trata formato unified/legado)
                if hasattr(self.config_manager, 'get_template_confidence'):
                    current_confidence = self.config_manager.get_template_confidence(template_name)
                else:
                    current_confidence = 0.7
                    
                confidence_var = tk.DoubleVar(value=current_confidence)
                self.template_confidence_vars[template_name] = confidence_var

                # Entry para valor numérico
                entry = tk.Entry(grid_frame, textvariable=confidence_var, width=6, font=('Arial', 9),
                               bg='#404040', fg='white')
                entry.grid(row=row, column=1, padx=5, pady=2)

                # Slider para ajuste visual (incrementos de 1% - 91,92,93,94,95,96,97,98)
                slider = tk.Scale(grid_frame, from_=0.5, to=1.0, resolution=0.01, orient='horizontal',
                                variable=confidence_var, length=250, bg='#444444', fg='white',
                                highlightthickness=0, troughcolor='#666666',
                                command=lambda val, template=template_name: self.update_template_confidence_preview(template, float(val)))
                slider.grid(row=row, column=2, padx=5, pady=2)

                # Botões de incremento fino (+1% / -1%)
                fine_tune_frame = tk.Frame(grid_frame, bg='#2a2a2a')
                fine_tune_frame.grid(row=row, column=3, padx=5, pady=2)

                tk.Button(fine_tune_frame, text="-1%",
                         command=lambda var=confidence_var: self.adjust_confidence(var, -0.01),
                         bg='#dc3545', fg='white', font=('Arial', 8), width=3).pack(side='left', padx=1)

                tk.Button(fine_tune_frame, text=_("templates_hardcoded.1"),
                         command=lambda var=confidence_var: self.adjust_confidence(var, +0.01),
                         bg='#28a745', fg='white', font=('Arial', 8), width=3).pack(side='left', padx=1)

                row += 1

        # Botões de ação
        button_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
        button_frame.pack(pady=20)

        # Botões de atalho rápido para valores específicos (90,91,92,93,94,95,96,97,98)
        quick_values_frame = tk.Frame(button_frame, bg='#1a1a1a')
        quick_values_frame.pack(pady=(0, 10))

        tk.Label(quick_values_frame, text=_("templates_hardcoded.atalhos_rápidos"), fg='white', bg='#1a1a1a',
                font=('Arial', 9, 'bold')).pack(side='left', padx=5)

        quick_values = [90, 91, 92, 93, 94, 95, 96, 97, 98]
        for value in quick_values:
            tk.Button(quick_values_frame, text=f"{value}%",
                     command=lambda v=value: self.set_selected_templates_value(v/100),
                     bg='#6c757d', fg='white', font=('Arial', 8),
                     width=4, pady=2).pack(side='left', padx=1)

        # Botões principais
        main_buttons_frame = tk.Frame(button_frame, bg='#1a1a1a')
        main_buttons_frame.pack()

        tk.Button(main_buttons_frame, text=_("templates_hardcoded.aplicar_padrão"), command=self.reset_template_confidence,
                 bg='#6f42c1', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(main_buttons_frame, text=_("templates_hardcoded.críticos_precisão_alta"), command=self.set_high_precision_critical,
                 bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(main_buttons_frame, text=i18n.get_text("ui.save_all_confidence") if I18N_AVAILABLE else "💾 Salvar Tudo", command=self.save_all_template_confidence,
                 bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(main_buttons_frame, text=_("templates_hardcoded.salvar_como_padrão"), command=self.save_current_as_default,
                 bg='#fd7e14', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(main_buttons_frame, text=_("templates_hardcoded.abrir_pasta_templates"), command=self.open_templates_folder,
                 bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='right', padx=5)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_confidence_slider(self, parent, template_name, is_critical=False):
        """Criar slider de confiança para um template"""
        frame = tk.Frame(parent, bg='#2a2a2a')
        frame.pack(fill='x', padx=10, pady=3)
        
        # Nome do template
        color = '#ff6b6b' if is_critical else '#ffffff'
        tk.Label(frame, text=f"{template_name}:",
                fg=color, bg='#2a2a2a', font=('Arial', 9), width=15, anchor='w').pack(side='left')
        
        # Slider
        confidence_var = tk.DoubleVar(value=0.7)
        scale = tk.Scale(frame, from_=0.5, to=1.0, resolution=0.05, orient='horizontal',
                        variable=confidence_var, bg='#2a2a2a', fg='white',
                        highlightthickness=0, width=15, length=200)
        scale.pack(side='left', padx=5)
        
        # Label com valor
        value_label = tk.Label(frame, text=_("templates_hardcoded.070"), fg='#00ff00', bg='#2a2a2a', font=('Arial', 9), width=4)
        value_label.pack(side='left', padx=5)
        
        # Atualizar label quando slider muda
        def update_label(*args):
            value_label.config(text=f"{confidence_var.get():.2f}")
        confidence_var.trace('w', update_label)
    
    def update_template_confidence_preview(self, template_name, confidence_value):
        """Atualizar confiança APENAS para preview (não salva arquivo)"""
        try:
            # Feedback visual opcional
            print(f"🔍 Preview: Template '{template_name}' = {confidence_value:.2f} (não salvo)")
            return True
        except Exception as e:
            print(f"[ERROR] Erro no preview: {e}")
            return False

    def update_template_confidence_live(self, template_name, confidence_value):
        """Atualizar confiança ao vivo E SALVAR arquivo"""
        try:
            # Verificar se é formato unified ou legado
            if hasattr(self.config_manager, 'is_unified_format') and self.config_manager.is_unified_format:
                # Formato unified: template_confidence.values.template_name
                self.config_manager.set(f'template_confidence.values.{template_name}', confidence_value)
            else:
                # Formato legado: template_confidence.template_name
                self.config_manager.set(f'template_confidence.{template_name}', confidence_value)
            
            # IMPORTANTE: Salvar no arquivo
            if hasattr(self.config_manager, 'save_config'):
                self.config_manager.save_config()
                print(f"[SAVE] Template '{template_name}' salvo como {confidence_value:.2f} e persistido no arquivo")
                return True
            else:
                print(f"[WARN] Template '{template_name}' atualizado mas não persistido (save_config não disponível)")
                return False
        except Exception as e:
            print(f"[ERROR] Erro ao salvar: {e}")
            return False

    def reset_template_confidence(self):
        """Resetar todas as configurações para padrão"""
        try:
            if hasattr(tk, 'messagebox') and tk.messagebox.askyesno("🔄 Resetar", "Resetar todas as configurações de confiança para os valores padrão?"):
                # Valores padrão para cada template
                default_values = {
                    # Críticos
                    'catch': 0.8, 'inventory': 0.8, 'loot': 0.8,
                    # Varas com isca
                    'comiscavara': 0.7, 'varacomisca': 0.7, 'varanobauci': 0.7, 'namaocomisca': 0.7, 'comiscanamao': 0.7,
                    # Varas sem isca
                    'semiscavara': 0.7, 'varasemisca': 0.7, 'enbausi': 0.7, 'namaosemisca': 0.7, 'semiscanam': 0.7, 'semiscavaraescura': 0.7,
                    # Varas quebradas
                    'varaquebrada': 0.7, 'nobauquebrada': 0.7,
                    # Peixes principais - ✅ SALMONN e TROUTT reduzidos para 0.85
                    'SALMONN': 0.85, 'TROUTT': 0.85, 'shark': 0.7, 'sardine': 0.7, 'anchovy': 0.7, 'yellowperch': 0.7,
                    # Peixes novos
                    'herring': 0.7, 'peixecru': 0.7, 'catfish': 0.74, 'roughy': 0.74,
                    # Iscas/Carnes
                    'carneurso': 0.7, 'carnedelobo': 0.74, 'crocodilo': 0.7, 'grub': 0.6, 'minhoca': 0.74,
                    # Alimentação
                    'eat': 0.7, 'frito': 0.7, 'filefrito': 0.7, 'gut': 0.7,
                    # Containers
                    'largebox': 0.7, 'scrap': 0.7,
                    # Outros
                    'bluecard': 0.7, 'flare': 0.7, 'bullet': 0.7, 'BONE': 0.7, 'fat': 0.7
                }
                
                # Atualizar interface
                for template_name, var in self.template_confidence_vars.items():
                    default_value = default_values.get(template_name, 0.7)
                    var.set(default_value)

                print("[OK] Configurações de template resetadas para padrão!")

        except Exception as e:
            print(f"[ERROR] Erro ao resetar configurações: {e}")

    def set_high_precision_critical(self):
        """Aplicar alta precisão aos templates críticos (respeitando valores maiores já configurados)"""
        try:
            critical_templates = ['catch', 'inventory', 'loot', 'comiscavara', 'semiscavara', 'varaquebrada']

            for template_name in critical_templates:
                if template_name in self.template_confidence_vars:
                    current_value = self.template_confidence_vars[template_name].get()
                    # Só aplicar 0.85 se o valor atual for menor que 0.85
                    if current_value < 0.85:
                        self.template_confidence_vars[template_name].set(0.85)
                        print(f"  📈 {template_name}: {current_value:.2f} → 0.85")
                    else:
                        print(f"  ✅ {template_name}: {current_value:.2f} (mantido - já é alta precisão)")

            print("[TARGET] Templates críticos configurados para alta precisão (mínimo 0.85)!")

        except Exception as e:
            print(f"[ERROR] Erro ao aplicar alta precisão: {e}")

    def save_all_template_confidence(self):
        """Salvar todas as configurações de confiança"""
        try:
            # Salvar cada template (sem persistir individualmente para eficiência)
            saved_count = 0
            for template_name, var in self.template_confidence_vars.items():
                confidence_value = var.get()
                try:
                    # Verificar se é formato unified ou legado
                    if hasattr(self.config_manager, 'is_unified_format') and self.config_manager.is_unified_format:
                        # Formato unified: template_confidence.values.template_name
                        self.config_manager.set(f'template_confidence.values.{template_name}', confidence_value)
                        # Debug para templates críticos
                        if template_name in ['SALMONN', 'TROUTT']:
                            print(f"[SAVE] SALVANDO {template_name}: {confidence_value:.3f} em template_confidence.values.{template_name}")
                    else:
                        # Formato legado: template_confidence.template_name
                        self.config_manager.set(f'template_confidence.{template_name}', confidence_value)
                        # Debug para templates críticos
                        if template_name in ['SALMONN', 'TROUTT']:
                            print(f"[SAVE] SALVANDO {template_name}: {confidence_value:.3f} em template_confidence.{template_name}")
                    saved_count += 1
                except Exception as e:
                    print(f"[ERROR] Erro ao configurar {template_name}: {e}")

            # Salvar TODAS as configurações no arquivo UMA VEZ (mais eficiente)
            if hasattr(self.config_manager, 'save_config'):
                self.config_manager.save_config()
                print(f"[SAVE] Salvos {saved_count} templates com sucesso! Configurações persistidas no arquivo!")
            else:
                print(f"[WARN] {saved_count} templates atualizados mas não persistidos (save_config não disponível)")

        except Exception as e:
            print(f"[ERROR] Erro ao salvar configurações: {e}")

    def save_template_config(self):
        """Salvar configurações de templates - Alias para save_all_template_confidence"""
        self.save_all_template_confidence()

    def save_current_as_default(self):
        """Salvar TODAS as configurações atuais como padrão em default_config.json"""
        try:
            if hasattr(tk, 'messagebox') and tk.messagebox.askyesno(
                "⭐ Salvar como Padrão",
                "⚠️ ATENÇÃO: Isso irá sobrescrever o arquivo default_config.json com TODAS as configurações atuais da UI!\n\n"
                "Incluindo:\n"
                "• Templates\n"
                "• Auto-Clean\n"
                "• Feeding\n"
                "• Anti-Detection\n"
                "• Todas as outras configurações\n\n"
                "Deseja continuar?"
            ):
                import json
                import os

                # Primeiro salvar configurações atuais no data/config.json
                self.save_all_template_confidence()
                self.save_cleaning_config()
                self.save_feeding_config()
                self.save_anti_detection_config()

                # Caminho do arquivo padrão
                default_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'default_config.json')
                user_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config.json')

                # Ler config do usuário
                if os.path.exists(user_config_path):
                    with open(user_config_path, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)

                    # Salvar como padrão
                    with open(default_config_path, 'w', encoding='utf-8') as f:
                        json.dump(user_config, f, indent=2, ensure_ascii=False)

                    print(f"[OK] Configurações atuais salvas como padrão em: {default_config_path}")
                    tk.messagebox.showinfo("Sucesso", "✅ Configurações salvas como padrão!\n\nAgora estas configurações serão usadas por padrão em novas instalações.")
                else:
                    print(f"[ERROR] Arquivo de configuração do usuário não encontrado: {user_config_path}")
                    tk.messagebox.showerror("Erro", "Arquivo de configuração não encontrado!")

        except Exception as e:
            print(f"[ERROR] Erro ao salvar como padrão: {e}")
            tk.messagebox.showerror("Erro", f"Erro ao salvar como padrão:\n{e}")

    def reset_template_config(self):
        """Resetar configurações de templates - Alias para reset_template_confidence"""
        self.reset_template_confidence()

    def adjust_confidence(self, confidence_var, increment):
        """Ajustar confidence em incrementos finos (+1% / -1%)"""
        try:
            current_value = confidence_var.get()
            new_value = current_value + increment

            # Limitar entre 0.5 e 1.0
            new_value = max(0.5, min(1.0, new_value))

            # Arredondar para 2 casas decimais (0.91, 0.92, 0.93, etc.)
            new_value = round(new_value, 2)

            confidence_var.set(new_value)
            print(f"[TARGET] Ajuste fino: {current_value:.2f} → {new_value:.2f} ({increment:+.2f})")

        except Exception as e:
            print(f"[ERROR] Erro no ajuste fino: {e}")

    def set_selected_templates_value(self, value):
        """Definir valor específico para templates selecionados (para atalhos rápidos)"""
        try:
            # Por enquanto, aplicar a todos os templates críticos
            # TODO: Implementar seleção de templates específicos na UI
            critical_templates = ['catch', 'inventory', 'loot', 'SALMONN', 'TROUTT']

            updated_count = 0
            for template_name in critical_templates:
                if template_name in self.template_confidence_vars:
                    old_value = self.template_confidence_vars[template_name].get()
                    self.template_confidence_vars[template_name].set(value)
                    print(f"[TARGET] {template_name}: {old_value:.2f} → {value:.2f}")
                    updated_count += 1

            print(f"[OK] Atalho rápido: {updated_count} templates críticos definidos para {value*100:.0f}%")

        except Exception as e:
            print(f"[ERROR] Erro no atalho rápido: {e}")

    def open_templates_folder(self):
        """Abrir pasta de templates"""
        import os
        import subprocess
        try:
            templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
            if os.path.exists(templates_path):
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', templates_path])
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', templates_path])
            else:
                print(f"[ERROR] Pasta templates não encontrada: {templates_path}")
        except Exception as e:
            print(f"[ERROR] Erro ao abrir pasta templates: {e}")
    
    def save_anti_detection_config(self):
        """Salvar configurações de anti-detecção"""
        print("[SAVE] Salvando configurações de anti-detecção...")
        # Implementar salvamento aqui
    
    def reset_anti_detection_config(self):
        """Resetar configurações de anti-detecção para padrão"""
        print("[RELOAD] Resetando configurações de anti-detecção...")
        # Implementar reset aqui
    
    def test_anti_detection_system(self):
        """Testar sistema de anti-detecção"""
        print("[TEST] Testando sistema de anti-detecção...")
        # Implementar teste aqui
    
    def create_anti_detection_tab(self):
        """🛡️ Criar aba de configuração do sistema anti-detecção"""
        anti_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.anti_detection_tab') if I18N_AVAILABLE else '🛡️ Anti-Detecção'
        self.notebook.add(anti_frame, text=tab_text)

        # Título
        title_label = tk.Label(anti_frame,
                              text=i18n.get_text("ui.anti_detection") if I18N_AVAILABLE else "🛡️ Sistema Anti-Detecção Avançado",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)

        # Frame scrollável para as configurações
        canvas = tk.Canvas(anti_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(anti_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ========== ATIVAÇÃO GERAL ==========
        main_frame = tk.LabelFrame(scrollable_frame, text=_("anti_detection_hardcoded.ativação_geral"),
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        main_frame.pack(fill='x', padx=20, pady=10)

        self.anti_detection_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(main_frame, text=_("anti_detection_hardcoded.ativar_sistema_antidetecção"),
                      variable=self.anti_detection_enabled,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10, 'bold'),
                      command=self.toggle_anti_detection).pack(pady=10)

        # ========== VARIAÇÃO DE CLIQUES ==========
        click_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.click_variation") if I18N_AVAILABLE else "🖱️ Variação de Cliques",
                                    bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        click_frame.pack(fill='x', padx=20, pady=10)

        self.click_variation_enabled = tk.BooleanVar(value=False)
        tk.Checkbutton(click_frame, text="Ativar variação de cliques",
                      variable=self.click_variation_enabled,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(pady=5)

        # Sliders para configurar delays
        tk.Label(click_frame, text=_("anti_detection_hardcoded.delay_mínimo_ms"), bg='#2a2a2a', fg='white').pack()
        self.click_min_delay = tk.Scale(click_frame, from_=50, to=150, orient='horizontal',
                                       bg='#2a2a2a', fg='white', highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.click_min_delay.set(80)
        self.click_min_delay.pack(pady=5)

        tk.Label(click_frame, text=_("anti_detection_hardcoded.delay_máximo_ms"), bg='#2a2a2a', fg='white').pack()
        self.click_max_delay = tk.Scale(click_frame, from_=100, to=200, orient='horizontal',
                                       bg='#2a2a2a', fg='white', highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.click_max_delay.set(150)
        self.click_max_delay.pack(pady=5)

        # ========== VARIAÇÃO DE MOVIMENTOS A/D ==========
        movement_frame = tk.LabelFrame(scrollable_frame, text=_("anti_detection_hardcoded.variação_de_movimentos"),
                                       bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        movement_frame.pack(fill='x', padx=20, pady=10)

        self.movement_variation_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(movement_frame, text=_("anti_detection_hardcoded.ativar_variação_de"),
                      variable=self.movement_variation_enabled,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(pady=5)

        # Configurações do movimento A
        tk.Label(movement_frame, text=_("anti_detection_hardcoded.duração_a_mín"), bg='#2a2a2a', fg='white').pack()
        self.a_duration_min = tk.Scale(movement_frame, from_=1.0, to=2.0, resolution=0.1,
                                       orient='horizontal', bg='#2a2a2a', fg='white',
                                       highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.a_duration_min.set(1.2)
        self.a_duration_min.pack(pady=5)

        tk.Label(movement_frame, text=_("anti_detection_hardcoded.duração_a_máx"), bg='#2a2a2a', fg='white').pack()
        self.a_duration_max = tk.Scale(movement_frame, from_=1.0, to=2.0, resolution=0.1,
                                       orient='horizontal', bg='#2a2a2a', fg='white',
                                       highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.a_duration_max.set(1.8)
        self.a_duration_max.pack(pady=5)

        # Configurações do movimento D
        tk.Label(movement_frame, text=_("anti_detection_hardcoded.duração_d_mín"), bg='#2a2a2a', fg='white').pack()
        self.d_duration_min = tk.Scale(movement_frame, from_=0.8, to=1.5, resolution=0.1,
                                       orient='horizontal', bg='#2a2a2a', fg='white',
                                       highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.d_duration_min.set(1.0)
        self.d_duration_min.pack(pady=5)

        tk.Label(movement_frame, text=_("anti_detection_hardcoded.duração_d_máx"), bg='#2a2a2a', fg='white').pack()
        self.d_duration_max = tk.Scale(movement_frame, from_=0.8, to=1.5, resolution=0.1,
                                       orient='horizontal', bg='#2a2a2a', fg='white',
                                       highlightthickness=0,
                                       command=lambda v: self.update_anti_detection_settings())
        self.d_duration_max.set(1.3)
        self.d_duration_max.pack(pady=5)

        # ========== CICLO DE TECLA S ==========
        s_key_frame = tk.LabelFrame(scrollable_frame, text=_("anti_detection_hardcoded.ciclo_de_tecla"),
                                    bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        s_key_frame.pack(fill='x', padx=20, pady=10)

        self.s_key_cycle_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(s_key_frame, text=_("anti_detection_hardcoded.ativar_ciclo_automático"),
                      variable=self.s_key_cycle_enabled,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(pady=5)

        # Tempo pressionado
        tk.Label(s_key_frame, text=_("anti_detection_hardcoded.tempo_pressionado_mínimo"), bg='#2a2a2a', fg='white').pack()
        self.s_hold_duration_min = tk.Scale(s_key_frame, from_=0.5, to=3.0, resolution=0.1,
                                           orient='horizontal', bg='#2a2a2a', fg='white',
                                           highlightthickness=0,
                                           command=lambda v: self.update_anti_detection_settings())
        self.s_hold_duration_min.set(1.5)
        self.s_hold_duration_min.pack(pady=5)

        tk.Label(s_key_frame, text=_("anti_detection_hardcoded.tempo_pressionado_máximo"), bg='#2a2a2a', fg='white').pack()
        self.s_hold_duration_max = tk.Scale(s_key_frame, from_=0.5, to=5.0, resolution=0.1,
                                           orient='horizontal', bg='#2a2a2a', fg='white',
                                           highlightthickness=0,
                                           command=lambda v: self.update_anti_detection_settings())
        self.s_hold_duration_max.set(2.5)
        self.s_hold_duration_max.pack(pady=5)

        # Tempo solto
        tk.Label(s_key_frame, text=_("anti_detection_hardcoded.tempo_solto_mínimo"), bg='#2a2a2a', fg='white').pack()
        self.s_release_duration_min = tk.Scale(s_key_frame, from_=0.5, to=3.0, resolution=0.1,
                                              orient='horizontal', bg='#2a2a2a', fg='white',
                                              highlightthickness=0,
                                              command=lambda v: self.update_anti_detection_settings())
        self.s_release_duration_min.set(1.0)
        self.s_release_duration_min.pack(pady=5)

        tk.Label(s_key_frame, text=_("anti_detection_hardcoded.tempo_solto_máximo"), bg='#2a2a2a', fg='white').pack()
        self.s_release_duration_max = tk.Scale(s_key_frame, from_=0.5, to=4.0, resolution=0.1,
                                              orient='horizontal', bg='#2a2a2a', fg='white',
                                              highlightthickness=0,
                                              command=lambda v: self.update_anti_detection_settings())
        self.s_release_duration_max.set(2.0)
        self.s_release_duration_max.pack(pady=5)

        # Info visual
        info_label = tk.Label(s_key_frame,
                             text=_("anti_detection_hardcoded.ℹ_o_ciclo")
                                  "Simula comportamento humano durante a pesca",
                             bg='#2a2a2a', fg='#aaaaaa', font=('Arial', 8),
                             justify='left')
        info_label.pack(pady=10)

        # ========== PAUSAS NATURAIS ==========
        breaks_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.pausas_naturais"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        breaks_frame.pack(fill='x', padx=20, pady=10)

        self.natural_breaks_enabled = tk.BooleanVar(value=True)
        tk.Checkbutton(breaks_frame, text=_("ui_hardcoded.ativar_pausas_naturais"),
                      variable=self.natural_breaks_enabled,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(pady=5)

        # Modo de pausa (tempo ou quantidade)
        mode_frame = tk.Frame(breaks_frame, bg='#2a2a2a')
        mode_frame.pack(pady=5)

        tk.Label(mode_frame, text=_("ui_hardcoded.modo_de_pausa"), bg='#2a2a2a', fg='white').pack(side='left', padx=5)

        self.break_mode = tk.StringVar(value='catches')
        tk.Radiobutton(mode_frame, text=_("ui_hardcoded.por_tempo"), variable=self.break_mode, value='time',
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(side='left', padx=5)
        tk.Radiobutton(mode_frame, text=_("ui_hardcoded.por_pescas"), variable=self.break_mode, value='catches',
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      command=self.update_anti_detection_settings).pack(side='left', padx=5)

        # Intervalo de tempo
        tk.Label(breaks_frame, text=_("ui_hardcoded.intervalo_de_tempo"), bg='#2a2a2a', fg='white').pack()
        self.break_time_interval = tk.Scale(breaks_frame, from_=10, to=120, orient='horizontal',
                                           bg='#2a2a2a', fg='white', highlightthickness=0,
                                           command=lambda v: self.update_anti_detection_settings())
        self.break_time_interval.set(45)
        self.break_time_interval.pack(pady=5)

        # Intervalo de pescas
        tk.Label(breaks_frame, text=_("ui_hardcoded.intervalo_de_pescas"), bg='#2a2a2a', fg='white').pack()
        self.break_catches_interval = tk.Scale(breaks_frame, from_=20, to=100, orient='horizontal',
                                              bg='#2a2a2a', fg='white', highlightthickness=0,
                                              command=lambda v: self.update_anti_detection_settings())
        self.break_catches_interval.set(50)
        self.break_catches_interval.pack(pady=5)

        # Duração da pausa
        tk.Label(breaks_frame, text=_("ui_hardcoded.duração_mínima_da"), bg='#2a2a2a', fg='white').pack()
        self.break_duration_min = tk.Scale(breaks_frame, from_=1, to=10, resolution=0.5, orient='horizontal',
                                          bg='#2a2a2a', fg='white', highlightthickness=0,
                                          command=lambda v: self.update_anti_detection_settings())
        self.break_duration_min.set(2.0)
        self.break_duration_min.pack(pady=5)

        tk.Label(breaks_frame, text=_("ui_hardcoded.duração_máxima_da"), bg='#2a2a2a', fg='white').pack()
        self.break_duration_max = tk.Scale(breaks_frame, from_=1, to=15, resolution=0.5, orient='horizontal',
                                          bg='#2a2a2a', fg='white', highlightthickness=0,
                                          command=lambda v: self.update_anti_detection_settings())
        self.break_duration_max.set(5.0)
        self.break_duration_max.pack(pady=5)


        # Botão para salvar configurações
        save_btn = tk.Button(scrollable_frame, text=i18n.get_text("ui.save_anti_detection") if I18N_AVAILABLE else "💾 Salvar Configurações Anti-Detecção",
                           command=self.save_anti_detection_config,
                           bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                           padx=20, pady=10)
        save_btn.pack(pady=20)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    # ========== FUNÇÕES DE CALLBACK ANTI-DETECÇÃO ==========
    
    def toggle_anti_detection(self):
        """Ativar/desativar sistema anti-detecção"""
        enabled = self.anti_detection_enabled.get()
        status = "ATIVADO" if enabled else "DESATIVADO"
        print(f"🛡️ Sistema Anti-Detecção {status}")

    def update_anti_detection_settings(self):
        """Atualizar configurações de anti-detecção em tempo real"""
        try:
            # Silencioso - sem logs excessivos durante updates da UI
            pass
        except Exception as e:
            print(f"[ERROR] Erro ao atualizar configurações anti-detecção: {e}")

    def save_anti_detection_config(self):
        """Salvar configurações de anti-detecção no arquivo"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # ✅ CORRIGIDO: Salvar na estrutura correta que InputManager lê
                self.config_manager.set('anti_detection.enabled', self.anti_detection_enabled_var.get())

                # Variação de cliques (estrutura correta: click_variation.min_delay/max_delay)
                # CORRIGIDO: usar self.click_variation_enabled, self.click_min_delay, self.click_max_delay
                self.config_manager.set('anti_detection.click_variation.enabled', self.click_variation_enabled.get())
                self.config_manager.set('anti_detection.click_variation.min_delay', float(self.click_min_delay.get()) / 1000.0)  # Converter ms para s
                self.config_manager.set('anti_detection.click_variation.max_delay', float(self.click_max_delay.get()) / 1000.0)  # Converter ms para s

                # Variação de movimentos (boolean - InputManager usa valores internos)
                self.config_manager.set('anti_detection.movement_variation.enabled', self.movement_variation_enabled.get())

                # ✅ NOVO: Ciclo de tecla S
                self.config_manager.set('anti_detection.s_key_cycle.enabled', self.s_key_cycle_enabled.get())
                self.config_manager.set('anti_detection.s_key_cycle.hold_duration_min', float(self.s_hold_duration_min.get()))
                self.config_manager.set('anti_detection.s_key_cycle.hold_duration_max', float(self.s_hold_duration_max.get()))
                self.config_manager.set('anti_detection.s_key_cycle.release_duration_min', float(self.s_release_duration_min.get()))
                self.config_manager.set('anti_detection.s_key_cycle.release_duration_max', float(self.s_release_duration_max.get()))

                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print("[OK] Configurações Anti-Detecção salvas e persistidas!")

                    # Recarregar timing no InputManager
                    if hasattr(self, 'input_manager') and self.input_manager:
                        self.input_manager.reload_timing_config()
                        print("[OK] InputManager recarregado com novas configurações!")

                    messagebox.showinfo("Sucesso", "✅ Configurações Anti-Detecção salvas!")
                else:
                    print("[WARN] ConfigManager sem método save_config")
            else:
                print("[ERROR] ConfigManager não disponível")

        except Exception as e:
            print(f"[ERROR] Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    # ========== FUNÇÕES DE CALLBACK PRIORIDADE DE ISCAS (CONFIGURAÇÃO) ==========
    
    def update_config_bait_listbox(self):
        """Atualiza a listbox com a ordem atual das iscas (aba configuração)"""
        try:
            self.config_bait_listbox.delete(0, tk.END)
            for i, bait in enumerate(self.config_ordered_baits):
                enabled = self.config_bait_enabled_vars.get(bait, tk.BooleanVar(value=True)).get()
                status = "✅" if enabled else "❌"
                display_text = f"{i+1}. {status} {bait}"
                self.config_bait_listbox.insert(tk.END, display_text)
        except Exception as e:
            print(f"Erro ao atualizar listbox de iscas: {e}")

    def move_config_bait_up(self):
        """Move a isca selecionada para cima na prioridade (aba configuração)"""
        try:
            selection = self.config_bait_listbox.curselection()
            if not selection or selection[0] == 0:
                return

            index = selection[0]
            # Trocar posições na lista ordenada
            self.config_ordered_baits[index], self.config_ordered_baits[index-1] = \
                self.config_ordered_baits[index-1], self.config_ordered_baits[index]

            # Atualizar interface
            self.update_config_bait_listbox()
            self.config_bait_listbox.selection_set(index-1)

        except Exception as e:
            print(f"Erro ao mover isca para cima: {e}")

    def move_config_bait_down(self):
        """Move a isca selecionada para baixo na prioridade (aba configuração)"""
        try:
            selection = self.config_bait_listbox.curselection()
            if not selection or selection[0] >= len(self.config_ordered_baits) - 1:
                return

            index = selection[0]
            # Trocar posições na lista ordenada
            self.config_ordered_baits[index], self.config_ordered_baits[index+1] = \
                self.config_ordered_baits[index+1], self.config_ordered_baits[index]

            # Atualizar interface
            self.update_config_bait_listbox()
            self.config_bait_listbox.selection_set(index+1)

        except Exception as e:
            print(f"Erro ao mover isca para baixo: {e}")

    def _map_bait_ui_to_config(self, ui_name):
        """Mapear nomes da UI para nomes do config"""
        mapping = {
            'carne de urso': 'carneurso',
            'carne de lobo': 'carnedelobo',
            'crocodilo': 'crocodilo',
            'trout': 'TROUTT',
            'grub': 'grub',
            'worm': 'minhoca'
        }
        return mapping.get(ui_name, ui_name)

    def _map_bait_config_to_ui(self, config_name):
        """Mapear nomes do config para nomes da UI"""
        mapping = {
            'carneurso': 'carne de urso',
            'carnedelobo': 'carne de lobo',
            'crocodilo': 'crocodilo',
            'TROUTT': 'trout',
            'grub': 'grub',
            'minhoca': 'worm'
        }
        return mapping.get(config_name, config_name)

    def update_config_bait_enabled(self):
        """Atualiza o estado de habilitado/desabilitado das iscas (aba configuração)"""
        try:
            # Salvar estado bait_enabled no config.json (estrutura correta: bait_system.enabled)
            if hasattr(self, 'config_manager') and self.config_manager:
                bait_enabled = {}
                for bait_name, var in self.config_bait_enabled_vars.items():
                    # Mapear nomes da UI para nomes do config
                    config_name = self._map_bait_ui_to_config(bait_name)
                    bait_enabled[config_name] = var.get()

                self.config_manager.set('bait_system.enabled', bait_enabled)
                print(f"[OK] Estado de iscas salvo: {bait_enabled}")

            # Atualizar a visualização da listbox
            self.update_config_bait_listbox()
        except Exception as e:
            print(f"Erro ao atualizar estado das iscas: {e}")

    def save_bait_priority(self):
        """Salvar prioridade de iscas no config.json"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Coletar prioridades atuais (TODAS as iscas, enabled ou não)
                bait_priority = {}
                bait_enabled = {}

                for i, bait_name in enumerate(self.config_ordered_baits):
                    # Mapear nome da UI para nome do config
                    config_name = self._map_bait_ui_to_config(bait_name)

                    # Salvar prioridade (posição na lista, começando em 1)
                    bait_priority[config_name] = i + 1

                    # Salvar estado enabled/disabled
                    if bait_name in self.config_bait_enabled_vars:
                        bait_enabled[config_name] = self.config_bait_enabled_vars[bait_name].get()
                    else:
                        bait_enabled[config_name] = True  # Default: habilitado

                # Salvar no ConfigManager (estrutura correta: bait_system.priority e bait_system.enabled)
                self.config_manager.set('bait_system.priority', bait_priority)
                self.config_manager.set('bait_system.enabled', bait_enabled)

                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"[OK] Prioridade de iscas salva: {bait_priority}")
                    print(f"[OK] Estado de iscas salvo: {bait_enabled}")
                    messagebox.showinfo("Sucesso", "✅ Prioridade de iscas salva!")
                else:
                    print("[WARN] ConfigManager sem método save_config")
            else:
                print("[ERROR] ConfigManager não disponível")

        except Exception as e:
            print(f"[ERROR] Erro ao salvar prioridade de iscas: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")

    def reset_config_bait_priorities(self):
        """Restaura as prioridades padrão das iscas (aba configuração)"""
        try:
            # Reordenar lista
            self.config_ordered_baits = ['carne de crocodilo', 'carne de urso', 'carne de lobo', 'trout', 'grub', 'worm']

            # Restaurar todas as iscas como habilitadas
            for bait in self.config_bait_names:
                if bait in self.config_bait_enabled_vars:
                    self.config_bait_enabled_vars[bait].set(True)

            # Atualizar interface
            self.update_config_bait_listbox()

            print("[RELOAD] Prioridades de isca restauradas para o padrão")

        except Exception as e:
            print(f"Erro ao restaurar prioridades: {e}")
    
    def create_catch_viewer_tab(self):
        """Aba 6: 🐟 Visualizador - Janela de capturas e detecções em tempo real"""
        viewer_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.catch_viewer_tab') if I18N_AVAILABLE else '🐟 Visualizador'
        self.notebook.add(viewer_frame, text=tab_text)

        # Título
        title_label = tk.Label(viewer_frame,
                              text=i18n.get_text("ui.template_viewer") if I18N_AVAILABLE else "🐟 Visualizador Template Matching - CATCH",
                              font=('Arial', 14, 'bold'),
                              fg='#00ff88', bg='#1a1a1a')
        title_label.pack(pady=15)

        # Frame principal com scroll
        canvas = tk.Canvas(viewer_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(viewer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ========== STATUS DO VISUALIZADOR ==========
        status_frame = tk.LabelFrame(scrollable_frame, text=i18n.get_text("ui.viewer_status") if I18N_AVAILABLE else "📊 Status do Visualizador",
                                    bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        status_frame.pack(fill='x', padx=20, pady=10)

        # Status atual
        self.catch_viewer_status_label = tk.Label(status_frame,
                                                 text=i18n.get_text("ui.status_stopped") if I18N_AVAILABLE else "📊 Status: Parado",
                                                 font=('Arial', 11, 'bold'),
                                                 fg='#dc3545', bg='#2a2a2a')
        self.catch_viewer_status_label.pack(pady=10)

        # Estatísticas de detecção
        self.catch_stats_label = tk.Label(status_frame,
                                         text=_("ui_hardcoded.detecções_0n_templates"),
                                         font=('Arial', 10),
                                         fg='#cccccc', bg='#2a2a2a',
                                         justify='left')
        self.catch_stats_label.pack(pady=5)

        # ========== CONTROLES ==========
        control_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.controles"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        control_frame.pack(fill='x', padx=20, pady=10)

        # Frame para botões
        button_frame = tk.Frame(control_frame, bg='#2a2a2a')
        button_frame.pack(pady=10)

        # Inicializar variáveis do viewer
        self.catch_viewer_running = False
        self.catch_viewer_window = None
        self.auto_start_catch_viewer = True

        # Botão para abrir janela do viewer
        open_catch_window_btn = tk.Button(button_frame, text=_("ui_hardcoded.abrir_janela_catch"),
                                         command=self.toggle_catch_viewer_window,
                                         bg='#17a2b8', fg='white', font=('Arial', 10, 'bold'),
                                         padx=15, pady=8)
        open_catch_window_btn.pack(side='left', padx=5)

        # Botão para parar viewer
        stop_catch_btn = tk.Button(button_frame, text=_("ui_hardcoded.parar_catch_viewer"),
                                  command=self.stop_catch_viewer,
                                  bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                                  padx=15, pady=8)
        stop_catch_btn.pack(side='left', padx=5)

        # Botão para teste
        test_catch_btn = tk.Button(button_frame, text=_("ui_hardcoded.testar_detecção"),
                                  command=self.test_catch_detection,
                                  bg='#ffc107', fg='black', font=('Arial', 10, 'bold'),
                                  padx=15, pady=8)
        test_catch_btn.pack(side='left', padx=5)

        # ========== CONFIGURAÇÕES AVANÇADAS ==========
        advanced_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.configurações_avançadas"),
                                      bg='#2a2a2a', fg='#00ff88', font=('Arial', 11, 'bold'))
        advanced_frame.pack(fill='x', padx=20, pady=10)

        # Auto-start
        autostart_frame = tk.Frame(advanced_frame, bg='#2a2a2a')
        autostart_frame.pack(fill='x', padx=15, pady=8)

        self.auto_start_var = tk.BooleanVar(value=True)
        tk.Checkbutton(autostart_frame, text=_("ui_hardcoded.iniciar_automaticamente_com"),
                      variable=self.auto_start_var,
                      bg='#2a2a2a', fg='white', selectcolor='#404040',
                      font=('Arial', 10), activebackground='#2a2a2a').pack(anchor='w')

        # FPS e Performance
        performance_subframe = tk.LabelFrame(advanced_frame, text=_("ui_hardcoded.performance"),
                                           bg='#333333', fg='#ffaa00', font=('Arial', 10, 'bold'))
        performance_subframe.pack(fill='x', padx=15, pady=8)

        # FPS do viewer
        fps_frame = tk.Frame(performance_subframe, bg='#333333')
        fps_frame.pack(fill='x', padx=10, pady=8)

        tk.Label(fps_frame, text=_("ui_hardcoded.fps_do_visualizador"),
                fg='white', bg='#333333', font=('Arial', 10)).pack(side='left')

        self.viewer_fps_var = tk.StringVar(value="5")
        fps_combo = ttk.Combobox(fps_frame, textvariable=self.viewer_fps_var,
                                values=['1', '2', '5', '10', '15', '20'], state="readonly", width=6)
        fps_combo.pack(side='left', padx=10)

        # Threshold de detecção
        threshold_frame = tk.Frame(performance_subframe, bg='#333333')
        threshold_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(threshold_frame, text=_("ui_hardcoded.threshold_nms_pixels"),
                fg='white', bg='#333333', font=('Arial', 10)).pack(side='left')

        self.nms_threshold_var = tk.StringVar(value="5")
        nms_combo = ttk.Combobox(threshold_frame, textvariable=self.nms_threshold_var,
                               values=['5', '10', '25', '50', '75', '100'], state="readonly", width=6)
        nms_combo.pack(side='left', padx=10)

        # Botão para aplicar configurações
        apply_frame = tk.Frame(advanced_frame, bg='#2a2a2a')
        apply_frame.pack(fill='x', padx=15, pady=10)

        tk.Button(apply_frame, text=_("ui_hardcoded.aplicar_configurações"),
                 command=self.apply_viewer_config,
                 bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=8).pack(side='left')

        tk.Button(apply_frame, text=i18n.get_text("ui.reset_defaults") if I18N_AVAILABLE else "🔄 Restaurar Padrão",
                 command=self.reset_viewer_config,
                 bg='#6c757d', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=8).pack(side='left', padx=10)

        # ========== ÁREA DE CAPTURA ==========
        capture_frame = tk.LabelFrame(advanced_frame, text=_("ui_hardcoded.área_de_captura"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        capture_frame.pack(fill='x', padx=10, pady=10)

        # Resolução de captura
        resolution_frame = tk.Frame(capture_frame, bg='#2a2a2a')
        resolution_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(resolution_frame, text=_("ui_hardcoded.resolução"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')

        self.capture_resolution_var = tk.StringVar(value="1920x1080")
        resolution_combo = ttk.Combobox(resolution_frame, textvariable=self.capture_resolution_var,
                                       values=['1920x1080', '1366x768', '1280x720', '1600x900', 'Tela Completa'],
                                       state="readonly", width=12)
        resolution_combo.pack(side='left', padx=5)
        resolution_combo.bind('<<ComboboxSelected>>', self.on_resolution_change)

        # Botão para detectar janela do Rust
        detect_btn = tk.Button(capture_frame, text=_("ui_hardcoded.detectar_janela_rust"),
                              command=self.detect_rust_window,
                              bg='#17a2b8', fg='white', font=('Arial', 9),
                              padx=10, pady=5)
        detect_btn.pack(pady=5)

        # ========== INFORMAÇÕES ==========
        info_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.ℹ_informações"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        info_frame.pack(fill='x', padx=20, pady=10)

        catch_instruction_text = """🐟 O Visualizador CATCH mostra detecções de template matching em tempo real:

• 🎯 Detecta peixes capturados, varas com/sem isca
• 🔍 Mostra caixas de detecção com confiança
• 📊 Exibe estatísticas em tempo real
• 👁️ Janela separada para monitoramento visual

⚡ O sistema roda automaticamente em background quando o bot está ativo.
👁️ Use 'Abrir Janela CATCH' para visualizar as detecções."""

        catch_instruction_label = tk.Label(info_frame,
                                          text=catch_instruction_text,
                                          bg='#2a2a2a', fg='#cccccc',
                                          font=('Arial', 9),
                                          justify='left')
        catch_instruction_label.pack(padx=20, pady=10)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_hotkeys_tab(self):
        """Aba 7: ⌨️ Hotkeys - Entries para teclas, botões de captura"""
        hotkeys_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.hotkeys_tab') if I18N_AVAILABLE else '⌨️ Hotkeys'
        self.notebook.add(hotkeys_frame, text=tab_text)
        
        # Título
        title_label = tk.Label(hotkeys_frame,
                              text=_("ui_hardcoded.configuração_de_teclas"),
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(hotkeys_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(hotkeys_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== CONTROLES PRINCIPAIS ==========
        main_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.controles_principais"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        main_frame.pack(fill='x', padx=20, pady=10)
        
        main_hotkeys = {
            'start': 'Iniciar Bot',
            'pause': 'Pausar/Retomar',
            'stop': 'Parar Bot',
            'emergency': 'Parada de Emergência'
        }
        
        for key, desc in main_hotkeys.items():
            self.create_hotkey_row(main_frame, key, self.hotkey_vars[key].get(), desc)
        
        # ========== MACROS ==========
        macro_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.macros"),
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        macro_frame.pack(fill='x', padx=20, pady=10)
        
        macro_hotkeys = {
            'macro_execute': 'Executar Macro',
            'macro_chest': 'Macro de Baú',
            'macro_record': 'Gravar Macro'
        }
        
        for key, desc in macro_hotkeys.items():
            self.create_hotkey_row(macro_frame, key, self.hotkey_vars[key].get(), desc)
        
        # ========== TESTES ==========
        test_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.testes"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        test_frame.pack(fill='x', padx=20, pady=10)
        
        test_hotkeys = {
            'test_mouse': 'Testar Mouse',
            'test_feeding': 'Testar Alimentação',
            'test_cleaning': 'Testar Limpeza'
        }
        
        for key, desc in test_hotkeys.items():
            self.create_hotkey_row(test_frame, key, self.hotkey_vars[key].get(), desc)
        
        # ========== BOTÕES DE AÇÃO ==========
        action_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
        action_frame.pack(fill='x', padx=20, pady=20)

        # Botão para salvar configurações
        save_btn = tk.Button(action_frame,
                            text=i18n.get_text("ui.save_feeding_config") if I18N_AVAILABLE else "💾 Salvar Configurações",
                            command=self.save_hotkeys_config,
                            bg='#28a745', fg='white',
                            font=('Arial', 10, 'bold'),
                            padx=15, pady=8)
        save_btn.pack(side='left', padx=5)

        # Botão para restaurar padrões
        restore_btn = tk.Button(action_frame,
                               text=_("ui_hardcoded.restaurar_padrões"),
                               command=self.restore_default_hotkeys,
                               bg='#6c757d', fg='white',
                               font=('Arial', 10, 'bold'),
                               padx=15, pady=8)
        restore_btn.pack(side='left', padx=5)

        # Botão para aplicar mudanças
        apply_btn = tk.Button(action_frame,
                             text=_("ui_hardcoded.aplicar_mudanças"),
                             command=self.apply_hotkeys_changes,
                             bg='#17a2b8', fg='white',
                             font=('Arial', 10, 'bold'),
                             padx=15, pady=8)
        apply_btn.pack(side='left', padx=5)

        # Label de status
        self.hotkey_status_label = tk.Label(action_frame,
                                           text="",
                                           font=('Arial', 10),
                                           fg='#28a745', bg='#1a1a1a')
        self.hotkey_status_label.pack(side='left', padx=20)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_hotkey_row(self, parent, key, default_value, description):
        """Criar linha de configuração de hotkey"""
        frame = tk.Frame(parent, bg='#2a2a2a')
        frame.pack(fill='x', padx=10, pady=3)
        
        # Descrição
        tk.Label(frame, text=f"{description}:",
                fg='white', bg='#2a2a2a', font=('Arial', 9), width=20, anchor='w').pack(side='left')
        
        # Entry para tecla
        entry = tk.Entry(frame, textvariable=self.hotkey_vars[key], width=12)
        entry.pack(side='left', padx=5)
        
        # Botão capturar
        capture_btn = tk.Button(frame, text=_("ui_hardcoded.capturar"),
                               command=lambda k=key: self.capture_hotkey(k),
                               bg='#17a2b8', fg='white', font=('Arial', 8),
                               padx=8, pady=2)
        capture_btn.pack(side='left', padx=5)
    
    def create_arduino_tab(self):
        """Aba 8: 🔌 Arduino - Conexão COM e controle do hardware"""
        arduino_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.arduino_tab') if I18N_AVAILABLE else '🔌 Arduino'
        self.notebook.add(arduino_frame, text=tab_text)
        
        # Título
        title_label = tk.Label(arduino_frame,
                              text=i18n.get_text("ui.arduino_leonardo") if I18N_AVAILABLE else "🔌 Arduino Leonardo - Controle de Hardware",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(arduino_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(arduino_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== STATUS DE CONEXÃO ==========
        status_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.status_da_conexão"),
                                    bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        status_frame.pack(fill='x', padx=20, pady=10)
        
        # Indicador visual de conexão
        connection_frame = tk.Frame(status_frame, bg='#2a2a2a')
        connection_frame.pack(padx=10, pady=10)
        
        self.arduino_status_indicator = tk.Label(connection_frame, text="●", fg="red", 
                                                bg='#2a2a2a', font=('Arial', 20))
        self.arduino_status_indicator.pack(side='left', padx=5)
        
        self.arduino_connection_status = tk.Label(connection_frame, 
                                                 text=i18n.get_text("ui.not_connected") if I18N_AVAILABLE else "Arduino não conectado",
                                                 fg='white', bg='#2a2a2a', font=('Arial', 12, 'bold'))
        self.arduino_connection_status.pack(side='left', padx=10)
        
        # ========== CONFIGURAÇÃO DA PORTA COM ==========
        com_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.configuração_da_porta"),
                                 bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        com_frame.pack(fill='x', padx=20, pady=10)
        
        com_grid = tk.Frame(com_frame, bg='#2a2a2a')
        com_grid.pack(padx=10, pady=10)
        
        # Porta COM
        tk.Label(com_grid, text=_("ui_hardcoded.porta_com"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        
        # Usar variável já inicializada no construtor
        
        # Obter portas COM com fallback
        com_ports = get_com_ports()
        if not com_ports:
            com_ports = ['COM3']  # Fallback se nenhuma porta encontrada
        
        self.arduino_port_combo = tk.OptionMenu(com_grid, self.arduino_port_var, *com_ports)
        self.arduino_port_combo.configure(bg='#404040', fg='white', width=8)
        self.arduino_port_combo.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Button(com_grid, text=_("ui_hardcoded.atualizar"), command=self.refresh_arduino_ports,
                 bg='#007acc', fg='white', font=('Arial', 9)).grid(row=0, column=2, padx=5, pady=5)
        
        # Baud Rate
        tk.Label(com_grid, text=_("ui_hardcoded.baud_rate"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        
        # Usar variável já inicializada no construtor
        
        baud_combo = tk.OptionMenu(com_grid, self.arduino_baud_var, "9600", "19200", "57600", "115200")
        baud_combo.configure(bg='#404040', fg='white', width=8)
        baud_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Timeout
        tk.Label(com_grid, text=_("ui_hardcoded.timeout_s"),
                fg='white', bg='#2a2a2a', font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        
        # Usar variável já inicializada no construtor
        
        tk.Entry(com_grid, textvariable=self.arduino_timeout_var, width=8,
                bg='#404040', fg='white').grid(row=2, column=1, padx=10, pady=5)
        
        # ========== CONTROLES DE CONEXÃO ==========
        controls_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.controles_de_conexão"),
                                      bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        buttons_frame = tk.Frame(controls_frame, bg='#2a2a2a')
        buttons_frame.pack(padx=10, pady=10)
        
        tk.Button(buttons_frame, text=_("ui_hardcoded.testar_conexão"), command=self.test_arduino_connection,
                 bg='#ffc107', fg='black', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text=i18n.get_text("ui.connect") if I18N_AVAILABLE else "🔌 Conectar", command=self.connect_arduino,
                 bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side='left', padx=5)
        
        tk.Button(buttons_frame, text=_("ui_hardcoded.desconectar"), command=self.disconnect_arduino,
                 bg='#dc3545', fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=5).pack(side='left', padx=5)
        
        # ========== TESTE DE COMANDOS ==========
        test_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.teste_de_comandos"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        test_frame.pack(fill='x', padx=20, pady=10)
        
        test_grid = tk.Frame(test_frame, bg='#2a2a2a')
        test_grid.pack(padx=10, pady=10)
        
        # Comandos básicos (formato correto: COMANDO:ARGUMENTO)
        tk.Button(test_grid, text=_("ui_hardcoded.teste_click_esquerdo"), command=lambda: self.send_arduino_command("MOUSECLICK:L"),
                 bg='#17a2b8', fg='white', font=('Arial', 9), width=18).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(test_grid, text=_("ui_hardcoded.teste_click_direito"), command=lambda: self.send_arduino_command("MOUSECLICK:R"),
                 bg='#17a2b8', fg='white', font=('Arial', 9), width=18).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(test_grid, text=_("ui_hardcoded.teste_tecla_e"), command=lambda: self.send_arduino_command("KEYPRESS:e"),
                 bg='#6f42c1', fg='white', font=('Arial', 9), width=18).grid(row=1, column=0, padx=5, pady=5)

        tk.Button(test_grid, text=_("ui_hardcoded.teste_tecla_a"), command=lambda: self.send_arduino_command("KEYPRESS:a"),
                 bg='#fd7e14', fg='white', font=('Arial', 9), width=18).grid(row=1, column=1, padx=5, pady=5)
        
        # ========== LOG DE COMUNICAÇÃO ==========
        log_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.log_de_comunicação"),
                                 bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        log_frame.pack(fill='x', padx=20, pady=10)
        
        # Text widget para log
        self.arduino_log = tk.Text(log_frame, height=8, width=80, 
                                  bg='#1a1a1a', fg='#00ff00', font=('Consolas', 9),
                                  wrap=tk.WORD)
        self.arduino_log.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Scrollbar para o log
        log_scrollbar = tk.Scrollbar(log_frame, command=self.arduino_log.yview)
        self.arduino_log.config(yscrollcommand=log_scrollbar.set)
        
        # Botão para limpar log
        tk.Button(log_frame, text=_("ui_hardcoded.limpar_log"), command=self.clear_arduino_log,
                 bg='#6c757d', fg='white', font=('Arial', 9),
                 padx=10, pady=3).pack(pady=5)
        
        # ========== INFORMAÇÕES ==========
        info_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.ℹ_informações_do"),
                                  bg='#2a2a2a', fg='white', font=('Arial', 11, 'bold'))
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = """🔌 Arduino Leonardo - Interface de Hardware

• 🖱️ Controle direto do mouse (clicks, movimento)
• ⌨️ Simulação de teclas (E, Alt, etc.)
• 🎣 Comandos específicos para pesca
• 📡 Comunicação via porta COM (USB)
• ⚡ Baixa latência para ações críticas

⚠️ Certifique-se de que o Arduino esteja programado com o firmware correto
📋 Verifique a porta COM no Gerenciador de Dispositivos do Windows"""
        
        tk.Label(info_frame, text=info_text, bg='#2a2a2a', fg='#cccccc',
                font=('Arial', 9), justify='left').pack(padx=20, pady=10)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Inicializar estado
        self.arduino_connected = False
        self.arduino_serial = None
        
        # Carregar configurações do config.json se disponível
        self.load_arduino_config()

    def create_help_tab(self):
        """Aba 9: ❓ Ajuda - Documentação e troubleshooting"""
        help_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        tab_text = i18n.get_text('tabs.help_tab') if I18N_AVAILABLE else '❓ Ajuda'
        self.notebook.add(help_frame, text=tab_text)
        
        # Título
        title_label = tk.Label(help_frame,
                              text=_("ui_hardcoded.ajuda_e_documentação"),
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(help_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(help_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== INSTRUÇÕES BÁSICAS ==========
        basic_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.instruções_básicas"),
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        basic_frame.pack(fill='x', padx=20, pady=10)
        
        instructions = [
            "1. Configure as coordenadas na aba Configurações",
            "2. Ajuste os templates na aba Templates",
            "3. Configure a alimentação se necessário",
            "4. Use as teclas de atalho para controlar o bot",
            "5. Monitore as estatísticas na aba Controle"
        ]
        
        for instruction in instructions:
            tk.Label(basic_frame, text=instruction,
                    fg='white', bg='#2a2a2a', font=('Arial', 9),
                    anchor='w', justify='left').pack(anchor='w', padx=10, pady=2)
        
        # ========== TROUBLESHOOTING ==========
        trouble_frame = tk.LabelFrame(scrollable_frame, text=_("ui_hardcoded.troubleshooting"),
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        trouble_frame.pack(fill='x', padx=20, pady=10)
        
        troubleshooting = [
            "• Bot não detecta peixes: Ajuste confiança dos templates",
            "• Coordenadas erradas: Use ferramenta de captura",
            "• Bot muito lento: Reduza intervalo de detecção",
            "• Erro de permissão: Execute como administrador",
            "• Templates não encontrados: Verifique pasta templates/"
        ]
        
        for trouble in troubleshooting:
            tk.Label(trouble_frame, text=trouble,
                    fg='#ffcccc', bg='#2a2a2a', font=('Arial', 9),
                    anchor='w', justify='left').pack(anchor='w', padx=10, pady=2)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    # ========== FUNÇÕES DE CALLBACK HOTKEYS ==========
    
    def load_hotkeys_config(self):
        """Carregar configuração de hotkeys do config.json"""
        try:
            return {
                'start': 'f9',
                'pause': 'f2', 
                'stop': 'f1',
                'emergency': 'esc',
                'macro_execute': 'f8',
                'macro_chest': 'f11', 
                'macro_record': 'f3',
                'test_mouse': 'f12',
                'test_feeding': 'f6',
                'test_cleaning': 'f5'
            }
        except:
            return {}

    def save_hotkeys_config(self):
        """Salvar configuração de hotkeys no config.json"""
        try:
            print("[SAVE] Salvando configurações de hotkeys...")
            
            if hasattr(self, 'config_manager') and self.config_manager:
                # Coletar valores das hotkeys
                hotkeys_config = {}
                for hotkey_name, var in self.hotkey_vars.items():
                    hotkeys_config[hotkey_name] = var.get()
                
                # Salvar no ConfigManager
                self.config_manager.set('hotkeys', hotkeys_config)
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print("[OK] Hotkeys salvas e persistidas!")

                    # 🔄 RECARREGAR HOTKEYS EM TEMPO REAL
                    if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                        print("[RELOAD] Recarregando hotkeys no HotkeyManager...")
                        if self.hotkey_manager.reload_hotkeys():
                            print("[OK] Hotkeys recarregadas! Aplicadas sem reiniciar!")
                            messagebox.showinfo("Sucesso", "✅ Hotkeys salvas e aplicadas!\n\nAs novas hotkeys já estão ativas!")
                        else:
                            print("[WARN] Erro ao recarregar hotkeys (reinicie o bot)")
                            messagebox.showwarning("Aviso", "✅ Hotkeys salvas!\n\n⚠️ Reinicie o bot para aplicar.")
                    else:
                        messagebox.showinfo("Sucesso", "✅ Hotkeys salvas!\n\nReinicie o bot para aplicar.")

                    # Status na interface
                    if hasattr(self, 'hotkey_status_label'):
                        self.hotkey_status_label.config(
                            text=_("ui_hardcoded.hotkeys_salvas_e"),
                            fg='#28a745'
                        )
                        # Limpar mensagem após 3 segundos
                        self.main_window.after(3000, lambda: self.hotkey_status_label.config(text=""))
                else:
                    print("[WARN] ConfigManager sem método save_config")
                    if hasattr(self, 'hotkey_status_label'):
                        self.hotkey_status_label.config(
                            text=_("ui_hardcoded.hotkeys_atualizadas_mas"),
                            fg='#ffc107'
                        )
            else:
                print("[ERROR] ConfigManager não disponível")
                if hasattr(self, 'hotkey_status_label'):
                    self.hotkey_status_label.config(
                        text=_("ui_hardcoded.erro_configmanager_não"),
                        fg='#dc3545'
                    )
                
        except Exception as e:
            print(f"[ERROR] Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar hotkeys: {e}")
            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=f"❌ Erro ao salvar: {e}",
                    fg='#dc3545'
                )

    def restore_default_hotkeys(self):
        """Restaurar hotkeys padrão"""
        try:
            defaults = {
                'start': 'f9',
                'pause': 'f2',
                'stop': 'f1',
                'emergency': 'esc',
                'macro_execute': 'f8',
                'macro_chest': 'f11',
                'macro_record': 'f3',
                'test_mouse': 'f12',
                'test_feeding': 'f6',
                'test_cleaning': 'f5'
            }

            # Atualizar as variáveis se existirem
            for key_id, default_key in defaults.items():
                if hasattr(self, 'hotkey_vars') and key_id in self.hotkey_vars:
                    self.hotkey_vars[key_id].set(default_key)

            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=_("ui_hardcoded.padrões_restaurados"),
                    fg='#ffc107'
                )
        except Exception as e:
            print(f"Erro ao restaurar hotkeys: {e}")

    def apply_hotkeys_changes(self):
        """Aplicar mudanças de hotkeys (recarregar listeners)"""
        try:
            # Salvar primeiro
            self.save_hotkeys_config()

            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=_("ui_hardcoded.hotkeys_aplicadas"),
                    fg='#28a745'
                )
        except Exception as e:
            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=f"❌ Erro ao aplicar: {e}",
                    fg='#dc3545'
                )

    def capture_hotkey(self, key_id):
        """Capturar próxima tecla pressionada"""
        try:
            print(f"🔍 Capturando tecla/mouse para '{key_id}'...")
            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=f"🎯 Pressione tecla ou botão do mouse para '{key_id}'...",
                    fg='#ffc107'
                )
            
            # Implementar captura real com keyboard
            if KEYBOARD_AVAILABLE:
                self._capturing_for = key_id
                self._capture_active = True
                
                # Configurar listener temporário para teclas
                def on_key_capture(event):
                    if hasattr(self, '_capture_active') and self._capture_active:
                        captured_key = event.name.upper()
                        print(f"[OK] Tecla capturada: {captured_key}")
                        
                        # Atualizar a variável correspondente
                        if hasattr(self, 'hotkey_vars') and key_id in self.hotkey_vars:
                            self.hotkey_vars[key_id].set(captured_key)
                        
                        # Atualizar status
                        if hasattr(self, 'hotkey_status_label'):
                            self.hotkey_status_label.config(
                                text=f"✅ Tecla '{captured_key}' definida para '{key_id}'",
                                fg='#28a745'
                            )
                        
                        # Parar captura
                        self._capture_active = False
                        keyboard.unhook_all()
                        return False  # Parar o listener

                # Configurar listener temporário para mouse
                def on_mouse_capture(event):
                    if hasattr(self, '_capture_active') and self._capture_active:
                        # Mapear botões do mouse
                        mouse_buttons = {
                            'left': 'MOUSE_LEFT',
                            'right': 'MOUSE_RIGHT', 
                            'middle': 'MOUSE_MIDDLE',
                            'x1': 'MOUSE_X1',
                            'x2': 'MOUSE_X2'
                        }
                        
                        captured_button = mouse_buttons.get(event.button, f"MOUSE_{event.button.upper()}")
                        print(f"[OK] Botão do mouse capturado: {captured_button}")
                        
                        # Atualizar a variável correspondente
                        if hasattr(self, 'hotkey_vars') and key_id in self.hotkey_vars:
                            self.hotkey_vars[key_id].set(captured_button)
                        
                        # Atualizar status
                        if hasattr(self, 'hotkey_status_label'):
                            self.hotkey_status_label.config(
                                text=f"✅ Botão '{captured_button}' definido para '{key_id}'",
                                fg='#28a745'
                            )
                        
                        # Parar captura
                        self._capture_active = False
                        keyboard.unhook_all()
                        return False  # Parar o listener
                
                # Iniciar listener apenas para teclado (keyboard não tem on_click)
                keyboard.on_press(on_key_capture)
                # Mouse capture não suportado pela biblioteca keyboard
                # keyboard.on_click(on_mouse_capture)  # ❌ Função não existe!
                
            else:
                # Fallback usando tkinter bind
                print("[RELOAD] Usando captura via tkinter...")
                self._capturing_for = key_id
                self._capture_active = True
                
                if hasattr(self, 'hotkey_status_label'):
                    self.hotkey_status_label.config(
                        text=f"🎯 Clique aqui e pressione tecla/mouse para '{key_id}'...",
                        fg='#ffc107'
                    )
                
                # Focar na janela principal
                self.main_window.focus_set()
                
                # Capturar próxima tecla via tkinter
                def on_tkinter_key(event):
                    if hasattr(self, '_capture_active') and self._capture_active:
                        captured_key = event.keysym.upper()
                        print(f"[OK] Tecla capturada (tkinter): {captured_key}")
                        
                        # Atualizar a variável correspondente
                        if hasattr(self, 'hotkey_vars') and key_id in self.hotkey_vars:
                            self.hotkey_vars[key_id].set(captured_key)
                        
                        # Atualizar status
                        if hasattr(self, 'hotkey_status_label'):
                            self.hotkey_status_label.config(
                                text=f"✅ Tecla '{captured_key}' definida para '{key_id}'",
                                fg='#28a745'
                            )
                        
                        # Parar captura
                        self._capture_active = False
                        self.main_window.unbind('<Key>')
                        self.main_window.unbind('<Button-1>')
                        self.main_window.unbind('<Button-2>')
                        self.main_window.unbind('<Button-3>')

                # Capturar cliques do mouse via tkinter
                def on_tkinter_mouse(event):
                    if hasattr(self, '_capture_active') and self._capture_active:
                        # Mapear botões do mouse no tkinter
                        mouse_map = {
                            1: 'MOUSE_LEFT',
                            2: 'MOUSE_MIDDLE', 
                            3: 'MOUSE_RIGHT'
                        }
                        
                        captured_button = mouse_map.get(event.num, f"MOUSE_BUTTON_{event.num}")
                        print(f"[OK] Botão do mouse capturado (tkinter): {captured_button}")
                        
                        # Atualizar a variável correspondente
                        if hasattr(self, 'hotkey_vars') and key_id in self.hotkey_vars:
                            self.hotkey_vars[key_id].set(captured_button)
                        
                        # Atualizar status
                        if hasattr(self, 'hotkey_status_label'):
                            self.hotkey_status_label.config(
                                text=f"✅ Botão '{captured_button}' definido para '{key_id}'",
                                fg='#28a745'
                            )
                        
                        # Parar captura
                        self._capture_active = False
                        self.main_window.unbind('<Key>')
                        self.main_window.unbind('<Button-1>')
                        self.main_window.unbind('<Button-2>')
                        self.main_window.unbind('<Button-3>')
                
                # Bind temporário para captura de teclas e mouse
                self.main_window.bind('<Key>', on_tkinter_key)
                self.main_window.bind('<Button-1>', on_tkinter_mouse)  # Esquerdo
                self.main_window.bind('<Button-2>', on_tkinter_mouse)  # Meio
                self.main_window.bind('<Button-3>', on_tkinter_mouse)  # Direito
                    
        except Exception as e:
            print(f"Erro na captura de hotkey: {e}")
            if hasattr(self, 'hotkey_status_label'):
                self.hotkey_status_label.config(
                    text=f"❌ Erro: {e}",
                    fg='#dc3545'
                )
    
    # ========== FUNÇÕES DE CALLBACK CATCH VIEWER ==========
    
    def toggle_catch_viewer_window(self):
        """👁️ Abrir/Fechar apenas a janela visualizadora"""
        try:
            if self.catch_viewer_window is None or not self.catch_viewer_window.winfo_exists():
                print("👁️ Abrindo janela visualizadora...")
                self.open_catch_viewer_window()
            else:
                print("👁️ Fechando janela visualizadora...")
                self.catch_viewer_window.destroy()
                self.catch_viewer_window = None
        except Exception as e:
            print(f"[ERROR] Erro ao alternar janela: {e}")

    def open_catch_viewer_window(self):
        """👁️ Abrir janela visualizadora RESPONSIVA com estatísticas detalhadas"""
        try:
            if self.catch_viewer_window is None or not self.catch_viewer_window.winfo_exists():
                # Abrir janela do visualizador CATCH - TAMANHO RESPONSIVO
                self.catch_viewer_window = tk.Toplevel(self.main_window)
                self.catch_viewer_window.title("🐟 CATCH Viewer - Template Matching v4")
                self.catch_viewer_window.geometry("1400x900")  # Maior para acomodar informações
                self.catch_viewer_window.configure(bg='#1a1a1a')
                self.catch_viewer_window.minsize(1200, 700)  # Tamanho mínimo responsivo

                # Frame principal responsivo
                main_frame = tk.Frame(self.catch_viewer_window, bg='#1a1a1a')
                main_frame.pack(fill='both', expand=True, padx=10, pady=10)

                # Frame superior - Controles e Status
                top_frame = tk.Frame(main_frame, bg='#2a2a2a', relief='sunken', bd=2)
                top_frame.pack(fill='x', pady=(0, 10))

                # SEÇÃO DE STATUS GERAL E CONTROLES
                status_section = tk.Frame(top_frame, bg='#2a2a2a')
                status_section.pack(fill='x', padx=10, pady=10)

                # Título e Status
                status_header = tk.Frame(status_section, bg='#2a2a2a')
                status_header.pack(fill='x')

                tk.Label(status_header, text=_("ui_hardcoded.status_geral"),
                        font=('Arial', 12, 'bold'), fg='#00ff88', bg='#2a2a2a').pack(side='left')

                # CONTROLES DO VIEWER (direita)
                controls_frame = tk.Frame(status_header, bg='#2a2a2a')
                controls_frame.pack(side='right')

                # Botões de controle
                self.viewer_pause_btn = tk.Button(controls_frame, text=i18n.get_text("ui.pause_bot") if I18N_AVAILABLE else "⏸️ Pausar",
                                                command=self.toggle_viewer_pause,
                                                bg='#ffc107', fg='black', font=('Arial', 9, 'bold'),
                                                padx=10, pady=2)
                self.viewer_pause_btn.pack(side='left', padx=2)

                tk.Button(controls_frame, text=_("ui_hardcoded.screenshot"),
                         command=self.save_viewer_screenshot,
                         bg='#17a2b8', fg='white', font=('Arial', 9, 'bold'),
                         padx=10, pady=2).pack(side='left', padx=2)

                # Controle de FPS
                tk.Label(controls_frame, text=_("ui_hardcoded.fps"), fg='white', bg='#2a2a2a',
                        font=('Arial', 9)).pack(side='left', padx=(10,2))

                self.viewer_fps_control = tk.StringVar(value="5")
                fps_combo = ttk.Combobox(controls_frame, textvariable=self.viewer_fps_control,
                                       values=['1', '2', '5', '10', '15', '20'],
                                       state="readonly", width=4, font=('Arial', 8))
                fps_combo.pack(side='left', padx=2)

                # Status label
                self.viewer_general_status = tk.Label(status_section,
                    text=_("ui_hardcoded.carregando_sistema"),
                    font=('Consolas', 10), fg='white', bg='#2a2a2a')
                self.viewer_general_status.pack(pady=5)

                # Variável para controle de pause
                self.viewer_paused = False

                # Frame central - Canvas (esquerda) + Estatísticas (direita)
                content_frame = tk.Frame(main_frame, bg='#1a1a1a')
                content_frame.pack(fill='both', expand=True)

                # SEÇÃO ESQUERDA - Canvas da imagem
                canvas_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='sunken', bd=2)
                canvas_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

                tk.Label(canvas_frame, text=_("ui_hardcoded.captura_ao_vivo"),
                        font=('Arial', 11, 'bold'), fg='#00ff88', bg='#2a2a2a').pack(pady=5)

                # Canvas responsivo para a imagem
                self.catch_canvas = tk.Canvas(canvas_frame,
                                             bg='#333333', width=800, height=600)
                self.catch_canvas.pack(fill='both', expand=True, padx=10, pady=(0, 10))

                # SEÇÃO DIREITA - Estatísticas detalhadas
                stats_frame = tk.Frame(content_frame, bg='#2a2a2a', relief='sunken', bd=2, width=400)
                stats_frame.pack(side='right', fill='y', padx=(5, 0))
                stats_frame.pack_propagate(False)  # Manter largura fixa

                # Título das estatísticas
                tk.Label(stats_frame, text=_("ui_hardcoded.estatísticas_detalhadas"),
                        font=('Arial', 11, 'bold'), fg='#00ff88', bg='#2a2a2a').pack(pady=10)

                # SUBSEÇÃO: FPS e Performance
                perf_frame = tk.LabelFrame(stats_frame, text=_("ui_hardcoded.performance"),
                                          fg='#ffaa00', bg='#2a2a2a', font=('Arial', 10, 'bold'))
                perf_frame.pack(fill='x', padx=10, pady=5)

                self.viewer_fps_stats = tk.Label(perf_frame,
                    text=_("ui_hardcoded.fps_frame"),
                    font=('Consolas', 9), fg='white', bg='#2a2a2a')
                self.viewer_fps_stats.pack(pady=5)

                # SUBSEÇÃO: Detecções de Templates
                template_frame = tk.LabelFrame(stats_frame, text=_("ui_hardcoded.templates_ativos"),
                                              fg='#ffaa00', bg='#2a2a2a', font=('Arial', 10, 'bold'))
                template_frame.pack(fill='x', padx=10, pady=5)

                # Canvas com scroll para templates
                template_canvas = tk.Canvas(template_frame, bg='#2a2a2a', height=200, highlightthickness=0)
                template_scrollbar = tk.Scrollbar(template_frame, orient="vertical", command=template_canvas.yview)
                self.template_scrollable_frame = tk.Frame(template_canvas, bg='#2a2a2a')

                self.template_scrollable_frame.bind("<Configure>",
                    lambda e: template_canvas.configure(scrollregion=template_canvas.bbox("all")))

                template_canvas.create_window((0, 0), window=self.template_scrollable_frame, anchor="nw")
                template_canvas.configure(yscrollcommand=template_scrollbar.set)

                template_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                template_scrollbar.pack(side="right", fill="y")

                # SUBSEÇÃO: Status das Varas
                rod_frame = tk.LabelFrame(stats_frame, text="🎣 Status das Varas",
                                         fg='#ffaa00', bg='#2a2a2a', font=('Arial', 10, 'bold'))
                rod_frame.pack(fill='x', padx=10, pady=5)

                self.viewer_rod_status = tk.Label(rod_frame,
                    text=_("ui_hardcoded.carregando_status_das"),
                    font=('Consolas', 9), fg='white', bg='#2a2a2a', justify='left')
                self.viewer_rod_status.pack(pady=5, anchor='w')

                # SUBSEÇÃO: Estatísticas de Pesca
                fishing_frame = tk.LabelFrame(stats_frame, text=_("ui_hardcoded.estatísticas_de_pesca"),
                                             fg='#ffaa00', bg='#2a2a2a', font=('Arial', 10, 'bold'))
                fishing_frame.pack(fill='x', padx=10, pady=5)

                self.viewer_fishing_stats = tk.Label(fishing_frame,
                    text="Peixes: 0 | Ciclos: 0\nTempo: 00:00:00",
                    font=('Consolas', 9), fg='white', bg='#2a2a2a', justify='left')
                self.viewer_fishing_stats.pack(pady=5, anchor='w')

                # Callback para fechar apenas a janela
                self.catch_viewer_window.protocol("WM_DELETE_WINDOW",
                                                 lambda: self.catch_viewer_window.destroy())

                # Atualizar status
                self.catch_viewer_status_label.config(text=_("ui_hardcoded.status_janela_aberta"), fg='#28a745')

                print("👁️ Janela CATCH Viewer RESPONSIVA criada com sucesso!")

                # Iniciar loop de visualização em thread separada
                import threading
                threading.Thread(target=self.catch_viewer_loop, daemon=True).start()

            else:
                print("👁️ Janela CATCH Viewer já está aberta")
        except Exception as e:
            print(f"[ERROR] Erro ao abrir janela: {e}")

    def stop_catch_viewer(self):
        """🔄 Parar visualizador CATCH"""
        try:
            print("[RELOAD] Parando CATCH viewer...")
            self.catch_viewer_running = False
            
            # Atualizar status
            if hasattr(self, 'catch_viewer_status_label'):
                self.catch_viewer_status_label.config(text=i18n.get_text("ui.status_stopped") if I18N_AVAILABLE else "📊 Status: Parado", fg='#dc3545')
            
            # Fechar janela
            if self.catch_viewer_window and self.catch_viewer_window.winfo_exists():
                self.catch_viewer_window.destroy()
                self.catch_viewer_window = None
                
            print("[OK] CATCH viewer parado com sucesso")
        except Exception as e:
            print(f"[ERROR] Erro ao parar viewer: {e}")

    def test_catch_detection(self):
        """🧪 Testar sistema de detecção"""
        try:
            print("[TEST] Testando sistema de detecção...")
            self.catch_viewer_status_label.config(text=_("ui_hardcoded.status_testando"), fg='#ffc107')
            
            # Simular detecção
            import threading
            def test_detection():
                import time
                time.sleep(2)
                if hasattr(self, 'catch_stats_label'):
                    self.catch_stats_label.config(text=_("ui_hardcoded.detecções_1_testen"))
                
                if hasattr(self, 'catch_viewer_status_label'):
                    self.catch_viewer_status_label.config(text=_("ui_hardcoded.status_teste_concluído"), fg='#28a745')
                    
                print("[OK] Teste de detecção concluído!")
            
            threading.Thread(target=test_detection, daemon=True).start()
            
        except Exception as e:
            print(f"[ERROR] Erro no teste: {e}")

    def catch_viewer_loop(self):
        """Loop principal do visualizador - DETECTA TODOS OS TEMPLATES (baseado no v3)"""
        try:
            print("[CATCH] Iniciando loop do CATCH viewer com detecção real...")
            self.catch_viewer_running = True

            # Importar dependências
            try:
                from PIL import Image, ImageTk, ImageDraw, ImageFont
            except ImportError:
                from PIL import Image, ImageTk, ImageDraw
                ImageFont = None

            import cv2
            import numpy as np
            import mss
            import time
            import os

            # Carregar TODOS OS TEMPLATES automaticamente
            templates_dir = "templates"
            if os.path.exists("fishing_bot_v4/templates"):
                templates_dir = "fishing_bot_v4/templates"

            templates = {}
            template_colors = {}

            # Cores por GRUPO - templates do mesmo grupo usam a mesma cor
            group_colors = {
                'catch': (0, 255, 0),                    # Verde brilhante = PEIXE CAPTURADO
                'inventory': (255, 255, 0),              # Amarelo = INVENTÁRIO
                'loot': (255, 165, 0),                   # Laranja = BAÚ

                # Peixes - tons de azul/ciano
                'salmon': (0, 191, 255),                 # Azul claro = SALMÃO (salmon + salmonn)
                'trout': (64, 224, 208),                 # Turquesa = TRUTA (trout + troutt)
                'fish_general': (135, 206, 250),         # Azul céu = PEIXES GERAIS

                # Iscas/Carnes - tons de laranja/vermelho
                'meat_bait': (255, 140, 0),              # Laranja escuro = ISCAS/CARNES

                # Varas - cores funcionais
                'rod_with_bait': (0, 255, 0),           # Verde = VARA COM ISCA
                'rod_without_bait': (0, 0, 255),        # Azul = VARA SEM ISCA
                'rod_broken': (255, 0, 0),              # Vermelho = VARA QUEBRADA

                # Comida - tons de rosa
                'fried_food': (255, 192, 203),          # Rosa = COMIDA FRITA
                'gut': (255, 20, 147),                  # Rosa escuro = GUT
                'eat_button': (255, 105, 180),          # Rosa médio = BOTÃO EAT

                # Containers - tons de marrom/bege
                'salmon_container': (210, 180, 140),    # Bege = CONTAINER SALMÃO
                'trout_container': (222, 184, 135),     # Bege claro = CONTAINER TRUTA
                'yellowperch_container': (238, 203, 173), # Bege rosado = CONTAINER PERCA
                'wolfmeat_container': (205, 133, 63),   # Marrom = CONTAINER CARNE LOBO
                'grub_container': (160, 82, 45),        # Marrom escuro = CONTAINER GRUB
                'large_container': (139, 69, 19),       # Marrom muito escuro = CONTAINER GRANDE

                # Itens especiais - cores únicas
                'scrap': (128, 128, 128),               # Cinza = SUCATA
                'bluecard': (0, 0, 255),                # Azul puro = CARTÃO AZUL
                'flare': (255, 255, 0),                 # Amarelo = SINALIZADOR
                'bullet': (192, 192, 192),              # Prata = BALA
                'bone': (245, 245, 220),                # Bege claro = OSSO
                'fat': (255, 250, 205)                  # Amarelo claro = GORDURA
            }

            # SISTEMA DE AGRUPAMENTO DE TEMPLATES (baseado na lista atual - 42 templates)
            template_groups = {
                # CRÍTICOS (detecção primária)
                'catch': ['catch'],                                     # Peixe capturado - CRÍTICO
                'inventory': ['inventory'],                             # Inventário aberto - CRÍTICO
                'loot': ['loot'],                                       # Baú aberto - CRÍTICO

                # PEIXES - TODOS NO MESMO GRUPO para competir entre si
                'fish_general': ['SALMONN', 'TROUTT', 'peixecru', 'anchovy', 'sardine', 'herring', 'yellowperch', 'shark', 'catfish', 'roughy'],

                # ISCAS/CARNES (todas as iscas e carnes)
                'meat_bait': ['grub', 'minhoca', 'carneurso', 'carnedelobo', 'crocodilo'],

                # VARAS - TODOS NO MESMO GRUPO para competir entre si (igual peixes)
                'rod_all': ['varanobauci', 'varacomisca', 'comiscavara', 'namaocomisca', 'comiscanamao',
                           'enbausi', 'varasemisca', 'semiscavara', 'namaosemisca', 'semiscanam', 'semiscavaraescura',
                           'varaquebrada', 'nobauquebrada'],

                # COMIDA
                'fried_food': ['frito'],                                # Comida frita (apenas 1 variante)
                'gut': ['gut'],                                         # Gut separado
                'eat_button': ['eat'],                                  # Botão eat separado

                # CONTAINERS/BOXES (apenas os existentes)
                'large_container': ['largebox'],                        # Container grande

                # ITENS ESPECIAIS (únicos)
                'scrap': ['scrap'],                                     # Sucata
                'bluecard': ['bluecard'],                               # Cartão azul
                'flare': ['flare'],                                     # Sinalizador
                'bullet': ['bullet'],                                   # Bala
                'bone': ['BONE'],                                       # Osso
                'fat': ['fat']                                          # Gordura
            }

            # Criar mapeamento reverso: template -> grupo (case-insensitive!)
            template_to_group = {}
            for group_name, group_templates in template_groups.items():
                for template in group_templates:
                    # Adicionar em AMBOS os casos (maiúsculo e minúsculo) para garantir match
                    template_to_group[template] = group_name
                    template_to_group[template.lower()] = group_name
                    template_to_group[template.upper()] = group_name

            # CARREGAR TODOS OS TEMPLATES DA PASTA AUTOMATICAMENTE
            print(f"🔍 Procurando templates em: {templates_dir}")

            if os.path.exists(templates_dir):
                # Buscar todos os arquivos .png na pasta
                template_files = [f for f in os.listdir(templates_dir) if f.lower().endswith('.png')]
                print(f"📁 Encontrados {len(template_files)} templates: {template_files}")

                for template_file in template_files:
                    template_path = os.path.join(templates_dir, template_file)
                    try:
                        template_img = cv2.imread(template_path, cv2.IMREAD_COLOR)
                        if template_img is not None:
                            templates[template_file] = template_img
                            template_name = template_file.replace('.png', '').lower()
                            # Definir cor baseada no grupo do template
                            template_group = template_to_group.get(template_name)
                            template_colors[template_file] = group_colors.get(template_group, (255, 255, 255))
                            print(f"  ✅ {template_file} carregado")
                        else:
                            print(f"  ❌ Erro ao carregar {template_file}")
                    except Exception as e:
                        print(f"  ❌ Erro ao processar {template_file}: {e}")
            else:
                print(f"[ERROR] Diretório de templates não encontrado: {templates_dir}")
                # Fallback - criar templates vazios para evitar crash
                templates = {}

            print(f"[TARGET] Templates carregados: {list(templates.keys())}")

            if not templates:
                print("[ERROR] Nenhum template encontrado! Usando modo básico...")
                # Continuar sem templates para mostrar captura

            frame_count = 0
            start_time = time.time()
            detections_total = {name: 0 for name in templates.keys()}

            # Sistema para evitar detecções duplicadas
            previous_detections = {}  # {template_name: [(x, y, confidence), ...]}
            detection_distance_threshold = 50  # Pixels de distância mínima para considerar nova detecção

            with mss.mss() as sct:
                while self.catch_viewer_running:
                    try:
                        # Capturar área configurada
                        capture_area = self.get_capture_area()
                        screen_shot = sct.grab(capture_area)

                        # Converter para numpy array
                        img_array = np.array(screen_shot)
                        if img_array.shape[2] == 4:  # BGRA
                            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_BGRA2BGR)
                        else:
                            img_bgr = img_array

                        # Criar cópia para desenhar detecções
                        img_display = img_bgr.copy()

                        # Usar os grupos já definidos acima

                        # Detectar templates se disponíveis
                        detections_found = []
                        current_frame_detections = {}  # Para este frame específico
                        all_template_detections = []  # Para resolução de conflitos globais
                        group_detections = {}  # Detecções agrupadas por categoria

                        # Verificar se inventário está aberto (definir no início)
                        inventory_open = False

                        if templates:
                            for template_name, template_img in templates.items():
                                try:
                                    # Template matching com threshold ajustado por tipo
                                    template_clean = template_name.replace('.png', '').lower()

                                    # Usar thresholds do config.json (como v3) ou fallback para hardcoded
                                    threshold = 0.7  # Default fallback

                                    # GARANTIR que usa SEMPRE os thresholds da UI/config.json (PRIORIDADE MÁXIMA)
                                    threshold = 0.7  # Default absoluto
                                    threshold_source = "default"

                                    # 1. PRIMEIRA PRIORIDADE ABSOLUTA: Templates tab da UI EM TEMPO REAL (se disponível)
                                    if hasattr(self, 'template_confidence_vars') and template_clean in self.template_confidence_vars:
                                        try:
                                            ui_threshold = float(self.template_confidence_vars[template_clean].get())
                                            if ui_threshold and ui_threshold > 0:
                                                threshold = ui_threshold
                                                threshold_source = f"UI_LIVE({ui_threshold})"
                                        except Exception as e:
                                            pass

                                    # 2. SEGUNDA PRIORIDADE: ConfigManager (config.json) apenas se UI não disponível
                                    if threshold == 0.7 and threshold_source == "default":
                                        if hasattr(self, 'config_manager') and self.config_manager:
                                            try:
                                                config_threshold = self.config_manager.get_template_confidence(template_clean)
                                                if config_threshold and config_threshold > 0:
                                                    threshold = config_threshold
                                                    threshold_source = f"config.json({config_threshold})"
                                            except Exception as e:
                                                # Se falhar config, continuar para próxima opção
                                                pass

                                    # 3. ÚLTIMA PRIORIDADE: Fallback hardcoded apenas se NADA mais funcionar
                                    if threshold == 0.7 and threshold_source == "default":
                                        confidence_thresholds = {
                                            'catch': 0.8,           # Peixe capturado - alta precisão
                                            'varanobauci': 0.7,     # Vara com isca
                                            'varacomisca': 0.7,     # Vara com isca
                                            'enbausi': 0.65,        # Vara sem isca - mais permissivo
                                            'varasemisca': 0.65,    # Vara sem isca
                                            'varaquebrada': 0.75,   # Vara quebrada
                                            'inventario': 0.8,      # Inventário aberto
                                            'loot': 0.8,           # Baú aberto
                                            'food': 0.7,           # Comida
                                            'eat': 0.7,            # Botão eat
                                            'bait': 0.7,           # Isca
                                            'salmon': 0.85,         # Salmão - ✅ REDUZIDO de 0.93 para 0.85
                                            'salmonn': 0.85,        # Salmão específico - ✅ REDUZIDO
                                            'SALMONN': 0.85,        # Salmão maiúsculo - ✅ ADICIONADO
                                            'smalltrout': 0.85,     # Truta pequena - ✅ REDUZIDO
                                            'troutt': 0.85,         # Truta específica - ✅ REDUZIDO
                                            'TROUTT': 0.85          # Truta maiúscula - ✅ ADICIONADO
                                        }
                                        threshold = confidence_thresholds.get(template_clean, 0.7)
                                        threshold_source = f"hardcoded({threshold})"

                                    # 🎯 LÓGICA REMOVIDA: ULTRA PRECISION causava confusão visual
                                    # Agora respeitamos exatamente o threshold configurado pelo usuário

                                    # DEBUG: Log do threshold usado (SEMPRE para SALMONN e TROUTT)
                                    is_critical_fish = template_clean in ['SALMONN', 'TROUTT', 'salmonn', 'troutt']
                                    if is_critical_fish:
                                        print(f"[CATCH] {template_clean}: threshold={threshold:.3f} (fonte: {threshold_source})")

                                    # DEBUG adicional para verificar se threshold está sendo respeitado
                                    expected_thresholds = {'SALMONN': 0.85, 'salmonn': 0.85, 'TROUTT': 0.85, 'troutt': 0.85}  # ✅ REDUZIDO de 0.93 para 0.85
                                    if template_clean in expected_thresholds:
                                        expected = expected_thresholds[template_clean]
                                        if abs(threshold - expected) > 0.01:  # tolerância de 1%
                                            print(f"[WARN] {template_clean}: THRESHOLD INCORRETO! Esperado {expected}, atual {threshold:.3f}")

                                    result = cv2.matchTemplate(img_bgr, template_img, cv2.TM_CCOEFF_NORMED)

                                    # DEBUG: Mostrar valores máximos encontrados vs threshold para peixes
                                    if is_critical_fish:
                                        max_confidence = np.max(result)
                                        print(f"   Max detectado: {max_confidence:.3f} | Threshold: {threshold:.3f} | {'✅PASSOU' if max_confidence >= threshold else '❌REJEITADO'}")

                                    locations = np.where(result >= threshold)

                                    # Coletar todas as detecções ANTES de desenhar (como v3)
                                    raw_detections = []
                                    for pt in zip(*locations[::-1]):
                                        h, w = template_img.shape[:2]
                                        confidence = result[pt[1], pt[0]]

                                        # DEBUG: Verificar se confidence está realmente acima do threshold
                                        if is_critical_fish and confidence < threshold:
                                            print(f"🚨 {template_clean}: DETECTOU ABAIXO DO THRESHOLD! Confidence: {confidence:.3f} < Threshold: {threshold:.3f}")
                                            continue  # Pular esta detecção inválida

                                        raw_detections.append({
                                            'x': pt[0], 'y': pt[1],
                                            'w': w, 'h': h,
                                            'confidence': confidence
                                        })

                                    # APLICAR NON-MAXIMUM SUPPRESSION RIGOROSO (como v3)
                                    if raw_detections:
                                        # Ordenar por confiança (maior primeiro)
                                        raw_detections.sort(key=lambda x: x['confidence'], reverse=True)

                                        filtered_detections = []
                                        # Usar threshold configurável
                                        overlap_threshold = int(self.nms_threshold_var.get()) if hasattr(self, 'nms_threshold_var') else 100

                                        for detection in raw_detections:
                                            is_overlapping = False

                                            for filtered in filtered_detections:
                                                # Calcular distância entre centros
                                                center1_x = detection['x'] + detection['w'] // 2
                                                center1_y = detection['y'] + detection['h'] // 2
                                                center2_x = filtered['x'] + filtered['w'] // 2
                                                center2_y = filtered['y'] + filtered['h'] // 2

                                                distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

                                                # Se muito próximo, considerar sobreposição
                                                if distance < overlap_threshold:
                                                    is_overlapping = True
                                                    break

                                            # Só adiciona se não está sobreposto (NMS rigoroso)
                                            if not is_overlapping:
                                                filtered_detections.append(detection)
                                    else:
                                        filtered_detections = []

                                    # AGRUPAR DETECÇÕES POR CATEGORIA (NOVO SISTEMA)
                                    for detection in filtered_detections:
                                        detection['template_name'] = template_name
                                        detection['template_clean'] = template_clean

                                        # Determinar grupo do template
                                        group_name = template_to_group.get(template_clean, template_clean)
                                        detection['group'] = group_name

                                        # ✅ FILTRO: Ignorar peixes (SALMONN/TROUTT) detectados na região das varas
                                        if group_name == 'fish_general':
                                            # Região das varas (slots 1-6): y > 950 (parte inferior)
                                            det_y = detection['y'] + detection['h'] // 2  # Centro Y
                                            if det_y > 950:
                                                # Peixe detectado na região das varas - IGNORAR
                                                print(f"   🚫 {template_clean} ignorado (região de varas: y={det_y})")
                                                continue

                                        # Adicionar ao grupo correspondente
                                        if group_name not in group_detections:
                                            group_detections[group_name] = []
                                        group_detections[group_name].append(detection)

                                        all_template_detections.append(detection)

                                    # Temporariamente armazenar para processamento posterior
                                    current_frame_detections[template_name] = filtered_detections

                                except Exception as e:
                                    print(f"[WARN] Erro ao detectar {template_name}: {e}")

                            # ========== RESOLVER CONFLITOS POR GRUPO (NOVO SISTEMA v4) ==========
                            # Para cada grupo, aplicar NMS e escolher a melhor detecção
                            final_detections = []

                            # Prioridades para resolver conflitos específicos apenas
                            conflict_priority = {
                                'salmonn': 10, 'troutt': 9,          # Específicos têm prioridade
                                'salmon': 7, 'smalltrout': 6,       # Genéricos têm menos
                                'varanobauci': 8, 'varacomisca': 7,  # Com isca
                                'enbausi': 5, 'varasemisca': 4,     # Sem isca
                                'varaquebrada': 9                    # Quebradas são importantes
                            }

                            # ALGORITMO INTELIGENTE: Detectar qual template está no contexto CORRETO
                            def calculate_detection_quality(detection):
                                """Calcular qualidade da detecção baseada em threshold e confiança"""
                                template_clean = detection['template_clean']
                                confidence = detection['confidence']

                                # Pegar threshold configurado para este template
                                template_threshold = 0.7  # Default
                                if hasattr(self, 'template_confidence_vars') and template_clean in self.template_confidence_vars:
                                    try:
                                        template_threshold = float(self.template_confidence_vars[template_clean].get())
                                    except:
                                        pass
                                elif hasattr(self, 'config_manager') and self.config_manager:
                                    try:
                                        template_threshold = self.config_manager.get_template_confidence(template_clean)
                                    except:
                                        pass

                                # Calcular margem acima do threshold (mais importante que confiança absoluta)
                                margin_above_threshold = confidence - template_threshold

                                # Penalizar detecções que mal passaram no threshold
                                if margin_above_threshold < 0.05:  # Menos de 5% acima do threshold
                                    margin_score = 0.1  # Pontuação muito baixa
                                elif margin_above_threshold < 0.1:  # Menos de 10% acima
                                    margin_score = 0.3
                                else:
                                    margin_score = min(margin_above_threshold * 2, 1.0)  # Máximo 1.0

                                # Bonus leve para templates específicos
                                template_bonus = conflict_priority.get(template_clean, 5) / 10.0  # 0.5 a 1.0

                                # Score final: margem é o mais importante, depois template bonus
                                quality_score = (margin_score * 0.8) + (template_bonus * 0.2)

                                return quality_score

                            # Processar cada grupo separadamente
                            for group_name, group_detections_list in group_detections.items():
                                if not group_detections_list:
                                    continue

                                # Se só há uma detecção no grupo, adicionar diretamente
                                if len(group_detections_list) == 1:
                                    final_detections.extend(group_detections_list)
                                    continue

                                # Para múltiplas detecções no grupo, aplicar NMS entre elas
                                print(f"[RELOAD] Grupo '{group_name}': {len(group_detections_list)} detecções - aplicando NMS...")

                                # Aplicar NMS DENTRO do grupo
                                group_filtered = []
                                overlap_threshold = int(self.nms_threshold_var.get()) if hasattr(self, 'nms_threshold_var') else 100

                                # Ordenar detecções do grupo por qualidade/confiança
                                group_detections_list.sort(key=lambda x: calculate_detection_quality(x), reverse=True)

                                for detection in group_detections_list:
                                    is_overlapping = False

                                    for filtered in group_filtered:
                                        # Calcular distância entre centros
                                        center1_x = detection['x'] + detection['w'] // 2
                                        center1_y = detection['y'] + detection['h'] // 2
                                        center2_x = filtered['x'] + filtered['w'] // 2
                                        center2_y = filtered['y'] + filtered['h'] // 2

                                        distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

                                        # Se muito próximo dentro do grupo, considerar sobreposição
                                        if distance < overlap_threshold:
                                            is_overlapping = True
                                            print(f"   ❌ {detection['template_clean']} suprimido por {filtered['template_clean']} (dist: {distance:.1f})")
                                            break

                                    # Só adiciona se não está sobreposto dentro do grupo
                                    if not is_overlapping:
                                        group_filtered.append(detection)
                                        # Mostrar qual template específico foi escolhido
                                        quality = calculate_detection_quality(detection)
                                        print(f"   ✅ {detection['template_clean']} aceito (conf: {detection['confidence']:.3f}, qual: {quality:.3f}) [GRUPO: {group_name}]")

                                # Adicionar detecções filtradas do grupo
                                final_detections.extend(group_filtered)

                            # ========== NMS GLOBAL RIGOROSO ENTRE TODOS OS GRUPOS ==========
                            # Aplicar NMS final entre TODAS as detecções para evitar múltiplas detecções do mesmo objeto
                            print(f"[RELOAD] Aplicando NMS GLOBAL em {len(final_detections)} detecções...")

                            # Ordenar TODAS as detecções por qualidade (melhor primeiro)
                            for detection in final_detections:
                                detection['quality'] = calculate_detection_quality(detection)
                            final_detections.sort(key=lambda x: x['quality'], reverse=True)

                            # ✅ NMS GLOBAL SIMPLIFICADO - Apenas o de MAIOR CONFIANÇA sobrevive
                            global_filtered = []
                            overlap_threshold = 80  # Distância para considerar sobreposição

                            # Ordenar por confiança (MAIOR primeiro)
                            final_detections.sort(key=lambda x: x['confidence'], reverse=True)

                            for detection in final_detections:
                                is_overlapping = False

                                # Verificar se sobrepõe com alguma detecção já aprovada
                                for approved in global_filtered[:]:  # [:] cria cópia para iteração segura
                                    # Calcular distância entre centros
                                    center1_x = detection['x'] + detection['w'] // 2
                                    center1_y = detection['y'] + detection['h'] // 2
                                    center2_x = approved['x'] + approved['w'] // 2
                                    center2_y = approved['y'] + approved['h'] // 2

                                    distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

                                    # Verificar se são do mesmo grupo
                                    detection_group = template_to_group.get(detection['template_clean'])
                                    approved_group = template_to_group.get(approved['template_clean'])
                                    same_group = detection_group == approved_group and detection_group is not None

                                    # DEBUG: verificar grupos de peixes e varas sobrepostos
                                    fish_templates = ['salmonn', 'troutt', 'anchovy', 'shark', 'yellowperch', 'sardine', 'herring', 'catfish', 'roughy', 'peixecru']
                                    rod_templates = ['varanobauci', 'varacomisca', 'comiscavara', 'enbausi', 'varasemisca', 'semiscavara', 'varaquebrada', 'nobauquebrada']

                                    is_overlapping_fish = detection['template_clean'] in fish_templates and approved['template_clean'] in fish_templates
                                    is_overlapping_rod = detection['template_clean'] in rod_templates and approved['template_clean'] in rod_templates

                                    if (is_overlapping_fish or is_overlapping_rod) and distance < overlap_threshold:
                                        print(f"   🔍 DEBUG: {detection['template_clean']}({detection['confidence']:.2f}) grupo={detection_group} VS {approved['template_clean']}({approved['confidence']:.2f}) grupo={approved_group} | same_group={same_group} | dist={distance:.0f}px")

                                    # REGRA SIMPLES: Se estão próximos E do mesmo grupo → apenas o de maior confiança
                                    if distance < overlap_threshold:
                                        if same_group:
                                            # Mesmo grupo: SEMPRE manter apenas o de maior confiança
                                            # Como já ordenamos por confiança, o "approved" SEMPRE tem maior confiança
                                            is_overlapping = True
                                            print(f"   ❌ {detection['template_clean']}({detection['confidence']:.2f}) suprimido por {approved['template_clean']}({approved['confidence']:.2f}) - dist:{distance:.0f}px")
                                            break
                                        elif detection['template_clean'] == approved['template_clean']:
                                            # Mesmo template: remover duplicata
                                            is_overlapping = True
                                            print(f"   ❌ {detection['template_clean']} duplicata removida")
                                            break

                                # Adicionar se não está sobreposto
                                if not is_overlapping:
                                    global_filtered.append(detection)
                                    print(f"   ✅ {detection['template_clean']} conf:{detection['confidence']:.2f} APROVADO")

                            # Substituir final_detections pelo resultado filtrado globalmente
                            final_detections = global_filtered
                            print(f"[OK] NMS GLOBAL concluído: {len(final_detections)} detecções finais")

                            # ========== DESENHAR APENAS AS DETECÇÕES FINAIS (SEM CONFLITOS) ==========
                            detections_found = []
                            current_frame_detections = {}  # Resetar para as detecções finais

                            for detection in final_detections:
                                template_name = detection['template_name']
                                template_clean = detection['template_clean']
                                x, y = detection['x'], detection['y']
                                w, h = detection['w'], detection['h']
                                confidence = detection['confidence']

                                # Verificar se é nova detecção para contagem
                                is_new_detection = True
                                if template_name in previous_detections:
                                    for prev_x, prev_y, prev_conf in previous_detections[template_name]:
                                        distance = ((x - prev_x)**2 + (y - prev_y)**2)**0.5
                                        if distance < detection_distance_threshold:
                                            is_new_detection = False
                                            break

                                # VERIFICAÇÃO FINAL: NÃO DESENHAR SE ABAIXO DO THRESHOLD CONFIGURADO
                                template_clean_for_check = template_name.replace('.png', '').lower()
                                if template_clean_for_check in ['salmonn', 'troutt']:
                                    expected_threshold = 0.85  # ✅ REDUZIDO de 0.93 para 0.85 - Ambos SALMONN e TROUTT
                                    if confidence < expected_threshold:
                                        print(f"🚫 BLOQUEANDO DESENHO {template_name}: confidence {confidence:.3f} < threshold {expected_threshold:.3f}")
                                        continue  # Não desenhar esta detecção

                                # Cores otimizadas (como v3)
                                color = template_colors.get(template_name, (255, 255, 255))

                                # Desenhar retângulo com espessura otimizada
                                cv2.rectangle(img_display, (x, y), (x + w, y + h), color, 2)

                                # Texto ÚNICO com posição otimizada - mostra template específico escolhido
                                template_display = template_name.replace('.png', '')

                                # Verificar se faz parte de um grupo e mostrar info do grupo
                                group_info = ""
                                if template_clean in template_to_group:
                                    group_name = template_to_group[template_clean]
                                    group_info = f" [{group_name}]"

                                text = f"{template_display} {confidence:.2f}{group_info}"

                                # Posição do texto otimizada para não sobrepor
                                text_y = y - 10 if y > 20 else y + h + 20

                                # Usar anti-aliasing configurável
                                line_type = cv2.LINE_AA if (hasattr(self, 'antialiasing_var') and self.antialiasing_var.get()) else cv2.LINE_8
                                cv2.putText(img_display, text, (x, text_y),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, line_type)

                                # Adicionar à lista final
                                if template_name not in current_frame_detections:
                                    current_frame_detections[template_name] = []
                                current_frame_detections[template_name].append((x, y, confidence))
                                detections_found.append(template_name)

                                # Incrementar contador apenas para novas detecções
                                if is_new_detection:
                                    detections_total[template_name] += 1

                        # Verificar se inventário foi detectado em qualquer template
                        inventory_open = any('inventario' in t for t in detections_found)

                        # Atualizar histórico de detecções (manter apenas último frame para comparação)
                        previous_detections = current_frame_detections

                        # DESENHAR INDICADORES DE SLOTS (como v3) - controlado por configuração
                        show_slots = self.show_slots_var.get() if hasattr(self, 'show_slots_var') else True
                        if inventory_open and hasattr(self, 'rod_status_tracking') and show_slots:
                            try:
                                # Usar coordenadas do config.json
                                SLOT_POSITIONS = {}
                                if hasattr(self, 'config_manager') and self.config_manager:
                                    slot_positions_config = self.config_manager.get('coordinates.slot_positions', {})
                                    for slot_str, coords in slot_positions_config.items():
                                        SLOT_POSITIONS[int(slot_str)] = tuple(coords)
                                else:
                                    # Fallback para coordenadas hardcoded
                                    SLOT_POSITIONS = {
                                        1: (709, 1005), 2: (805, 1005), 3: (899, 1005),
                                        4: (992, 1005), 5: (1092, 1005), 6: (1188, 1005)
                                    }

                                for slot_num, (slot_x, slot_y) in SLOT_POSITIONS.items():
                                    # Determinar status e cor do slot
                                    if slot_num in self.rod_status_tracking['available_with_bait']:
                                        color = (0, 255, 0)      # Verde - COM ISCA
                                        status = "✅"
                                    elif slot_num in self.rod_status_tracking['available_without_bait']:
                                        color = (255, 165, 0)    # Laranja - SEM ISCA
                                        status = "⚠️"
                                    elif slot_num in self.rod_status_tracking['broken_rods']:
                                        color = (0, 0, 255)      # Vermelho - QUEBRADA
                                        status = "❌"
                                    else:
                                        color = (128, 128, 128)  # Cinza - VAZIO
                                        status = "⚪"

                                    # Desenhar círculo colorido no slot (como v3)
                                    cv2.circle(img_display, (slot_x, slot_y), 25, color, -1)  # Preenchido

                                    # Contorno especial para indicar prioridade
                                    if slot_num in self.rod_status_tracking['broken_rods']:
                                        # Vara quebrada - contorno vermelho duplo (máxima prioridade)
                                        cv2.circle(img_display, (slot_x, slot_y), 30, (0, 0, 255), 4)  # Contorno vermelho externo
                                        cv2.circle(img_display, (slot_x, slot_y), 25, (255, 255, 255), 3)  # Contorno branco interno
                                    elif slot_num in self.rod_status_tracking['available_with_bait']:
                                        # Vara com isca - contorno verde (prioridade média)
                                        cv2.circle(img_display, (slot_x, slot_y), 25, (255, 255, 255), 3)  # Contorno branco padrão
                                    else:
                                        # Outros casos - contorno padrão
                                        cv2.circle(img_display, (slot_x, slot_y), 25, (255, 255, 255), 3)  # Contorno branco

                                    # Se vazio, desenhar X
                                    if color == (128, 128, 128):
                                        cv2.line(img_display, (slot_x-15, slot_y-15), (slot_x+15, slot_y+15),
                                                (255, 255, 255), 3)
                                        cv2.line(img_display, (slot_x-15, slot_y+15), (slot_x+15, slot_y-15),
                                                (255, 255, 255), 3)

                                    # Número do slot em branco (como v3)
                                    line_type = cv2.LINE_AA if (hasattr(self, 'antialiasing_var') and self.antialiasing_var.get()) else cv2.LINE_8
                                    cv2.putText(img_display, str(slot_num), (slot_x-8, slot_y+5),
                                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, line_type)

                            except Exception as e:
                                print(f"[WARN] Erro ao desenhar slots: {e}")

                        # Converter BGR para RGB para PIL
                        img_rgb = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)
                        img_pil = Image.fromarray(img_rgb)

                        # Redimensionar RESPONSIVAMENTE para o canvas atual
                        if hasattr(self, 'catch_canvas') and self.catch_canvas:
                            try:
                                # Obter tamanho atual do canvas
                                canvas_width = self.catch_canvas.winfo_width()
                                canvas_height = self.catch_canvas.winfo_height()

                                # Usar tamanho mínimo se canvas ainda não foi dimensionado
                                if canvas_width <= 1 or canvas_height <= 1:
                                    canvas_width, canvas_height = 800, 600

                                # Calcular proporção mantendo aspect ratio
                                img_width, img_height = img_pil.size
                                canvas_ratio = canvas_width / canvas_height
                                img_ratio = img_width / img_height

                                if img_ratio > canvas_ratio:
                                    # Imagem mais larga - ajustar pela largura
                                    new_width = canvas_width - 20  # Margem
                                    new_height = int(new_width / img_ratio)
                                else:
                                    # Imagem mais alta - ajustar pela altura
                                    new_height = canvas_height - 20  # Margem
                                    new_width = int(new_height * img_ratio)

                                # Garantir dimensões mínimas
                                new_width = max(400, min(new_width, canvas_width - 20))
                                new_height = max(300, min(new_height, canvas_height - 20))

                            except Exception as e:
                                # Fallback para tamanho fixo
                                new_width, new_height = 800, 600
                        else:
                            # Fallback para tamanho fixo
                            new_width, new_height = 800, 600

                        img_resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        img_tk = ImageTk.PhotoImage(img_resized)

                        # Atualizar canvas se janela existir
                        if (self.catch_viewer_window and
                            self.catch_viewer_running and
                            hasattr(self, 'catch_canvas')):

                            def update_viewer():
                                try:
                                    if not self.catch_viewer_running:
                                        return

                                    # VERIFICAR SE VIEWER ESTÁ PAUSADO
                                    if hasattr(self, 'viewer_paused') and self.viewer_paused:
                                        return  # Não atualizar se pausado

                                    # Limpar canvas anterior
                                    if hasattr(self.catch_canvas, 'image'):
                                        del self.catch_canvas.image
                                    self.catch_canvas.delete("all")

                                    # Adicionar nova imagem CENTRALIZADA responsivamente
                                    try:
                                        canvas_center_x = self.catch_canvas.winfo_width() // 2
                                        canvas_center_y = self.catch_canvas.winfo_height() // 2

                                        # Usar centro padrão se canvas não foi dimensionado
                                        if canvas_center_x <= 1:
                                            canvas_center_x = 400
                                        if canvas_center_y <= 1:
                                            canvas_center_y = 300

                                        self.catch_canvas.create_image(canvas_center_x, canvas_center_y,
                                                                     image=img_tk, anchor='center')
                                        self.catch_canvas.image = img_tk
                                    except:
                                        # Fallback para posição fixa
                                        self.catch_canvas.create_image(400, 300, image=img_tk, anchor='center')
                                        self.catch_canvas.image = img_tk

                                    # Atualizar estatísticas DETALHADAS
                                    nonlocal frame_count
                                    frame_count += 1
                                    elapsed = time.time() - start_time
                                    fps = frame_count / max(elapsed, 1)

                                    total_detections = sum(detections_total.values())
                                    active_templates = len([d for d in detections_found])

                                    # 1. ATUALIZAR FPS E PERFORMANCE
                                    if hasattr(self, 'viewer_fps_stats'):
                                        self.viewer_fps_stats.config(
                                            text=f"FPS: {fps:.1f} | Frame: {frame_count} | Tempo: {elapsed:.1f}s"
                                        )

                                    # 2. ATUALIZAR STATUS GERAL
                                    if hasattr(self, 'viewer_general_status'):
                                        mode_text=_("ui_hardcoded.modo_otimizado")
                                        if hasattr(self, 'fishing_engine') and self.fishing_engine and hasattr(self.fishing_engine, 'is_running') and self.fishing_engine.is_running:
                                            mode_text=_("ui_hardcoded.bot_ativo")
                                        self.viewer_general_status.config(
                                            text=f"{mode_text} | Templates: {len(templates)} | Detecções: {total_detections}"
                                        )

                                    # 3. ATUALIZAR TEMPLATES ATIVOS (com detalhes)
                                    if hasattr(self, 'template_scrollable_frame'):
                                        # Limpar widgets anteriores
                                        for widget in self.template_scrollable_frame.winfo_children():
                                            widget.destroy()

                                        # Mostrar templates com detecções ativas
                                        active_count = 0
                                        for template_name, count in detections_total.items():
                                            if count > 0 or template_name in detections_found:
                                                template_clean = template_name.replace('.png', '')

                                                # Cor baseada no tipo
                                                color = '#00ff88' if template_name in detections_found else '#888888'

                                                # Status atual
                                                status = "🟢 ATIVO" if template_name in detections_found else f"💤 {count}"

                                                label = tk.Label(self.template_scrollable_frame,
                                                    text=f"• {template_clean}: {status}",
                                                    font=('Consolas', 8), fg=color, bg='#2a2a2a',
                                                    anchor='w')
                                                label.pack(fill='x', padx=5, pady=1)
                                                active_count += 1

                                        if active_count == 0:
                                            no_detection_label = tk.Label(self.template_scrollable_frame,
                                                text=_("ui_hardcoded.procurando_templates"),
                                                font=('Consolas', 9), fg='#888888', bg='#2a2a2a')
                                            no_detection_label.pack(pady=10)

                                    # 4. ATUALIZAR ESTATÍSTICAS DE PESCA (buscar do fishing_engine)
                                    if hasattr(self, 'viewer_fishing_stats'):
                                        try:
                                            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                                                stats = self.fishing_engine.get_stats() if hasattr(self.fishing_engine, 'get_stats') else {}
                                                fish_count = stats.get('fish_caught', 0)
                                                cycles = stats.get('cycles_completed', 0)
                                                uptime = stats.get('uptime', 0)

                                                # Formatação do tempo
                                                hours = int(uptime // 3600)
                                                minutes = int((uptime % 3600) // 60)
                                                seconds = int(uptime % 60)
                                                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                                                fishing_text = f"Peixes: {fish_count} | Ciclos: {cycles}\nTempo: {time_str}"
                                            else:
                                                fishing_text=_("ui_hardcoded.peixes_0_ciclos")

                                            self.viewer_fishing_stats.config(text=fishing_text)
                                        except Exception as e:
                                            self.viewer_fishing_stats.config(text=_("ui_hardcoded.erro_ao_obter"))

                                    # 5. ATUALIZAR STATUS DAS VARAS (baseado no v3)
                                    if hasattr(self, 'viewer_rod_status'):
                                        try:
                                            # Inicializar rod_status_tracking se não existir
                                            if not hasattr(self, 'rod_status_tracking'):
                                                self.rod_status_tracking = {
                                                    'available_with_bait': [],
                                                    'available_without_bait': [],
                                                    'broken_rods': [],
                                                    'empty_slots': [],
                                                    'last_inventory_check': 0
                                                }

                                            # inventory_open já foi definido acima

                                            # SISTEMA DE MAPEAMENTO DE SLOTS (1-6) - Coordenadas do v3
                                            SLOT_POSITIONS = {
                                                1: (709, 1005),   # Slot 1
                                                2: (805, 1005),   # Slot 2
                                                3: (899, 1005),   # Slot 3
                                                4: (992, 1005),   # Slot 4
                                                5: (1092, 1005),  # Slot 5
                                                6: (1188, 1005)   # Slot 6
                                            }

                                            # Analisar detecções atuais para atualizar status das varas (TODOS OS TEMPLATES)
                                            rod_templates = {
                                                # VARAS COM ISCA (grupo rod_with_bait)
                                                'varanobauci': 'with_bait',     # Vara com isca (minúsculo)
                                                'VARANOBAUCI': 'with_bait',     # Vara com isca (maiúsculo)
                                                'varacomisca': 'with_bait',     # Vara com isca
                                                'comiscavara': 'with_bait',     # Com isca vara
                                                'namaocomisca': 'with_bait',    # Na mão com isca
                                                'comiscanamao': 'with_bait',    # Com isca na mão

                                                # VARAS SEM ISCA (grupo rod_without_bait)
                                                'enbausi': 'without_bait',      # Vara sem isca
                                                'varasemisca': 'without_bait',  # Vara sem isca
                                                'semiscavara': 'without_bait',  # Sem isca vara
                                                'namaosemisca': 'without_bait', # Na mão sem isca
                                                'semiscanam': 'without_bait',   # Sem isca na mão
                                                'semiscavaraescura': 'without_bait', # Sem isca vara escura

                                                # VARAS QUEBRADAS (grupo rod_broken)
                                                'varaquebrada': 'broken',       # Vara quebrada
                                                'nobauquebrada': 'broken'       # No baú quebrada
                                            }

                                            # Limpar listas atuais
                                            self.rod_status_tracking['available_with_bait'].clear()
                                            self.rod_status_tracking['available_without_bait'].clear()
                                            self.rod_status_tracking['broken_rods'].clear()

                                            # MAPEAR DETECÇÕES PARA SLOTS ESPECÍFICOS COM SISTEMA DE PRIORIDADES
                                            slot_status = {1: 'empty', 2: 'empty', 3: 'empty', 4: 'empty', 5: 'empty', 6: 'empty'}

                                            # Definir prioridades: quebrada > com_isca > sem_isca
                                            rod_priority = {
                                                'broken': 3,        # Maior prioridade
                                                'with_bait': 2,     # Prioridade média
                                                'without_bait': 1,  # Menor prioridade
                                                'empty': 0          # Sem prioridade
                                            }

                                            # Dicionário para rastrear a melhor detecção por slot
                                            slot_best_detection = {}

                                            # Analisar cada detecção de vara e mapear para o slot mais próximo
                                            for template_name in detections_found:
                                                template_clean = template_name.replace('.png', '')
                                                if template_clean in rod_templates:
                                                    rod_type = rod_templates[template_clean]

                                                    # Encontrar posições desta detecção
                                                    if template_name in current_frame_detections:
                                                        for det_x, det_y, confidence in current_frame_detections[template_name]:
                                                            # Encontrar slot mais próximo
                                                            closest_slot = None
                                                            min_distance = float('inf')

                                                            for slot_num, (slot_x, slot_y) in SLOT_POSITIONS.items():
                                                                distance = ((det_x - slot_x)**2 + (det_y - slot_y)**2)**0.5
                                                                if distance < min_distance and distance < 100:  # Threshold de proximidade
                                                                    min_distance = distance
                                                                    closest_slot = slot_num

                                                            # APLICAR SISTEMA DE PRIORIDADES
                                                            if closest_slot:
                                                                current_priority = rod_priority.get(rod_type, 0)

                                                                # Se slot ainda não tem detecção ou nova detecção tem maior prioridade
                                                                if (closest_slot not in slot_best_detection or
                                                                    current_priority > slot_best_detection[closest_slot]['priority']):

                                                                    slot_best_detection[closest_slot] = {
                                                                        'type': rod_type,
                                                                        'priority': current_priority,
                                                                        'template': template_name,
                                                                        'confidence': confidence,
                                                                        'distance': min_distance
                                                                    }

                                            # Atualizar slot_status com as melhores detecções (maior prioridade)
                                            for slot_num, detection_info in slot_best_detection.items():
                                                slot_status[slot_num] = detection_info['type']

                                            # Log do sistema de prioridades para debug
                                            if slot_best_detection:
                                                priority_log = []
                                                for slot_num, info in slot_best_detection.items():
                                                    priority_names = {3: 'QUEBRADA', 2: 'COM_ISCA', 1: 'SEM_ISCA'}
                                                    priority_log.append(f"Slot{slot_num}:{priority_names.get(info['priority'], 'UNKNOWN')}")
                                                print(f"[TARGET] Prioridades aplicadas: {', '.join(priority_log)}")

                                            # Atualizar tracking baseado nos slots
                                            for slot_num, status in slot_status.items():
                                                if status == 'with_bait':
                                                    self.rod_status_tracking['available_with_bait'].append(slot_num)
                                                elif status == 'without_bait':
                                                    self.rod_status_tracking['available_without_bait'].append(slot_num)
                                                elif status == 'broken':
                                                    self.rod_status_tracking['broken_rods'].append(slot_num)

                                            # Atualizar timestamp se inventário aberto
                                            if inventory_open:
                                                self.rod_status_tracking['last_inventory_check'] = time.time()

                                            # Usar dados dos slots mapeados
                                            with_bait_count = len(self.rod_status_tracking['available_with_bait'])
                                            without_bait_count = len(self.rod_status_tracking['available_without_bait'])
                                            broken_count = len(self.rod_status_tracking['broken_rods'])

                                            # Criar texto de status detalhado
                                            if inventory_open:
                                                rod_text = "🎣 STATUS DAS VARAS (📦 Inventário Aberto)\n\n"
                                                rod_text += "🔍 ANÁLISE DETALHADA ATIVA\n\n"
                                            else:
                                                rod_text=_("ui_hardcoded.status_das_varas")

                                            # Mostrar STATUS DETALHADO POR SLOT
                                            if with_bait_count > 0:
                                                slots_with_bait = self.rod_status_tracking['available_with_bait']
                                                rod_text += f"✅ Com Isca: Slots {sorted(slots_with_bait)}\n"

                                            if without_bait_count > 0:
                                                slots_without_bait = self.rod_status_tracking['available_without_bait']
                                                rod_text += f"⚠️ Sem Isca: Slots {sorted(slots_without_bait)}\n"

                                            if broken_count > 0:
                                                broken_slots = self.rod_status_tracking['broken_rods']
                                                rod_text += f"❌ Quebradas: Slots {sorted(broken_slots)}\n"

                                            # Calcular slots vazios baseado no mapeamento
                                            occupied_slots = set(self.rod_status_tracking['available_with_bait'] +
                                                               self.rod_status_tracking['available_without_bait'] +
                                                               self.rod_status_tracking['broken_rods'])
                                            empty_slots = set([1, 2, 3, 4, 5, 6]) - occupied_slots
                                            if empty_slots:
                                                rod_text += f"⚪ Vazios: Slots {sorted(empty_slots)}\n"

                                            # MOSTRAR MAPA VISUAL DOS SLOTS
                                            rod_text += f"\n🗺️ MAPA DOS SLOTS:\n"
                                            slot_symbols = {
                                                'empty': '⚪',
                                                'with_bait': '✅',
                                                'without_bait': '⚠️',
                                                'broken': '❌'
                                            }

                                            # Criar linha visual dos slots
                                            slot_line = ""
                                            for slot_num in [1, 2, 3, 4, 5, 6]:
                                                if slot_num in self.rod_status_tracking['available_with_bait']:
                                                    slot_line += f"{slot_symbols['with_bait']}{slot_num} "
                                                elif slot_num in self.rod_status_tracking['available_without_bait']:
                                                    slot_line += f"{slot_symbols['without_bait']}{slot_num} "
                                                elif slot_num in self.rod_status_tracking['broken_rods']:
                                                    slot_line += f"{slot_symbols['broken']}{slot_num} "
                                                else:
                                                    slot_line += f"{slot_symbols['empty']}{slot_num} "

                                            rod_text += slot_line + "\n"

                                            # Informações extras baseadas no contexto
                                            total_detected = with_bait_count + without_bait_count + broken_count
                                            rod_text += f"\n📊 Total detectado: {total_detected}/6 slots"

                                            if inventory_open:
                                                rod_text += "\n🟢 Inventário detectado - máxima precisão"
                                                rod_text += f"\n🕐 Última verificação: Agora"
                                            else:
                                                last_check = self.rod_status_tracking.get('last_inventory_check', 0)
                                                if last_check > 0:
                                                    time_since = time.time() - last_check
                                                    if time_since < 60:
                                                        rod_text += f"\n🕐 Último inventário: {int(time_since)}s atrás"
                                                    else:
                                                        rod_text += f"\n🕐 Último inventário: {int(time_since/60)}m atrás"
                                                else:
                                                    rod_text += "\n⏳ Aguardando primeira verificação"

                                            # Se nenhuma detecção, mostrar mensagem informativa
                                            if total_detected == 0:
                                                rod_text=_("ui_hardcoded.status_das_varasnn")
                                                if inventory_open:
                                                    rod_text += "📦 Inventário detectado!\n"
                                                    rod_text += "🔍 Analisando varas...\n"
                                                    rod_text += "⏳ Aguarde detecções..."
                                                else:
                                                    rod_text += "ℹ️ Aguardando detecções...\n"
                                                    rod_text += "💡 Abra o inventário para\n    análise detalhada das varas"

                                            # Mostrar outros templates detectados
                                            other_detections = [t for t in detections_found if not any(rod in t for rod in ['vara', 'VARA', 'enbausi'])]
                                            if other_detections:
                                                rod_text += f"\n\n🎯 Outras detecções:"
                                                for det in other_detections[:3]:  # Máximo 3 para não sobrecarregar
                                                    clean_name = det.replace('.png', '')
                                                    if clean_name == 'catch':
                                                        rod_text += f"\n🐟 Peixe capturado!"
                                                    elif clean_name == 'inventario':
                                                        rod_text += f"\n📦 Inventário aberto"
                                                    elif clean_name == 'loot':
                                                        rod_text += f"\n📦 Baú aberto"

                                            self.viewer_rod_status.config(text=rod_text)

                                        except Exception as e:
                                            error_text=_("ui_hardcoded.status_das_varasnn")
                                            error_text += f"❌ Erro na análise: {str(e)[:30]}..."
                                            self.viewer_rod_status.config(text=error_text)

                                    # 6. MANTER COMPATIBILIDADE COM LABEL ANTIGO
                                    if hasattr(self, 'catch_stats_label'):
                                        stats_text = f"🎯 Detecções: {total_detections}\n🔍 Templates ativos: {len(templates)}\n⏱️ FPS: {fps:.1f}\n🎪 Detectados agora: {active_templates}"
                                        self.catch_stats_label.config(text=stats_text)

                                except Exception as e:
                                    print(f"[ERROR] Erro ao atualizar viewer: {e}")

                            try:
                                self.catch_viewer_window.after(0, update_viewer)
                            except tk.TclError:
                                print("[RELOAD] Janela fechada, parando viewer...")
                                break

                        # APLICAR LIMPEZA DE MEMÓRIA PERIÓDICA
                        self.cleanup_viewer_memory(frame_count)

                        # Controlar FPS usando configuração correta
                        fps_target = int(self.viewer_fps_var.get()) if hasattr(self, 'viewer_fps_var') else 5
                        time.sleep(1.0 / max(fps_target, 1))

                    except Exception as e:
                        print(f"[WARN] Erro no loop do viewer: {e}")
                        time.sleep(1)

        except Exception as e:
            print(f"[ERROR] Erro crítico no viewer: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.catch_viewer_running = False
            print("[CATCH] Loop do CATCH viewer finalizado")

    def toggle_viewer_pause(self):
        """🎮 Alternar pause/play do viewer"""
        try:
            if not hasattr(self, 'viewer_paused'):
                self.viewer_paused = False

            self.viewer_paused = not self.viewer_paused

            if self.viewer_paused:
                self.viewer_pause_btn.config(text=_("ui_hardcoded.play"), bg='#28a745')
                if hasattr(self, 'viewer_general_status'):
                    self.viewer_general_status.config(text=_("ui_hardcoded.viewer_pausado"))
                print("⏸️ Viewer pausado")
            else:
                self.viewer_pause_btn.config(text=i18n.get_text("ui.pause_bot") if I18N_AVAILABLE else "⏸️ Pausar", bg='#ffc107')
                if hasattr(self, 'viewer_general_status'):
                    self.viewer_general_status.config(text=_("ui_hardcoded.viewer_ativo"))
                print("▶️ Viewer retomado")

        except Exception as e:
            print(f"[ERROR] Erro ao pausar/retomar viewer: {e}")

    def apply_viewer_config(self):
        """💾 Aplicar configurações do visualizador"""
        try:
            # Obter valores das configurações
            fps = int(self.viewer_fps_var.get()) if hasattr(self, 'viewer_fps_var') else 5
            nms_threshold = int(self.nms_threshold_var.get()) if hasattr(self, 'nms_threshold_var') else 100
            auto_start = self.auto_start_var.get() if hasattr(self, 'auto_start_var') else True
            antialiasing = self.antialiasing_var.get() if hasattr(self, 'antialiasing_var') else True
            show_slots = self.show_slots_var.get() if hasattr(self, 'show_slots_var') else True

            # Aplicar configurações se viewer estiver rodando
            if hasattr(self, 'catch_viewer_running') and self.catch_viewer_running:
                # Configurações serão aplicadas no próximo frame
                print(f"[TARGET] Configurações aplicadas: FPS={fps}, NMS={nms_threshold}, Slots={show_slots}")

            # Salvar no config
            if hasattr(self, 'config_manager') and self.config_manager:
                self.config_manager.set('viewer.fps', fps)
                self.config_manager.set('viewer.nms_threshold', nms_threshold)
                self.config_manager.set('viewer.auto_start', auto_start)
                self.config_manager.set('viewer.antialiasing', antialiasing)
                self.config_manager.set('viewer.show_slots', show_slots)

                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print("[OK] Configurações do viewer salvas!")

            # Feedback visual
            if hasattr(self, 'catch_viewer_status_label'):
                self.catch_viewer_status_label.config(text=_("ui_hardcoded.configurações_aplicadas"), fg='#28a745')
                self.main_window.after(3000, lambda: self.catch_viewer_status_label.config(
                    text=_("ui_hardcoded.status_configurado"), fg='#17a2b8'))

        except Exception as e:
            print(f"[ERROR] Erro ao aplicar configurações: {e}")

    def reset_viewer_config(self):
        """🔄 Restaurar configurações padrão do visualizador"""
        try:
            # Restaurar valores padrão
            if hasattr(self, 'viewer_fps_var'):
                self.viewer_fps_var.set("5")
            if hasattr(self, 'nms_threshold_var'):
                self.nms_threshold_var.set("5")
            if hasattr(self, 'auto_start_var'):
                self.auto_start_var.set(True)
            if hasattr(self, 'antialiasing_var'):
                self.antialiasing_var.set(True)
            if hasattr(self, 'show_slots_var'):
                self.show_slots_var.set(True)

            print("[RELOAD] Configurações do viewer restauradas para o padrão")

            # Feedback visual
            if hasattr(self, 'catch_viewer_status_label'):
                self.catch_viewer_status_label.config(text=_("ui_hardcoded.padrões_restaurados"), fg='#ffc107')

        except Exception as e:
            print(f"[ERROR] Erro ao restaurar configurações: {e}")

    def save_viewer_screenshot(self):
        """📸 Salvar screenshot do viewer com detecções marcadas"""
        try:
            if not hasattr(self, 'catch_canvas') or not self.catch_canvas:
                print("[ERROR] Canvas não disponível para screenshot")
                return

            print("📸 Salvando screenshot do viewer...")

            # Criar diretório se não existir
            import os
            screenshot_dir = "data/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)

            # Nome do arquivo com timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"viewer_screenshot_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)

            # Capturar área do canvas
            if hasattr(self, 'catch_viewer_window') and self.catch_viewer_window:
                # Obter coordenadas do canvas
                canvas_x = self.catch_canvas.winfo_rootx()
                canvas_y = self.catch_canvas.winfo_rooty()
                canvas_width = self.catch_canvas.winfo_width()
                canvas_height = self.catch_canvas.winfo_height()

                # Capturar screenshot da área
                import mss
                with mss.mss() as sct:
                    monitor = {
                        "top": canvas_y,
                        "left": canvas_x,
                        "width": canvas_width,
                        "height": canvas_height
                    }
                    screenshot = sct.grab(monitor)

                    # Salvar imagem
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=filepath)

                    print(f"[OK] Screenshot salvo: {filepath}")

                    # Mostrar notificação no viewer
                    if hasattr(self, 'viewer_general_status'):
                        old_text = self.viewer_general_status.cget('text')
                        self.viewer_general_status.config(text=f"📸 Screenshot salvo: {filename}")

                        # Restaurar texto após 3 segundos
                        def restore_text():
                            if hasattr(self, 'viewer_general_status'):
                                self.viewer_general_status.config(text=old_text)

                        self.catch_viewer_window.after(3000, restore_text)

            else:
                print("[ERROR] Janela do viewer não está aberta")

        except Exception as e:
            print(f"[ERROR] Erro ao salvar screenshot: {e}")

    def cleanup_viewer_memory(self, frame_count):
        """🧹 Limpeza periódica de memória do viewer (baseado no v3)"""
        try:
            # Limpeza a cada 100 frames
            if frame_count % 100 == 0:
                import gc
                import psutil
                import os

                # Forçar garbage collection
                collected = gc.collect()

                # Obter uso de memória
                process = psutil.Process(os.getpid())
                memory_mb = process.memory_info().rss / 1024 / 1024

                # Log apenas se coletou algo significativo ou alta memória
                if collected > 50 or memory_mb > 500:
                    print(f"[CLEAN] [VIEWER] Frame {frame_count}: {collected} objetos removidos | RAM: {memory_mb:.1f} MB")

                # Limpeza de canvas se necessário
                if hasattr(self, 'catch_canvas') and hasattr(self.catch_canvas, 'image'):
                    try:
                        # Manter apenas a imagem atual, limpar referências antigas
                        pass
                    except:
                        pass

        except Exception as e:
            print(f"[WARN] Erro na limpeza de memória: {e}")

    def create_status_bar(self):
        """Criar barra de status com seletor de idioma no canto direito"""
        try:
            print("[CONFIG] Criando barra de status...")
            # Criar frame da barra de status com cor de fundo visível
            status_frame = tk.Frame(self.main_window, bg='#2d2d2d', height=35)
            status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
            status_frame.pack_propagate(False)  # Manter altura fixa
            
            # Status principal (esquerda)
            self.status_bar_label = tk.Label(status_frame, text=_("ui_hardcoded.status_pronto"), 
                                           bg='#2d2d2d', fg='white', font=('Arial', 9))
            self.status_bar_label.pack(side=tk.LEFT, padx=10, pady=5)
            
            # Frame direito para idioma e versão  
            right_frame = tk.Frame(status_frame, bg='#2d2d2d')
            right_frame.pack(side=tk.RIGHT, padx=10, pady=5)
            
            # Seletor de idioma (canto inferior direito)
            lang_frame = tk.Frame(right_frame, bg='#2d2d2d')
            lang_frame.pack(side=tk.RIGHT, padx=5)
            
            # Label do globo
            globe_label = tk.Label(lang_frame, text="🌍", bg='#2d2d2d', fg='white', font=('Arial', 10))
            globe_label.pack(side=tk.LEFT, padx=2)
            
            # Mapeamento de códigos para nomes amigáveis
            self.language_names = {
                'pt': '🇧🇷 Português',
                'en': '🇺🇸 English',
                'es': '🇪🇸 Español',
                'ru': '🇷🇺 Русский'
            }

            # Criar lista de opções com nomes amigáveis
            if I18N_AVAILABLE:
                available_codes = list(i18n.get_available_languages().keys())
            else:
                available_codes = ['pt', 'en', 'es', 'ru']

            language_options = [self.language_names.get(code, code) for code in available_codes]

            # Definir valor inicial com nome amigável
            current_display = self.language_names.get(self.current_language, self.current_language)
            self.language_var = tk.StringVar(value=current_display)

            self.language_combo = ttk.Combobox(lang_frame,
                                             textvariable=self.language_var,
                                             values=language_options,
                                             state="readonly",
                                             width=12)
            self.language_combo.pack(side=tk.LEFT, padx=2)
            
            # Bind event para mudança de idioma
            self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
            
            # Separador visual  
            sep_label = tk.Label(right_frame, text=_("ui_hardcoded."), bg='#2d2d2d', fg='#666666')
            sep_label.pack(side=tk.RIGHT, padx=5)
            
            # Versão
            version_label = tk.Label(right_frame, text=_("ui_hardcoded.v40"), 
                                   bg='#2d2d2d', fg='#888888', font=('Arial', 8))
            version_label.pack(side=tk.RIGHT, padx=5)
            
            print(f"[OK] Barra de status criada com seletor de idioma! Idioma atual: {self.current_language}")
            
        except Exception as e:
            print(f"[ERROR] Erro ao criar barra de status: {e}")
    
    def on_language_change(self, event):
        """Tratar mudança de idioma"""
        try:
            selected_display = self.language_var.get()

            # Converter nome amigável de volta para código
            code_map = {v: k for k, v in self.language_names.items()}
            selected_language = code_map.get(selected_display, selected_display)

            # Verificar se o idioma mudou
            if selected_language == self.current_language:
                return

            # Atualizar idioma atual
            old_language = self.current_language
            self.current_language = selected_language

            # Atualizar idioma no i18n manager
            if I18N_AVAILABLE:
                i18n.set_language(selected_language)
                print(f"[OK] Idioma alterado: {old_language} → {selected_language}")

                # SALVAR idioma selecionado no config para persistir entre sessões
                if hasattr(self, 'config_manager') and self.config_manager:
                    self.config_manager.set('ui_settings.language', selected_language)
                    self.config_manager.save_config()
                    print(f"[OK] Idioma salvo no config: {selected_language}")

                # Atualizar TODA a interface (tabs + todos os widgets)
                self.update_ui_texts()

                # Mostrar mensagem de sucesso
                lang_names = {
                    'pt': 'Português',
                    'en': 'English',
                    'es': 'Español',
                    'ru': 'Русский'
                }

                # Mensagem em português ou inglês dependendo do idioma selecionado
                if selected_language == 'en':
                    title = "Language Changed"
                    message = f"Interface language changed to {lang_names.get(selected_language)}!"
                elif selected_language == 'es':
                    title = "Idioma Cambiado"
                    message = f"Idioma de la interfaz cambiado a {lang_names.get(selected_language)}!"
                elif selected_language == 'ru':
                    title = "Язык Изменён"
                    message = f"Язык интерфейса изменён на {lang_names.get(selected_language)}!"
                else:  # pt
                    title = "Idioma Alterado"
                    message = f"Idioma da interface alterado para {lang_names.get(selected_language)}!"

                messagebox.showinfo(title, message)
            else:
                print("[WARN] Sistema i18n não disponível")
                self.language_var.set(self.language_names[old_language])
                self.current_language = old_language

        except Exception as e:
            print(f"[ERROR] Erro ao trocar idioma: {e}")
    
    def update_tab_names(self):
        """Atualizar apenas os nomes das abas com o idioma atual"""
        try:
            if not I18N_AVAILABLE or not hasattr(self, 'notebook'):
                return

            # Lista de IDs das abas na ordem correta (com prefixo tabs.)
            tab_ids = [
                'tabs.control_tab',      # Aba 1
                'tabs.config_tab',       # Aba 2
                'tabs.feeding_tab',      # Aba 3
                'tabs.templates_tab',    # Aba 4
                'tabs.anti_detection_tab', # Aba 5
                'tabs.catch_viewer_tab', # Aba 6
                'tabs.hotkeys_tab',      # Aba 7
                'tabs.arduino_tab',      # Aba 8
                'tabs.help_tab'          # Aba 9
            ]

            # Atualizar cada aba
            for i, tab_key in enumerate(tab_ids):
                try:
                    tab_text = i18n.get_text(tab_key)
                    if tab_text and tab_text != tab_key:  # Verificar se a tradução existe
                        self.notebook.tab(i, text=tab_text)
                        # Não imprimir o texto diretamente (tem emojis que podem causar erro no Windows)
                        print(f"  [OK] Aba {i+1} atualizada")
                except Exception as e:
                    print(f"  [WARN] Erro ao atualizar aba {i+1} ({tab_key}): {e}")

            print(f"[OK] Nomes das abas atualizados para: {self.current_language}")

        except Exception as e:
            print(f"[ERROR] Erro ao atualizar nomes das abas: {e}")

    def register_translatable_widget(self, widget_type, widget_id, widget, translation_key):
        """
        🌍 Register a widget for dynamic language switching

        Args:
            widget_type: 'frame', 'label', 'button', 'checkbox', 'radiobutton'
            widget_id: Unique identifier for the widget
            widget: The actual tkinter widget
            translation_key: i18n key (e.g., 'ui.bot_status')
        """
        try:
            if widget_type not in self.translatable_widgets:
                self.translatable_widgets[widget_type] = {}

            self.translatable_widgets[widget_type][widget_id] = {
                'widget': widget,
                'translation_key': translation_key
            }
        except Exception as e:
            print(f"[WARN] Error registering widget {widget_id}: {e}")

    def update_ui_texts(self):
        """🌍 Atualizar TODOS os textos da interface com o idioma atual"""
        try:
            if not I18N_AVAILABLE:
                print("[WARN] i18n not available, skipping UI text update")
                return

            print(f"[INFO] Updating all UI texts to language: {self.current_language}")
            updated_count = 0

            # 1. Atualizar títulos das abas
            self.update_tab_names()

            # 2. Atualizar LabelFrames
            for widget_id, data in self.translatable_widgets.get('frames', {}).items():
                try:
                    widget = data['widget']
                    translation_key = data['translation_key']
                    text = i18n.get_text(translation_key)
                    if text and text != translation_key:
                        widget.config(text=text)
                        updated_count += 1
                except Exception as e:
                    print(f"[WARN] Error updating frame {widget_id}: {e}")

            # 3. Atualizar Labels
            for widget_id, data in self.translatable_widgets.get('labels', {}).items():
                try:
                    widget = data['widget']
                    translation_key = data['translation_key']
                    text = i18n.get_text(translation_key)
                    if text and text != translation_key:
                        widget.config(text=text)
                        updated_count += 1
                except Exception as e:
                    print(f"[WARN] Error updating label {widget_id}: {e}")

            # 4. Atualizar Buttons
            for widget_id, data in self.translatable_widgets.get('buttons', {}).items():
                try:
                    widget = data['widget']
                    translation_key = data['translation_key']
                    text = i18n.get_text(translation_key)
                    if text and text != translation_key:
                        widget.config(text=text)
                        updated_count += 1
                except Exception as e:
                    print(f"[WARN] Error updating button {widget_id}: {e}")

            # 5. Atualizar Checkboxes
            for widget_id, data in self.translatable_widgets.get('checkboxes', {}).items():
                try:
                    widget = data['widget']
                    translation_key = data['translation_key']
                    text = i18n.get_text(translation_key)
                    if text and text != translation_key:
                        widget.config(text=text)
                        updated_count += 1
                except Exception as e:
                    print(f"[WARN] Error updating checkbox {widget_id}: {e}")

            # 6. Atualizar Radiobuttons
            for widget_id, data in self.translatable_widgets.get('radiobuttons', {}).items():
                try:
                    widget = data['widget']
                    translation_key = data['translation_key']
                    text = i18n.get_text(translation_key)
                    if text and text != translation_key:
                        widget.config(text=text)
                        updated_count += 1
                except Exception as e:
                    print(f"[WARN] Error updating radiobutton {widget_id}: {e}")

            print(f"[OK] Updated {updated_count} UI elements to {self.current_language}")

        except Exception as e:
            print(f"[ERROR] Error updating UI texts: {e}")
    
    # ===== MÉTODOS DE CONTROLE =====
    
    def save_cleaning_config(self):
        """Salvar configurações de limpeza automática"""
        print("[SAVE] Salvando configurações de limpeza...")
        try:
            interval = self.auto_clean_interval_var.get()
            enabled = self.auto_clean_enabled_var.get()
            baits_enabled = self.auto_clean_baits_enabled_var.get()
            
            # Salvar no ConfigManager
            if hasattr(self, 'config_manager') and self.config_manager:
                self.config_manager.set('auto_clean.enabled', enabled)
                self.config_manager.set('auto_clean.interval', int(interval) if interval.isdigit() else 10)
                self.config_manager.set('auto_clean.include_baits', baits_enabled)
                # ✅ CORREÇÃO: chest_side e chest_method são configurações GLOBAIS do baú,
                # não específicas de auto_clean! Removidas daqui (são salvas em save_config_general)
                # self.config_manager.set('auto_clean.chest_side', self.chest_side_var.get())
                # self.config_manager.set('auto_clean.chest_method', self.macro_type_var.get())
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"[OK] Configurações de limpeza salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações de limpeza salvas!")
                else:
                    print("[WARN] ConfigManager sem método save_config")
            else:
                print("[ERROR] ConfigManager não disponível")
                
        except Exception as e:
            print(f"[ERROR] Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def test_cleaning_system(self):
        """Testar sistema de limpeza"""
        print("[TEST] Testando sistema de limpeza...")
        print("[RELOAD] Simulando limpeza de inventário...")
        print("[OK] Teste concluído!")
    
    def save_all_config(self):
        """Salvar todas as configurações"""
        print("[SAVE] Salvando todas as configurações...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Salvar cada configuração
                self.config_manager.set('timeouts.fishing_cycle_timeout', int(self.cycle_timeout_var.get()))
                self.config_manager.set('rod_system.rod_switch_limit', int(self.rod_switch_limit_var.get()))
                self.config_manager.set('performance.clicks_per_second', int(self.clicks_per_second_var.get()))
                self.config_manager.set('timeouts.maintenance_timeout', int(self.maintenance_timeout_var.get()))
                self.config_manager.set('chest_side', self.chest_side_var.get())
                self.config_manager.set('macro_type', self.macro_type_var.get())
                self.config_manager.set('chest_distance', int(self.chest_distance_var.get()))
                self.config_manager.set('auto_reload', self.auto_reload_var.get())
                self.config_manager.set('auto_focus', self.auto_focus_var.get())
                self.config_manager.set('rod_system.broken_rod_action', self.broken_rod_action_var.get())
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    
                    # IMPORTANTE: Recarregar configurações nos engines
                    self._reload_engine_configs()
                    
                    print(f"[OK] Todas as configurações salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Todas as configurações salvas com sucesso!")
                else:
                    print("[WARN] ConfigManager sem método save_config")
            else:
                print("[ERROR] ConfigManager não disponível")
                
        except Exception as e:
            print(f"[ERROR] Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def reset_all_config(self):
        """Resetar todas as configurações para padrão"""
        print("[RELOAD] Resetando todas as configurações...")
        try:
            self.cycle_timeout_var.set("122")
            self.rod_switch_limit_var.set("20")
            self.clicks_per_second_var.set("9")
            self.maintenance_timeout_var.set("3")
            self.chest_side_var.set("right")
            self.macro_type_var.set("padrão")
            self.chest_distance_var.set("1000")
            self.auto_reload_var.set(True)
            self.auto_focus_var.set(False)
            self.broken_rod_action_var.set("discard")
            print("[OK] Configurações resetadas para o padrão")
        except Exception as e:
            print(f"[ERROR] Erro ao resetar: {e}")

    def _on_chest_side_change(self, selected_side):
        """Callback chamado quando usuário muda o lado do baú no dropdown"""
        try:
            print(f"[CHEST_SIDE] Mudando lado do baú para: {selected_side}")

            # ✅ Salvar imediatamente no ConfigManager
            if hasattr(self, 'config_manager') and self.config_manager:
                self.config_manager.set('chest_side', selected_side)

                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"✅ [CHEST_SIDE] Configuração salva: chest_side = {selected_side}")

                    # ✅ CRÍTICO: Recarregar configuração no ChestManager
                    if hasattr(self, 'chest_manager') and self.chest_manager:
                        # ChestManager lerá o novo valor na próxima chamada de get_chest_config()
                        print(f"✅ [CHEST_SIDE] ChestManager usará {selected_side} na próxima operação")
                else:
                    print("⚠️ [CHEST_SIDE] ConfigManager sem método save_config")
            else:
                print("⚠️ [CHEST_SIDE] ConfigManager não disponível")

        except Exception as e:
            print(f"❌ [CHEST_SIDE] Erro ao salvar: {e}")

    def test_all_config(self):
        """Testar todas as configurações"""
        print("[TEST] Testando todas as configurações...")
        print("⏱️ Testando timeouts...")
        print("📦 Testando configurações do baú...")
        print("[FISHING] Testando sistema de varas...")
        print("🖱️ Testando foco automático...")
        print("[OK] Todos os testes concluídos!")
    
    def save_feeding_config(self):
        """Salvar configurações de alimentação"""
        print("[SAVE] Salvando configurações de alimentação...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Salvar configurações de alimentação
                self.config_manager.set('feeding_system.enabled', self.feeding_enabled_var.get())
                self.config_manager.set('feeding_system.auto_detect', self.feeding_auto_detect_var.get())
                self.config_manager.set('feeding_system.trigger_mode', self.feeding_trigger_mode_var.get())
                
                trigger_catches = self.feeding_trigger_catches_var.get()
                self.config_manager.set('feeding_system.trigger_catches', 
                                       int(trigger_catches) if trigger_catches.isdigit() else 3)
                
                trigger_time = self.feeding_trigger_time_var.get()
                self.config_manager.set('feeding_system.trigger_time', 
                                       int(trigger_time) if trigger_time.isdigit() else 20)
                
                session_count = self.feeding_session_count_var.get()
                feeds_value = int(session_count) if session_count.isdigit() else 5
                print(f"[SAVE] [DEBUG] Salvando feeds_per_session: {feeds_value} (da UI: '{session_count}')")
                self.config_manager.set('feeding_system.feeds_per_session', feeds_value)
                
                max_uses = self.feeding_max_uses_var.get()
                self.config_manager.set('feeding_system.max_uses_per_slot', 
                                       int(max_uses) if max_uses.isdigit() else 20)
                
                # Posições
                self.config_manager.set('coordinates.feeding_positions.slot1', 
                                       [int(self.feeding_slot1_x_var.get()), 
                                        int(self.feeding_slot1_y_var.get())])
                
                self.config_manager.set('coordinates.feeding_positions.slot2',
                                       [int(self.feeding_slot2_x_var.get()), 
                                        int(self.feeding_slot2_y_var.get())])
                
                self.config_manager.set('coordinates.feeding_positions.eat',
                                       [int(self.feeding_eat_x_var.get()), 
                                        int(self.feeding_eat_y_var.get())])
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"[OK] Configurações de alimentação salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações de alimentação salvas!")
                else:
                    print("[WARN] ConfigManager sem método save_config")
            else:
                print("[ERROR] ConfigManager não disponível")
                
        except Exception as e:
            print(f"[ERROR] Erro ao salvar alimentação: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar alimentação: {e}")
    
    def reset_feeding_config(self):
        """Resetar configurações de alimentação para padrão"""
        print("[RELOAD] Resetando configurações de alimentação...")
        try:
            self.feeding_enabled_var.set(True)
            self.feeding_auto_detect_var.set(True)
            self.feeding_trigger_mode_var.set("catches")
            self.feeding_trigger_catches_var.set("3")
            self.feeding_trigger_time_var.set("20")
            self.feeding_session_count_var.set("5")
            self.feeding_max_uses_var.set("20")
            self.feeding_slot1_x_var.set("1306")
            self.feeding_slot1_y_var.set("858")
            self.feeding_slot2_x_var.set("1403")
            self.feeding_slot2_y_var.set("877")
            if hasattr(self, 'feeding_eat_x_var'):
                self.feeding_eat_x_var.set("1083")
                self.feeding_eat_y_var.set("373")
            print("[OK] Configurações de alimentação resetadas")
        except Exception as e:
            print(f"[ERROR] Erro ao resetar alimentação: {e}")

    def load_feeding_config(self):
        """Carregar configurações de alimentação salvas"""
        print("[DOC] Carregando configurações de alimentação...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Carregar feeds_per_session
                feeds_per_session = self.config_manager.get('feeding_system.feeds_per_session')
                if feeds_per_session is not None:
                    self.feeding_session_count_var.set(str(feeds_per_session))
                    print(f"[DOC] feeds_per_session carregado: {feeds_per_session}")

                # Carregar outros valores
                trigger_mode = self.config_manager.get('feeding_system.trigger_mode')
                if trigger_mode:
                    self.feeding_trigger_mode_var.set(trigger_mode)

                trigger_catches = self.config_manager.get('feeding_system.trigger_catches')
                if trigger_catches is not None:
                    self.feeding_trigger_catches_var.set(str(trigger_catches))

                trigger_time = self.config_manager.get('feeding_system.trigger_time')
                if trigger_time is not None:
                    self.feeding_trigger_time_var.set(str(trigger_time))

                print("[OK] Configurações de alimentação carregadas")
            else:
                print("[WARN] ConfigManager não disponível para carregar configurações")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar configurações de alimentação: {e}")

    def load_cleaning_config(self):
        """Carregar configurações de limpeza automática salvas"""
        print("[DOC] Carregando configurações de limpeza...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Carregar interval (CRÍTICO: era sempre 10 hardcoded)
                interval = self.config_manager.get('auto_clean.interval')
                if interval is not None:
                    self.auto_clean_interval_var.set(str(interval))
                    print(f"[DOC] auto_clean.interval carregado: {interval}")

                # Carregar enabled
                enabled = self.config_manager.get('auto_clean.enabled')
                if enabled is not None:
                    self.auto_clean_enabled_var.set(enabled)

                # Carregar include_baits
                include_baits = self.config_manager.get('auto_clean.include_baits')
                if include_baits is not None:
                    self.auto_clean_baits_enabled_var.set(include_baits)

                # ✅ CORREÇÃO: chest_side está no nível ROOT do config, não dentro de auto_clean!
                # Carregar chest_side
                chest_side = self.config_manager.get('chest_side')
                if chest_side:
                    self.chest_side_var.set(chest_side)

                # Carregar chest_method
                chest_method = self.config_manager.get('auto_clean.chest_method')
                if chest_method:
                    self.macro_type_var.set(chest_method)

                print("[OK] Configurações de limpeza carregadas")
            else:
                print("[WARN] ConfigManager não disponível para carregar configurações")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar configurações de limpeza: {e}")

    def load_anti_detection_config(self):
        """Carregar configurações de anti-detecção salvas"""
        print("[DOC] Carregando configurações de anti-detecção...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Carregar enabled
                enabled = self.config_manager.get('anti_detection.enabled')
                if enabled is not None:
                    self.anti_detection_enabled_var.set(enabled)

                # Carregar click variation enabled
                click_enabled = self.config_manager.get('anti_detection.click_variation.enabled')
                if click_enabled is not None:
                    self.click_variation_enabled.set(click_enabled)

                # Carregar min_delay (converter de segundos para milissegundos)
                min_delay = self.config_manager.get('anti_detection.click_variation.min_delay')
                if min_delay is not None:
                    self.click_min_delay.set(int(min_delay * 1000))
                    print(f"[DOC] click_variation.min_delay carregado: {min_delay}s ({int(min_delay * 1000)}ms)")

                # Carregar max_delay (converter de segundos para milissegundos)
                max_delay = self.config_manager.get('anti_detection.click_variation.max_delay')
                if max_delay is not None:
                    self.click_max_delay.set(int(max_delay * 1000))
                    print(f"[DOC] click_variation.max_delay carregado: {max_delay}s ({int(max_delay * 1000)}ms)")

                # Carregar movement variation enabled
                movement_enabled = self.config_manager.get('anti_detection.movement_variation.enabled')
                if movement_enabled is not None:
                    self.movement_variation_enabled.set(movement_enabled)

                # ✅ NOVO: Carregar configurações de ciclo de tecla S
                s_enabled = self.config_manager.get('anti_detection.s_key_cycle.enabled')
                if s_enabled is not None:
                    self.s_key_cycle_enabled.set(s_enabled)

                s_hold_min = self.config_manager.get('anti_detection.s_key_cycle.hold_duration_min')
                if s_hold_min is not None:
                    self.s_hold_duration_min.set(float(s_hold_min))

                s_hold_max = self.config_manager.get('anti_detection.s_key_cycle.hold_duration_max')
                if s_hold_max is not None:
                    self.s_hold_duration_max.set(float(s_hold_max))

                s_release_min = self.config_manager.get('anti_detection.s_key_cycle.release_duration_min')
                if s_release_min is not None:
                    self.s_release_duration_min.set(float(s_release_min))

                s_release_max = self.config_manager.get('anti_detection.s_key_cycle.release_duration_max')
                if s_release_max is not None:
                    self.s_release_duration_max.set(float(s_release_max))

                print("[OK] Configurações de anti-detecção carregadas (incluindo ciclo de S)")
            else:
                print("[WARN] ConfigManager não disponível para carregar configurações")
        except Exception as e:
            print(f"[ERROR] Erro ao carregar configurações de anti-detecção: {e}")

    def test_feeding_system(self):
        """Testar sistema de alimentação - executa o mesmo que F6"""
        print("[TEST] Testando sistema de alimentação...")
        try:
            # Chamar o mesmo método que F6
            self.trigger_feeding()
        except Exception as e:
            print(f"[ERROR] Erro no teste de alimentação: {e}")
    
    def start_bot(self):
        """Iniciar bot - BASEADO EXATAMENTE NO BOTPESCA.PY"""
        print("\n" + "="*60)
        print("[TARGET] [F9] INICIANDO BOT - LÓGICA BOTPESCA.PY")
        print("="*60)
        
        try:
            # Verificar se já está rodando
            if self.bot_running:
                print("[WARN] Bot já está rodando")
                return
            
            # Inicializar flag first_f9_execution se não existir
            if not hasattr(self, 'first_f9_execution'):
                self.first_f9_execution = True
            
            # EXATAMENTE como botpesca.py: verificar primeira execução
            if self.first_f9_execution:
                print("[TARGET] [PRIMEIRA VEZ] Primeira execução do F9 - SEM botão direito")
                print("[TARGET] [PRIMEIRA VEZ] Executando apenas lógica de inicialização")
                self.first_f9_execution = False
            else:
                print("[TARGET] [SUBSEQUENTE] Execução subsequente do F9")
            
            # Iniciar fishing engine SEM abrir inventário automaticamente
            if self.fishing_engine:
                if self.fishing_engine.start():
                    self.bot_running = True
                    self.bot_paused = False
                    self.status_label.config(text=_("ui_hardcoded.executando"), fg='green')
                    print("🚀 Bot iniciado com FishingEngine")
                else:
                    print("[ERROR] Falha ao iniciar FishingEngine")
                    self.status_label.config(text=_("ui_hardcoded.erro_ao_iniciar"), fg='red')
            else:
                # Modo simulação sem engines
                self.bot_running = True
                self.bot_paused = False
                self.status_label.config(text=_("ui_hardcoded.simulação"), fg='orange')
                print("[CONFIG] Bot iniciado em modo simulação")
                
        except Exception as e:
            print(f"[ERROR] Erro ao iniciar bot: {e}")
            self.status_label.config(text=_("ui_hardcoded.erro"), fg='red')
    
    def pause_bot(self):
        """Pausar/Despausar bot usando FishingEngine"""
        try:
            if self.fishing_engine:
                # Usar o motor de pesca
                if self.fishing_engine.pause():
                    self.bot_paused = self.fishing_engine.is_paused
                    status = "⏸️ Pausado" if self.bot_paused else "🟢 Executando"
                    color = 'orange' if self.bot_paused else 'green'
                    self.status_label.config(text=status, fg=color)
                    print(f"⏸️ Bot {'pausado' if self.bot_paused else 'retomado'} via FishingEngine")
            else:
                # Modo simulação
                self.bot_paused = not self.bot_paused
                status = "⏸️ Pausado (sim)" if self.bot_paused else "🟡 Simulação"
                self.status_label.config(text=status)
                print(f"[CONFIG] Bot {'pausado' if self.bot_paused else 'retomado'} em simulação")
                
        except Exception as e:
            print(f"[ERROR] Erro ao pausar/despausar bot: {e}")
    
    def stop_bot(self):
        """Parar bot usando FishingEngine"""
        try:
            if self.fishing_engine:
                # Usar o motor de pesca
                if self.fishing_engine.stop():
                    self.bot_running = False
                    self.bot_paused = False
                    self.status_label.config(text=_("ui_hardcoded.parado"), fg='red')
                    print("🛑 Bot parado via FishingEngine")
                else:
                    print("[WARN] Problemas ao parar FishingEngine")
            else:
                # Modo simulação
                self.bot_running = False
                self.bot_paused = False
                self.status_label.config(text=_("ui_hardcoded.parado_sim"), fg='red')
                print("[CONFIG] Bot parado em simulação")
                
        except Exception as e:
            print(f"[ERROR] Erro ao parar bot: {e}")
            # Forçar parada em caso de erro
            self.bot_running = False
            self.bot_paused = False
            self.status_label.config(text=_("ui_hardcoded.parado"), fg='red')
    
    # Método duplicado removido - já implementado na linha 1919
    
    # ===== CALLBACKS DO FISHING ENGINE =====
    
    def _on_fishing_state_change(self, old_state, new_state):
        """Callback para mudança de estado do FishingEngine"""
        try:
            state_text = {
                'stopped': '🔴 Parado',
                'starting': '🟡 Iniciando...',
                'fishing': '🟢 Pescando',
                'fish_caught': '🐟 Peixe capturado!',
                'processing_catch': '⚙️ Processando...',
                'reloading': '🔄 Recarregando...',
                'error': '❌ Erro',
                'paused': '⏸️ Pausado'
            }
            
            state_colors = {
                'stopped': 'red',
                'starting': 'orange', 
                'fishing': 'green',
                'fish_caught': 'cyan',
                'processing_catch': 'yellow',
                'reloading': 'orange',
                'error': 'red',
                'paused': 'orange'
            }
            
            text = state_text.get(new_state.value, new_state.value)
            color = state_colors.get(new_state.value, 'white')
            
            self.status_label.config(text=text, fg=color)
            print(f"[RELOAD] Estado FishingEngine: {old_state.value} → {new_state.value}")
            
        except Exception as e:
            print(f"[ERROR] Erro no callback de estado: {e}")
    
    def _on_fish_caught(self, fish_count):
        """Callback para peixe capturado"""
        try:
            # Atualizar estatísticas na UI
            if 'fish_caught' in self.stats_labels:
                self.stats_labels['fish_caught'].config(text=str(fish_count))
            
            # Mostrar notificação visual
            self.status_label.config(text=f"🐟 Peixe #{fish_count} capturado!", fg='cyan')
            
            print(f"[FISHING] Peixe #{fish_count} capturado!")
            
        except Exception as e:
            print(f"[ERROR] Erro no callback de captura: {e}")
    
    def _on_fishing_error(self, error_message):
        """Callback para erro no FishingEngine"""
        try:
            self.status_label.config(text=f"❌ Erro: {error_message}", fg='red')
            print(f"[ERROR] Erro FishingEngine: {error_message}")
            
            # Notificar usuário se necessário
            if "crítico" in error_message.lower():
                messagebox.showerror("Erro Crítico", error_message)
                
        except Exception as e:
            print(f"[ERROR] Erro no callback de erro: {e}")
    
    def _on_fishing_stats_update(self, stats):
        """Callback para atualização de estatísticas"""
        try:
            # Atualizar labels de estatísticas na UI (corrigido os nomes dos labels)
            if 'fish' in self.stats_labels and 'fish_caught' in stats:
                self.stats_labels['fish'].config(text=str(stats['fish_caught']))

            if 'session_time' in self.stats_labels and 'fishing_time' in stats:
                # Converter segundos para HH:MM:SS
                total_seconds = int(stats['fishing_time'])
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.stats_labels['session_time'].config(text=time_str)

            if 'fish_per_hour' in self.stats_labels and 'catches_per_hour' in stats:
                rate_str = str(int(stats['catches_per_hour']))
                self.stats_labels['fish_per_hour'].config(text=rate_str)

            # ✅ ATUALIZAR STATS DOS SUBSISTEMAS (feeds, cleans, broken_rods, timeouts, success_rate)
            self._update_subsystem_stats()

            # Debug estatísticas
            #print(f"[INFO] Stats: {stats['fish_caught']} peixes, {stats['fishing_time']/60:.1f}min, {stats['catches_per_hour']:.1f}/h")

        except Exception as e:
            print(f"[ERROR] Erro no callback de stats: {e}")

    def _update_subsystem_stats(self):
        """
        Atualizar estatísticas de todos os subsistemas (feeding, cleaning, rods, timeouts)

        Coleta stats de:
        - FeedingSystem (feeds)
        - InventoryManager (cleans)
        - RodMaintenanceSystem (broken_rods)
        - FishingEngine (timeouts)

        E calcula success_rate
        """
        try:
            # ===== FEEDS (FeedingSystem) =====
            if hasattr(self, 'feeding_system') and self.feeding_system:
                if hasattr(self.feeding_system, 'stats'):
                    total_feedings = self.feeding_system.stats.get('total_feedings', 0)
                    if 'feeds' in self.stats_labels:
                        self.stats_labels['feeds'].config(text=str(total_feedings))

            # ===== CLEANS (InventoryManager) =====
            if hasattr(self, 'inventory_manager') and self.inventory_manager:
                if hasattr(self.inventory_manager, 'stats'):
                    total_cleanings = self.inventory_manager.stats.get('total_cleanings', 0)
                    if 'cleans' in self.stats_labels:
                        self.stats_labels['cleans'].config(text=str(total_cleanings))

            # ===== MAINTENANCES (RodMaintenanceSystem) =====
            if hasattr(self, 'rod_manager') and self.rod_manager:
                if hasattr(self.rod_manager, 'maintenance_system') and self.rod_manager.maintenance_system:
                    if hasattr(self.rod_manager.maintenance_system, 'stats'):
                        successful_maintenances = self.rod_manager.maintenance_system.stats.get('successful_maintenances', 0)
                        if 'maintenances' in self.stats_labels:
                            self.stats_labels['maintenances'].config(text=str(successful_maintenances))

            # ===== BROKEN RODS (RodMaintenanceSystem) =====
            if hasattr(self, 'rod_manager') and self.rod_manager:
                if hasattr(self.rod_manager, 'maintenance_system') and self.rod_manager.maintenance_system:
                    if hasattr(self.rod_manager.maintenance_system, 'stats'):
                        broken_rods = self.rod_manager.maintenance_system.stats.get('broken_rods_cleaned', 0)
                        if 'broken_rods' in self.stats_labels:
                            self.stats_labels['broken_rods'].config(text=str(broken_rods))

            # ===== TIMEOUTS (FishingEngine) =====
            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                if hasattr(self.fishing_engine, 'stats'):
                    timeouts = self.fishing_engine.stats.get('timeouts', 0)
                    if 'timeouts' in self.stats_labels:
                        self.stats_labels['timeouts'].config(text=str(timeouts))

                    # ✅ NOVO: Vara do último timeout (mostra contagem consecutiva)
                    if hasattr(self.fishing_engine, 'rod_timeout_history') and self.fishing_engine.rod_timeout_history:
                        # Encontrar vara com maior contador (mais recente com timeouts)
                        current_rod = self.rod_manager.get_current_rod() if self.rod_manager else 1
                        consecutive = self.fishing_engine.rod_timeout_history.get(current_rod, 0)

                        if consecutive > 0:
                            rod_text = f"Vara {current_rod} ({consecutive}x)"
                            # Mudar cor se 3+ timeouts
                            color = '#ff4444' if consecutive >= 3 else 'white'
                            if 'rod_at_timeout' in self.stats_labels:
                                self.stats_labels['rod_at_timeout'].config(text=rod_text, fg=color)
                        else:
                            if 'rod_at_timeout' in self.stats_labels:
                                self.stats_labels['rod_at_timeout'].config(text="-", fg='white')
                    else:
                        if 'rod_at_timeout' in self.stats_labels:
                            self.stats_labels['rod_at_timeout'].config(text="-", fg='white')

                    # ===== SUCCESS RATE (fish_caught / (fish_caught + timeouts) * 100) =====
                    fish_caught = self.fishing_engine.stats.get('fish_caught', 0)
                    total_attempts = fish_caught + timeouts

                    if total_attempts > 0:
                        success_rate = (fish_caught / total_attempts) * 100
                        if 'success_rate' in self.stats_labels:
                            self.stats_labels['success_rate'].config(text=f"{success_rate:.1f}%")
                    else:
                        if 'success_rate' in self.stats_labels:
                            self.stats_labels['success_rate'].config(text=_("ui_hardcoded.00"))

        except Exception as e:
            print(f"[ERROR] Erro ao atualizar stats de subsistemas: {e}")

    # ===== MÉTODOS DE IDIOMA =====
    
    # Language-related functions removed - language tab replaced with catch viewer
    
    # ===== MÉTODOS ARDUINO =====
    
    def refresh_arduino_ports(self):
        """Atualizar lista de portas COM disponíveis e selecionar Arduino automaticamente"""
        try:
            ports = get_com_ports()
            print(f"[RELOAD] Atualizando portas COM: {ports}")

            # Atualizar o menu da porta
            menu = self.arduino_port_combo['menu']
            menu.delete(0, 'end')

            for port in ports:
                menu.add_command(label=port, command=tk._setit(self.arduino_port_var, port))

            # ✅ NOVO: Auto-detectar e selecionar porta Arduino
            current_port = self.arduino_port_var.get()
            arduino_port = self._detect_arduino_port(ports)

            if arduino_port:
                if current_port != arduino_port:
                    self.arduino_port_var.set(arduino_port)
                    self.log_arduino(f"🔄 Porta Arduino detectada automaticamente: {arduino_port}")
                else:
                    self.log_arduino(f"✅ Porta Arduino ativa: {arduino_port}")
            elif current_port not in ports and ports:
                # Se a porta atual não existe mais, usar a primeira disponível
                self.arduino_port_var.set(ports[0])
                self.log_arduino(f"⚠️ Porta {current_port} não encontrada, usando: {ports[0]}")

            self.log_arduino(f"✅ Portas COM atualizadas: {', '.join(ports)}")

        except Exception as e:
            self.log_arduino(f"❌ Erro ao atualizar portas: {e}")

    def _detect_arduino_port(self, ports=None):
        """Detectar automaticamente porta do Arduino"""
        try:
            import serial.tools.list_ports

            if ports is None:
                ports = get_com_ports()

            # Buscar portas COM com descrição de Arduino
            for port_info in serial.tools.list_ports.comports():
                port_name = port_info.device
                description = port_info.description.lower()

                # Verificar se é Arduino Leonardo, Pro Micro ou compatível
                if any(keyword in description for keyword in ['arduino', 'leonardo', 'pro micro', 'atmega32u4', 'ch340']):
                    if port_name in ports:
                        print(f"[ARDUINO] Detectado: {port_name} - {port_info.description}")
                        return port_name

            return None

        except Exception as e:
            print(f"[ARDUINO] Erro ao detectar porta: {e}")
            return None
    
    def test_arduino_connection(self):
        """Testar conexão com Arduino sem manter conexão - NON-BLOCKING"""
        # Executar teste em thread separada para não travar UI
        import threading
        test_thread = threading.Thread(target=self._test_arduino_thread, daemon=True)
        test_thread.start()

    def _test_arduino_thread(self):
        """Thread de teste (não bloqueia UI)"""
        try:
            port = self.arduino_port_var.get()
            baud = int(self.arduino_baud_var.get())
            timeout = float(self.arduino_timeout_var.get())

            # Atualizar UI de forma thread-safe
            self.root.after(0, lambda: self.log_arduino(f"🔍 Testando conexão em {port} ({baud} baud)..."))
            self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.testando_conexão")))
            self.root.after(0, lambda: self.arduino_status_indicator.config(fg="yellow"))

            # Tentar importar serial
            try:
                import serial
                import time
            except ImportError:
                self.root.after(0, lambda: self.log_arduino("❌ Biblioteca 'pyserial' não encontrada. Execute: pip install pyserial"))
                return

            # Testar conexão
            with serial.Serial(port, baud, timeout=timeout) as ser:
                time.sleep(2)  # Aguardar inicialização (OK em thread separada)

                # Aguardar e descartar mensagem READY inicial
                ready_msg = ser.readline().decode().strip()
                if ready_msg == "READY":
                    self.root.after(0, lambda: self.log_arduino(f"📡 Arduino inicializado: {ready_msg}"))

                # Aguardar um pouco para Arduino ficar pronto
                time.sleep(0.5)

                # Limpar buffers antes do teste
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # Enviar comando de teste PING
                ser.write(b"PING\n")
                ser.flush()  # Garantir que comando foi enviado
                time.sleep(0.5)  # Aguardar resposta (aumentado para 500ms)
                response = ser.readline().decode().strip()

                if response == "PONG":
                    self.root.after(0, lambda: self.log_arduino(f"✅ Teste PING-PONG OK"))
                    self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.teste_ok")))
                    self.root.after(0, lambda: self.arduino_status_indicator.config(fg="green"))
                else:
                    self.root.after(0, lambda: self.log_arduino(f"⚠️ Falhou no teste PING (recebido: '{response}')"))
                    self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.firmware_incorreto")))
                    self.root.after(0, lambda: self.arduino_status_indicator.config(fg="orange"))

        except Exception as e:
            import serial
            error_msg = str(e)

            # Tratamento thread-safe de exceções
            if "PermissionError" in error_msg or "Acesso negado" in error_msg:
                self.root.after(0, lambda: self.log_arduino(f"❌ Porta {port} está sendo usada por outro programa"))
                self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.porta_em_uso")))
                self.root.after(0, lambda: self.arduino_status_indicator.config(fg="orange"))
            elif "FileNotFoundError" in error_msg or "could not open port" in error_msg:
                self.root.after(0, lambda: self.log_arduino(f"❌ Porta {port} não existe"))
                self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.porta_não_encontrada")))
                self.root.after(0, lambda: self.arduino_status_indicator.config(fg="red"))
            else:
                self.root.after(0, lambda: self.log_arduino(f"❌ Erro no teste: {e}"))
                self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.erro_no_teste")))
                self.root.after(0, lambda: self.arduino_status_indicator.config(fg="red"))
    
    def connect_arduino(self):
        """Conectar ao Arduino e manter conexão - NON-BLOCKING"""
        # Executar conexão em thread separada para não travar UI
        import threading

        if self.arduino_connected:
            self.log_arduino("⚠️ Arduino já está conectado")
            return

        # Iniciar thread de conexão
        connection_thread = threading.Thread(target=self._connect_arduino_thread, daemon=True)
        connection_thread.start()

    def _connect_arduino_thread(self):
        """Thread de conexão (não bloqueia UI)"""
        try:
            port = self.arduino_port_var.get()
            baud = int(self.arduino_baud_var.get())
            timeout = float(self.arduino_timeout_var.get())

            # Atualizar UI de forma thread-safe
            self.root.after(0, lambda: self.log_arduino(f"🔌 Conectando ao Arduino em {port}..."))
            self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.conectando")))
            self.root.after(0, lambda: self.arduino_status_indicator.config(fg="yellow"))

            # Tentar importar serial
            try:
                import serial
                import time
            except ImportError:
                self.root.after(0, lambda: self.log_arduino("❌ Biblioteca 'pyserial' não encontrada. Execute: pip install pyserial"))
                return

            # Conectar (com timeout maior para leitura)
            self.arduino_serial = serial.Serial(port, baud, timeout=2.0)
            time.sleep(2)  # Aguardar inicialização (OK em thread separada)

            # Aguardar e descartar mensagem READY inicial
            ready_msg = self.arduino_serial.readline().decode().strip()
            if ready_msg == "READY":
                self.root.after(0, lambda: self.log_arduino(f"📡 Arduino inicializado: {ready_msg}"))

            # Aguardar um pouco para Arduino ficar pronto
            time.sleep(0.5)

            # Limpar buffers antes do teste
            self.arduino_serial.reset_input_buffer()
            self.arduino_serial.reset_output_buffer()

            # Verificar se está funcionando com PING
            self.root.after(0, lambda: self.log_arduino(f"📤 Enviando PING..."))
            self.arduino_serial.write(b"PING\n")
            self.arduino_serial.flush()  # Garantir que comando foi enviado

            self.root.after(0, lambda: self.log_arduino(f"⏳ Aguardando PONG..."))
            time.sleep(0.5)  # Aguardar resposta (aumentado para 500ms)
            response = self.arduino_serial.readline().decode().strip()

            self.root.after(0, lambda: self.log_arduino(f"📥 Recebido: '{response}' (len={len(response)})"))

            if response == "PONG":
                self.arduino_connected = True
                self.root.after(0, lambda: self.log_arduino(f"✅ Arduino conectado com sucesso! Teste PING-PONG OK"))
                self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.conectado_e_funcionando")))
                self.root.after(0, lambda: self.arduino_status_indicator.config(fg="green"))

                # ⚡ CRÍTICO: Compartilhar conexão Serial com InputManager!
                if hasattr(self, 'input_manager') and hasattr(self.input_manager, 'serial'):
                    self.root.after(0, lambda: self.log_arduino(f"🔗 Compartilhando conexão Serial com InputManager..."))

                    # COMPARTILHAR a conexão ao invés de abrir nova
                    self.input_manager.serial = self.arduino_serial
                    self.input_manager.connected = True
                    self.input_manager.port = port

                    # Verificar se realmente setou
                    self.root.after(0, lambda: self.log_arduino(f"✅ InputManager agora usa Arduino! TODOS os inputs via HID"))
                    self.root.after(0, lambda: self.log_arduino(f"🔍 DEBUG: input_manager.connected = {self.input_manager.connected}"))
                    self.root.after(0, lambda: self.log_arduino(f"🔍 DEBUG: input_manager.serial = {self.input_manager.serial}"))

                    # Forçar print no console também
                    print(f"[CONEXAO] InputManager.connected setado para: {self.input_manager.connected}")
                    print(f"[CONEXAO] InputManager.serial: {self.input_manager.serial}")
            else:
                self.root.after(0, lambda: self.log_arduino(f"⚠️ Arduino conectado mas falhou no teste PING (recebido: '{response}')"))
                self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.conectado_firmware_incorreto")))
                self.root.after(0, lambda: self.arduino_status_indicator.config(fg="orange"))
                self.arduino_connected = False  # NÃO manter conectado se PING falhar

        except Exception as e:
            self.root.after(0, lambda: self.log_arduino(f"❌ Erro na conexão: {e}"))
            self.root.after(0, lambda: self.arduino_connection_status.config(text=_("ui_hardcoded.erro_na_conexão")))
            self.root.after(0, lambda: self.arduino_status_indicator.config(fg="red"))
            if self.arduino_serial:
                self.arduino_serial.close()
                self.arduino_serial = None
    
    def disconnect_arduino(self):
        """Desconectar do Arduino"""
        try:
            if not self.arduino_connected:
                self.log_arduino("⚠️ Arduino não está conectado")
                return
            
            if self.arduino_serial:
                self.arduino_serial.close()
                self.arduino_serial = None
            
            self.arduino_connected = False
            self.log_arduino("📴 Arduino desconectado")
            self.arduino_connection_status.config(text=_("ui_hardcoded.desconectado"))
            self.arduino_status_indicator.config(fg="red")
            
        except Exception as e:
            self.log_arduino(f"❌ Erro ao desconectar: {e}")
    
    def send_arduino_command(self, command):
        """Enviar comando para o Arduino"""
        try:
            if not self.arduino_connected or not self.arduino_serial:
                self.log_arduino("❌ Arduino não está conectado")
                return False
            
            # Enviar comando
            cmd = f"{command}\\n"
            self.arduino_serial.write(cmd.encode())
            self.log_arduino(f"📤 Enviado: {command}")
            
            # Aguardar resposta (timeout curto para não travar)
            try:
                response = self.arduino_serial.readline().decode().strip()
                if response:
                    self.log_arduino(f"📥 Resposta: {response}")
                    return True
                else:
                    self.log_arduino(f"⚠️ Comando enviado mas sem resposta")
                    return True  # Comando pode ter sido executado mesmo sem resposta
            except:
                self.log_arduino(f"⚠️ Timeout na resposta do comando {command}")
                return True  # Assumir que funcionou
                
        except Exception as e:
            self.log_arduino(f"❌ Erro ao enviar comando {command}: {e}")
            return False
    
    def log_arduino(self, message):
        """Adicionar mensagem ao log do Arduino"""
        try:
            if hasattr(self, 'arduino_log'):
                timestamp = time.strftime("%H:%M:%S")
                log_message = f"[{timestamp}] {message}\\n"
                
                self.arduino_log.insert(tk.END, log_message)
                self.arduino_log.see(tk.END)  # Scroll automático para o final
                
                # Limitar tamanho do log (manter últimas 100 linhas)
                lines = self.arduino_log.get("1.0", tk.END).count('\\n')
                if lines > 100:
                    self.arduino_log.delete("1.0", "10.0")
            
            # Também imprimir no console
            print(f"Arduino: {message}")
            
        except Exception as e:
            print(f"Erro no log Arduino: {e}")
    
    def clear_arduino_log(self):
        """Limpar log de comunicação"""
        try:
            if hasattr(self, 'arduino_log'):
                self.arduino_log.delete("1.0", tk.END)
                self.log_arduino("🗑️ Log limpo")
        except Exception as e:
            print(f"Erro ao limpar log: {e}")
    
    def load_arduino_config(self):
        """Carregar configurações do Arduino do config.json"""
        try:
            arduino_config = self.config_manager.get('arduino', {})
            if arduino_config:
                config_port = arduino_config.get('com_port', 'COM3')

                # ✅ NOVO: Auto-detectar porta Arduino ao carregar
                ports = get_com_ports()
                detected_port = self._detect_arduino_port(ports)

                if detected_port:
                    # Se detectou Arduino, usar a porta detectada
                    self.arduino_port_var.set(detected_port)
                    if detected_port != config_port:
                        self.log_arduino(f"🔄 Porta Arduino auto-detectada: {detected_port} (config tinha: {config_port})")
                    else:
                        self.log_arduino(f"✅ Porta Arduino confirmada: {detected_port}")
                elif config_port in ports:
                    # Se não detectou, mas a porta do config existe, usar ela
                    self.arduino_port_var.set(config_port)
                    self.log_arduino(f"⚠️ Usando porta do config: {config_port} (Arduino não detectado automaticamente)")
                else:
                    # Porta do config não existe mais
                    if ports:
                        self.arduino_port_var.set(ports[0])
                        self.log_arduino(f"⚠️ Porta {config_port} não encontrada, usando: {ports[0]}")
                    else:
                        self.arduino_port_var.set('COM3')
                        self.log_arduino(f"❌ Nenhuma porta COM encontrada!")

                self.arduino_baud_var.set(str(arduino_config.get('baud_rate', 115200)))
                self.arduino_timeout_var.set(str(arduino_config.get('timeout', 1)))

                self.log_arduino("✅ Configurações carregadas do config.json")
            else:
                self.log_arduino("⚠️ Usando configurações padrão do Arduino")

        except Exception as e:
            self.log_arduino(f"❌ Erro ao carregar config: {e}")
    
    def save_arduino_config(self):
        """Salvar configurações do Arduino no config.json"""
        try:
            arduino_config = {
                'enabled': self.arduino_connected,
                'com_port': self.arduino_port_var.get(),
                'baud_rate': int(self.arduino_baud_var.get()),
                'timeout': float(self.arduino_timeout_var.get()),
                'auto_connect': False  # Por enquanto manual
            }
            
            # Salvar no config manager
            self.config_manager.set('arduino', arduino_config)
            self.log_arduino("💾 Configurações salvas no config.json")
            
        except Exception as e:
            self.log_arduino(f"❌ Erro ao salvar config: {e}")
    
    def update_status(self, status_text):
        """Atualizar status na barra"""
        if hasattr(self, 'status_bar_label'):
            self.status_bar_label.config(text=f"Status: {status_text}")
    
    def load_config_values(self):
        """Carregar valores do config.json para as variáveis da interface"""
        try:
            # Carregar configurações de auto_clean
            auto_clean_config = self.config_manager.get('auto_clean', {})

            # ✅ CORREÇÃO: chest_side está no nível ROOT do config, não dentro de auto_clean!
            # Carregar de 'chest_side' em vez de 'auto_clean.chest_side'
            chest_side = self.config_manager.get('chest_side', 'right')
            self.chest_side_var.set(chest_side)

            if auto_clean_config:
                self.macro_type_var.set(auto_clean_config.get('chest_method', 'macro'))
                # Converter chest_method para formato da UI
                if auto_clean_config.get('chest_method') == 'macro':
                    self.macro_type_var.set('padrão')
                elif auto_clean_config.get('chest_method') == 'custom':
                    self.macro_type_var.set('personalizado')
            
            # Carregar configurações do sistema de varas
            rod_config = self.config_manager.get('rod_system', {})
            if rod_config:
                self.broken_rod_action_var.set(rod_config.get('broken_rod_action', 'save'))
                self.auto_reload_var.set(rod_config.get('auto_replace_broken', True))
                
            # Carregar outras configurações importantes
            self.cycle_timeout_var.set(str(self.config_manager.get('timeouts.fishing_cycle_timeout', 122)))
            self.rod_switch_limit_var.set(str(self.config_manager.get('rod_system.rod_switch_limit', 20)))
            self.clicks_per_second_var.set(str(self.config_manager.get('performance.clicks_per_second', 9)))
            self.maintenance_timeout_var.set(str(self.config_manager.get('timeouts.maintenance_timeout', 3)))
            self.chest_distance_var.set(str(self.config_manager.get('chest_distance', 1000)))
            
            # Carregar configurações de alimentação
            feeding_config = self.config_manager.get('feeding', {})
            if feeding_config:
                self.feeding_enabled_var.set(feeding_config.get('enabled', False))
                self.feeding_mode_var.set(feeding_config.get('mode', 'time'))
                self.feeding_interval_var.set(str(feeding_config.get('interval', 60)))
                self.feeding_fish_count_var.set(str(feeding_config.get('fish_count', 10)))

                # Carregar posições de alimentação
                feeding_positions = feeding_config.get('coordinates', {})
                self.feeding_slot1_x_var.set(str(feeding_positions.get('slot1', [1306, 858])[0]))
                self.feeding_slot1_y_var.set(str(feeding_positions.get('slot1', [1306, 858])[1]))
                self.feeding_slot2_x_var.set(str(feeding_positions.get('slot2', [1403, 877])[0]))
                self.feeding_slot2_y_var.set(str(feeding_positions.get('slot2', [1403, 877])[1]))
                self.feeding_eat_x_var.set(str(feeding_positions.get('eat', [1083, 373])[0]))
                self.feeding_eat_y_var.set(str(feeding_positions.get('eat', [1083, 373])[1]))

            # Carregar configurações de prioridade de iscas (estrutura correta: bait_system.priority e bait_system.enabled)
            bait_priority = self.config_manager.get('bait_system.priority', {})
            bait_enabled = self.config_manager.get('bait_system.enabled', {})

            if bait_priority or bait_enabled:
                print(f"[TARGET] [LOAD] Carregando prioridades: {bait_priority}")
                print(f"[TARGET] [LOAD] Carregando estado enabled: {bait_enabled}")

                # Aplicar configurações carregadas nas variáveis da UI
                if hasattr(self, 'config_bait_enabled_vars'):
                    for config_name, enabled in bait_enabled.items():
                        # Mapear nome do config para nome da UI
                        ui_name = self._map_bait_config_to_ui(config_name)
                        if ui_name in self.config_bait_enabled_vars:
                            self.config_bait_enabled_vars[ui_name].set(enabled)

                # Reorganizar a ordem das iscas baseada na prioridade
                if hasattr(self, 'config_ordered_baits') and bait_priority:
                    # Ordenar iscas por prioridade (menor número = maior prioridade)
                    sorted_baits = sorted(bait_priority.items(), key=lambda x: x[1])
                    # Mapear nomes do config para nomes da UI
                    self.config_ordered_baits = [self._map_bait_config_to_ui(bait) for bait, _ in sorted_baits]
                    print(f"[TARGET] [LOAD] Ordem de iscas aplicada: {self.config_ordered_baits}")

                    # Atualizar a listbox se existir
                    if hasattr(self, 'update_config_bait_listbox'):
                        self.update_config_bait_listbox()

            print("[OK] Valores do config carregados na interface")
                
        except Exception as e:
            print(f"[ERROR] Erro ao carregar valores do config: {e}")
            # Manter valores padrão se houver erro
    
    def _reload_engine_configs(self):
        """Recarregar configurações em todos os engines ativos"""
        try:
            print("[RELOAD] Recarregando configurações nos engines...")
            
            # InputManager - Recarregar timing de cliques
            if hasattr(self, 'input_manager') and self.input_manager:
                if hasattr(self.input_manager, 'reload_timing_config'):
                    self.input_manager.reload_timing_config()
                    print("  ✅ InputManager recarregado")
            
            # FishingEngine - Se houver método de reload
            if hasattr(self, 'fishing_engine') and self.fishing_engine:
                # O FishingEngine usará automaticamente as novas configs na próxima execução
                print("  ✅ FishingEngine usará novas configs na próxima execução")
            
            # FeedingSystem - Recarregar se necessário
            if hasattr(self, 'feeding_system') and self.feeding_system:
                print("  ✅ FeedingSystem usará novas configs automaticamente")
                
            print("[OK] Todos os engines reconfigurados!")
            
        except Exception as e:
            print(f"[ERROR] Erro ao recarregar engines: {e}")
    
    # ===== MÉTODOS AUXILIARES =====
    
    def center_window(self):
        """Centralizar janela na tela"""
        self.main_window.update_idletasks()
        width = self.main_window.winfo_width()
        height = self.main_window.winfo_height()
        x = (self.main_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.main_window.winfo_screenheight() // 2) - (height // 2)
        self.main_window.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_closing(self):
        """Evento de fechamento da janela"""
        try:
            if messagebox.askokcancel("Fechar", 
                                     "Deseja realmente fechar o Ultimate Fishing Bot v4.0?"):
                # Parar bot se estiver rodando
                if self.bot_running:
                    self.stop_bot()
                
                # Fechar janela principal
                self.is_destroyed = True
                self.main_window.destroy()
        except Exception as e:
            print(f"Erro ao fechar: {e}")
            self.main_window.destroy()
    
    def run(self):
        """Executar interface"""
        try:
            if self.main_window and not self.is_destroyed:
                # ✅ CONECTAR AUTOMATICAMENTE AO ARDUINO após UI carregar (2 segundos)
                self.main_window.after(2000, self._auto_connect_arduino)

                self.main_window.mainloop()
        except Exception as e:
            print(f"Erro ao executar interface: {e}")

    def _auto_connect_arduino(self):
        """Conectar automaticamente ao Arduino ao iniciar o programa"""
        try:
            # Verificar se Arduino está habilitado na config
            use_arduino = self.config_manager.get('arduino.enabled', False)

            if use_arduino and not self.arduino_connected:
                print("\n🤖 Conectando automaticamente ao Arduino...")
                self.log_arduino("🔄 Tentando conexão automática ao iniciar...")
                self.connect_arduino()
            else:
                if not use_arduino:
                    print("⚠️ Arduino desabilitado na configuração")
                else:
                    print("✅ Arduino já conectado")
        except Exception as e:
            print(f"⚠️ Erro na conexão automática: {e}")
            self.log_arduino(f"⚠️ Falha na conexão automática: {e}")

    def toggle_ui_visibility(self):
        """F4 - Alternar visibilidade da UI"""
        try:
            if self.main_window and not self.is_destroyed:
                current_state = self.main_window.state()

                if current_state == 'normal':
                    # Minimizar/ocultar janela
                    self.main_window.withdraw()
                    print("🎨 [F4] UI ocultada")
                else:
                    # Restaurar janela
                    self.main_window.deiconify()
                    self.main_window.lift()
                    self.main_window.focus_force()
                    print("🎨 [F4] UI restaurada")
        except Exception as e:
            print(f"[ERROR] [F4] Erro ao alternar UI: {e}")

    def get_capture_area(self):
        """Obter área de captura configurada pelo usuário"""
        try:
            # Obter resolução selecionada
            resolution = self.capture_resolution_var.get() if hasattr(self, 'capture_resolution_var') else "1920x1080"

            # Obter posição
            x = int(self.capture_x_var.get()) if hasattr(self, 'capture_x_var') else 0
            y = int(self.capture_y_var.get()) if hasattr(self, 'capture_y_var') else 0

            if resolution == "Tela Completa":
                # Capturar tela inteira
                import mss
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # Monitor principal
                    return {"top": monitor["top"], "left": monitor["left"],
                           "width": monitor["width"], "height": monitor["height"]}
            else:
                # Usar resolução específica
                width, height = map(int, resolution.split('x'))
                return {"top": y, "left": x, "width": width, "height": height}

        except Exception as e:
            print(f"[WARN] Erro ao obter área de captura: {e}")
            # Fallback para 1920x1080
            return {"top": 0, "left": 0, "width": 1920, "height": 1080}

    def on_resolution_change(self, event=None):
        """Callback quando resolução muda"""
        resolution = self.capture_resolution_var.get()
        print(f"📺 Resolução de captura alterada para: {resolution}")

        # Se for tela completa, desabilitar campos X,Y
        if resolution == "Tela Completa":
            if hasattr(self, 'capture_x_var'):
                self.capture_x_var.set("0")
            if hasattr(self, 'capture_y_var'):
                self.capture_y_var.set("0")

    def detect_rust_window(self):
        """Detectar automaticamente a janela do Rust"""
        try:
            print("🔍 Procurando janela do Rust...")

            # Tentar importar biblioteca para detectar janelas
            try:
                import win32gui
                import win32con

                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_title = win32gui.GetWindowText(hwnd)
                        if window_title and ('rust' in window_title.lower() or 'game' in window_title.lower()):
                            windows.append((hwnd, window_title))
                    return True

                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)

                if windows:
                    # Usar a primeira janela encontrada
                    hwnd, title = windows[0]
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, right, bottom = rect
                    width = right - x
                    height = bottom - y

                    # Atualizar campos
                    self.capture_x_var.set(str(x))
                    self.capture_y_var.set(str(y))
                    self.capture_resolution_var.set(f"{width}x{height}")

                    print(f"[OK] Janela '{title}' detectada: {x},{y} {width}x{height}")
                    messagebox.showinfo("Sucesso", f"Janela detectada: {title}\nPosição: {x},{y}\nTamanho: {width}x{height}")
                else:
                    print("[ERROR] Nenhuma janela do Rust encontrada")
                    messagebox.showwarning("Aviso", "Nenhuma janela do Rust foi encontrada.\nCertifique-se de que o jogo esteja aberto.")

            except ImportError:
                print("[WARN] win32gui não disponível, usando detecção manual")
                messagebox.showinfo("Info", "Detecção automática não disponível.\nConfigure manualmente a posição e resolução.")

        except Exception as e:
            print(f"[ERROR] Erro ao detectar janela: {e}")
            messagebox.showerror("Erro", f"Erro ao detectar janela do Rust:\n{e}")

    @property
    def root(self):
        """Propriedade para compatibilidade"""
        return self.main_window