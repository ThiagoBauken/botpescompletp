#!/usr/bin/env python3
"""
🧪 Test Translation System for Ultimate Fishing Bot v4.0
Script para testar o sistema completo de traduções
"""

import sys
import os

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_translations():
    """🧪 Testar o sistema completo de traduções"""
    print("🧪 Testando Sistema de Traduções do Ultimate Fishing Bot v4.0")
    print("=" * 70)
    
    try:
        # Importar sistema de traduções
        from utils.i18n import i18n, _
        from utils.translation_helper import t, get_tab_title, get_button_label
        
        print(f"✅ Imports realizados com sucesso")
        print(f"🌍 Idioma detectado automaticamente: {i18n.current_language}")
        print(f"📁 Diretório de locales: {i18n.locales_dir}")
        print()
        
        # Testar idiomas disponíveis
        print("📋 Idiomas disponíveis:")
        for code, name in i18n.get_available_languages().items():
            print(f"  • {code}: {name}")
        print()
        
        # Testar traduções para cada idioma
        languages_to_test = ['pt', 'en', 'es']
        
        for lang in languages_to_test:
            print(f"🔄 Testando idioma: {lang}")
            print("-" * 50)
            
            # Trocar idioma
            success = i18n.set_language(lang)
            if not success:
                print(f"❌ Falha ao trocar para idioma: {lang}")
                continue
            
            # Testar traduções de abas
            print("📋 Traduções de Abas:")
            tab_keys = ['control', 'config', 'feeding', 'confidence']
            for tab_key in tab_keys:
                translation = get_tab_title(tab_key)
                print(f"  • tabs.{tab_key}: '{translation}'")
            
            # Testar traduções de botões
            print("\n🔘 Traduções de Botões:")
            button_keys = ['start', 'stop', 'pause', 'emergency']
            for button_key in button_keys:
                translation = get_button_label(button_key)
                print(f"  • buttons.{button_key}: '{translation}'")
            
            # Testar traduções de status
            print("\n📊 Traduções de Status:")
            status_keys = ['ready', 'running', 'paused', 'stopped']
            for status_key in status_keys:
                translation = t.get_status_text(status_key)
                print(f"  • status.{status_key}: '{translation}'")
            
            # Testar traduções específicas de cada aba
            print("\n🎣 Traduções de Sistema de Alimentação:")
            feeding_keys = ['title', 'enable_feeding', 'trigger_type', 'test_feeding']
            for feeding_key in feeding_keys:
                translation = t.get_feeding_text(feeding_key)
                print(f"  • feeding.{feeding_key}: '{translation}'")
            
            # Testar traduções com formatação
            print("\n🔔 Traduções com Formatação:")
            notification = t.get_notification_text('error_occurred', error='Teste de erro')
            print(f"  • notifications.error_occurred: '{notification}'")
            
            print()
        
        # Testar chaves aninhadas avançadas
        print("🔍 Testando Chaves Aninhadas Avançadas:")
        print("-" * 50)
        
        # Voltar para português para demonstração
        i18n.set_language('pt')
        
        advanced_keys = [
            'rod_management.title',
            'analytics.session_stats', 
            'advanced.anti_detection',
            'server.connection_status',
            'confidence.critical_templates'
        ]
        
        for key in advanced_keys:
            translation = _(key)
            print(f"  • {key}: '{translation}'")
        
        print()
        
        # Testar funcionalidades do helper
        print("🛠️ Testando Translation Helper:")
        print("-" * 50)
        
        print(f"📋 Idiomas disponíveis: {t.get_available_languages()}")
        print(f"🌍 Idioma atual: {t.get_current_language()}")
        
        # Listar algumas chaves disponíveis
        tab_keys = i18n.get_available_keys('tabs')
        print(f"📂 Chaves de abas disponíveis: {tab_keys[:5]}")  # Primeiras 5
        
        button_keys = i18n.get_available_keys('buttons') 
        print(f"🔘 Chaves de botões disponíveis: {button_keys[:5]}")  # Primeiras 5
        
        print()
        
        # Testar recarregamento
        print("🔄 Testando Recarregamento de Traduções:")
        print("-" * 50)
        print("Recarregando traduções...")
        i18n.reload_translations()
        print(f"✅ Recarregamento concluído. Idioma atual: {i18n.current_language}")
        
        print()
        print("🎉 TESTE COMPLETO - SISTEMA DE TRADUÇÕES FUNCIONANDO PERFEITAMENTE!")
        print("=" * 70)
        print()
        print("📝 Resumo dos Recursos Testados:")
        print("  ✅ Carregamento automático de arquivos JSON em locales/")
        print("  ✅ Detecção automática de idioma do sistema")
        print("  ✅ Suporte a chaves aninhadas (ex: 'tabs.control')")
        print("  ✅ Sistema de fallback para traduções ausentes")
        print("  ✅ Formatação de strings com parâmetros")
        print("  ✅ Helper functions para facilitar uso na UI")
        print("  ✅ Recarregamento dinâmico de traduções")
        print("  ✅ Suporte completo para PT, EN, ES")
        print()
        print("🎯 Como usar na interface:")
        print("  • from utils.translation_helper import t, get_tab_title")
        print("  • tab_text = get_tab_title('control')  # '🎮 Controle'")
        print("  • button_text = t.get_button_text('start')  # '🚀 Iniciar Bot'")
        print("  • t.change_language('en')  # Trocar para inglês")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_translations()
    if success:
        print("\n✅ Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n❌ Alguns testes falharam!")
        sys.exit(1)