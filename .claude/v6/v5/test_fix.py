#!/usr/bin/env python3
"""
Teste rápido para verificar se os erros foram corrigidos
"""

def test_template_engine():
    """Testar TemplateEngine com captura de tela"""
    try:
        from core.template_engine import TemplateEngine
        from core.config_manager import ConfigManager
        
        config = ConfigManager()
        engine = TemplateEngine(config_manager=config)
        
        # Testar captura de tela
        screenshot = engine.capture_screen()
        if screenshot is not None:
            print("✅ Captura de tela funcionando")
            return True
        else:
            print("❌ Falha na captura de tela")
            return False
            
    except Exception as e:
        print(f"❌ Erro no TemplateEngine: {e}")
        return False

def test_game_mode():
    """Testar GameMode import"""
    try:
        from core.game_state import GameMode
        from core.fishing_engine import FishingEngine
        
        print(f"✅ GameMode disponível: {list(GameMode)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no GameMode: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testando correções...")
    
    print("\n1. Testando TemplateEngine...")
    test_template_engine()
    
    print("\n2. Testando GameMode...")
    test_game_mode()
    
    print("\n✅ Testes concluídos!")