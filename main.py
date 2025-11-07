#!/usr/bin/env python3
"""
🎣 Ultimate Fishing Bot v5.0 - Main Entry Point
Sistema principal com verificação de licença e inicialização modular
"""

import sys
import os
import traceback

# ✅ Adicionar pasta atual ao path (funciona em .exe e Python)
if getattr(sys, 'frozen', False):
    # Rodando como .exe
    base_dir = os.path.dirname(sys.executable)
else:
    # Rodando como script Python
    base_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_dir)

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

        # 1. Sistema de Autenticação Unificado (License + Login)
        safe_print("\n🔐 Verificando autenticação...")
        license_manager = None
        ws_client = None

        try:
            from utils.license_manager import LicenseManager
            from client.credential_manager import CredentialManager
            from ui.unified_auth_dialog import UnifiedAuthDialog
            from client.server_connector import connect_to_server, register_server_callbacks

            license_manager = LicenseManager()
            cred_manager = CredentialManager()

            # Verificar se já está autenticado (license.key E credentials.dat válidos)
            safe_print("⏳ Validando licença online... (pode levar alguns segundos)")
            license_valid = license_manager.check_license()
            credentials_valid = cred_manager.load_credentials() is not None

            # ✅ Mostrar hardware ID atual para debug
            safe_print(f"\n🆔 Hardware ID deste computador: {license_manager.get_hardware_id_display()}")

            if license_valid and credentials_valid:
                # ✅ Já autenticado - pular dialog
                safe_print("✅ Autenticação existente encontrada!")
                safe_print("   📝 License key: Válida")
                safe_print("   🔐 Credenciais: Salvas")

                # Carregar credenciais para conectar ao servidor
                saved_credentials = cred_manager.load_credentials()
                login = saved_credentials['login']
                password = saved_credentials['password']
                license_key = saved_credentials['license_key']

                # ✅ CORREÇÃO: Sincronizar license.key com credentials.dat
                # Se license.key foi atualizado manualmente, atualizar credentials.dat também
                license_key_from_file = license_manager.load_license()
                if license_key_from_file and license_key_from_file != license_key:
                    safe_print("\n⚠️ Detectada atualização de licença - sincronizando...")
                    safe_print(f"   Antiga: {license_key[:10]}...")
                    safe_print(f"   Nova: {license_key_from_file[:10]}...")

                    # Atualizar credentials.dat com a nova chave
                    license_key = license_key_from_file
                    cred_manager.save_credentials(login, password, license_key)
                    safe_print("   ✅ Credenciais sincronizadas!")

            else:
                # ❌ Não autenticado - mostrar dialog unificado UMA VEZ
                safe_print("\n🔐 Primeira autenticação necessária...")
                safe_print("   Por favor, insira suas credenciais:")

                # Mostrar dialog unificado
                auth_dialog = UnifiedAuthDialog(license_manager)
                auth_result = auth_dialog.show()

                if not auth_result:
                    safe_print("❌ Autenticação cancelada")
                    input("Pressione Enter para sair...")
                    return 1

                # Extrair credenciais
                login = auth_result['login']
                password = auth_result['password']
                license_key = auth_result['license_key']
                remember = auth_result['remember']

                # Salvar credenciais se solicitado
                if remember:
                    safe_print("   💾 Salvando credenciais...")
                    cred_manager.save_credentials(login, password, license_key)

                safe_print("✅ Autenticação completa!")

            # ✅ VERIFICAR SE A LICENÇA ESTÁ EXPIRADA E SE O HARDWARE_ID CORRESPONDE
            if license_manager and license_manager.is_licensed():
                from datetime import datetime

                license_info = license_manager.get_license_info()

                # ✅ VERIFICAÇÃO DE HARDWARE_ID (Proteção contra cópia de license.key)
                registered_hardware_id = license_info.get('hardware_id')
                current_hardware_id = license_manager.hardware_id

                if registered_hardware_id and registered_hardware_id != current_hardware_id:
                    safe_print("\n" + "="*60)
                    safe_print("❌ HARDWARE ID NÃO CORRESPONDE!")
                    safe_print("="*60)
                    safe_print("")
                    safe_print("⚠️ Esta licença está registrada para outro computador.")
                    safe_print(f"🆔 Hardware ID registrado: {registered_hardware_id[:8]}...{registered_hardware_id[-8:]}")
                    safe_print(f"🆔 Hardware ID atual: {license_manager.get_hardware_id_display()}")
                    safe_print("")
                    safe_print("💡 Entre em contato para transferir a licença para este computador.")
                    safe_print("="*60)

                    # Remover licença inválida
                    try:
                        import os
                        if os.path.exists(license_manager.license_file):
                            os.remove(license_manager.license_file)
                            safe_print("🗑️ Licença inválida removida.")
                    except:
                        pass

                    input("\nPressione Enter para sair...")
                    return 1

                expires_at_str = license_info.get('expires_at')

                if expires_at_str:
                    try:
                        # Parse da data de expiração
                        expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
                        now = datetime.now(expires_at.tzinfo)

                        # Verificar se expirou
                        if now >= expires_at:
                            safe_print("\n" + "="*60)
                            safe_print("❌ LICENÇA EXPIRADA!")
                            safe_print("="*60)
                            safe_print("")
                            safe_print("⚠️ Sua licença expirou e o bot não pode ser iniciado.")
                            safe_print(f"📅 Data de expiração: {expires_at_str}")
                            safe_print("")
                            safe_print("💡 Entre em contato para renovar sua licença.")
                            safe_print("="*60)
                            input("\nPressione Enter para sair...")
                            return 1
                        else:
                            # Calcular tempo restante
                            time_remaining = expires_at - now
                            days_remaining = time_remaining.days
                            hours_remaining = (time_remaining.seconds // 3600)

                            safe_print(f"✅ Licença válida! Expira em: {days_remaining}d {hours_remaining}h")

                            # Avisar se está próximo de expirar
                            if days_remaining <= 3:
                                safe_print(f"⚠️ ATENÇÃO: Sua licença expira em {days_remaining} dias!")

                    except Exception as e:
                        safe_print(f"⚠️ Não foi possível verificar data de expiração: {e}")
                else:
                    # Usar days_remaining se expires_at não estiver disponível
                    days_remaining = license_info.get('days_remaining')
                    if days_remaining is not None:
                        if days_remaining <= 0:
                            safe_print("\n" + "="*60)
                            safe_print("❌ LICENÇA EXPIRADA!")
                            safe_print("="*60)
                            safe_print("")
                            safe_print("⚠️ Sua licença expirou e o bot não pode ser iniciado.")
                            safe_print(f"📅 Dias restantes: {days_remaining}")
                            safe_print("")
                            safe_print("💡 Entre em contato para renovar sua licença.")
                            safe_print("="*60)
                            input("\nPressione Enter para sair...")
                            return 1
                        else:
                            safe_print(f"✅ Licença válida! Expira em: {days_remaining} dias")

                            if days_remaining <= 3:
                                safe_print(f"⚠️ ATENÇÃO: Sua licença expira em {days_remaining} dias!")

        except ImportError as e:
            safe_print(f"⚠️ Sistema de autenticação não disponível: {e}")
            safe_print("🔄 Continuando sem verificação de licença...")
            license_manager = None
        except Exception as e:
            safe_print(f"❌ Erro na autenticação: {e}")
            traceback.print_exc()
            input("Pressione Enter para sair...")
            return 1

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

        # 4. Conectar ao Servidor Multi-Usuário (usando credenciais já coletadas)
        try:
            # Verificar se licença está válida e temos credenciais
            if license_manager and license_manager.is_licensed() and 'login' in locals():
                safe_print("\n🌐 Conectando ao servidor multi-usuário...")

                # Ler URL do servidor do config.json
                server_url = config.get('server.url', 'wss://private-serverpesca.pbzgje.easypanel.host/ws')
                safe_print(f"   🌐 Servidor: {server_url}")
                safe_print("   ⏳ Aguarde, estabelecendo conexão WebSocket...")

                # Conectar usando as credenciais já coletadas no passo 1
                ws_client = connect_to_server(
                    login=login,
                    password=password,
                    license_key=license_key,
                    server_url=server_url,
                    config_manager=config
                )

                if ws_client and ws_client.is_connected():
                    safe_print("✅ Conectado ao servidor multi-usuário!")
                else:
                    safe_print("⚠️ Não foi possível conectar ao servidor")
                    safe_print("   Bot continuará em modo offline")

            else:
                safe_print("⚠️ Bot rodará em modo offline (sem licença)")

        except Exception as e:
            safe_print(f"⚠️ Erro ao conectar ao servidor: {e}")
            traceback.print_exc()

        # 5. Interface Principal
        safe_print("\n🎨 Inicializando interface...")
        try:
            from ui.main_window import FishingBotUI
            ui = FishingBotUI(config, ws_client=ws_client, license_manager=license_manager)  # ✅ Passar ws_client e license_manager
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
