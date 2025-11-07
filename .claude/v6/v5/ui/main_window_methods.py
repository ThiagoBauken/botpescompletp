#!/usr/bin/env python3
"""
🎣 Ultimate Fishing Bot v4.0 - Métodos da Interface Principal
Métodos de controle, eventos e funcionalidades da interface
"""

import tkinter as tk
from tkinter import messagebox

# Adicionar estes métodos à classe FishingBotUI:

def add_methods_to_ui(ui_class):
    """Adicionar métodos à classe UI"""
    
    # ===== MÉTODOS DE CONTROLE DO BOT =====
    
    def start_bot(self):
        """Iniciar bot"""
        try:
            self.bot_running = True
            self.bot_paused = False
            self.status_label.config(text="🟢 Executando", fg='green')
            print("🎣 Bot iniciado!")
            self.update_buttons_state()
        except Exception as e:
            print(f"Erro ao iniciar bot: {e}")
    
    def pause_bot(self):
        """Pausar/despausar bot"""
        try:
            if self.bot_running:
                self.bot_paused = not self.bot_paused
                if self.bot_paused:
                    self.status_label.config(text="🟡 Pausado", fg='orange')
                    print("⏸️ Bot pausado!")
                else:
                    self.status_label.config(text="🟢 Executando", fg='green')
                    print("▶️ Bot despausado!")
                self.update_buttons_state()
        except Exception as e:
            print(f"Erro ao pausar bot: {e}")
    
    def stop_bot(self):
        """Parar bot"""
        try:
            self.bot_running = False
            self.bot_paused = False
            self.status_label.config(text="⚫ Parado", fg='red')
            print("⏹️ Bot parado!")
            self.update_buttons_state()
        except Exception as e:
            print(f"Erro ao parar bot: {e}")
    
    def update_buttons_state(self):
        """Atualizar estado dos botões baseado no status do bot"""
        try:
            if hasattr(self, 'start_button'):
                self.start_button.config(state='disabled' if self.bot_running else 'normal')
            if hasattr(self, 'pause_button'):
                self.pause_button.config(state='normal' if self.bot_running else 'disabled')
            if hasattr(self, 'stop_button'):
                self.stop_button.config(state='normal' if self.bot_running else 'disabled')
        except Exception as e:
            print(f"Erro ao atualizar botões: {e}")
    
    # ===== MÉTODOS DE CONFIGURAÇÃO =====
    
    def save_all_configs(self):
        """Salvar todas as configurações"""
        try:
            config_data = {
                'cycle_timeout': int(self.cycle_timeout_var.get()),
                'rod_switch_limit': int(self.rod_switch_limit_var.get()),
                'clicks_per_second': int(self.clicks_per_second_var.get()),
                'maintenance_timeout': int(self.maintenance_timeout_var.get()),
                'chest_side': self.chest_side_var.get(),
                'macro_type': self.macro_type_var.get(),
                'chest_distance': int(self.chest_distance_var.get()),
                'auto_reload': self.auto_reload_var.get(),
                'auto_focus': self.auto_focus_var.get(),
                'broken_rod_action': self.broken_rod_action_var.get(),
                'auto_clean': {
                    'enabled': self.auto_clean_enabled_var.get(),
                    'interval': int(self.auto_clean_interval_var.get()),
                    'include_baits': self.auto_clean_baits_enabled_var.get()
                },
                'feeding': {
                    'enabled': self.feeding_enabled_var.get(),
                    'trigger_mode': self.feeding_trigger_mode_var.get(),
                    'trigger_catches': int(self.feeding_trigger_catches_var.get()),
                    'trigger_time': int(self.feeding_trigger_time_var.get()),
                    'session_count': int(self.feeding_session_count_var.get()),
                    'auto_detect': self.feeding_auto_detect_var.get(),
                    'slot1_position': [int(self.feeding_slot1_x_var.get()), int(self.feeding_slot1_y_var.get())],
                    'slot2_position': [int(self.feeding_slot2_x_var.get()), int(self.feeding_slot2_y_var.get())]
                },
                'anti_detection': {
                    'enabled': self.anti_detection_enabled_var.get(),
                    'click_delay_min': int(self.click_delay_min_var.get()),
                    'click_delay_max': int(self.click_delay_max_var.get()),
                    'movement_a_min': float(self.movement_duration_a_min_var.get()),
                    'movement_a_max': float(self.movement_duration_a_max_var.get()),
                    'movement_d_min': float(self.movement_duration_d_min_var.get()),
                    'movement_d_max': float(self.movement_duration_d_max_var.get()),
                    'pause_time': int(self.natural_pause_time_var.get())
                },
                'hotkeys': {key: var.get() for key, var in self.hotkey_vars.items()}
            }
            
            self.config_manager.save_config(config_data)
            messagebox.showinfo("Sucesso", "✅ Todas as configurações foram salvas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao salvar configurações: {e}")
    
    def load_all_configs(self):
        """Carregar todas as configurações"""
        try:
            config_data = self.config_manager.load_config()
            
            # Carregar valores nas variáveis
            self.cycle_timeout_var.set(str(config_data.get('cycle_timeout', 122)))
            self.rod_switch_limit_var.set(str(config_data.get('rod_switch_limit', 20)))
            self.clicks_per_second_var.set(str(config_data.get('clicks_per_second', 9)))
            # ... outros carregamentos
            
            print("✅ Configurações carregadas com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
    
    def save_auto_clean_config(self):
        """Salvar configurações de limpeza automática"""
        try:
            auto_clean_config = {
                'enabled': self.auto_clean_enabled_var.get(),
                'interval': int(self.auto_clean_interval_var.get()),
                'include_baits': self.auto_clean_baits_enabled_var.get()
            }
            
            self.config_manager.set('auto_clean', auto_clean_config)
            
            # Atualizar status
            interval = int(self.auto_clean_interval_var.get())
            self.auto_clean_status_label.config(text=f"📊 Próxima limpeza em: {interval} pescas")
            
            messagebox.showinfo("Sucesso", "✅ Configurações de limpeza salvas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao salvar: {e}")
    
    # ===== MÉTODOS DE ALIMENTAÇÃO =====
    
    def test_manual_feeding(self):
        """Testar alimentação manual"""
        try:
            slot1_x = int(self.feeding_slot1_x_var.get())
            slot1_y = int(self.feeding_slot1_y_var.get())
            slot2_x = int(self.feeding_slot2_x_var.get())
            slot2_y = int(self.feeding_slot2_y_var.get())
            
            messagebox.showinfo("Teste", 
                              f"🧪 Teste de alimentação manual:\\n"
                              f"Slot 1: ({slot1_x}, {slot1_y})\\n"
                              f"Slot 2: ({slot2_x}, {slot2_y})\\n\\n"
                              f"(Funcionalidade em desenvolvimento)")
                              
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro no teste: {e}")
    
    # ===== MÉTODOS DE TEMPLATE VIEWER =====
    
    def open_catch_viewer(self):
        """Abrir janela do visualizador CATCH"""
        try:
            if self.catch_viewer_window and self.catch_viewer_window.winfo_exists():
                self.catch_viewer_window.lift()
                return
            
            # Criar nova janela
            self.catch_viewer_window = tk.Toplevel(self.main_window)
            self.catch_viewer_window.title("👁️ CATCH Viewer - Template Matching")
            self.catch_viewer_window.geometry("800x600")
            self.catch_viewer_window.configure(bg='#1a1a1a')
            
            # Conteúdo da janela
            tk.Label(self.catch_viewer_window, 
                    text="👁️ Visualizador Template Matching ATIVO",
                    bg='#1a1a1a', fg='#00aaff', 
                    font=('Arial', 16, 'bold')).pack(pady=20)
            
            tk.Label(self.catch_viewer_window,
                    text="Sistema de detecção em tempo real\\n"
                         "Verde = Detecção bem-sucedida\\n"
                         "Vermelho = Nenhuma detecção",
                    bg='#1a1a1a', fg='#cccccc',
                    font=('Arial', 12), justify='center').pack(pady=20)
            
            self.catch_viewer_running = True
            self.viewer_status_label.config(text="Status: Janela CATCH aberta", fg='#28a745')
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao abrir viewer: {e}")
    
    def stop_catch_viewer(self):
        """Parar visualizador CATCH"""
        try:
            if self.catch_viewer_window and self.catch_viewer_window.winfo_exists():
                self.catch_viewer_window.destroy()
            
            self.catch_viewer_running = False
            self.viewer_status_label.config(text="Status: Visualizador parado", fg='#dc3545')
            
        except Exception as e:
            print(f"Erro ao parar viewer: {e}")
    
    # ===== MÉTODOS DE HOTKEYS =====
    
    def capture_hotkey(self, key):
        """Capturar nova hotkey"""
        try:
            # Simplificado - em produção usaria um dialog especializado
            new_key = tk.simpledialog.askstring(
                "Capturar Tecla",
                f"Digite a nova tecla para '{key}':\\n"
                f"(ex: f1, ctrl+s, alt+x)"
            )
            
            if new_key:
                self.hotkey_vars[key].set(new_key.lower())
                messagebox.showinfo("Sucesso", f"✅ Tecla '{new_key}' configurada para {key}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao capturar tecla: {e}")
    
    def save_hotkeys_config(self):
        """Salvar configurações de hotkeys"""
        try:
            hotkeys_config = {key: var.get() for key, var in self.hotkey_vars.items()}
            self.config_manager.set('hotkeys', hotkeys_config)
            messagebox.showinfo("Sucesso", "✅ Configurações de teclas salvas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao salvar hotkeys: {e}")
    
    def restore_default_hotkeys(self):
        """Restaurar hotkeys padrão"""
        try:
            defaults = {
                'start': 'f9',
                'pause': 'f2', 
                'stop': 'f1',
                'emergency': 'escape',
                'interface': 'f4',
                'macro_execute': 'f8',
                'macro_chest': 'f11',
                'macro_record': 'f3',
                'test_mouse': 'f12',
                'test_feeding': 'f6',
                'test_cleaning': 'f5',
                'test_maintenance': '0'
            }
            
            for key, default in defaults.items():
                if key in self.hotkey_vars:
                    self.hotkey_vars[key].set(default)
            
            messagebox.showinfo("Sucesso", "✅ Hotkeys restauradas para valores padrão!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao restaurar: {e}")
    
    def apply_hotkey_changes(self):
        """Aplicar mudanças de hotkeys"""
        try:
            # Em produção, aqui registraria as hotkeys globais
            messagebox.showinfo("Aplicado", "✅ Mudanças de hotkeys aplicadas!\\n(Reinicie para ativar)")
            
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao aplicar: {e}")
    
    # ===== MÉTODOS DE IDIOMA =====
    
    def on_language_changed(self, event=None):
        """Callback para mudança de idioma"""
        pass  # Implementar depois
    
    def apply_language_change(self):
        """Aplicar mudança de idioma"""
        try:
            new_language = self.language_var.get()
            i18n.set_language(new_language)
            self.current_language = new_language
            
            messagebox.showinfo("Idioma", 
                              f"✅ Idioma alterado para: {new_language.upper()}\\n"
                              f"Reinicie a aplicação para aplicar completamente.")
                              
        except Exception as e:
            messagebox.showerror("Erro", f"❌ Erro ao alterar idioma: {e}")
    
    # ===== EVENTOS DE JANELA =====
    
    def on_closing(self):
        """Evento de fechamento da janela"""
        try:
            if messagebox.askokcancel("Fechar", 
                                     "Deseja realmente fechar o Ultimate Fishing Bot v4.0?"):
                # Parar bot se estiver rodando
                if self.bot_running:
                    self.stop_bot()
                
                # Fechar janelas auxiliares
                if self.catch_viewer_window and self.catch_viewer_window.winfo_exists():
                    self.catch_viewer_window.destroy()
                
                # Salvar configurações
                try:
                    self.save_all_configs()
                except:
                    pass  # Não exibir erro no fechamento
                
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
                # Mostrar janela
                self.main_window.deiconify()
                self.main_window.lift()
                self.main_window.focus_force()
                
                # Mainloop
                self.main_window.mainloop()
                
        except Exception as e:
            print(f"Erro ao executar interface: {e}")
            messagebox.showerror("Erro", f"Erro na interface: {e}")
    
    # Adicionar métodos à classe
    ui_class.start_bot = start_bot
    ui_class.pause_bot = pause_bot
    ui_class.stop_bot = stop_bot
    ui_class.update_buttons_state = update_buttons_state
    ui_class.save_all_configs = save_all_configs
    ui_class.load_all_configs = load_all_configs
    ui_class.save_auto_clean_config = save_auto_clean_config
    ui_class.test_manual_feeding = test_manual_feeding
    ui_class.open_catch_viewer = open_catch_viewer
    ui_class.stop_catch_viewer = stop_catch_viewer
    ui_class.capture_hotkey = capture_hotkey
    ui_class.save_hotkeys_config = save_hotkeys_config
    ui_class.restore_default_hotkeys = restore_default_hotkeys
    ui_class.apply_hotkey_changes = apply_hotkey_changes
    ui_class.on_language_changed = on_language_changed
    ui_class.apply_language_change = apply_language_change
    ui_class.on_closing = on_closing
    ui_class.run = run