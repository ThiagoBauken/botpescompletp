#!/usr/bin/env python3
"""
Correção para o erro de save_anti_detection_config
"""

def fix_anti_detection_save():
    """Corrigir função save_anti_detection_config"""
    
    file_path = "D:/finalbot/fishing_bot_v4/ui/main_window.py"
    
    # Ler arquivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Texto problemático
    old_text = """                self.config_manager.set('anti_detection.human_delay.min', float(self.human_delay_min_var.get()))
                self.config_manager.set('anti_detection.human_delay.max', float(self.human_delay_max_var.get()))
                self.config_manager.set('anti_detection.movement_variation', self.movement_variation_var.get())
                self.config_manager.set('anti_detection.random_pauses', self.random_pauses_var.get())
                self.config_manager.set('anti_detection.realistic_patterns', self.realistic_patterns_var.get())"""
    
    # Texto corrigido
    new_text = """                # Salvar configurações de cliques (usando variáveis corretas)
                self.config_manager.set('anti_detection.click_variation.enabled', self.click_variation_var.get())
                self.config_manager.set('anti_detection.click_variation.min_delay', float(self.click_delay_min_var.get()) / 1000)  # converter ms para s
                self.config_manager.set('anti_detection.click_variation.max_delay', float(self.click_delay_max_var.get()) / 1000)  # converter ms para s
                
                # Salvar configurações de movimento  
                self.config_manager.set('anti_detection.movement_variation.enabled', self.movement_variation_var.get())
                self.config_manager.set('anti_detection.natural_breaks.enabled', self.natural_breaks_var.get())"""
    
    # Substituir
    if old_text in content:
        content = content.replace(old_text, new_text)
        
        # Salvar arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Arquivo corrigido com sucesso!")
        print("✅ Variáveis inexistentes substituídas por variáveis reais")
        return True
    else:
        print("❌ Texto para substituir não encontrado")
        print("O arquivo pode já estar corrigido ou ter sido modificado")
        return False

if __name__ == "__main__":
    print("🔧 Corrigindo erro save_anti_detection_config...")
    
    success = fix_anti_detection_save()
    
    if success:
        print("\n🎉 Correção aplicada!")
        print("📝 Agora salvar anti-detecção deve funcionar")
    else:
        print("\n⚠️ Não foi possível aplicar a correção automaticamente")
        print("📝 Verifique manualmente o arquivo ui/main_window.py")