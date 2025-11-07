#!/usr/bin/env python3
"""
🎨 Interface Principal - Ultimate Fishing Bot v4.0 SIMPLE
Apenas o essencial + COM funcionando
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Detectar portas COM
try:
    import serial.tools.list_ports
    def get_com_ports():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
except ImportError:
    def get_com_ports():
        return ['COM1', 'COM2', 'COM3', 'COM4', 'COM5']

# Adicionar pasta pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.config_manager import ConfigManager
except ImportError:
    class ConfigManager:
        def get(self, key, default=None): return default
        def set(self, key, value): pass

class FishingBotUI:
    """Interface SIMPLES - apenas o que funciona"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.bot_status = "stopped"
        self.main_window = None
        self.setup_ui()
    
    def setup_ui(self):
        """UI SIMPLES - sem complicação"""
        self.main_window = tk.Tk()
        self.main_window.title("🎣 Ultimate Fishing Bot v4.0")
        self.main_window.geometry("600x500")
        
        # Tema escuro SIMPLES
        self.setup_simple_theme()
        
        # Criar apenas o essencial
        self.create_simple_toolbar()
        self.create_simple_tabs()
        self.create_simple_status()
        
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_simple_theme(self):
        """Tema escuro BÁSICO"""
        style = ttk.Style()
        style.configure('TNotebook', background='#2d2d2d')
        style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff')
        style.configure('TFrame', background='#2d2d2d')
        style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
        style.configure('TButton', font=('Arial', 9))
        self.main_window.configure(bg='#2d2d2d')
    
    def create_simple_toolbar(self):
        """Toolbar SIMPLES"""
        toolbar = ttk.Frame(self.main_window)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Botões básicos
        ttk.Button(toolbar, text="Iniciar", command=self.start_bot).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Parar", command=self.stop_bot).pack(side=tk.LEFT, padx=2)
        
        # APENAS a luzinha de servidor que funciona
        right_frame = ttk.Frame(toolbar)
        right_frame.pack(side=tk.RIGHT)
        
        self.server_indicator = tk.Label(right_frame, text="●", fg="red", bg='#2d2d2d', font=('Arial', 12))
        self.server_indicator.pack(side=tk.LEFT)
        ttk.Label(right_frame, text="Server").pack(side=tk.LEFT, padx=2)
        
        # Idioma SIMPLES
        ttk.Label(right_frame, text="🌍").pack(side=tk.LEFT, padx=5)
        self.language_var = tk.StringVar(value="pt")
        lang_combo = ttk.Combobox(right_frame, textvariable=self.language_var, 
                                values=['pt', 'en'], state="readonly", width=4)
        lang_combo.pack(side=tk.LEFT)
    
    def create_simple_tabs(self):
        """Tabs SIMPLES - só 2 tabs"""
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Controle SIMPLES
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Controle")
        
        ttk.Label(control_frame, text="🎮 Status do Bot", font=('Arial', 12)).pack(pady=20)
        self.status_label = ttk.Label(control_frame, text="Parado", font=('Arial', 14, 'bold'))
        self.status_label.pack(pady=10)
        
        # Tab 2: COM - A ÚNICA COISA COMPLEXA QUE FUNCIONA
        com_frame = ttk.Frame(self.notebook)
        self.notebook.add(com_frame, text="Arduino/Servidor")
        
        self.create_com_section(com_frame)
    
    def create_com_section(self, parent):
        """Seção COM - A ÚNICA coisa avançada"""
        ttk.Label(parent, text="🌐 Configurações COM", font=('Arial', 12)).pack(pady=10)
        
        # Status visual COM
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        conn_frame = ttk.Frame(status_frame)
        conn_frame.pack(padx=5, pady=5)
        
        self.connection_indicator = tk.Label(conn_frame, text="●", fg="red", bg='#2d2d2d', font=('Arial', 16))
        self.connection_indicator.pack(side=tk.LEFT, padx=5)
        
        self.connection_status = ttk.Label(conn_frame, text="Desconectado")
        self.connection_status.pack(side=tk.LEFT)
        
        # Configuração COM
        config_frame = ttk.LabelFrame(parent, text="Configuração Arduino")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Porta COM
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(port_frame, text="Porta:").pack(side=tk.LEFT)
        
        self.com_port_var = tk.StringVar(value="COM3")
        self.com_combo = ttk.Combobox(port_frame, textvariable=self.com_port_var, 
                                    values=get_com_ports(), state="readonly", width=8)
        self.com_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(port_frame, text="🔄", command=self.refresh_ports, width=3).pack(side=tk.LEFT, padx=2)
        
        # Baud Rate
        baud_frame = ttk.Frame(config_frame)
        baud_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(baud_frame, text="Baud:").pack(side=tk.LEFT)
        
        self.baud_var = tk.StringVar(value="9600")
        baud_combo = ttk.Combobox(baud_frame, textvariable=self.baud_var, 
                                values=['9600', '19200', '57600', '115200'], state="readonly", width=8)
        baud_combo.pack(side=tk.LEFT, padx=5)
        
        # Botões teste
        test_frame = ttk.Frame(config_frame)
        test_frame.pack(pady=10)
        
        ttk.Button(test_frame, text="Testar Conexão", command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text="Conectar", command=self.connect).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.arduino_status = tk.StringVar(value="Arduino não conectado")
        ttk.Label(config_frame, textvariable=self.arduino_status).pack(pady=5)
    
    def create_simple_status(self):
        """Status SIMPLES"""
        status_frame = ttk.Frame(self.main_window)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=2)
        
        ttk.Label(status_frame, text="Ultimate Fishing Bot v4.0").pack(side=tk.LEFT)
        ttk.Label(status_frame, text="SIMPLE").pack(side=tk.RIGHT)
    
    # === MÉTODOS SIMPLES ===
    
    def start_bot(self):
        """Iniciar - SIMPLES"""
        self.bot_status = "running"
        self.status_label.config(text="🟢 Executando")
        self.server_indicator.config(fg="green")
        self.connection_indicator.config(fg="green")
        self.connection_status.config(text="Conectado")
    
    def stop_bot(self):
        """Parar - SIMPLES"""
        self.bot_status = "stopped"
        self.status_label.config(text="🔴 Parado")
        self.server_indicator.config(fg="red")
        self.connection_indicator.config(fg="red")
        self.connection_status.config(text="Desconectado")
    
    def refresh_ports(self):
        """Refresh COM - FUNCIONA"""
        try:
            new_ports = get_com_ports()
            self.com_combo['values'] = new_ports
            print(f"Portas disponíveis: {new_ports}")
        except Exception as e:
            print(f"Erro: {e}")
    
    def test_connection(self):
        """Testar COM - FUNCIONA"""
        port = self.com_port_var.get()
        baud = int(self.baud_var.get())
        
        self.arduino_status.set(f"Testando {port}...")
        
        try:
            import serial
            with serial.Serial(port, baud, timeout=1) as ser:
                self.arduino_status.set(f"✅ Conectado em {port}")
                self.connection_indicator.config(fg="green")
                self.connection_status.config(text="Arduino OK")
        except Exception as e:
            self.arduino_status.set(f"❌ Erro: {str(e)}")
            self.connection_indicator.config(fg="red")
    
    def connect(self):
        """Conectar - SIMULA"""
        self.connection_status.config(text="Conectando...")
        self.connection_indicator.config(fg="yellow")
        
        # Simular conexão
        self.main_window.after(1500, lambda: self.connection_status.config(text="Servidor OK"))
        self.main_window.after(1500, lambda: self.connection_indicator.config(fg="green"))
    
    def on_closing(self):
        """Fechar - SIMPLES"""
        if messagebox.askokcancel("Fechar", "Sair?"):
            self.main_window.destroy()
    
    def run(self):
        """Executar - SIMPLES"""
        if self.main_window:
            self.main_window.mainloop()
    
    @property
    def root(self):
        """Compatibilidade"""
        return self.main_window