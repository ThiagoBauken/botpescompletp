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

# Imports essenciais com fallback
try:
    import cv2
    import numpy as np
    import pyautogui
    import keyboard
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV/PyAutoGUI não disponível - funcionalidades limitadas")

# Sistema de internacionalização
try:
    from utils.i18n import i18n, _
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def _(text, **kwargs): 
        return text

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
    def get(self, key, default=None): return default
    def set(self, key, value): pass
    def get_template_confidence(self, template): return 0.7
    def get_feeding_position(self, slot): return (1306, 858)

class FishingBotUI:
    """Interface principal - 8 ABAS CONFORME ESPECIFICADO"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager if config_manager else MockConfig()
        self.notebook = None
        self.is_destroyed = False
        
        # Criar janela principal PRIMEIRO (antes das variáveis tkinter)
        self.main_window = tk.Tk()
        self.main_window.title("🎣 Ultimate Fishing Bot v4.0")
        self.main_window.geometry("900x700")
        self.main_window.configure(bg='#1a1a1a')
        self.main_window.resizable(True, True)
        
        # Estado do bot
        self.bot_running = False
        self.bot_paused = False
        
        # Stats e labels
        self.stats_labels = {}
        
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
        self.macro_type_var = tk.StringVar(value="standard")
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
        self.feeding_auto_detect_var = tk.BooleanVar(value=True)
        self.feeding_slot1_x_var = tk.StringVar(value="1306")
        self.feeding_slot1_y_var = tk.StringVar(value="858")
        self.feeding_slot2_x_var = tk.StringVar(value="1403")
        self.feeding_slot2_y_var = tk.StringVar(value="877")
        
        # Anti-detection tab
        self.anti_detection_enabled_var = tk.BooleanVar(value=True)
        self.click_delay_min_var = tk.StringVar(value="80")
        self.click_delay_max_var = tk.StringVar(value="150")
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
        
        # Inicializar UI
        self.setup_ui_components()
    
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
            
            # Cores melhoradas para melhor contraste e legibilidade
            style.configure('TNotebook', background='#2d2d2d')
            style.configure('TNotebook.Tab',
                           background='#404040',
                           foreground='#e0e0e0',  # Texto claro para fundo escuro padrão
                           padding=[12, 8],
                           font=('Arial', 9, 'bold'))
            style.map('TNotebook.Tab',
                     background=[('selected', '#0078d4'), ('active', '#555555')],
                     foreground=[('selected', '#000000'), ('active', '#ffffff')])  # Texto preto quando selecionado (fundo azul claro)
            
            # Configurar outros estilos para melhor legibilidade
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TButton', font=('Arial', 9, 'bold'))
            style.configure('TEntry', font=('Arial', 9))
            style.configure('TCheckbutton', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TScale', background='#2d2d2d')
            
        except Exception as e:
            print(f"Erro ao configurar tema: {e}")
    
    def create_interface(self):
        """Criar interface com 8 abas na ordem especificada"""
        try:
            # Frame principal
            main_frame = tk.Frame(self.main_window, bg='#1a1a1a')
            main_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Título
            title_label = tk.Label(main_frame,
                                 text="🎣 Ultimate Fishing Bot v4.0",
                                 font=('Arial', 18, 'bold'),
                                 fg='#00aaff',
                                 bg='#1a1a1a')
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
            self.create_language_tab()       # Aba 6: 🌍 Idioma - Radio buttons PT/EN/RU, detecção automática
            self.create_hotkeys_tab()        # Aba 7: ⌨️ Hotkeys - Entries para teclas, botões de captura
            self.create_help_tab()           # Aba 8: ❓ Ajuda - Documentação e troubleshooting
            
            # Criar barra de status no final (canto inferior direito)
            self.create_status_bar()
            
        except Exception as e:
            print(f"Erro ao criar interface: {e}")
    
    def create_control_tab(self):
        """Aba 1: 🎮 Controle - Status, estatísticas, botões Start/Stop/Pause"""
        control_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(control_frame, text='🎮 Controle')

        # Status do Bot
        status_frame = tk.LabelFrame(control_frame, text="🤖 Status do Bot",
                                   fg='white', bg='#1a1a1a',
                                   font=('Arial', 12, 'bold'))
        status_frame.pack(fill='x', pady=10, padx=10)

        self.status_label = tk.Label(status_frame, text="⚫ Parado",
                                   font=('Arial', 14, 'bold'),
                                   fg='red', bg='#1a1a1a')
        self.status_label.pack(pady=10)

        # Estatísticas Detalhadas
        stats_frame = tk.LabelFrame(control_frame, text="📊 Estatísticas Detalhadas",
                                  fg='white', bg='#1a1a1a',
                                  font=('Arial', 12, 'bold'))
        stats_frame.pack(fill='x', pady=10, padx=10)

        # Grid para organizar estatísticas em duas colunas
        stats_grid = tk.Frame(stats_frame, bg='#1a1a1a')
        stats_grid.pack(pady=10, padx=10)

        # Coluna 1 - Estatísticas principais
        col1_frame = tk.Frame(stats_grid, bg='#1a1a1a')
        col1_frame.grid(row=0, column=0, padx=20, sticky='n')

        self.stats_labels = {}

        # Peixes capturados
        fish_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        fish_frame.pack(anchor='w', pady=2)
        tk.Label(fish_frame, text="🐟 Peixes capturados:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['fish'] = tk.Label(fish_frame, text="0",
                                            fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['fish'].pack(side='left')

        # Tempo de sessão
        time_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        time_frame.pack(anchor='w', pady=2)
        tk.Label(time_frame, text="⏱️ Tempo de sessão:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['session_time'] = tk.Label(time_frame, text="00:00:00",
                                                    fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['session_time'].pack(side='left')

        # Peixes por hora
        rate_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        rate_frame.pack(anchor='w', pady=2)
        tk.Label(rate_frame, text="⚡ Peixes/hora:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['fish_per_hour'] = tk.Label(rate_frame, text="0",
                                                     fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['fish_per_hour'].pack(side='left')

        # Taxa de sucesso
        success_frame = tk.Frame(col1_frame, bg='#1a1a1a')
        success_frame.pack(anchor='w', pady=2)
        tk.Label(success_frame, text="🎯 Taxa de sucesso:",
                fg='#00aaff', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['success_rate'] = tk.Label(success_frame, text="0%",
                                                    fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['success_rate'].pack(side='left')

        # Coluna 2 - Contadores de eventos
        col2_frame = tk.Frame(stats_grid, bg='#1a1a1a')
        col2_frame.grid(row=0, column=1, padx=20, sticky='n')

        # Alimentações
        feed_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        feed_frame.pack(anchor='w', pady=2)
        tk.Label(feed_frame, text="🍖 Alimentações:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['feeds'] = tk.Label(feed_frame, text="0",
                                             fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['feeds'].pack(side='left')

        # Limpezas
        clean_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        clean_frame.pack(anchor='w', pady=2)
        tk.Label(clean_frame, text="🧹 Limpezas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['cleans'] = tk.Label(clean_frame, text="0",
                                              fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['cleans'].pack(side='left')

        # Varas quebradas
        broken_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        broken_frame.pack(anchor='w', pady=2)
        tk.Label(broken_frame, text="🔧 Varas quebradas:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['broken_rods'] = tk.Label(broken_frame, text="0",
                                                   fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['broken_rods'].pack(side='left')

        # Timeouts
        timeout_frame = tk.Frame(col2_frame, bg='#1a1a1a')
        timeout_frame.pack(anchor='w', pady=2)
        tk.Label(timeout_frame, text="⏱️ Timeouts:",
                fg='#ffaa00', bg='#1a1a1a', font=('Arial', 10, 'bold'), width=20, anchor='w').pack(side='left')
        self.stats_labels['timeouts'] = tk.Label(timeout_frame, text="0",
                                                fg='white', bg='#1a1a1a', font=('Arial', 10))
        self.stats_labels['timeouts'].pack(side='left')

        # Botões de Controle
        button_frame = tk.Frame(control_frame, bg='#1a1a1a')
        button_frame.pack(pady=30)

        self.start_button = tk.Button(button_frame, text="🚀 Iniciar", command=self.start_bot,
                                     bg='#28a745', fg='white', font=('Arial', 12, 'bold'),
                                     padx=20, pady=8)
        self.start_button.pack(side='left', padx=10)

        self.pause_button = tk.Button(button_frame, text="⏸️ Pausar", command=self.pause_bot,
                                     bg='#ffc107', fg='black', font=('Arial', 12, 'bold'),
                                     padx=20, pady=8)
        self.pause_button.pack(side='left', padx=10)

        self.stop_button = tk.Button(button_frame, text="🛑 Parar", command=self.stop_bot,
                                    bg='#dc3545', fg='white', font=('Arial', 12, 'bold'),
                                    padx=20, pady=8)
        self.stop_button.pack(side='left', padx=10)

        # Sistema de Limpeza Automática
        auto_frame = tk.LabelFrame(control_frame, text="🔄 Limpeza Automática",
                                 fg='white', bg='#1a1a1a',
                                 font=('Arial', 12, 'bold'))
        auto_frame.pack(fill='x', pady=10, padx=10)

        # Configuração a cada X pescas
        fish_frame = tk.Frame(auto_frame, bg='#1a1a1a')
        fish_frame.pack(fill='x', padx=10, pady=5)

        tk.Label(fish_frame, text="🐟 Limpar inventário a cada:",
                fg='white', bg='#1a1a1a', font=('Arial', 10)).pack(side='left')

        self.auto_clean_interval_var = tk.StringVar(value="10")
        tk.Entry(fish_frame, textvariable=self.auto_clean_interval_var, width=5).pack(side='left', padx=5)

        tk.Label(fish_frame, text="pescas",
                fg='white', bg='#1a1a1a', font=('Arial', 10)).pack(side='left')

        # Toggle para ativação
        self.auto_clean_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_frame, text="✅ Ativar limpeza automática",
                      variable=self.auto_clean_enabled_var,
                      bg='#1a1a1a', fg='white', font=('Arial', 10),
                      selectcolor='#333333').pack(padx=10, pady=5)
        
        # Toggle para limpeza de iscas
        self.auto_clean_baits_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(auto_frame, text="🎣 Incluir limpeza de iscas (manter apenas 4)",
                      variable=self.auto_clean_baits_enabled_var,
                      bg='#1a1a1a', fg='#ffaa00', font=('Arial', 10),
                      selectcolor='#333333').pack(padx=10, pady=2)

        # Status da limpeza
        self.auto_clean_status_label = tk.Label(auto_frame,
                                              text="📊 Próxima limpeza em: 10 pescas",
                                              font=('Arial', 10),
                                              fg='#28a745', bg='#1a1a1a')
        self.auto_clean_status_label.pack(pady=5)
    
    def create_config_tab(self):
        """Aba 2: ⚙️ Configurações - Timeout, lado do baú, varas quebradas"""
        config_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(config_frame, text='⚙️ Configurações')
        
        # Título
        title_label = tk.Label(config_frame,
                              text="⚙️ Configurações Gerais do Sistema",
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
        timeout_frame = tk.LabelFrame(scrollable_frame, text="⏱️ Timeouts e Ciclos",
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        timeout_frame.pack(fill='x', padx=20, pady=10)
        
        # Timeout do ciclo
        cycle_frame = tk.Frame(timeout_frame, bg='#2a2a2a')
        cycle_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(cycle_frame, text="Timeout do ciclo (segundos):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(cycle_frame, textvariable=self.cycle_timeout_var, width=8).pack(side='left', padx=5)
        
        # ========== CONFIGURAÇÕES DO BAÚ ==========
        chest_frame = tk.LabelFrame(scrollable_frame, text="📦 Configurações do Baú",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        chest_frame.pack(fill='x', padx=20, pady=10)
        
        # Lado do baú
        side_frame = tk.Frame(chest_frame, bg='#2a2a2a')
        side_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(side_frame, text="Lado do baú:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        
        chest_combo = ttk.Combobox(side_frame, textvariable=self.chest_side_var, 
                                  values=['left', 'right'], state="readonly", width=10)
        chest_combo.pack(side='left', padx=5)
        
        # ========== SISTEMA DE VARAS ==========
        rods_frame = tk.LabelFrame(scrollable_frame, text="🎣 Sistema de Varas",
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        rods_frame.pack(fill='x', padx=20, pady=10)
        
        # Auto reload
        tk.Checkbutton(rods_frame, text="🔄 Auto-reload de varas",
                      variable=self.auto_reload_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Ação para vara quebrada
        broken_frame = tk.Frame(rods_frame, bg='#2a2a2a')
        broken_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(broken_frame, text="Ação para vara quebrada:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        
        broken_combo = ttk.Combobox(broken_frame, textvariable=self.broken_rod_action_var,
                                   values=['discard', 'save', 'repair'], state="readonly", width=10)
        broken_combo.pack(side='left', padx=5)
        
        # ========== FOCO AUTOMÁTICO ==========
        focus_frame = tk.LabelFrame(scrollable_frame, text="🖱️ Foco Automático",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        focus_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(focus_frame, text="🎯 Ativar foco automático na janela do jogo",
                      variable=self.auto_focus_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_feeding_tab(self):
        """Aba 3: 🍖 Alimentação - Modos de detecção, triggers, posições"""
        feeding_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(feeding_frame, text='🍖 Alimentação')
        
        # Título
        title_label = tk.Label(feeding_frame,
                              text="🍖 Sistema de Alimentação Automática",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(feeding_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(feeding_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== ALIMENTAÇÃO HABILITADA ==========
        enable_frame = tk.LabelFrame(scrollable_frame, text="🎛️ Controle Geral",
                                    bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        enable_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(enable_frame, text="✅ Alimentação automática ativada",
                      variable=self.feeding_enabled_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # ========== MODOS DE DETECÇÃO ==========
        detection_frame = tk.LabelFrame(scrollable_frame, text="🔍 Modos de Detecção",
                                       bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        detection_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(detection_frame, text="🤖 Auto-detectar posição de alimentação",
                      variable=self.feeding_auto_detect_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # ========== TRIGGERS DE ALIMENTAÇÃO ==========
        trigger_frame = tk.LabelFrame(scrollable_frame, text="⚡ Triggers de Alimentação",
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        trigger_frame.pack(fill='x', padx=20, pady=10)
        
        # Modo de trigger
        mode_frame = tk.Frame(trigger_frame, bg='#2a2a2a')
        mode_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(mode_frame, text="Modo de trigger:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        
        trigger_combo = ttk.Combobox(mode_frame, textvariable=self.feeding_trigger_mode_var,
                                    values=['catches', 'time'], state="readonly", width=10)
        trigger_combo.pack(side='left', padx=5)
        
        # Trigger por capturas
        catches_frame = tk.Frame(trigger_frame, bg='#2a2a2a')
        catches_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(catches_frame, text="Alimentar a cada:",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(catches_frame, textvariable=self.feeding_trigger_catches_var, width=5).pack(side='left', padx=5)
        tk.Label(catches_frame, text="capturas",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        
        # ========== POSIÇÕES DOS SLOTS ==========
        positions_frame = tk.LabelFrame(scrollable_frame, text="📍 Posições dos Slots",
                                       bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        positions_frame.pack(fill='x', padx=20, pady=10)
        
        # Slot 1
        slot1_frame = tk.Frame(positions_frame, bg='#2a2a2a')
        slot1_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(slot1_frame, text="Slot 1 (X,Y):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(slot1_frame, textvariable=self.feeding_slot1_x_var, width=6).pack(side='left', padx=2)
        tk.Entry(slot1_frame, textvariable=self.feeding_slot1_y_var, width=6).pack(side='left', padx=2)
        
        # Slot 2
        slot2_frame = tk.Frame(positions_frame, bg='#2a2a2a')
        slot2_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(slot2_frame, text="Slot 2 (X,Y):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(slot2_frame, textvariable=self.feeding_slot2_x_var, width=6).pack(side='left', padx=2)
        tk.Entry(slot2_frame, textvariable=self.feeding_slot2_y_var, width=6).pack(side='left', padx=2)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_confidence_tab(self):
        """Aba 4: 🎯 Templates - Sliders de confiança, categorias"""
        confidence_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(confidence_frame, text='🎯 Templates')
        
        # Título
        title_label = tk.Label(confidence_frame,
                              text="🎯 Configuração de Confiança por Template",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(confidence_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(confidence_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== TEMPLATES CRÍTICOS ==========
        critical_frame = tk.LabelFrame(scrollable_frame, text="🔥 Templates Críticos",
                                      bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        critical_frame.pack(fill='x', padx=20, pady=10)
        
        critical_templates = ['catch', 'comiscavara', 'semiscavara', 'varaquebrada']
        
        for template in critical_templates:
            self.create_confidence_slider(critical_frame, template, is_critical=True)
        
        # ========== TEMPLATES DE ISCAS ==========
        baits_frame = tk.LabelFrame(scrollable_frame, text="🎣 Templates de Iscas",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        baits_frame.pack(fill='x', padx=20, pady=10)
        
        bait_templates = ['carneurso', 'wolfmeat', 'grub', 'worm']
        
        for template in bait_templates:
            self.create_confidence_slider(baits_frame, template)
        
        # ========== TEMPLATES DE PEIXES ==========
        fish_frame = tk.LabelFrame(scrollable_frame, text="🐟 Templates de Peixes",
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        fish_frame.pack(fill='x', padx=20, pady=10)
        
        fish_templates = ['salmon', 'smalltrout', 'shark', 'sardine']
        
        for template in fish_templates:
            self.create_confidence_slider(fish_frame, template)
        
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
        value_label = tk.Label(frame, text="0.70", fg='#00ff00', bg='#2a2a2a', font=('Arial', 9), width=4)
        value_label.pack(side='left', padx=5)
        
        # Atualizar label quando slider muda
        def update_label(*args):
            value_label.config(text=f"{confidence_var.get():.2f}")
        confidence_var.trace('w', update_label)
    
    def create_anti_detection_tab(self):
        """Aba 5: 🛡️ Anti-Detecção - Variação de cliques, pausas naturais"""
        anti_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(anti_frame, text='🛡️ Anti-Detecção')
        
        # Título
        title_label = tk.Label(anti_frame,
                              text="🛡️ Sistema Anti-Detecção e Prioridade de Iscas",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)
        
        # Frame scrollável
        canvas = tk.Canvas(anti_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(anti_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ========== CONTROLE GERAL ==========
        control_frame = tk.LabelFrame(scrollable_frame, text="🎛️ Controle Geral",
                                     bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        control_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Checkbutton(control_frame, text="🛡️ Ativar sistema anti-detecção",
                      variable=self.anti_detection_enabled_var,
                      bg='#2a2a2a', fg='white', selectcolor='#2a2a2a',
                      font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # ========== VARIAÇÃO DE CLIQUES ==========
        click_frame = tk.LabelFrame(scrollable_frame, text="🖱️ Variação de Cliques",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        click_frame.pack(fill='x', padx=20, pady=10)
        
        # Delay mínimo
        delay_min_frame = tk.Frame(click_frame, bg='#2a2a2a')
        delay_min_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(delay_min_frame, text="Delay mínimo (ms):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(delay_min_frame, textvariable=self.click_delay_min_var, width=8).pack(side='left', padx=5)
        
        # Delay máximo
        delay_max_frame = tk.Frame(click_frame, bg='#2a2a2a')
        delay_max_frame.pack(fill='x', padx=10, pady=3)
        tk.Label(delay_max_frame, text="Delay máximo (ms):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(delay_max_frame, textvariable=self.click_delay_max_var, width=8).pack(side='left', padx=5)
        
        # ========== PAUSAS NATURAIS ==========
        pause_frame = tk.LabelFrame(scrollable_frame, text="⏸️ Pausas Naturais",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        pause_frame.pack(fill='x', padx=20, pady=10)
        
        # Tempo de pausa
        pause_time_frame = tk.Frame(pause_frame, bg='#2a2a2a')
        pause_time_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(pause_time_frame, text="Pausa natural a cada (minutos):",
                fg='white', bg='#2a2a2a', font=('Arial', 10)).pack(side='left')
        tk.Entry(pause_time_frame, textvariable=self.natural_pause_time_var, width=8).pack(side='left', padx=5)
        
        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_language_tab(self):
        """Aba 6: 🌍 Idioma - Radio buttons PT/EN/RU, detecção automática"""
        language_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(language_frame, text='🌍 Idioma')

        # Título
        title_label = tk.Label(language_frame,
                              text="🌍 Seleção de Idioma / Language Selection",
                              font=('Arial', 14, 'bold'),
                              fg='#ffaa00', bg='#1a1a1a')
        title_label.pack(pady=15)

        # Frame principal com scroll
        canvas = tk.Canvas(language_frame, bg='#1a1a1a', highlightthickness=0)
        scrollbar = tk.Scrollbar(language_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # ========== SELEÇÃO DE IDIOMA ==========
        lang_frame = tk.LabelFrame(scrollable_frame, text="Idioma Atual / Current Language",
                                   bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        lang_frame.pack(fill='x', padx=20, pady=10)

        # Mostrar idioma atual
        current_lang_label = tk.Label(lang_frame,
                                      text=f"Idioma Atual: {self.current_language.upper()}",
                                      font=('Arial', 11),
                                      fg='#00ff00', bg='#2a2a2a')
        current_lang_label.pack(pady=10)

        # Variable para o idioma selecionado
        self.selected_language_tab = tk.StringVar(value=self.current_language)

        # Radio buttons para os 3 idiomas
        languages = {
            'pt': '🇧🇷 Português (Brasil)', 
            'en': '🇺🇸 English (US)',
            'ru': '🇷🇺 Русский (Russian)'
        }
        
        for lang_code, lang_name in languages.items():
            radio = tk.Radiobutton(lang_frame,
                                   text=lang_name,
                                   variable=self.selected_language_tab,
                                   value=lang_code,
                                   bg='#2a2a2a', fg='white',
                                   selectcolor='#2a2a2a',
                                   font=('Arial', 10),
                                   command=self.on_language_tab_change)
            radio.pack(anchor='w', padx=20, pady=5)

        # ========== APLICAR MUDANÇAS SEM REINICIAR ==========
        apply_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
        apply_frame.pack(fill='x', padx=20, pady=20)

        # Botão aplicar (sem reiniciar)
        apply_btn = tk.Button(apply_frame,
                              text="✅ Aplicar Idioma (Sem Reiniciar)",
                              command=self.apply_language_change_live,
                              bg='#28a745', fg='white',
                              font=('Arial', 12, 'bold'),
                              padx=20, pady=10)
        apply_btn.pack(pady=10)

        # Status label
        self.language_status_label = tk.Label(apply_frame,
                                              text="",
                                              font=('Arial', 9),
                                              fg='#ffc107', bg='#1a1a1a')
        self.language_status_label.pack(pady=5)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_hotkeys_tab(self):
        """Aba 7: ⌨️ Hotkeys - Entries para teclas, botões de captura"""
        hotkeys_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(hotkeys_frame, text='⌨️ Hotkeys')
        
        # Título
        title_label = tk.Label(hotkeys_frame,
                              text="⌨️ Configuração de Teclas Personalizáveis",
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
        main_frame = tk.LabelFrame(scrollable_frame, text="🎮 Controles Principais",
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
        macro_frame = tk.LabelFrame(scrollable_frame, text="🤖 Macros",
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
        test_frame = tk.LabelFrame(scrollable_frame, text="🧪 Testes",
                                  bg='#2a2a2a', fg='white', font=('Arial', 10, 'bold'))
        test_frame.pack(fill='x', padx=20, pady=10)
        
        test_hotkeys = {
            'test_mouse': 'Testar Mouse',
            'test_feeding': 'Testar Alimentação',
            'test_cleaning': 'Testar Limpeza'
        }
        
        for key, desc in test_hotkeys.items():
            self.create_hotkey_row(test_frame, key, self.hotkey_vars[key].get(), desc)
        
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
        capture_btn = tk.Button(frame, text="📋 Capturar",
                               command=lambda k=key: self.capture_hotkey(k),
                               bg='#17a2b8', fg='white', font=('Arial', 8),
                               padx=8, pady=2)
        capture_btn.pack(side='left', padx=5)
    
    def create_help_tab(self):
        """Aba 8: ❓ Ajuda - Documentação e troubleshooting"""
        help_frame = tk.Frame(self.notebook, bg='#1a1a1a')
        self.notebook.add(help_frame, text='❓ Ajuda')
        
        # Título
        title_label = tk.Label(help_frame,
                              text="❓ Ajuda e Documentação",
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
        basic_frame = tk.LabelFrame(scrollable_frame, text="📖 Instruções Básicas",
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
        trouble_frame = tk.LabelFrame(scrollable_frame, text="🔧 Troubleshooting",
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
    
    def create_status_bar(self):
        """Criar barra de status com seletor de idioma no canto direito"""
        try:
            status_frame = ttk.Frame(self.main_window)
            status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
            
            # Status principal (esquerda)
            self.status_label = ttk.Label(status_frame, text="Status: Pronto")
            self.status_label.pack(side=tk.LEFT)
            
            # Frame direito para idioma e versão
            right_frame = ttk.Frame(status_frame)
            right_frame.pack(side=tk.RIGHT)
            
            # Seletor de idioma (canto inferior direito)
            lang_frame = ttk.Frame(right_frame)
            lang_frame.pack(side=tk.RIGHT, padx=10)
            
            ttk.Label(lang_frame, text="🌍").pack(side=tk.LEFT, padx=2)
            
            # StringVar para idioma atual
            self.language_var = tk.StringVar(value=self.current_language)
            
            # Combobox com os 3 idiomas: Português, Inglês, Russo
            self.language_combo = ttk.Combobox(lang_frame, 
                                             textvariable=self.language_var,
                                             values=['pt', 'en', 'ru'], 
                                             state="readonly", 
                                             width=4)
            self.language_combo.pack(side=tk.LEFT, padx=2)
            
            # Bind para troca de idioma funcional
            self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
            
            # Separador
            ttk.Separator(right_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, fill=tk.Y, padx=10)
            
            # Versão
            version_label = ttk.Label(right_frame, text="Ultimate Fishing Bot v4.0")
            version_label.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            print(f"Erro ao criar barra de status: {e}")
    
    # ===== MÉTODOS DE CONTROLE =====
    
    def start_bot(self):
        """Iniciar bot"""
        self.bot_running = True
        self.bot_paused = False
        self.status_label.config(text="🟢 Executando", fg='green')
        print("🚀 Bot iniciado")
    
    def pause_bot(self):
        """Pausar bot"""
        self.bot_paused = not self.bot_paused
        status = "⏸️ Pausado" if self.bot_paused else "🟢 Executando"
        self.status_label.config(text=status)
        print(f"⏸️ Bot {'pausado' if self.bot_paused else 'retomado'}")
    
    def stop_bot(self):
        """Parar bot"""
        self.bot_running = False
        self.bot_paused = False
        self.status_label.config(text="🔴 Parado", fg='red')
        print("🛑 Bot parado")
    
    def capture_hotkey(self, key):
        """Capturar hotkey"""
        print(f"Capturando hotkey para: {key}")
        # Implementar captura de tecla aqui
    
    # ===== MÉTODOS DE IDIOMA =====
    
    def on_language_tab_change(self):
        """Callback para mudança na aba de idioma"""
        try:
            selected = self.selected_language_tab.get()
            print(f"Idioma selecionado na aba: {selected}")
        except Exception as e:
            print(f"Erro no callback da aba: {e}")
    
    def on_language_change(self, event=None):
        """Callback para mudança no combobox da barra de status"""
        try:
            new_language = self.language_var.get()
            self.apply_language_change_live_status(new_language)
        except Exception as e:
            print(f"Erro no callback da barra de status: {e}")
    
    def apply_language_change_live(self):
        """Aplicar mudança de idioma SEM REINICIAR (da aba)"""
        try:
            new_language = self.selected_language_tab.get()
            self.apply_language_change_live_status(new_language)
            
            # Atualizar status na aba
            self.language_status_label.config(text=f"✅ Idioma alterado para: {new_language.upper()}")
            
        except Exception as e:
            print(f"Erro ao aplicar idioma da aba: {e}")
            if hasattr(self, 'language_status_label'):
                self.language_status_label.config(text=f"❌ Erro: {e}")
    
    def apply_language_change_live_status(self, new_language):
        """Aplicar mudança de idioma imediatamente (método central)"""
        try:
            # Atualizar idioma atual
            self.current_language = new_language
            
            # Atualizar config do i18n se disponível
            if I18N_AVAILABLE:
                i18n.set_language(new_language)
            
            # Atualizar config manager
            self.config_manager.set('language', new_language)
            
            # Sincronizar ambos os seletores
            self.language_var.set(new_language)
            if hasattr(self, 'selected_language_tab'):
                self.selected_language_tab.set(new_language)
            
            # Atualizar status na barra de status
            self.update_status(f"Idioma: {new_language.upper()}")
            
            print(f"✅ Idioma alterado para: {new_language} (sem reiniciar)")
            
        except Exception as e:
            print(f"❌ Erro ao aplicar idioma: {e}")
    
    def update_status(self, status_text):
        """Atualizar status na barra"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Status: {status_text}")
    
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
                self.main_window.mainloop()
        except Exception as e:
            print(f"Erro ao executar interface: {e}")
    
    @property
    def root(self):
        """Propriedade para compatibilidade"""
        return self.main_window