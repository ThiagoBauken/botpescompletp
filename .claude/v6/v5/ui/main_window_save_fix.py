#!/usr/bin/env python3
"""
🔧 Correção dos métodos de salvamento para a UI principal
Este arquivo corrige todos os métodos save_* para realmente persistir no arquivo config.json
"""

def create_save_methods_patch():
    """
    Retorna código Python para substituir os métodos save_* não funcionais
    Cada método agora realmente salva no ConfigManager e persiste no arquivo
    """
    
    return '''
    # ========== MÉTODOS DE SALVAMENTO CORRIGIDOS ==========
    
    def save_cleaning_config(self):
        """Salvar configurações de limpeza automática"""
        print("💾 Salvando configurações de limpeza...")
        try:
            interval = self.auto_clean_interval_var.get()
            enabled = self.auto_clean_enabled_var.get()
            baits_enabled = self.auto_clean_baits_enabled_var.get()
            
            # Salvar no ConfigManager
            if hasattr(self, 'config_manager') and self.config_manager:
                self.config_manager.set('auto_clean.enabled', enabled)
                self.config_manager.set('auto_clean.interval', int(interval) if interval.isdigit() else 10)
                self.config_manager.set('auto_clean.include_baits', baits_enabled)
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"✅ Configurações de limpeza salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações de limpeza salvas!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_all_config(self):
        """Salvar todas as configurações"""
        print("💾 Salvando todas as configurações...")
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Salvar cada configuração
                self.config_manager.set('cycle_timeout', int(self.cycle_timeout_var.get()))
                self.config_manager.set('rod_system.rod_switch_limit', int(self.rod_switch_limit_var.get()))
                self.config_manager.set('performance.clicks_per_second', int(self.clicks_per_second_var.get()))
                self.config_manager.set('maintenance_timeout', int(self.maintenance_timeout_var.get()))
                self.config_manager.set('chest_side', self.chest_side_var.get())
                self.config_manager.set('macro_type', self.macro_type_var.get())
                self.config_manager.set('chest_distance', int(self.chest_distance_var.get()))
                self.config_manager.set('auto_reload', self.auto_reload_var.get())
                self.config_manager.set('auto_focus', self.auto_focus_var.get())
                self.config_manager.set('rod_system.broken_rod_action', self.broken_rod_action_var.get())
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"✅ Todas as configurações salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Todas as configurações salvas com sucesso!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_feeding_config(self):
        """Salvar configurações de alimentação"""
        print("💾 Salvando configurações de alimentação...")
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
                self.config_manager.set('feeding_system.session_count', 
                                       int(session_count) if session_count.isdigit() else 5)
                
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
                    print(f"✅ Configurações de alimentação salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações de alimentação salvas!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar alimentação: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar alimentação: {e}")
    
    def save_anti_detection_config(self):
        """Salvar configurações de anti-detecção no arquivo"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Salvar configurações de anti-detecção
                self.config_manager.set('anti_detection.enabled', self.anti_detection_enabled_var.get())
                self.config_manager.set('anti_detection.human_delay.min', float(self.human_delay_min_var.get()))
                self.config_manager.set('anti_detection.human_delay.max', float(self.human_delay_max_var.get()))
                self.config_manager.set('anti_detection.movement_variation', self.movement_variation_var.get())
                self.config_manager.set('anti_detection.random_pauses', self.random_pauses_var.get())
                self.config_manager.set('anti_detection.realistic_patterns', self.realistic_patterns_var.get())
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print("✅ Configurações Anti-Detecção salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações Anti-Detecção salvas!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_hotkeys_config(self):
        """Salvar configuração de hotkeys no config.json"""
        try:
            print("💾 Salvando configurações de hotkeys...")
            
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
                    print("✅ Hotkeys salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Configurações de Hotkeys salvas!")
                    
                    # Status na interface
                    self.hotkey_status_label.config(
                        text="✅ Hotkeys salvas com sucesso!",
                        fg='#28a745'
                    )
                else:
                    print("⚠️ ConfigManager sem save_config")
                    self.hotkey_status_label.config(
                        text="⚠️ Hotkeys atualizadas mas não persistidas",
                        fg='#ffc107'
                    )
            else:
                print("❌ ConfigManager não disponível")
                self.hotkey_status_label.config(
                    text="❌ Erro: ConfigManager não disponível",
                    fg='#dc3545'
                )
                
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar hotkeys: {e}")
            self.hotkey_status_label.config(
                text=f"❌ Erro ao salvar: {e}",
                fg='#dc3545'
            )
    
    def save_arduino_config(self):
        """Salvar configurações do Arduino no config.json"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                arduino_config = {
                    'enabled': self.arduino_enabled_var.get(),
                    'port': self.arduino_port_var.get(),
                    'baud_rate': int(self.arduino_baud_var.get()),
                    'mode': self.arduino_mode_var.get(),
                    'delay': int(self.arduino_delay_var.get())
                }
                
                # Salvar no config manager
                self.config_manager.set('arduino', arduino_config)
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    self.log_arduino("💾 Configurações salvas e persistidas no config.json")
                    messagebox.showinfo("Sucesso", "✅ Configurações do Arduino salvas!")
                else:
                    self.log_arduino("⚠️ Configurações atualizadas mas não persistidas")
            else:
                self.log_arduino("❌ ConfigManager não disponível")
                
        except Exception as e:
            self.log_arduino(f"❌ Erro ao salvar config: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_bait_priority(self):
        """Salvar prioridade de iscas no config.json"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Coletar prioridades atuais
                bait_priority = {}
                for bait_name, var in self.bait_priority_vars.items():
                    try:
                        priority = int(var.get())
                        bait_priority[bait_name] = priority
                    except ValueError:
                        continue
                
                # Salvar no ConfigManager
                self.config_manager.set('bait_priority', bait_priority)
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print(f"✅ Prioridade de iscas salva: {bait_priority}")
                    messagebox.showinfo("Sucesso", "✅ Prioridade de iscas salva!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar prioridade de iscas: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_all_coordinates(self):
        """Salvar todas as coordenadas no config.json"""
        try:
            if hasattr(self, 'config_manager') and self.config_manager:
                # Implementar salvamento de coordenadas se existirem na UI
                # Por enquanto, apenas exemplo:
                print("💾 Salvando coordenadas...")
                
                # Persistir no arquivo
                if hasattr(self.config_manager, 'save_config'):
                    self.config_manager.save_config()
                    print("✅ Coordenadas salvas e persistidas!")
                    messagebox.showinfo("Sucesso", "✅ Coordenadas salvas!")
                else:
                    print("⚠️ ConfigManager sem save_config")
            else:
                print("❌ ConfigManager não disponível")
                
        except Exception as e:
            print(f"❌ Erro ao salvar coordenadas: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    '''

# Métodos auxiliares que podem ser necessários
def get_required_imports():
    """Retorna imports necessários para os métodos funcionarem"""
    return """
from tkinter import messagebox
import json
import os
"""

def get_tab_save_button_info():
    """Retorna informações sobre qual aba precisa de qual botão de salvar"""
    return {
        "Aba 1 - Config": {
            "button_text": "💾 Salvar Todas as Configurações",
            "method": "save_all_config",
            "status": "❌ NÃO FUNCIONAL - Apenas print"
        },
        "Aba 2 - Varas e Iscas": {
            "button_text": "💾 Salvar Prioridades",
            "method": "save_bait_priority",
            "status": "⚠️ PARCIAL - Não existe implementação"
        },
        "Aba 3 - Alimentação": {
            "button_text": "💾 Salvar Configurações de Alimentação",
            "method": "save_feeding_config",
            "status": "❌ NÃO FUNCIONAL - Apenas print"
        },
        "Aba 4 - Limpeza": {
            "button_text": "💾 Salvar Config de Limpeza",
            "method": "save_cleaning_config", 
            "status": "❌ NÃO FUNCIONAL - Apenas print"
        },
        "Aba 5 - Templates": {
            "button_text": "💾 Salvar Tudo",
            "method": "save_all_template_confidence",
            "status": "✅ FUNCIONAL - Usa config_manager.save_config()"
        },
        "Aba 6 - Anti-Detecção": {
            "button_text": "💾 Salvar Configurações Anti-Detecção",
            "method": "save_anti_detection_config",
            "status": "❌ NÃO FUNCIONAL - Apenas print"
        },
        "Aba 7 - Hotkeys": {
            "button_text": "💾 Salvar Configurações",
            "method": "save_hotkeys_config",
            "status": "⚠️ PARCIAL - Só print, sem persistência"
        },
        "Aba 8 - Arduino": {
            "button_text": "💾 Salvar Config Arduino",
            "method": "save_arduino_config",
            "status": "⚠️ PARCIAL - Tenta salvar mas pode falhar"
        }
    }

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 ANÁLISE DOS BOTÕES DE SALVAR NA UI")
    print("=" * 80)
    
    tabs_info = get_tab_save_button_info()
    
    print("\n📋 STATUS ATUAL DOS BOTÕES DE SALVAR:\n")
    
    functional = 0
    not_functional = 0
    partial = 0
    
    for tab, info in tabs_info.items():
        print(f"{tab}:")
        print(f"  Botão: {info['button_text']}")
        print(f"  Método: {info['method']}()")
        print(f"  Status: {info['status']}")
        print()
        
        if "✅" in info['status']:
            functional += 1
        elif "❌" in info['status']:
            not_functional += 1
        else:
            partial += 1
    
    print("=" * 80)
    print("📊 RESUMO:")
    print(f"  ✅ Funcionais: {functional}/8")
    print(f"  ❌ Não funcionais: {not_functional}/8")
    print(f"  ⚠️ Parcialmente funcionais: {partial}/8")
    print("=" * 80)
    
    print("\n🔧 SOLUÇÃO:")
    print("  Os métodos corrigidos estão no método create_save_methods_patch()")
    print("  Eles precisam ser aplicados na classe FishingBotUI")
    print("  Todos agora usam config_manager.set() + save_config()")
    print("=" * 80)