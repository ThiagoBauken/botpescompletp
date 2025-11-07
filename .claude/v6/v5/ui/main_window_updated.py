#!/usr/bin/env python3
"""
🎨 Interface Principal - Ultimate Fishing Bot v4.0
Baseada na UI original funcional do botpesca.py com tema escuro
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import serial.tools.list_ports

# Adicionar pasta pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.i18n import i18n, _
    from utils.config_manager import ConfigManager
    from utils.logging_manager import setup_logging
except ImportError as e:
    print(f"Import error: {e}")
    # Fallback simples
    def _(text): return text
    class MockI18n:
        current_language = 'pt'
        def set_language(self, lang): pass
    i18n = MockI18n()

class FishingBotUI:
    """Interface principal baseada na UI original funcional"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.logger = None
        try:
            self.logger = setup_logging()
        except:
            pass
        
        # Estado da aplicação
        self.bot_status = "stopped"  # stopped, running, paused
        self.is_destroyed = False
        self.main_window = None
        
        # Widgets principais
        self.notebook = None
        self.status_label = None
        self.language_var = None
        
        # Sistema de tradução - widgets rastreáveis (como na UI original)
        self.translatable_widgets = {
            'labels': {},
            'buttons': {},
            'frames': {},
            'checkboxes': {},
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configurar interface principal (baseado na UI original)"""
        try:
            self.main_window = tk.Tk()
            self.main_window.title("🎣 Ultimate Fishing Bot v4.0")
            self.main_window.geometry("800x800")
            self.main_window.resizable(True, True)
            
            # Configurar tema escuro (exatamente como na UI original)
            self.setup_dark_theme()
            
            # Criar componentes principais
            self.create_menu_bar()
            self.create_toolbar()
            self.create_main_content()
            self.create_status_bar()
            
            # Configurar eventos
            self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
        except Exception as e:
            print(f"Erro ao criar UI: {e}")
            if self.logger:
                self.logger.error(f"Erro ao criar UI: {e}")
    
    def setup_dark_theme(self):
        """Configurar tema escuro (exatamente como na UI original)"""
        try:
            style = ttk.Style()
            style.configure('TNotebook', background='#2d2d2d')
            style.configure('TNotebook.Tab',
                           background='#404040',
                           foreground='#ffffff',
                           padding=[10, 5])
            style.map('TNotebook.Tab',
                     background=[('selected', '#4a4a4a'),
                               ('active', '#505050')])
            
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TButton', font=('Arial', 9, 'bold'))
            style.configure('TEntry', font=('Arial', 9))
            style.configure('TCheckbutton', background='#2d2d2d', foreground='#ffffff', font=('Arial', 9))
            style.configure('TScale', background='#2d2d2d')
            style.configure('TLabelFrame', background='#2d2d2d', foreground='#ffffff')
            style.configure('TCombobox', font=('Arial', 9))
            
            # Configurar cor de fundo da janela principal
            self.main_window.configure(bg='#2d2d2d')
            
        except Exception as e:
            print(f"Erro ao configurar tema: {e}")
    
    def create_menu_bar(self):
        """Criar barra de menu (como na UI original)"""
        try:
            menubar = tk.Menu(self.main_window)
            self.main_window.config(menu=menubar)
            
            # Menu Arquivo
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Arquivo", menu=file_menu)
            file_menu.add_command(label="Sair", command=self.on_closing)
            
            # Menu Idioma
            language_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Idioma", menu=language_menu)
            language_menu.add_command(label="Português", command=lambda: self.change_language('pt'))
            language_menu.add_command(label="English", command=lambda: self.change_language('en'))
            
        except Exception as e:
            print(f"Erro ao criar menu: {e}")
    
    def create_toolbar(self):
        """Toolbar com botões principais (baseada na UI original)"""
        try:
            # Frame principal da toolbar
            toolbar_frame = ttk.Frame(self.main_window)
            toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Frame esquerdo - botões principais
            left_frame = ttk.Frame(toolbar_frame)
            left_frame.pack(side=tk.LEFT)
            
            # Botões de controle
            self.start_button = ttk.Button(left_frame, text=_("start"), command=self.start_bot, width=10)
            self.start_button.pack(side=tk.LEFT, padx=2)
            
            self.pause_button = ttk.Button(left_frame, text=_("pause"), command=self.pause_bot, width=10)
            self.pause_button.pack(side=tk.LEFT, padx=2)
            
            self.stop_button = ttk.Button(left_frame, text=_("stop"), command=self.stop_bot, width=10)
            self.stop_button.pack(side=tk.LEFT, padx=2)
            
            # Botão de emergência
            emergency_button = tk.Button(left_frame, text=_("emergency_stop"), command=self.emergency_stop,
                                       bg='#dc3545', fg='white', font=('Arial', 9, 'bold'))
            emergency_button.pack(side=tk.LEFT, padx=10)
            
            # Frame direito - controles secundários
            right_frame = ttk.Frame(toolbar_frame)
            right_frame.pack(side=tk.RIGHT)
            
            # Indicador de conexão do servidor (luzinha)
            self.server_status_frame = ttk.Frame(right_frame)
            self.server_status_frame.pack(side=tk.RIGHT, padx=5)
            
            self.server_indicator = tk.Label(self.server_status_frame, text="●", fg="red", bg='#2d2d2d', font=('Arial', 12))
            self.server_indicator.pack(side=tk.LEFT)
            
            ttk.Label(self.server_status_frame, text="Server").pack(side=tk.LEFT, padx=2)
            
            # Seletor de idioma (no canto como na UI original)
            language_frame = ttk.Frame(right_frame)
            language_frame.pack(side=tk.RIGHT, padx=10)
            
            ttk.Label(language_frame, text="🌍").pack(side=tk.LEFT, padx=2)
            
            self.language_var = tk.StringVar(value=i18n.current_language)
            language_combo = ttk.Combobox(language_frame, textvariable=self.language_var, 
                                        values=['pt', 'en'], state="readonly", width=6)
            language_combo.pack(side=tk.LEFT, padx=2)
            language_combo.bind('<<ComboboxSelected>>', self.on_language_changed)
            
        except Exception as e:
            print(f"Erro ao criar toolbar: {e}")
    
    def create_main_content(self):
        """Criar conteúdo principal com tabs (baseado na estrutura original)"""
        try:
            self.notebook = ttk.Notebook(self.main_window)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Criar tabs principais (4 tabs como na UI original + server)
            self.create_control_tab()
            self.create_config_tab() 
            self.create_confidence_tab()
            self.create_feeding_tab()
            self.create_server_tab()
            
        except Exception as e:
            print(f"Erro ao criar conteúdo principal: {e}")
    
    def create_control_tab(self):
        """Aba de controle principal"""
        try:
            control_frame = ttk.Frame(self.notebook)
            self.notebook.add(control_frame, text=_("control_tab"))
            
            # Importar painel de controle se existir
            try:
                from ui.control_panel import ControlPanel
                self.control_panel = ControlPanel(control_frame, self.config_manager)
            except ImportError:
                # Criar painel básico
                ttk.Label(control_frame, text="🎮 Painel de Controle Principal").pack(pady=10)
                
                # Status do bot
                status_frame = ttk.LabelFrame(control_frame, text="Status do Bot")
                status_frame.pack(fill=tk.X, padx=10, pady=5)
                
                self.bot_status_label = ttk.Label(status_frame, text="Parado", font=('Arial', 12, 'bold'))
                self.bot_status_label.pack(pady=5)
                
                # Estatísticas básicas
                stats_frame = ttk.LabelFrame(control_frame, text="Estatísticas")
                stats_frame.pack(fill=tk.X, padx=10, pady=5)
                
                self.fish_count_label = ttk.Label(stats_frame, text="Peixes: 0")
                self.fish_count_label.pack(pady=2)
                
                self.time_label = ttk.Label(stats_frame, text="Tempo: 00:00:00")
                self.time_label.pack(pady=2)
                
        except Exception as e:
            print(f"Erro ao criar aba de controle: {e}")
    
    def create_config_tab(self):
        """Aba de configurações (como na UI original)"""
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=_("config_tab"))
            
            ttk.Label(frame, text="⚙️ Configurações").pack(pady=10)
            
            # Configurações básicas
            config_frame = ttk.LabelFrame(frame, text="Configurações Principais")
            config_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Auto-clean
            auto_clean_frame = ttk.Frame(config_frame)
            auto_clean_frame.pack(fill=tk.X, padx=5, pady=2)
            
            self.auto_clean_var = tk.BooleanVar(value=self.config_manager.get('auto_clean.enabled', True))
            ttk.Checkbutton(auto_clean_frame, text="Limpeza Automática", variable=self.auto_clean_var).pack(side=tk.LEFT)
            
            # Intervalo de limpeza
            clean_interval_frame = ttk.Frame(config_frame)
            clean_interval_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(clean_interval_frame, text="Limpar inventário a cada:").pack(side=tk.LEFT)
            
            self.clean_interval_var = tk.StringVar(value=str(self.config_manager.get('auto_clean.interval', 1)))
            ttk.Entry(clean_interval_frame, textvariable=self.clean_interval_var, width=5).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(clean_interval_frame, text="pescas").pack(side=tk.LEFT)
            
            # Timeout do ciclo
            timeout_frame = ttk.Frame(config_frame)
            timeout_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(timeout_frame, text="Timeout do ciclo (s):").pack(side=tk.LEFT)
            
            self.timeout_var = tk.StringVar(value="120")
            ttk.Entry(timeout_frame, textvariable=self.timeout_var, width=8).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            print(f"Erro ao criar aba de configuração: {e}")
    
    def create_confidence_tab(self):
        """Aba de confiança dos templates (como na UI original)"""
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=_("confidence_tab"))
            
            ttk.Label(frame, text="🎯 Ajuste de Confiança dos Templates").pack(pady=10)
            
            # Scroll para muitos templates
            canvas = tk.Canvas(frame, bg='#2d2d2d')
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Templates críticos
            critical_templates = ['catch', 'comiscavara', 'semiscavara', 'varaquebrada', 'inventory', 'loot']
            
            for template in critical_templates:
                template_frame = ttk.Frame(scrollable_frame)
                template_frame.pack(fill=tk.X, padx=10, pady=2)
                
                ttk.Label(template_frame, text=f"{template}:", width=15).pack(side=tk.LEFT)
                
                current_confidence = self.config_manager.get_template_confidence(template)
                scale = ttk.Scale(template_frame, from_=0.5, to=1.0, orient=tk.HORIZONTAL, 
                                length=200, value=current_confidence)
                scale.pack(side=tk.LEFT, padx=5)
                
                confidence_label = ttk.Label(template_frame, text=f"{current_confidence:.1f}")
                confidence_label.pack(side=tk.LEFT, padx=5)
                
                # Callback para atualizar o valor
                def update_confidence(val, template_name=template, label=confidence_label):
                    label.config(text=f"{float(val):.1f}")
                    self.config_manager.set(f'template_confidence.{template_name}', float(val))
                
                scale.config(command=update_confidence)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            print(f"Erro ao criar aba de confiança: {e}")
    
    def create_feeding_tab(self):
        """Aba de alimentação (como na UI original)"""
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=_("feeding_tab"))
            
            ttk.Label(frame, text="🍖 Sistema de Alimentação").pack(pady=10)
            
            # Configurações de alimentação
            feeding_frame = ttk.LabelFrame(frame, text="Configurações")
            feeding_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Feeding habilitado
            self.feeding_enabled_var = tk.BooleanVar(value=self.config_manager.get('feeding.enabled', True))
            ttk.Checkbutton(feeding_frame, text="Alimentação Automática", variable=self.feeding_enabled_var).pack(anchor=tk.W, padx=5, pady=2)
            
            # Modo de alimentação
            mode_frame = ttk.Frame(feeding_frame)
            mode_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(mode_frame, text="Modo:").pack(side=tk.LEFT)
            
            self.feeding_mode_var = tk.StringVar(value=self.config_manager.get('feeding.mode', 'detecao_auto'))
            mode_combo = ttk.Combobox(mode_frame, textvariable=self.feeding_mode_var, 
                                    values=['detecao_auto', 'slots_fixos'], state="readonly")
            mode_combo.pack(side=tk.LEFT, padx=5)
            
            # Trigger
            trigger_frame = ttk.Frame(feeding_frame)
            trigger_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(trigger_frame, text="Alimentar a cada:").pack(side=tk.LEFT)
            
            self.feeding_catches_var = tk.StringVar(value=str(self.config_manager.get('feeding.trigger_catches', 2)))
            ttk.Entry(trigger_frame, textvariable=self.feeding_catches_var, width=5).pack(side=tk.LEFT, padx=5)
            
            ttk.Label(trigger_frame, text="pescas").pack(side=tk.LEFT)
            
            # Posições de alimentação
            positions_frame = ttk.LabelFrame(frame, text="Posições")
            positions_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Slot 1
            slot1_frame = ttk.Frame(positions_frame)
            slot1_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(slot1_frame, text="Slot 1:").pack(side=tk.LEFT)
            
            slot1_pos = self.config_manager.get_feeding_position('slot1')
            self.slot1_x_var = tk.StringVar(value=str(slot1_pos[0]))
            self.slot1_y_var = tk.StringVar(value=str(slot1_pos[1]))
            
            ttk.Entry(slot1_frame, textvariable=self.slot1_x_var, width=6).pack(side=tk.LEFT, padx=2)
            ttk.Label(slot1_frame, text=",").pack(side=tk.LEFT)
            ttk.Entry(slot1_frame, textvariable=self.slot1_y_var, width=6).pack(side=tk.LEFT, padx=2)
            
        except Exception as e:
            print(f"Erro ao criar aba de alimentação: {e}")
    
    def create_server_tab(self):
        """Aba do servidor com luzinha e seleção de COM"""
        try:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Servidor")
            
            ttk.Label(frame, text="🌐 Configurações do Servidor").pack(pady=10)
            
            # Status de conexão
            status_frame = ttk.LabelFrame(frame, text="Status da Conexão")
            status_frame.pack(fill=tk.X, padx=10, pady=5)
            
            connection_frame = ttk.Frame(status_frame)
            connection_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Luzinha de status
            self.connection_indicator = tk.Label(connection_frame, text="●", fg="red", bg='#2d2d2d', font=('Arial', 16))
            self.connection_indicator.pack(side=tk.LEFT, padx=5)
            
            self.connection_status_label = ttk.Label(connection_frame, text="Desconectado")
            self.connection_status_label.pack(side=tk.LEFT, padx=5)
            
            # Configurações do Servidor
            server_config_frame = ttk.LabelFrame(frame, text="Configurações do Servidor")
            server_config_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Habilitar servidor
            self.server_enabled_var = tk.BooleanVar(value=self.config_manager.get('server.enabled', False))
            ttk.Checkbutton(server_config_frame, text="Habilitar Servidor", variable=self.server_enabled_var).pack(anchor=tk.W, padx=5, pady=2)
            
            # URL do servidor
            url_frame = ttk.Frame(server_config_frame)
            url_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(url_frame, text="URL:").pack(side=tk.LEFT)
            
            self.server_url_var = tk.StringVar(value=self.config_manager.get('server.url', 'ws://localhost:8765'))
            ttk.Entry(url_frame, textvariable=self.server_url_var, width=30).pack(side=tk.LEFT, padx=5)
            
            # Configurações do Arduino
            arduino_frame = ttk.LabelFrame(frame, text="Configurações do Arduino")
            arduino_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Habilitar Arduino
            self.arduino_enabled_var = tk.BooleanVar(value=self.config_manager.get('arduino.enabled', False))
            ttk.Checkbutton(arduino_frame, text="Habilitar Arduino", variable=self.arduino_enabled_var).pack(anchor=tk.W, padx=5, pady=2)
            
            com_frame = ttk.Frame(arduino_frame)
            com_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(com_frame, text="Porta COM:").pack(side=tk.LEFT)
            
            # Seletor de porta COM (detectar portas disponíveis)
            self.com_port_var = tk.StringVar(value=self.config_manager.get('arduino.com_port', 'COM3'))
            com_ports = self.get_available_com_ports()
            com_combo = ttk.Combobox(com_frame, textvariable=self.com_port_var, values=com_ports, state="readonly", width=8)
            com_combo.pack(side=tk.LEFT, padx=5)
            
            # Botão para refresh das portas
            ttk.Button(com_frame, text="🔄", command=self.refresh_com_ports, width=3).pack(side=tk.LEFT, padx=5)
            
            # Baud rate
            baud_frame = ttk.Frame(arduino_frame)
            baud_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(baud_frame, text="Baud Rate:").pack(side=tk.LEFT)
            
            self.baud_rate_var = tk.StringVar(value=str(self.config_manager.get('arduino.baud_rate', 9600)))
            baud_combo = ttk.Combobox(baud_frame, textvariable=self.baud_rate_var, 
                                    values=['9600', '19200', '38400', '57600', '115200'], state="readonly", width=8)
            baud_combo.pack(side=tk.LEFT, padx=5)
            
            # Botões de teste
            test_frame = ttk.Frame(arduino_frame)
            test_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Button(test_frame, text="Testar Conexão", command=self.test_arduino_connection).pack(side=tk.LEFT, padx=5)
            ttk.Button(test_frame, text="Conectar Servidor", command=self.connect_server).pack(side=tk.LEFT, padx=5)
            
            # Status Arduino
            self.arduino_status_var = tk.StringVar(value="Arduino não conectado")
            ttk.Label(arduino_frame, textvariable=self.arduino_status_var).pack(pady=5)
            
        except Exception as e:
            print(f"Erro ao criar aba do servidor: {e}")
    
    def get_available_com_ports(self):
        """Obter portas COM disponíveis"""
        try:
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except:
            # Fallback para portas comuns
            return ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']
    
    def refresh_com_ports(self):
        """Atualizar lista de portas COM"""
        try:
            new_ports = self.get_available_com_ports()
            # Atualizar combobox (precisaria de referência do widget)
            print(f"Portas disponíveis: {new_ports}")
        except Exception as e:
            print(f"Erro ao atualizar portas: {e}")
    
    def create_status_bar(self):
        """Criar barra de status (baseada na UI original)"""
        try:
            status_frame = ttk.Frame(self.main_window)
            status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
            
            # Status principal
            self.status_label = ttk.Label(status_frame, text=_("status") + ": " + _("ready"))
            self.status_label.pack(side=tk.LEFT)
            
            # Separador
            ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
            
            # Versão
            version_label = ttk.Label(status_frame, text="Ultimate Fishing Bot v4.0")
            version_label.pack(side=tk.RIGHT)
            
        except Exception as e:
            print(f"Erro ao criar barra de status: {e}")
    
    # === MÉTODOS DE CONTROLE ===
    
    def start_bot(self):
        """Iniciar bot"""
        self.bot_status = "running"
        self.update_status(_("running"))
        self.update_server_indicator("green")
        if hasattr(self, 'bot_status_label'):
            self.bot_status_label.config(text="🟢 Executando")
    
    def pause_bot(self):
        """Pausar bot"""
        self.bot_status = "paused"
        self.update_status(_("paused"))
        self.update_server_indicator("yellow")
        if hasattr(self, 'bot_status_label'):
            self.bot_status_label.config(text="🟡 Pausado")
    
    def stop_bot(self):
        """Parar bot"""
        self.bot_status = "stopped"
        self.update_status(_("stopped"))
        self.update_server_indicator("red")
        if hasattr(self, 'bot_status_label'):
            self.bot_status_label.config(text="🔴 Parado")
    
    def emergency_stop(self):
        """Parada de emergência"""
        self.bot_status = "stopped"
        self.update_status("🚨 " + _("emergency_stop"))
        self.update_server_indicator("red")
        if hasattr(self, 'bot_status_label'):
            self.bot_status_label.config(text="🚨 Emergência")
    
    def update_status(self, status_text):
        """Atualizar status na barra"""
        if self.status_label:
            self.status_label.config(text=_("status") + ": " + status_text)
    
    def update_server_indicator(self, color):
        """Atualizar indicador do servidor"""
        if hasattr(self, 'server_indicator'):
            self.server_indicator.config(fg=color)
        if hasattr(self, 'connection_indicator'):
            self.connection_indicator.config(fg=color)
            status_text = {"green": "Conectado", "yellow": "Conectando", "red": "Desconectado"}
            if hasattr(self, 'connection_status_label'):
                self.connection_status_label.config(text=status_text.get(color, "Desconhecido"))
    
    def test_arduino_connection(self):
        """Testar conexão com Arduino"""
        com_port = self.com_port_var.get()
        baud_rate = int(self.baud_rate_var.get())
        
        self.arduino_status_var.set(f"Testando {com_port}...")
        
        try:
            # TODO: Implementar teste real de conexão serial
            import serial
            with serial.Serial(com_port, baud_rate, timeout=1) as ser:
                self.arduino_status_var.set(f"✅ Arduino conectado em {com_port}")
                self.update_server_indicator("green")
        except Exception as e:
            self.arduino_status_var.set(f"❌ Erro: {str(e)}")
            self.update_server_indicator("red")
    
    def connect_server(self):
        """Conectar ao servidor"""
        server_url = self.server_url_var.get()
        self.connection_status_label.config(text="Conectando...")
        self.connection_indicator.config(fg="yellow")
        
        # TODO: Implementar conexão WebSocket real
        self.main_window.after(2000, lambda: self.connection_status_label.config(text="Conectado"))
        self.main_window.after(2000, lambda: self.connection_indicator.config(fg="green"))
    
    def change_language(self, lang_code):
        """Mudar idioma"""
        try:
            i18n.set_language(lang_code)
            self.config_manager.set('language', lang_code)
            messagebox.showinfo("Idioma", "Reinicie a aplicação para aplicar o novo idioma.")
        except Exception as e:
            print(f"Erro ao mudar idioma: {e}")
    
    def on_language_changed(self, event=None):
        """Callback para mudança de idioma via combobox"""
        try:
            new_language = self.language_var.get()
            self.change_language(new_language)
        except Exception as e:
            print(f"Erro no callback de idioma: {e}")
    
    def on_closing(self):
        """Callback para fechamento da janela"""
        try:
            if messagebox.askokcancel("Fechar", "Deseja realmente fechar o Ultimate Fishing Bot?"):
                self.is_destroyed = True
                if self.main_window:
                    self.main_window.destroy()
        except Exception as e:
            print(f"Erro ao fechar: {e}")
    
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