#!/usr/bin/env python3
"""
🎣 Ultimate Fishing Bot v4.0 - Main Entry Point
Sistema principal com verificação de licença e inicialização modular
"""

import sys
import os
import traceback

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar codificação para Unicode no Windows
if sys.platform == "win32":
    import codecs
    import locale
    # Tentar configurar UTF-8 no console
    try:
        # Python 3.7+ suporta UTF-8 mode
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Fallback para versões antigas
        pass

def safe_print(text):
    """Print com fallback para caracteres Unicode"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remover emojis e caracteres especiais
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)

def main():
    """Função principal com sistema de licenciamento"""
    # INICIALIZAR CRASH-SAFE LOGGER PRIMEIRO (ANTES DE TUDO!)
    try:
        from utils.crash_safe_logger import (
            get_crash_safe_logger,
            log_info,
            log_error,
            log_exception,
            log_section,
            log_warning,
            log_debug
        )
        logger = get_crash_safe_logger(log_dir="data/logs", prefix="FULL_DEBUG")
        log_section("INÍCIO DO PROGRAMA")
        log_info("MAIN", "Ultimate Fishing Bot v4.0 - Inicializando...")
        log_info("MAIN", f"Python version: {sys.version}")
        log_info("MAIN", f"Platform: {sys.platform}")
        log_info("MAIN", f"Working directory: {os.getcwd()}")
    except Exception as e:
        print(f"ERRO AO INICIAR LOGGER: {e}")
        traceback.print_exc()
        input("Pressione Enter para sair...")
        return 1

    try:
        safe_print("\n" + "="*60)
        safe_print("🎣 Ultimate Fishing Bot v4.0 - Inicializando...")
        safe_print("="*60)
        log_info("MAIN", "Interface de console inicializada")
        
        # 1. Sistema de Licenciamento
        log_section("SISTEMA DE LICENCIAMENTO")
        safe_print("\n🔐 Inicializando sistema de licenças...")
        log_info("LICENSE", "Importando módulos de licença...")
        try:
            from utils.license_manager import LicenseManager
            from ui.license_dialog import LicenseDialog
            log_info("LICENSE", "Módulos importados com sucesso")

            log_info("LICENSE", "Criando LicenseManager...")
            license_manager = LicenseManager()
            log_info("LICENSE", "LicenseManager criado")

            # Verificar licença (seguindo lógica do v3 - linha 10264)
            log_info("LICENSE", "Verificando licença existente...")
            if not license_manager.check_license():
                log_info("LICENSE", "Licença não encontrada, solicitando ao usuário...")
                safe_print("\n🔐 Solicitando licença...")
                license_dialog = LicenseDialog(license_manager)
                license_key = license_dialog.show()

                if license_key:
                    log_info("LICENSE", f"Chave recebida: {license_key[:10]}...")
                    # Validar a chave (lógica do v3 - linha 10288)
                    valid, data = license_manager.validate_license(license_key)
                    if valid:
                        safe_print("✅ Licença ativada com sucesso!")
                        log_info("LICENSE", "Licença validada com sucesso")
                    else:
                        safe_print("❌ Falha na validação da licença")
                        log_error("LICENSE", "Falha na validação da licença")
                        input("Pressione Enter para sair...")
                        return 1
                else:
                    safe_print("❌ Licenciamento cancelado")
                    log_error("LICENSE", "Usuário cancelou o licenciamento")
                    input("Pressione Enter para sair...")
                    return 1
            else:
                log_info("LICENSE", "Licença válida encontrada")

            safe_print("✅ Sistema licenciado com sucesso!")
            log_info("LICENSE", "Sistema licenciado OK")

        except ImportError as e:
            safe_print(f"⚠️ Sistema de licenças não disponível: {e}")
            log_error("LICENSE", f"ImportError: {e}")
            safe_print("🔄 Continuando sem verificação de licença...")
            license_manager = None
        except Exception as e:
            log_exception("LICENSE", f"Erro inesperado no sistema de licenças: {e}")
            raise
        
        # 2. Sistema de Internacionalização
        log_section("SISTEMA DE INTERNACIONALIZAÇÃO")
        safe_print("\n🌍 Configurando idioma...")
        log_info("I18N", "Importando módulo i18n...")
        try:
            from utils.i18n import i18n, _
            safe_print("✅ Sistema i18n carregado")
            log_info("I18N", "Módulo i18n importado com sucesso")
        except ImportError as e:
            safe_print(f"⚠️ Sistema i18n não disponível: {e}")
            log_error("I18N", f"ImportError: {e}")
        except Exception as e:
            log_exception("I18N", f"Erro inesperado no i18n: {e}")
            raise

        # 3. Gerenciador de Configuração
        log_section("GERENCIADOR DE CONFIGURAÇÃO")
        safe_print("\n⚙️ Inicializando configurações...")
        log_info("CONFIG", "Tentando carregar ConfigManager...")
        try:
            # Tentar o novo ConfigManager primeiro
            log_info("CONFIG", "Importando core.config_manager...")
            from core.config_manager import ConfigManager
            log_info("CONFIG", "Criando instância do ConfigManager...")
            config = ConfigManager()
            safe_print("✅ ConfigManager v4.0 carregado")
            log_info("CONFIG", "ConfigManager v4.0 carregado com sucesso")
        except ImportError as e1:
            log_error("CONFIG", f"core.config_manager não encontrado: {e1}")
            try:
                # Fallback para config antigo
                log_info("CONFIG", "Tentando fallback para utils.config_manager...")
                from utils.config_manager import ConfigManager
                config = ConfigManager()
                safe_print("✅ Config legado carregado")
                log_info("CONFIG", "Config legado carregado com sucesso")
            except ImportError as e2:
                log_error("CONFIG", f"utils.config_manager também não encontrado: {e2}")
                config = None
                safe_print("⚠️ Nenhum ConfigManager disponível")
        except Exception as e:
            safe_print(f"⚠️ Erro no ConfigManager: {e}")
            log_exception("CONFIG", f"Erro ao criar ConfigManager: {e}")
            config = None

        if config:
            log_info("CONFIG", "ConfigManager criado, configurando idioma...")
            # Configurar idioma se disponível
            if 'i18n' in locals():
                language = config.get('ui_settings.language') or config.get('language', 'pt')
                log_info("CONFIG", f"Idioma detectado na config: {language}")
                i18n.set_language(language)
                safe_print(f"✅ Idioma configurado: {language}")
                log_info("CONFIG", f"Idioma {language} configurado no i18n")
        else:
            log_info("CONFIG", "Config não disponível, criando MockConfig...")
            # Criar MockConfig se necessário
            class MockConfig:
                def get(self, key, default=None): return default
                def set(self, key, value): pass
                def get_template_confidence(self, template): return 0.7
                def get_feeding_position(self, slot): return (1306, 858)
                def save_config(self): pass
                def has_template_categories(self): return False
                def get_template_categories(self): return {}
                def is_unified_format(self): return False
            config = MockConfig()
            safe_print("✅ MockConfig ativo")
            log_info("CONFIG", "MockConfig criado como fallback")

        # 4. Interface Principal
        log_section("INTERFACE PRINCIPAL")
        safe_print("\n🎨 Inicializando interface...")
        log_info("UI", "Importando FishingBotUI...")
        try:
            from ui.main_window import FishingBotUI
            log_info("UI", "Criando instância do FishingBotUI...")
            ui = FishingBotUI(config)
            safe_print("✅ Interface criada!")
            log_info("UI", "Interface criada com sucesso")
        except ImportError as e:
            safe_print(f"❌ Erro ao importar UI: {e}")
            log_exception("UI", f"Erro ao importar UI: {e}")
            traceback.print_exc()
            return 1
        except Exception as e:
            safe_print(f"❌ Erro ao criar UI: {e}")
            log_exception("UI", f"Erro ao criar UI: {e}")
            traceback.print_exc()
            return 1

        # 5. Iniciar sistema
        log_section("INICIANDO SISTEMA")
        safe_print("\n🚀 Iniciando Ultimate Fishing Bot v4.0...")
        safe_print("="*60)
        if license_manager and license_manager.is_licensed():
            safe_print("✅ Bot inicializado e licenciado com sucesso!")
            log_info("MAIN", "Bot licenciado e pronto")
        else:
            safe_print("⚠️ Bot inicializado sem verificação de licença")
            log_warning("MAIN", "Bot rodando sem licença")
        safe_print("🎮 Use a interface gráfica para controlar o bot")
        safe_print("🌍 Seletor de idioma disponível no canto inferior direito")
        safe_print("="*60)

        log_info("MAIN", "Executando UI.run()...")
        log_info("MAIN", "═══════════════════════════════════════════════════════════")
        log_info("MAIN", "   SISTEMA INICIALIZADO - MONITORANDO OPERAÇÕES")
        log_info("MAIN", "═══════════════════════════════════════════════════════════")

        # Executar UI
        ui.run()

        log_info("MAIN", "UI.run() retornou, encerrando aplicação...")
        return 0

    except KeyboardInterrupt:
        safe_print("\n🛑 Interrompido pelo usuário")
        log_warning("MAIN", "Programa interrompido por KeyboardInterrupt")
        return 0
    except Exception as e:
        safe_print(f"❌ Erro fatal: {e}")
        log_exception("MAIN", f"ERRO FATAL: {e}")
        traceback.print_exc()
        input("Pressione Enter para sair...")
        return 1

if __name__ == "__main__":
    sys.exit(main())