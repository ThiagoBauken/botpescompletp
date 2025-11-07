#!/usr/bin/env python3
"""
🎣 Ultimate Fishing Bot v5.0 - Main Entry Point
Sistema principal com verificação de licença e inicialização modular
"""

import sys
import os
import traceback

# Adicionar pasta atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════
# OCULTAR JANELA CMD NO WINDOWS
# ═══════════════════════════════════════════════════════
if sys.platform == "win32":
    try:
        import ctypes
        import ctypes.wintypes

        # Obter handle da janela do console
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        user32 = ctypes.WinDLL('user32', use_last_error=True)

        # Obter handle da janela do console atual
        hwnd = kernel32.GetConsoleWindow()

        if hwnd:
            # SW_HIDE = 0 (ocultar janela)
            user32.ShowWindow(hwnd, 0)
    except Exception as e:
        # Se falhar, continuar normalmente
        pass

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
    try:
        # ═══════════════════════════════════════════════════════
        # CONFIGURAR NÍVEL DE LOG NO CONSOLE (QUIET/NORMAL/VERBOSE)
        # ═══════════════════════════════════════════════════════
        try:
            from utils.console_logger import console_logger, LogLevel
            import os

            # Ler nível de log do config ou variável de ambiente
            log_level_str = os.getenv("CONSOLE_LOG_LEVEL", "QUIET").upper()

            # Mapear string para enum
            level_map = {
                "QUIET": LogLevel.QUIET,
                "NORMAL": LogLevel.NORMAL,
                "VERBOSE": LogLevel.VERBOSE
            }

            log_level = level_map.get(log_level_str, LogLevel.QUIET)
            console_logger.set_level(log_level)

            safe_print(f"\n✅ Console log level: {log_level.name}")
        except Exception as e:
            safe_print(f"⚠️ Erro ao configurar console logger: {e}")

        safe_print("\n" + "="*60)
        safe_print("🎣 Ultimate Fishing Bot v5.0 - Inicializando...")
        safe_print("="*60)

        # 1. Sistema de Internacionalização
        safe_print("\n🌍 Configurando idioma...")
        try:
            from utils.license_manager import LicenseManager
            from ui.license_dialog import LicenseDialog

            license_manager = LicenseManager()

            # Verificar licença (seguindo lógica do v3 - linha 10264)
            if not license_manager.check_license():
                safe_print("\n🔐 Solicitando licença...")
                license_dialog = LicenseDialog(license_manager)
                license_key = license_dialog.show()

                if license_key:
                    # Validar a chave (lógica do v3 - linha 10288)
                    valid, data = license_manager.validate_license(license_key)
                    if valid:
                        safe_print("✅ Licença ativada com sucesso!")
                    else:
                        safe_print("❌ Falha na validação da licença")
                        input("Pressione Enter para sair...")
                        return 1
                else:
                    safe_print("❌ Licenciamento cancelado")
                    input("Pressione Enter para sair...")
                    return 1
            else:
                safe_print("✅ Sistema licenciado com sucesso!")

        except ImportError as e:
            safe_print(f"⚠️ Sistema de licenças não disponível: {e}")
            safe_print("🔄 Continuando sem verificação de licença...")
            license_manager = None
        except Exception as e:
            raise

        # 2. Sistema de Internacionalização
        safe_print("\n🌍 Configurando idioma...")
        try:
            from utils.i18n import i18n, _
            safe_print("✅ Sistema i18n carregado")
        except ImportError as e:
            safe_print(f"⚠️ Sistema i18n não disponível: {e}")
        except Exception as e:
            raise

        # 3. Gerenciador de Configuração
        safe_print("\n⚙️ Inicializando configurações...")
        try:
            # Tentar o novo ConfigManager primeiro
            from core.config_manager import ConfigManager
            config = ConfigManager()
            safe_print("✅ ConfigManager v5.0 carregado")
        except ImportError as e1:
            try:
                # Fallback para config antigo
                from utils.config_manager import ConfigManager
                config = ConfigManager()
                safe_print("✅ Config legado carregado")
            except ImportError as e2:
                config = None
                safe_print("⚠️ Nenhum ConfigManager disponível")
        except Exception as e:
            safe_print(f"⚠️ Erro no ConfigManager: {e}")
            config = None

        if config:
            # Configurar idioma se disponível
            if 'i18n' in locals():
                language = config.get('ui_settings.language') or config.get('language', 'pt')
                i18n.set_language(language)
                safe_print(f"✅ Idioma configurado: {language}")
        else:
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

        # 4. Servidor Multi-Usuário (Novo Fluxo com Login/Senha/License)
        ws_client = None
        try:
            # Verificar se licença está válida
            if license_manager and license_manager.is_licensed():
                safe_print("\n🌐 Conectando ao servidor multi-usuário...")

                # Importar módulos necessários
                from client.server_connector import connect_to_server, register_server_callbacks
                from client.credential_manager import CredentialManager
                from client.activation_dialog import ActivationDialog

                # Criar gerenciador de credenciais
                cred_manager = CredentialManager()

                # Verificar se existem credenciais salvas
                saved_credentials = cred_manager.load_credentials()

                if saved_credentials:
                    # Usar credenciais salvas
                    safe_print("   🔐 Credenciais salvas encontradas")

                    login = saved_credentials['login']
                    password = saved_credentials['password']
                    license_key = saved_credentials['license_key']

                else:
                    # Solicitar ativação (primeira vez)
                    safe_print("   🔐 Primeira ativação - solicitando credenciais...")

                    activation_dialog = ActivationDialog()
                    activation_result = activation_dialog.show()

                    if not activation_result:
                        safe_print("   ⚠️ Ativação cancelada - continuando offline")
                        login = None
                        password = None
                        license_key = None
                    else:
                        login = activation_result['login']
                        password = activation_result['password']
                        license_key = activation_result['license_key']

                        # Salvar credenciais se solicitado
                        if activation_result['remember']:
                            safe_print("   💾 Salvando credenciais...")
                            cred_manager.save_credentials(login, password, license_key)

                # Tentar conectar ao servidor
                if login and password and license_key:
                    # Ler URL do servidor do config.json
                    server_url = config.get('server.url', 'wss://private-serverpesca.pbzgje.easypanel.host/ws')
                    safe_print(f"   🌐 Conectando em: {server_url}")

                    ws_client = connect_to_server(
                        login=login,
                        password=password,
                        license_key=license_key,
                        server_url=server_url,
                        config_manager=config  # ✅ Passar config existente!
                    )

                    if ws_client:
                        safe_print("✅ Conectado ao servidor multi-usuário!")
                    else:
                        safe_print("⚠️ Não foi possível conectar ao servidor")
                        safe_print("   Bot continuará em modo offline")
                else:
                    safe_print("⚠️ Bot rodará em modo offline (sem servidor)")

            else:
                safe_print("⚠️ Bot rodará em modo offline (sem licença)")

        except ImportError as e:
            safe_print(f"⚠️ Módulo de servidor não disponível: {e}")
        except Exception as e:
            safe_print(f"⚠️ Erro ao conectar ao servidor: {e}")
            import traceback
            traceback.print_exc()

        # 5. Interface Principal
        safe_print("\n🎨 Inicializando interface...")
        try:
            from ui.main_window import FishingBotUI
            ui = FishingBotUI(config, ws_client=ws_client)  # ✅ Passar ws_client
            safe_print("✅ Interface criada!")

            # 5.1. Registrar callbacks do servidor (se conectado)
            if ws_client and ws_client.is_connected():
                try:
                    register_server_callbacks(ws_client, ui.fishing_engine)
                    safe_print("✅ Callbacks do servidor registrados!")
                except Exception as e:
                    safe_print(f"⚠️ Erro ao registrar callbacks: {e}")

        except ImportError as e:
            safe_print(f"❌ Erro ao importar UI: {e}")
            traceback.print_exc()
            return 1
        except Exception as e:
            safe_print(f"❌ Erro ao criar UI: {e}")
            traceback.print_exc()
            return 1

        # 6. Iniciar sistema
        safe_print("\n🚀 Iniciando Ultimate Fishing Bot v5.0...")
        safe_print("="*60)
        if license_manager and license_manager.is_licensed():
            safe_print("✅ Bot inicializado e licenciado com sucesso!")
        else:
            safe_print("⚠️ Bot inicializado sem verificação de licença")
        safe_print("🎮 Use a interface gráfica para controlar o bot")
        safe_print("🌍 Seletor de idioma disponível no canto inferior direito")
        safe_print("="*60)


        # Executar UI
        ui.run()

        return 0

    except KeyboardInterrupt:
        safe_print("\n🛑 Interrompido pelo usuário")
        return 0
    except Exception as e:
        safe_print(f"❌ Erro fatal: {e}")
        traceback.print_exc()
        input("Pressione Enter para sair...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
