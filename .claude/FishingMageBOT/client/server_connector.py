#!/usr/bin/env python3
"""
🔗 Server Connector
Conecta ao servidor multi-usuário com login/senha/license_key + validação Keymaster
"""

import sys
import os
import requests
import time
import platform

# Adicionar pasta parent ao path para importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.ws_client import WebSocketClient

# Importar função de HWID do license manager
try:
    from utils.license_manager import LicenseManager
except ImportError:
    LicenseManager = None

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

def _sync_config_with_server(ws_client, config_manager=None):
    """
    ✅ CORRIGIDO: Sincronizar configurações locais com o servidor

    Usa ConfigManager para ler configurações mescladas (default + user).
    Envia configurações importantes ao servidor:
    - Intervalos de alimentação/limpeza/break
    - Limite de usos por vara
    - Outros configs relevantes

    Args:
        ws_client: Cliente WebSocket conectado
        config_manager: Instância existente do ConfigManager (opcional)
    """
    try:
        # ✅ CORREÇÃO CRÍTICA: Usar config_manager existente do main.py
        # NÃO criar nova instância - causava leituras diferentes!
        if config_manager:
            config = config_manager
            _safe_print("   ✅ Usando ConfigManager existente do main.py")
        else:
            # Fallback: criar nova instância apenas se não foi passado
            from core.config_manager import ConfigManager
            config = ConfigManager()
            _safe_print("   ⚠️ Criando nova instância do ConfigManager (fallback)")

        if not config.is_loaded:
            _safe_print("   ⚠️ Erro ao carregar configurações")
            return

        # Extrair configurações importantes para o servidor
        server_config = {}

        # Feeding system - usar merged config
        trigger_mode = config.get("feeding_system.trigger_mode", "catches")
        if trigger_mode == "catches":
            server_config["feed_interval_fish"] = config.get("feeding_system.trigger_catches", 10)

        # ✅ CORREÇÃO CRÍTICA: Auto clean - LER DO MERGED CONFIG (default: 2)
        server_config["clean_interval_fish"] = config.get("auto_clean.interval", 2)

        # Rod system
        server_config["rod_switch_limit"] = config.get("rod_system.rod_switch_limit", 20)

        # Anti-detection (breaks)
        break_mode = config.get("anti_detection.break_mode", "catches")
        if break_mode == "catches":
            server_config["break_interval_fish"] = config.get("anti_detection.break_catches", 50)
        server_config["break_duration_minutes"] = config.get("anti_detection.break_minutes", 45)

        # Timeouts (maintenance trigger)
        server_config["maintenance_timeout"] = config.get("timeouts.maintenance_timeout", 1)

        # ✅ CORREÇÃO CRÍTICA: Coordenadas de baú - LER DO MERGED CONFIG (default: "right")
        server_config["chest_side"] = config.get("chest_side", "right")
        server_config["chest_distance"] = config.get("chest_distance", 1200)
        server_config["chest_vertical_offset"] = config.get("chest_vertical_offset", 200)

        # ✅ NOVO: Coordenadas de slots de varas
        slot_positions = config.get("coordinates.slot_positions")
        if slot_positions:
            server_config["slot_positions"] = slot_positions

        inventory_area = config.get("coordinates.inventory_area")
        if inventory_area:
            server_config["inventory_area"] = inventory_area

        chest_area = config.get("coordinates.chest_area")
        if chest_area:
            server_config["chest_area"] = chest_area

        # ✅ NOVO: Prioridades de isca
        bait_priority = config.get("bait_system.priority")
        if bait_priority:
            server_config["bait_priority"] = bait_priority

        # ✅ NOVO: Feeding per session
        server_config["feeds_per_session"] = config.get("feeding_system.feeds_per_session", 2)

        # Enviar configs ao servidor
        _safe_print(f"   ⚙️ Sincronizando configs com servidor:")
        _safe_print(f"      • Alimentar a cada: {server_config.get('feed_interval_fish', 'N/A')} peixes")
        _safe_print(f"      • Limpar a cada: {server_config.get('clean_interval_fish', 'N/A')} peixe(s)")
        _safe_print(f"      • Rod switch limit: {server_config.get('rod_switch_limit', 'N/A')} usos")
        _safe_print(f"      • Break a cada: {server_config.get('break_interval_fish', 'N/A')} peixes")
        _safe_print(f"      • Timeout limit: {server_config.get('maintenance_timeout', 'N/A')} timeout(s)")
        _safe_print(f"      • Chest side: {server_config.get('chest_side', 'N/A')}")
        _safe_print(f"      • Feeds per session: {server_config.get('feeds_per_session', 'N/A')}")

        # Log prioridade de iscas se presente
        if "bait_priority" in server_config:
            _safe_print(f"      • Prioridade de iscas: {server_config['bait_priority']}")
        else:
            _safe_print(f"      • Prioridade de iscas: NÃO ENCONTRADA")

        ws_client.send_config_sync(server_config)

    except Exception as e:
        _safe_print(f"   ⚠️ Erro ao sincronizar configs: {e}")
        import traceback
        traceback.print_exc()

def connect_to_server(
    login: str,
    password: str,
    license_key: str,
    server_url: str = "wss://private-serverpesca.pbzgje.easypanel.host/ws",
    config_manager=None
) -> WebSocketClient:
    """
    Conectar ao servidor multi-usuário com login/senha/license_key

    FLUXO:
    1. Captura HWID do PC
    2. Envia login/senha/license_key/HWID para servidor
    3. Servidor valida com Keymaster automaticamente
    4. Servidor verifica HWID binding (anti-compartilhamento)
    5. Retorna token + regras de configuração
    6. Conecta WebSocket

    Args:
        login: Login do usuário
        password: Senha do usuário
        license_key: License key (validada com Keymaster pelo servidor)
        server_url: URL do servidor WebSocket (padrão: Easypanel WSS)
        config_manager: Instância existente do ConfigManager (opcional)

    Returns:
        WebSocketClient conectado ou None se falhar
    """
    try:
        # Converter ws:// para http:// para autenticação
        http_url = server_url.replace("ws://", "http://").replace("wss://", "https://")
        http_url = http_url.replace("/ws", "")

        _safe_print("\n🌐 Conectando ao servidor multi-usuário...")
        _safe_print(f"   URL: {http_url}")
        _safe_print(f"   Login: {login}")

        # 1. Capturar HWID (Hardware ID) - OBRIGATÓRIO para anti-compartilhamento
        hwid = None
        pc_name = platform.node()

        if LicenseManager:
            try:
                license_mgr = LicenseManager()
                hwid = license_mgr.get_hardware_id()
                _safe_print(f"   🔑 HWID: {hwid[:16]}...")
                _safe_print(f"   💻 PC: {pc_name}")
            except Exception as e:
                _safe_print(f"   ⚠️ Erro ao capturar HWID: {e}")
                _safe_print(f"   ❌ HWID é obrigatório para anti-compartilhamento!")
                return None
        else:
            _safe_print("   ❌ LicenseManager não disponível (HWID obrigatório)")
            return None

        # 2. Autenticar com login/senha/license_key + HWID
        _safe_print("   🔐 Autenticando (servidor valida com Keymaster)...")

        try:
            payload = {
                "login": login,
                "password": password,
                "license_key": license_key,
                "hwid": hwid,
                "pc_name": pc_name
            }

            response = requests.post(
                f"{http_url}/auth/activate",
                json=payload,
                timeout=10  # Keymaster pode demorar
            )

            if response.status_code != 200:
                _safe_print(f"   ❌ Erro HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    _safe_print(f"   ❌ {error_data.get('message', 'Erro desconhecido')}")
                except:
                    pass
                return None

            data = response.json()

            if not data.get("success"):
                message = data.get('message', 'Erro desconhecido')
                _safe_print(f"   ❌ Falha na ativação: {message}")
                return None

            token = data.get("token")
            rules = data.get("rules", {})

            _safe_print(f"   ✅ Ativação bem-sucedida!")
            _safe_print(f"   🎯 Regras recebidas do servidor:")
            _safe_print(f"      • Alimentar a cada {rules.get('feed_interval_fish', 'N/A')} peixes")
            _safe_print(f"      • Limpar a cada {rules.get('clean_interval_fish', 'N/A')} peixe")
            _safe_print(f"      • Break a cada {rules.get('break_interval_fish', 'N/A')} peixes")

        except requests.exceptions.ConnectionError:
            _safe_print(f"   ⚠️ Não foi possível conectar ao servidor")
            _safe_print(f"   ℹ️ Continuando em modo offline (sem servidor)")
            return None

        except requests.exceptions.Timeout:
            _safe_print(f"   ⚠️ Timeout ao conectar ao servidor")
            _safe_print(f"   ℹ️ Continuando em modo offline")
            return None

        except Exception as e:
            _safe_print(f"   ⚠️ Erro ao autenticar: {e}")
            return None

        # 3. Criar WebSocket client
        _safe_print("   🔌 Criando conexão WebSocket...")
        ws_client = WebSocketClient(server_url)

        # 4. Conectar WebSocket
        _safe_print("   🔗 Conectando ao WebSocket...")
        if ws_client.connect(login, token):
            _safe_print("   ✅ Conectado ao servidor!")
            _safe_print("   💚 Heartbeat ativo (validação contínua)")

            # ✅ NOVO: Sincronizar configurações locais com o servidor
            try:
                _sync_config_with_server(ws_client, config_manager)
            except Exception as e:
                _safe_print(f"   ⚠️ Erro ao sincronizar configs: {e}")

            return ws_client
        else:
            _safe_print("   ❌ Falha ao conectar WebSocket")
            return None

    except Exception as e:
        _safe_print(f"❌ Erro ao conectar ao servidor: {e}")
        import traceback
        traceback.print_exc()
        return None


def register_server_callbacks(ws_client: WebSocketClient, fishing_engine):
    """
    Registrar callbacks do servidor no FishingEngine

    Servidor envia comandos (feed/clean/break) baseado no fish_count.
    Cliente executa os comandos localmente.

    Args:
        ws_client: Cliente WebSocket conectado
        fishing_engine: Instância do FishingEngine
    """
    if not ws_client or not fishing_engine:
        return

    _safe_print("\n📝 Registrando callbacks do servidor...")

    # Callback: FEED (alimentação)
    def on_server_feed(params):
        """
        Callback de alimentação comandada pelo servidor

        ✅ ENFILEIRA comando para execução entre ciclos
        NÃO executa imediatamente (evita conflitos)
        """
        _safe_print(f"\n🍖 [SERVIDOR] Comando de feeding recebido")

        # Enfileirar comando ao invés de executar imediatamente
        with fishing_engine.command_lock:
            fishing_engine.pending_server_commands.append(('feed', params))
            _safe_print(f"   📋 Comando feed enfileirado ({len(fishing_engine.pending_server_commands)} na fila)")

    # Callback: CLEAN (limpeza)
    def on_server_clean(params=None):
        """
        Callback de limpeza com coordenadas do servidor

        ✅ ENFILEIRA comando para execução entre ciclos
        NÃO executa imediatamente (evita conflitos)
        """
        _safe_print(f"\n🧹 [SERVIDOR] Comando de limpeza recebido")

        # Enfileirar comando ao invés de executar imediatamente
        with fishing_engine.command_lock:
            fishing_engine.pending_server_commands.append(('clean', params if params else {}))
            _safe_print(f"   📋 Comando clean enfileirado ({len(fishing_engine.pending_server_commands)} na fila)")

    # Callback: BREAK (pausa)
    def on_server_break(duration_minutes):
        _safe_print(f"\n☕ [SERVIDOR] Comando de break recebido ({duration_minutes} min)")

        # Pausar fishing engine
        if hasattr(fishing_engine, 'pause'):
            _safe_print(f"   Pausando bot por {duration_minutes} minutos...")
            fishing_engine.pause()

            # Aguardar
            time.sleep(duration_minutes * 60)

            # Retomar
            _safe_print(f"   ✅ Break finalizado, retomando pesca...")
            fishing_engine.resume()

    # ✅ NOVO: Callback: SWITCH_ROD_PAIR (troca de par de varas)
    def on_server_rod_switch(params):
        """
        Callback para troca de par de varas comandada pelo servidor

        ✅ ENFILEIRA comando para execução entre ciclos
        NÃO executa imediatamente (evita conflitos)
        """
        target_rod = params.get("target_rod", 1)
        _safe_print(f"\n🎣 [SERVIDOR] Comando de troca de par recebido (vara {target_rod})")

        # Enfileirar comando ao invés de executar imediatamente
        with fishing_engine.command_lock:
            fishing_engine.pending_server_commands.append(('switch_rod_pair', params))
            _safe_print(f"   📋 Comando switch_rod_pair enfileirado ({len(fishing_engine.pending_server_commands)} na fila)")

    # ✅ NOVO: Callback genérico para comandos de detecção/execução
    def on_handle_command(command):
        """
        Callback genérico para comandos do servidor

        Encaminha para fishing_engine.handle_server_command()
        Processa: request_template_detection, request_inventory_scan, execute_sequence
        """
        if hasattr(fishing_engine, 'handle_server_command'):
            fishing_engine.handle_server_command(command)
        else:
            _safe_print("⚠️ FishingEngine não possui método handle_server_command")

    # Registrar callbacks
    ws_client.register_callback("feed", on_server_feed)
    ws_client.register_callback("clean", on_server_clean)
    ws_client.register_callback("break", on_server_break)
    ws_client.register_callback("switch_rod_pair", on_server_rod_switch)  # ✅ NOVO
    ws_client.register_callback("handle_command", on_handle_command)  # ✅ NOVO

    _safe_print("   ✅ Callbacks registrados:")
    _safe_print("      • feed → Alimentação automática")
    _safe_print("      • clean → Limpeza de inventário")
    _safe_print("      • break → Pausa natural")
    _safe_print("      • switch_rod_pair → Troca de par de varas")  # ✅ NOVO
    _safe_print("      • handle_command → Detecção e execução de sequências")  # ✅ NOVO


# ═══════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    # Testar conexão com credenciais
    login = "usuario@teste.com"
    password = "senha123"
    license_key = "TEST-KEY-12345"

    ws_client = connect_to_server(
        login=login,
        password=password,
        license_key=license_key
    )

    if ws_client:
        _safe_print("\n✅ Teste de conexão bem-sucedido!")
        _safe_print(f"   Conectado: {ws_client.is_connected()}")

        # Enviar heartbeat
        _safe_print("\n💚 Enviando heartbeat...")
        import json
        ws_client.ws.send(json.dumps({"event": "ping"}))

        time.sleep(2)
        ws_client.disconnect()
        _safe_print("   ✅ Desconectado")
    else:
        _safe_print("\n⚠️ Teste falhou, mas bot pode continuar offline")
