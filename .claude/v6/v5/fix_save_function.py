#!/usr/bin/env python3
"""
Correção rápida para o erro de save_anti_detection_config
"""

import re

def fix_save_function():
    """Corrigir função de salvamento"""
    
    print("🔧 Corrigindo função save_anti_detection_config...")
    
    # Ler arquivo
    with open("ui/main_window.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Padrão a ser substituído
    pattern = r"self\.config_manager\.set\('anti_detection\.human_delay\.min', float\(self\.human_delay_min_var\.get\(\)\)\)"
    replacement = "self.config_manager.set('anti_detection.click_variation.min_delay', float(self.click_delay_min_var.get()) / 1000)"
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("✅ Substituído human_delay.min")
    
    # Segundo padrão
    pattern2 = r"self\.config_manager\.set\('anti_detection\.human_delay\.max', float\(self\.human_delay_max_var\.get\(\)\)\)"
    replacement2 = "self.config_manager.set('anti_detection.click_variation.max_delay', float(self.click_delay_max_var.get()) / 1000)"
    
    if re.search(pattern2, content):
        content = re.sub(pattern2, replacement2, content)
        print("✅ Substituído human_delay.max")
    
    # Remover linhas problemáticas que referenciam variáveis inexistentes
    patterns_to_remove = [
        r"self\.config_manager\.set\('anti_detection\.random_pauses', self\.random_pauses_var\.get\(\)\)",
        r"self\.config_manager\.set\('anti_detection\.realistic_patterns', self\.realistic_patterns_var\.get\(\)\)"
    ]
    
    for pattern in patterns_to_remove:
        if re.search(pattern, content):
            content = re.sub(pattern + r"\s*\n", "", content)
            print(f"✅ Removido linha problemática")
    
    # Salvar arquivo corrigido
    with open("ui/main_window.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Arquivo corrigido!")
    return True

if __name__ == "__main__":
    import os
    os.chdir("D:/finalbot/fishing_bot_v4")
    
    try:
        fix_save_function()
        print("\n🎉 Correção aplicada com sucesso!")
        print("📝 Agora salvar anti-detecção deve funcionar")
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("📝 Correção manual necessária")