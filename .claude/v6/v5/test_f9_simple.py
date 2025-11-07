#!/usr/bin/env python3
"""
🧪 Teste Simples F9
Verificar se F9 está chamando start_bot ou trigger_rod_switch
"""

def test_f9_mapping():
    """Teste simples do mapeamento F9"""
    print("🧪 Testando mapeamento F9...")
    
    try:
        # Simular a classe UI
        class MockUI:
            def __init__(self):
                self.f9_calls = 0
                self.tab_calls = 0
            
            def start_bot(self):
                self.f9_calls += 1
                print(f"✅ start_bot() chamado! Total: {self.f9_calls}")
                return True
            
            def trigger_rod_switch(self):
                self.tab_calls += 1
                print(f"🔄 trigger_rod_switch() chamado! Total: {self.tab_calls}")
                return True
        
        # Testar mapeamento
        ui = MockUI()
        
        # Simular configuração de hotkeys
        hotkeys_config = {
            'f9': ('start_bot', "🚀 Iniciar bot"),
            'tab': ('trigger_rod_switch', "🎣 Troca de vara")
        }
        
        print("🔧 Testando getattr...")
        for hotkey, (method_name, description) in hotkeys_config.items():
            method = getattr(ui, method_name, None)
            if method:
                print(f"✅ {hotkey.upper()}: {method_name} -> {method}")
                # Testar chamada
                result = method()
                print(f"    Resultado: {result}")
            else:
                print(f"❌ {hotkey.upper()}: método {method_name} não encontrado")
        
        # Verificar resultados
        print(f"\n📊 Resultados:")
        print(f"start_bot calls: {ui.f9_calls}")
        print(f"trigger_rod_switch calls: {ui.tab_calls}")
        
        if ui.f9_calls == 1 and ui.tab_calls == 1:
            print("✅ Ambos os métodos funcionaram corretamente")
            return True
        else:
            print("❌ Problemas no mapeamento de métodos")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_f9_mapping()