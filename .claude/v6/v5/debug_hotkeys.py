#!/usr/bin/env python3
"""
Debug do sistema de hotkeys para identificar o problema do F9
"""

def debug_hotkey_issue():
    """Debugar problema com F9 executando troca de vara"""
    
    print("🔧 Debug do problema F9 -> troca de vara")
    print("\nProblema reportado:")
    print("- F9 deveria iniciar pesca (start_bot)")
    print("- F9 está executando troca de vara (trigger_rod_switch)")
    print("- TAB deveria fazer troca de vara")
    
    print("\n📋 Verificações necessárias:")
    
    print("\n1. Configuração de hotkeys:")
    print("   F9 -> start_bot ✅ (correto no código)")
    print("   TAB -> trigger_rod_switch ✅ (correto no código)")
    
    print("\n2. Possíveis causas:")
    print("   a) Sobreposição de hotkeys")
    print("   b) Conflito na biblioteca keyboard")
    print("   c) start_bot chamando trigger_rod_switch por engano")
    print("   d) Método start_bot redirecionando incorretamente")
    
    print("\n3. Soluções sugeridas:")
    print("   A) Verificar se start_bot está correto")
    print("   B) Limpar hotkeys e reconfigurar")
    print("   C) Adicionar debug em start_bot")
    print("   D) Verificar se há outros mapeamentos de F9")
    
    print("\n🔍 Análise do problema:")
    print("O log mostra:")
    print("- '🔧 [TAB] Trigger manual de troca de vara ativado'")
    print("- Isso indica que trigger_rod_switch está sendo chamado")
    print("- Mas deveria ser start_bot para F9")
    
    print("\n💡 Solução recomendada:")
    print("1. Adicionar debug print em start_bot")
    print("2. Verificar se há mapeamento duplo de F9")
    print("3. Limpar e recriar hotkeys")

if __name__ == "__main__":
    debug_hotkey_issue()
    
    print("\n" + "="*50)
    print("📝 CORREÇÃO SUGERIDA:")
    print("="*50)
    
    print("""
1. Adicione debug print no início de start_bot():

def start_bot(self):
    print("🎯 [DEBUG] start_bot() chamado por F9!")
    print("🔧 [F9] start_bot() chamado - iniciando bot...")
    
2. Verifique se não há conflito:
   - Procure por outros add_hotkey('f9', ...)
   - Verifique se keyboard está funcionando corretamente
   
3. Se o problema persistir, remova e re-adicione F9:
   keyboard.remove_hotkey('f9')
   keyboard.add_hotkey('f9', self.start_bot)
    """)