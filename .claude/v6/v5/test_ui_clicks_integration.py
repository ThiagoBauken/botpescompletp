#!/usr/bin/env python3
"""
Teste específico para verificar se a aba de configurações
funciona corretamente com o sistema de cliques
"""

def test_config_flow():
    """Testar fluxo completo: UI -> Config -> InputManager"""
    try:
        from core.config_manager import ConfigManager
        from core.input_manager import InputManager
        
        print("🔧 Testando fluxo completo da configuração...")
        
        # 1. Simular salvamento da UI
        config = ConfigManager()
        
        # Simular valores da UI (como se usuário digitasse na interface)
        ui_clicks_per_second = 15
        
        print(f"📝 Simulando UI: usuário define {ui_clicks_per_second} cliques/s")
        
        # 2. Salvar como a UI faz
        config.set('performance.clicks_per_second', ui_clicks_per_second)
        
        # 3. Verificar se foi salvo
        saved_value = config.get('performance.clicks_per_second')
        print(f"💾 Valor salvo no config: {saved_value}")
        
        if saved_value != ui_clicks_per_second:
            print("❌ Valor não foi salvo corretamente!")
            return False
        
        # 4. Criar InputManager (como o sistema faz)
        input_manager = InputManager(config_manager=config)
        
        # 5. Verificar se InputManager carregou corretamente
        expected_delay = 1.0 / ui_clicks_per_second  # ~0.067s para 15 cliques/s
        actual_delay = input_manager.timing_config['click_delay']
        
        print(f"⏱️ Delay esperado: {expected_delay:.3f}s")
        print(f"⏱️ Delay no InputManager: {actual_delay:.3f}s")
        
        if abs(actual_delay - expected_delay) < 0.001:
            print("✅ InputManager carregou configuração da UI corretamente!")
        else:
            print("❌ InputManager NÃO carregou configuração da UI!")
            return False
        
        # 6. Testar reload dinâmico
        print("\n🔄 Testando reload dinâmico...")
        
        # Simular mudança na UI
        new_speed = 20
        config.set('performance.clicks_per_second', new_speed)
        
        # Chamar reload (como a UI faz ao salvar)
        input_manager.reload_timing_config()
        
        # Verificar se atualizou
        new_expected_delay = 1.0 / new_speed  # 0.05s para 20 cliques/s
        new_actual_delay = input_manager.timing_config['click_delay']
        
        print(f"🔄 Novo delay esperado: {new_expected_delay:.3f}s")
        print(f"🔄 Novo delay no InputManager: {new_actual_delay:.3f}s")
        
        if abs(new_actual_delay - new_expected_delay) < 0.001:
            print("✅ Reload dinâmico funcionando!")
            return True
        else:
            print("❌ Reload dinâmico NÃO funcionando!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_to_continuous_clicks():
    """Testar se cliques contínuos usam configuração da UI"""
    try:
        from core.config_manager import ConfigManager
        from core.input_manager import InputManager
        
        print("\n🖱️ Testando cliques contínuos com configuração da UI...")
        
        # Configurar diferentes velocidades
        test_speeds = [8, 12, 15, 20]
        
        for speed in test_speeds:
            print(f"\n⚡ Testando {speed} cliques/s...")
            
            # Configurar
            config = ConfigManager()
            config.set('performance.clicks_per_second', speed)
            
            # Criar InputManager
            input_manager = InputManager(config_manager=config)
            
            # Simular início de cliques contínuos (sem realmente clicar)
            # Verificar se a velocidade é calculada corretamente
            
            # Verificar delay calculado
            calculated_delay = input_manager.timing_config['click_delay']
            expected_delay = 1.0 / speed
            
            print(f"  Delay calculado: {calculated_delay:.3f}s")
            print(f"  Delay esperado: {expected_delay:.3f}s")
            
            if abs(calculated_delay - expected_delay) < 0.001:
                print(f"  ✅ {speed} cliques/s configurado corretamente")
            else:
                print(f"  ❌ {speed} cliques/s NÃO configurado corretamente")
                return False
        
        print("\n✅ Cliques contínuos funcionando com todas as velocidades da UI!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de cliques contínuos: {e}")
        return False

def test_default_values():
    """Testar valores padrão"""
    try:
        from core.config_manager import ConfigManager
        from core.input_manager import InputManager
        
        print("\n📋 Testando valores padrão...")
        
        # Criar config sem definir nada
        config = ConfigManager()
        
        # Verificar valor padrão
        default_speed = config.get('performance.clicks_per_second', 12)  # 12 é o padrão
        print(f"🎯 Velocidade padrão: {default_speed} cliques/s")
        
        # Criar InputManager
        input_manager = InputManager(config_manager=config)
        
        # Verificar se carregou o padrão
        expected_delay = 1.0 / default_speed
        actual_delay = input_manager.timing_config['click_delay']
        
        print(f"⏱️ Delay padrão esperado: {expected_delay:.3f}s")
        print(f"⏱️ Delay padrão carregado: {actual_delay:.3f}s")
        
        if abs(actual_delay - expected_delay) < 0.001:
            print("✅ Valores padrão funcionando!")
            return True
        else:
            print("❌ Valores padrão NÃO funcionando!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de padrões: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Teste de Integração: Aba Config -> Sistema de Cliques\n")
    
    test1 = test_config_flow()
    test2 = test_ui_to_continuous_clicks()
    test3 = test_default_values()
    
    print("\n" + "="*60)
    if test1 and test2 and test3:
        print("🎉 SUCESSO: Aba de configurações funciona perfeitamente!")
        print("✅ UI -> Config -> InputManager: funcionando")
        print("✅ Reload dinâmico: funcionando")
        print("✅ Cliques contínuos: usando configuração da UI")
        print("✅ Valores padrão: funcionando")
        print("\n👍 Resposta: SIM, a aba de config funciona para cliques por segundo!")
    else:
        print("❌ PROBLEMA: Aba de configurações NÃO funciona corretamente!")
        print("\n👎 Resposta: NÃO, há problemas na integração da aba de config!")
    print("="*60)