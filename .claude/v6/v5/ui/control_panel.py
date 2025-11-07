#!/usr/bin/env python3
"""
🎮 Painel de Controle Principal
Interface de controle do bot com status e controles manuais
"""

import tkinter as tk
from tkinter import ttk
import logging
from datetime import datetime, timedelta

from utils.i18n_manager import _
from utils.config_manager import ConfigManager

class ControlPanel:
    """Painel de controle principal do bot"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.logger = logging.getLogger('ui.control')
        
        # Estado do painel
        self.session_start_time = None
        self.fish_count = 0
        self.last_action = "Nenhuma"
        self.current_rod = 1
        
        # Widgets
        self.frame = ttk.Frame(parent)
        self.status_labels = {}
        self.log_text = None
        
        self.setup_control_ui()
        
    def setup_control_ui(self):
        """Configurar interface do painel de controle"""
        
        # === STATUS ATUAL ===
        status_frame = ttk.LabelFrame(self.frame, text=_("control.current_status"))
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Grid de status em 2 colunas
        status_items = [
            ("fishing_active", _("status.fishing_inactive")),
            ("current_rod", f"Vara {self.current_rod}"),
            ("fish_count", str(self.fish_count)),
            ("session_time", "00:00:00"),
            ("last_action", self.last_action),
            ("bot_status", _("status.idle"))
        ]
        
        for i, (key, default_value) in enumerate(status_items):
            row = i // 2
            col = (i % 2) * 2
            
            # Label do campo
            ttk.Label(status_frame, text=_(f"status.{key}") + ":").grid(
                row=row, column=col, sticky=tk.W, padx=5, pady=2
            )
            
            # Valor do campo
            self.status_labels[key] = ttk.Label(status_frame, text=default_value,
                                              font=('Arial', 9, 'bold'), foreground='blue')
            self.status_labels[key].grid(
                row=row, column=col+1, sticky=tk.W, padx=5, pady=2
            )
            
        # === CONTROLES MANUAIS ===
        manual_frame = ttk.LabelFrame(self.frame, text=_("control.manual_controls"))
        manual_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botões manuais em grid 3x3
        manual_buttons = [
            ("open_inventory", self.open_inventory),
            ("open_chest", self.open_chest),
            ("feed_character", self.feed_character),
            ("switch_rod", self.show_rod_selector),
            ("auto_clean", self.auto_clean),
            ("test_detection", self.test_detection),
            ("cast_line", self.cast_line),
            ("stop_fishing", self.stop_fishing),
            ("emergency_actions", self.emergency_actions)
        ]
        
        for i, (button_key, callback) in enumerate(manual_buttons):
            row = i // 3
            col = i % 3
            
            try:
                button_text = _(f"manual.{button_key}")
            except:
                button_text = button_key.replace('_', ' ').title()
                
            ttk.Button(manual_frame, text=button_text,
                      command=callback, width=15).grid(
                row=row, column=col, padx=5, pady=5, sticky=tk.EW
            )
            
        # Configurar expansão das colunas
        for col in range(3):
            manual_frame.columnconfigure(col, weight=1)
            
        # === CONFIGURAÇÕES RÁPIDAS ===
        quick_config_frame = ttk.LabelFrame(self.frame, text=_("control.quick_config"))
        quick_config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Intervalo de limpeza
        clean_frame = ttk.Frame(quick_config_frame)
        clean_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(clean_frame, text=_("config.auto_clean_interval") + ":").pack(side=tk.LEFT)
        self.clean_interval_var = tk.IntVar(value=self.config_manager.get('auto_clean.interval', 1))
        clean_spinbox = tk.Spinbox(clean_frame, from_=1, to=50, width=5,
                                  textvariable=self.clean_interval_var,
                                  command=self.update_clean_interval)
        clean_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(clean_frame, text=_("config.catches")).pack(side=tk.LEFT)
        
        # Trigger de alimentação
        feed_frame = ttk.Frame(quick_config_frame)
        feed_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(feed_frame, text=_("config.feeding_trigger") + ":").pack(side=tk.LEFT)
        self.feed_trigger_var = tk.IntVar(value=self.config_manager.get('feeding.trigger_catches', 2))
        feed_spinbox = tk.Spinbox(feed_frame, from_=1, to=20, width=5,
                                 textvariable=self.feed_trigger_var,
                                 command=self.update_feed_trigger)
        feed_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(feed_frame, text=_("config.catches")).pack(side=tk.LEFT)
        
        # === LOG DE AÇÕES ===
        log_frame = ttk.LabelFrame(self.frame, text=_("control.action_log"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Container para text widget e scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget para logs
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD,
                               font=('Consolas', 9), state=tk.DISABLED,
                               bg='white', fg='black')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                 command=self.log_text.yview)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões do log
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(log_buttons_frame, text=_("log.clear"),
                  command=self.clear_log).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_buttons_frame, text=_("log.save"),
                  command=self.save_log).pack(side=tk.LEFT, padx=2)
        
        # Inicializar log
        self.add_log_entry("Sistema iniciado", "INFO")
        
    # === MÉTODOS DE CONTROLE MANUAL ===
    
    def open_inventory(self):
        """Abrir inventário (TAB)"""
        self.add_log_entry("Abrindo inventário...", "ACTION")
        # TODO: Implementar ação real
        
    def open_chest(self):
        """Abrir baú"""
        self.add_log_entry("Executando macro de abertura do baú...", "ACTION")
        # TODO: Implementar ação real
        
    def feed_character(self):
        """Alimentar personagem"""
        self.add_log_entry("Alimentando personagem...", "ACTION")
        # TODO: Implementar ação real
        
    def show_rod_selector(self):
        """Mostrar seletor de vara"""
        self.rod_selector_window()
        
    def auto_clean(self):
        """Executar limpeza automática"""
        self.add_log_entry("Iniciando limpeza automática...", "ACTION")
        # TODO: Implementar ação real
        
    def test_detection(self):
        """Testar detecção de templates"""
        self.add_log_entry("Testando detecção de templates...", "TEST")
        # TODO: Implementar teste real
        
    def cast_line(self):
        """Lançar linha"""
        self.add_log_entry("Lançando linha de pesca...", "ACTION")
        # TODO: Implementar ação real
        
    def stop_fishing(self):
        """Parar pesca"""
        self.add_log_entry("Parando pesca...", "ACTION")
        self.update_status("fishing_active", _("status.fishing_inactive"))
        
    def emergency_actions(self):
        """Ações de emergência"""
        self.emergency_window()
        
    def rod_selector_window(self):
        """Janela de seleção de vara"""
        rod_window = tk.Toplevel(self.frame)
        rod_window.title(_("rod.selector_title"))
        rod_window.geometry("300x200")
        rod_window.transient(self.frame)
        rod_window.grab_set()
        
        ttk.Label(rod_window, text=_("rod.select_rod"), 
                 font=('Arial', 12)).pack(pady=10)
        
        # Botões para cada vara
        for rod_num in range(1, 7):
            ttk.Button(rod_window, text=f"Vara {rod_num}",
                      command=lambda r=rod_num: self.switch_to_rod(r, rod_window),
                      width=20).pack(pady=2)
                      
    def switch_to_rod(self, rod_number, window=None):
        """Trocar para vara específica"""
        self.current_rod = rod_number
        self.update_status("current_rod", f"Vara {rod_number}")
        self.add_log_entry(f"Trocado para vara {rod_number}", "ACTION")
        
        if window:
            window.destroy()
            
    def emergency_window(self):
        """Janela de ações de emergência"""
        emergency_window = tk.Toplevel(self.frame)
        emergency_window.title(_("emergency.title"))
        emergency_window.geometry("250x150")
        emergency_window.transient(self.frame)
        emergency_window.grab_set()
        
        # Botão de parada total
        tk.Button(emergency_window, text=_("emergency.stop_all"),
                 bg='red', fg='white', font=('Arial', 12, 'bold'),
                 command=lambda: self.emergency_stop_all(emergency_window)).pack(pady=10)
                 
        # Botão de reset
        ttk.Button(emergency_window, text=_("emergency.reset"),
                  command=lambda: self.emergency_reset(emergency_window)).pack(pady=5)
                  
    def emergency_stop_all(self, window):
        """Parada de emergência total"""
        self.add_log_entry("PARADA DE EMERGÊNCIA ATIVADA!", "EMERGENCY")
        window.destroy()
        
    def emergency_reset(self, window):
        """Reset de emergência"""
        self.add_log_entry("Reset de emergência executado", "EMERGENCY")
        window.destroy()
        
    # === MÉTODOS DE ATUALIZAÇÃO ===
    
    def update_clean_interval(self):
        """Atualizar intervalo de limpeza"""
        new_interval = self.clean_interval_var.get()
        self.config_manager.set('auto_clean.interval', new_interval)
        self.add_log_entry(f"Intervalo de limpeza alterado para {new_interval}", "CONFIG")
        
    def update_feed_trigger(self):
        """Atualizar trigger de alimentação"""
        new_trigger = self.feed_trigger_var.get()
        self.config_manager.set('feeding.trigger_catches', new_trigger)
        self.add_log_entry(f"Trigger de alimentação alterado para {new_trigger}", "CONFIG")
        
    def update_status(self, key: str, value: str):
        """Atualizar valor de status"""
        if key in self.status_labels:
            self.status_labels[key].config(text=value)
            
    def increment_fish_count(self):
        """Incrementar contador de peixes"""
        self.fish_count += 1
        self.update_status("fish_count", str(self.fish_count))
        
    def update_session_time(self):
        """Atualizar tempo de sessão"""
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            time_str = str(elapsed).split('.')[0]  # Remove microsegundos
            self.update_status("session_time", time_str)
            
    def start_session(self):
        """Iniciar sessão"""
        self.session_start_time = datetime.now()
        self.fish_count = 0
        self.update_status("fish_count", "0")
        self.add_log_entry("Sessão de pesca iniciada", "SESSION")
        
    def end_session(self):
        """Finalizar sessão"""
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            self.add_log_entry(f"Sessão finalizada. Duração: {elapsed}, Peixes: {self.fish_count}", "SESSION")
            
    # === MÉTODOS DE LOG ===
    
    def add_log_entry(self, message: str, level: str = "INFO"):
        """Adicionar entrada no log"""
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Cores por nível
            colors = {
                "INFO": "black",
                "ACTION": "blue", 
                "ERROR": "red",
                "WARNING": "orange",
                "SUCCESS": "green",
                "TEST": "purple",
                "CONFIG": "brown",
                "SESSION": "navy",
                "EMERGENCY": "red"
            }
            
            color = colors.get(level, "black")
            
            # Adicionar ao log
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{timestamp}] [{level}] {message}\\n")
            self.log_text.config(state=tk.DISABLED)
            
            # Auto-scroll para o final
            self.log_text.see(tk.END)
            
    def clear_log(self):
        """Limpar log"""
        if self.log_text:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            self.add_log_entry("Log limpo", "INFO")
            
    def save_log(self):
        """Salvar log em arquivo"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.add_log_entry(f"Log salvo em: {filename}", "SUCCESS")
                
        except Exception as e:
            self.add_log_entry(f"Erro ao salvar log: {e}", "ERROR")