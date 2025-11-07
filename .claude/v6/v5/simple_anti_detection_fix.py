#!/usr/bin/env python3
"""
Código de substituição para a função save_anti_detection_config
"""

# Implementação correta para substituir na ui/main_window.py:

def save_anti_detection_config_FIXED(self):
    """Salvar configurações de anti-detecção no arquivo - VERSÃO CORRIGIDA"""
    try:
        print("💾 Salvando configurações de anti-detecção...")
        
        if hasattr(self, 'config_manager') and self.config_manager:
            # Salvar configurações básicas de anti-detecção
            self.config_manager.set('anti_detection.enabled', self.anti_detection_enabled_var.get())
            
            # Salvar configurações de cliques (usando variáveis que EXISTEM)
            if hasattr(self, 'click_variation_var'):
                self.config_manager.set('anti_detection.click_variation.enabled', self.click_variation_var.get())
            
            if hasattr(self, 'click_delay_min_var') and hasattr(self, 'click_delay_max_var'):
                # Converter ms para segundos
                min_delay = float(self.click_delay_min_var.get()) / 1000
                max_delay = float(self.click_delay_max_var.get()) / 1000
                self.config_manager.set('anti_detection.click_variation.min_delay', min_delay)
                self.config_manager.set('anti_detection.click_variation.max_delay', max_delay)
            
            # Salvar configurações de movimento (usando variáveis que EXISTEM)
            if hasattr(self, 'movement_variation_var'):
                self.config_manager.set('anti_detection.movement_variation.enabled', self.movement_variation_var.get())
            
            # Salvar configurações de pausas naturais (usando variáveis que EXISTEM)
            if hasattr(self, 'natural_breaks_var'):
                self.config_manager.set('anti_detection.natural_breaks.enabled', self.natural_breaks_var.get())
            
            if hasattr(self, 'break_mode_var'):
                self.config_manager.set('anti_detection.natural_breaks.mode', self.break_mode_var.get())
                
            if hasattr(self, 'break_catches_var'):
                self.config_manager.set('anti_detection.natural_breaks.catches_interval', int(self.break_catches_var.get()))
            
            # Persistir no arquivo
            if hasattr(self.config_manager, 'save_config'):
                self.config_manager.save_config()
                print("✅ Configurações Anti-Detecção salvas e persistidas!")
                # Usar messagebox se disponível
                try:
                    from tkinter import messagebox
                    messagebox.showinfo("Sucesso", "✅ Configurações Anti-Detecção salvas!")
                except:
                    pass
            else:
                print("⚠️ ConfigManager sem save_config")
        else:
            print("❌ ConfigManager não disponível")
            
    except Exception as e:
        print(f"❌ Erro ao salvar configurações: {e}")
        try:
            from tkinter import messagebox
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
        except:
            pass

# INSTRUÇÕES:
# 1. Substitua a função save_anti_detection_config no main_window.py
# 2. Use apenas as variáveis que realmente existem
# 3. Adicione verificações hasattr() para evitar erros

print("""
🔧 CORREÇÃO PARA save_anti_detection_config:

1. A função original tentava usar variáveis que não existem:
   - self.human_delay_min_var ❌
   - self.human_delay_max_var ❌
   - self.random_pauses_var ❌ 
   - self.realistic_patterns_var ❌

2. A função corrigida usa apenas variáveis que EXISTEM:
   - self.click_delay_min_var ✅
   - self.click_delay_max_var ✅
   - self.click_variation_var ✅
   - self.movement_variation_var ✅
   - self.natural_breaks_var ✅

3. Adiciona verificações hasattr() para segurança
4. Converte ms para segundos corretamente
5. Trata erros adequadamente

📝 Copie a função save_anti_detection_config_FIXED acima e 
   substitua no arquivo ui/main_window.py
""")