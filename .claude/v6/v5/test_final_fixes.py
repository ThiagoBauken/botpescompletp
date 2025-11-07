#!/usr/bin/env python3
"""
Teste final das correções
"""

def test_template_engine_capture():
    """Testar captura de tela thread-safe"""
    try:
        from core.template_engine import TemplateEngine
        from core.config_manager import ConfigManager
        
        print("🔧 Testando TemplateEngine com captura thread-safe...")
        
        config = ConfigManager()
        engine = TemplateEngine(config_manager=config)
        
        # Testar captura de tela
        screenshot = engine.capture_screen()
        if screenshot is not None:
            print(f"✅ Captura funcionando: {screenshot.shape}")
            return True
        else:
            print("❌ Falha na captura")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_gamestate_class():
    """Testar se GameState é a classe real"""
    try:
        from core.game_state import GameState, GameMode
        
        print("🎮 Testando GameState real...")
        
        # Criar GameState
        gs = GameState()
        
        # Testar método que estava falhando
        can_fish, reason = gs.can_start_fishing()
        print(f"✅ can_start_fishing(): {can_fish}, {reason}")
        
        # Testar change_mode
        gs.change_mode(GameMode.FISHING, "teste")
        print(f"✅ change_mode funciona, modo atual: {gs.current_mode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no GameState: {e}")
        return False

def test_rod_detection():
    """Testar detecção de vara"""
    try:
        from core.template_engine import TemplateEngine
        from core.config_manager import ConfigManager
        
        print("🎣 Testando detecção de vara...")
        
        config = ConfigManager()
        engine = TemplateEngine(config_manager=config)
        
        # Testar detect_rod_status (que estava falhando)
        status = engine.detect_rod_status(1)
        print(f"✅ detect_rod_status(1): {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na detecção de vara: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Teste Final das Correções\n")
    
    test1 = test_template_engine_capture()
    test2 = test_gamestate_class()
    test3 = test_rod_detection()
    
    if test1 and test2 and test3:
        print("\n🎉 Todas as correções funcionando!")
    else:
        print("\n⚠️ Algumas correções ainda precisam de ajuste")