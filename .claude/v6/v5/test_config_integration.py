#!/usr/bin/env python3
"""
Teste de integração de configurações da UI com o sistema de pesca
"""

def test_config_loading():
    """Testar carregamento de configurações"""
    try:
        from core.config_manager import ConfigManager
        from core.input_manager import InputManager
        
        print("🔧 Testando carregamento de configurações...")
        
        # Criar ConfigManager
        config = ConfigManager()
        
        # Simular configuração da UI
        config.set('performance.clicks_per_second', 15)  # 15 cliques/s
        config.set('cycle_timeout', 120)
        config.set('anti_detection.enabled', True)
        
        print(f"✅ Configuração definida: clicks_per_second = {config.get('performance.clicks_per_second')}")
        
        # Criar InputManager
        input_manager = InputManager(config_manager=config)
        
        # Verificar se carregou corretamente
        click_delay = input_manager.timing_config['click_delay']
        expected_delay = 1.0 / 15  # ~0.067s
        
        print(f"📊 Delay de clique calculado: {click_delay:.3f}s (esperado: {expected_delay:.3f}s)")
        
        if abs(click_delay - expected_delay) < 0.001:
            print("✅ Configuração de cliques carregada corretamente!")
        else:
            print("❌ Configuração de cliques não está sendo aplicada")
            
        # Testar reload
        print("\n🔄 Testando reload de configurações...")
        config.set('performance.clicks_per_second', 20)  # Mudar para 20 cliques/s
        input_manager.reload_timing_config()
        
        new_delay = input_manager.timing_config['click_delay']
        expected_new_delay = 1.0 / 20  # 0.05s
        
        print(f"📊 Novo delay de clique: {new_delay:.3f}s (esperado: {expected_new_delay:.3f}s)")
        
        if abs(new_delay - expected_new_delay) < 0.001:
            print("✅ Reload de configurações funcionando!")
            return True
        else:
            print("❌ Reload de configurações não funcionando")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_button_state():
    """Testar controle de estado do botão direito"""
    try:
        from core.config_manager import ConfigManager
        from core.input_manager import InputManager
        
        print("\n🖱️ Testando controle de estado do botão...")
        
        config = ConfigManager()
        input_manager = InputManager(config_manager=config)
        
        # Estado inicial
        print(f"Estado inicial botão direito: {input_manager.mouse_state['right_button_down']}")
        
        # Simular início de pesca (sem pressionar botão real)
        input_manager.mouse_state['right_button_down'] = True
        print(f"Após 'início' pesca: {input_manager.mouse_state['right_button_down']}")
        
        # Simular parada com emergency_stop
        input_manager.emergency_stop()
        print(f"Após emergency_stop: {input_manager.mouse_state['right_button_down']}")
        
        if not input_manager.mouse_state['right_button_down']:
            print("✅ Emergency stop limpa estado do botão corretamente!")
            return True
        else:
            print("❌ Emergency stop não limpa estado do botão")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de botão: {e}")
        return False

if __name__ == "__main__":
    print("🎣 Teste de Integração de Configurações\n")
    
    success1 = test_config_loading()
    success2 = test_button_state()
    
    if success1 and success2:
        print("\n🎉 Todos os testes passaram!")
        print("✅ Sistema está corretamente integrado")
    else:
        print("\n❌ Alguns testes falharam")
        print("⚠️ Verifique a integração das configurações")