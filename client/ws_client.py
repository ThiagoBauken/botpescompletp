#!/usr/bin/env python3
"""
🌐 WebSocket Client Manager
Gerencia conexão com servidor multi-usuário
"""

import asyncio
import json
import threading
import time
import websockets
from typing import Callable, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def _safe_print(text):
    """Print com fallback para Unicode"""
    try:
        print(text)
    except (UnicodeEncodeError, UnicodeDecodeError):
        import re
        clean = re.sub(r'[^\x00-\x7F]+', '?', str(text))
        print(clean)

class WebSocketClient:
    """
    Cliente WebSocket para comunicação com servidor

    Funcionalidade:
    - Conecta ao servidor e autentica
    - Envia eventos: fish_caught, feeding_done, cleaning_done
    - Recebe comandos: feed, clean, break
    - Callbacks para executar comandos localmente
    """

    def __init__(self, server_url: str = "ws://localhost:8000/ws"):
        """
        Inicializar cliente WebSocket

        Args:
            server_url: URL do servidor (ex: ws://localhost:8000/ws ou wss://seu-dominio.com/ws)
        """
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.authenticated = False
        self.email = None
        self.token = None

        # Thread para loop assíncrono
        self.loop = None
        self.thread = None
        self.running = False

        # Callbacks para comandos do servidor
        self.callbacks: Dict[str, Callable] = {}

        # Lock para thread-safety
        self.lock = threading.Lock()

        # Estatísticas
        self.fish_count = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

        # Arduino Command Executor (para comandos genéricos do servidor)
        self.arduino_executor = None

        _safe_print("✅ WebSocketClient inicializado")

    def register_callback(self, command: str, callback: Callable):
        """
        Registrar callback para comando do servidor

        Args:
            command: Tipo de comando ('feed', 'clean', 'break')
            callback: Função a ser chamada quando comando for recebido
        """
        with self.lock:
            self.callbacks[command] = callback
            logger.info(f"📝 Callback registrado para comando: {command}")

    def connect(self, email: str, token: str) -> bool:
        """
        Conectar ao servidor e autenticar

        Args:
            email: Email do usuário
            token: Token de autenticação (da API /auth/login)

        Returns:
            True se conectado com sucesso
        """
        self.email = email
        self.token = token

        # Iniciar thread assíncrona
        self.running = True
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

        # Aguardar conexão (timeout 5s)
        timeout = 5.0
        start_time = time.time()
        while not self.connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)

        if self.connected:
            _safe_print(f"🟢 Conectado ao servidor: {self.server_url}")
            return True
        else:
            _safe_print(f"🔴 Falha ao conectar ao servidor")
            return False

    def disconnect(self):
        """Desconectar do servidor"""
        self.running = False

        if self.websocket:
            try:
                # Agendar fechamento no loop
                if self.loop and self.loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        self.websocket.close(),
                        self.loop
                    )
            except Exception as e:
                logger.error(f"Erro ao fechar WebSocket: {e}")

        self.connected = False
        self.authenticated = False
        _safe_print("🔴 Desconectado do servidor")

    def send_fish_caught(self, rod_uses: int = 0, current_rod: int = 1):
        """
        Enviar evento de peixe capturado ao servidor com dados de vara

        Args:
            rod_uses: Quantidade de usos da vara atual
            current_rod: Número da vara atual (1-6)

        O servidor vai decidir se precisa alimentar/limpar/break/trocar vara
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, evento fish_caught não enviado")
            return

        with self.lock:
            self.fish_count += 1

        message = {
            "event": "fish_caught",
            "data": {
                "fish_count": self.fish_count,
                "rod_uses": rod_uses,
                "current_rod": current_rod,  # ✅ NOVO: Vara atual
                "timestamp": datetime.now().isoformat()
            }
        }

        self._send_async(message)
        _safe_print(f"🐟 [WS→SERVER] Peixe #{self.fish_count} (Vara {current_rod}: {rod_uses} usos)")
        logger.info(f"🐟 Evento fish_caught enviado (total: {self.fish_count}, vara {current_rod}: {rod_uses} usos)")

    def send_feeding_done(self):
        """Notificar servidor que feeding foi concluído"""
        message = {"event": "feeding_done"}
        self._send_async(message)
        _safe_print("✅ [WS→SERVER] Evento feeding_done enviado")
        logger.info("✅ Evento feeding_done enviado")

    def send_cleaning_done(self):
        """Notificar servidor que limpeza foi concluída"""
        message = {"event": "cleaning_done"}
        self._send_async(message)
        _safe_print("✅ [WS→SERVER] Evento cleaning_done enviado")
        logger.info("✅ Evento cleaning_done enviado")

    def send_config_sync(self, config: dict):
        """
        ✅ NOVO: Sincronizar configurações do cliente com o servidor

        Envia configurações da UI local para o servidor usar nas decisões.
        Servidor armazena configs por sessão e usa ao invés de DEFAULT_RULES.

        Args:
            config: Dicionário com configurações importantes:
                - feed_interval_fish: A cada quantos peixes alimentar
                - clean_interval_fish: A cada quantos peixes limpar
                - break_interval_fish: A cada quantos peixes pausar
                - break_duration_minutes: Duração da pausa
                - rod_switch_limit: Limite de usos por vara

        Exemplo:
            ws_client.send_config_sync({
                "feed_interval_fish": 2,
                "clean_interval_fish": 1,
                "rod_switch_limit": 20
            })
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, config_sync não enviado")
            return

        message = {
            "event": "sync_config",
            "data": config
        }
        self._send_async(message)
        _safe_print(f"✅ [WS→SERVER] Configurações sincronizadas: {config}")
        logger.info(f"⚙️ Configurações sincronizadas com servidor: {config}")

    def send_timeout(self, current_rod: int = 1):
        """
        ✅ NOVO: Enviar evento de timeout ao servidor

        Quando ciclo de pesca atinge timeout (120s sem peixe), servidor
        decide se precisa executar limpeza baseado em timeouts consecutivos.

        Args:
            current_rod: Número da vara atual que teve timeout (1-6)

        Exemplo:
            ws_client.send_timeout(current_rod=1)
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, evento timeout não enviado")
            return

        message = {
            "event": "timeout",
            "data": {
                "current_rod": current_rod
            }
        }
        self._send_async(message)
        _safe_print(f"⏰ [WS→SERVER] Evento timeout enviado (vara {current_rod})")
        logger.info(f"⏰ Timeout enviado: vara {current_rod}")

    def send_detection(self, template_name: str, location: tuple):
        """
        ✅ NOVO: Enviar coordenadas detectadas ao servidor

        ARQUITETURA:
        - Cliente detecta template via OpenCV
        - Cliente NÃO sabe o que fazer com a coordenada
        - Cliente ENVIA ao servidor para análise
        - Servidor decide o que fazer e envia comando específico

        Args:
            template_name: Nome do template detectado (ex: "eat_button", "filefrito")
            location: Tupla (x, y) da coordenada detectada

        Exemplo:
            ws_client.send_detection("eat_button", (1083, 373))
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, detecção não enviada")
            return

        message = {
            "event": "template_detected",
            "data": {
                "template": template_name,
                "location": {
                    "x": location[0],
                    "y": location[1]
                },
                "timestamp": datetime.now().isoformat()
            }
        }

        self._send_async(message)
        _safe_print(f"👁️  [WS→SERVER] Detecção enviada: {template_name} em {location}")
        logger.info(f"👁️  Detecção enviada: {template_name} em {location}")

    def send_feeding_locations_detected(self, food_location: dict, eat_location: dict):
        """
        ✅ NOVO: Enviar coordenadas de comida e botão eat detectadas

        Args:
            food_location: {"x": 1306, "y": 858}
            eat_location: {"x": 1083, "y": 373}
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, feeding_locations não enviadas")
            return

        message = {
            "event": "feeding_locations_detected",
            "data": {
                "food_location": food_location,
                "eat_location": eat_location
            }
        }
        self._send_async(message)
        _safe_print(f"🍖 [WS→SERVER] Localizações de feeding enviadas")
        logger.info(f"🍖 Feeding locations: food={food_location}, eat={eat_location}")

    def send_fish_locations_detected(self, fish_locations: list):
        """
        ✅ NOVO: Enviar lista de peixes detectados no inventário

        Args:
            fish_locations: [{"x": 709, "y": 700}, {"x": 750, "y": 700}, ...]
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, fish_locations não enviadas")
            return

        message = {
            "event": "fish_locations_detected",
            "data": {
                "fish_locations": fish_locations
            }
        }
        self._send_async(message)
        _safe_print(f"🐟 [WS→SERVER] {len(fish_locations)} peixes detectados enviados")
        logger.info(f"🐟 Fish locations enviadas: {len(fish_locations)} itens")

    def send_rod_status_detected(self, rod_status: dict, available_items: dict):
        """
        ✅ NOVO: Enviar status das varas e itens disponíveis

        Args:
            rod_status: {1: "COM_ISCA", 2: "SEM_ISCA", ...}
            available_items: {"rods": [...], "baits": [...]}
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, rod_status não enviado")
            return

        message = {
            "event": "rod_status_detected",
            "data": {
                "rod_status": rod_status,
                "available_items": available_items
            }
        }
        self._send_async(message)
        _safe_print(f"🎣 [WS→SERVER] Status das varas enviado")
        logger.info(f"🎣 Rod status: {rod_status}")

    def send_sequence_completed(self, operation: str = "unknown"):
        """
        ✅ NOVO: Confirmar que sequência foi executada com sucesso

        Args:
            operation: Tipo de operação (feeding, cleaning, maintenance)
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, sequence_completed não enviado")
            return

        message = {
            "event": "sequence_completed",
            "data": {
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            }
        }
        self._send_async(message)
        _safe_print(f"✅ [WS→SERVER] Sequência {operation} concluída")
        logger.info(f"✅ Sequence completed: {operation}")

    def send_sequence_failed(self, operation: str = "unknown", step_index: int = 0, error: str = ""):
        """
        ✅ NOVO: Reportar falha na execução de sequência

        Args:
            operation: Tipo de operação (feeding, cleaning, maintenance)
            step_index: Índice da ação que falhou
            error: Descrição do erro
        """
        if not self.connected or not self.websocket:
            logger.warning("⚠️ Não conectado, sequence_failed não enviado")
            return

        message = {
            "event": "sequence_failed",
            "data": {
                "operation": operation,
                "step_index": step_index,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }
        }
        self._send_async(message)
        _safe_print(f"❌ [WS→SERVER] Sequência {operation} falhou no step {step_index}: {error}")
        logger.error(f"❌ Sequence failed: {operation} at step {step_index}: {error}")

    def send_ping(self):
        """Enviar ping (heartbeat)"""
        message = {"event": "ping"}
        self._send_async(message)

    def set_arduino_executor(self, executor):
        """
        ✅ NOVO: Registrar ArduinoCommandExecutor

        Args:
            executor: Instância de ArduinoCommandExecutor
        """
        self.arduino_executor = executor
        _safe_print("✅ ArduinoCommandExecutor registrado no WebSocketClient")
        logger.info("✅ ArduinoCommandExecutor registrado")

    def _send_async(self, message: dict):
        """
        Enviar mensagem de forma assíncrona

        Args:
            message: Dicionário a ser enviado como JSON
        """
        if not self.loop or not self.loop.is_running():
            logger.error("Loop assíncrono não está rodando")
            return

        asyncio.run_coroutine_threadsafe(
            self._send_message(message),
            self.loop
        )

    async def _send_message(self, message: dict):
        """Enviar mensagem (async)"""
        if self.websocket:
            try:
                await self.websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem: {e}")

    def _run_async_loop(self):
        """Executar loop assíncrono em thread separada"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            logger.error(f"Erro no loop assíncrono: {e}")
        finally:
            self.loop.close()

    async def _connect_and_listen(self):
        """Conectar ao servidor e escutar mensagens"""

        while self.running:
            try:
                _safe_print(f"🔌 Conectando a {self.server_url}...")

                async with websockets.connect(self.server_url) as websocket:
                    self.websocket = websocket

                    # 1. AUTENTICAÇÃO
                    auth_msg = {
                        "token": self.token
                    }
                    await websocket.send(json.dumps(auth_msg))

                    # Aguardar resposta de autenticação
                    response = await websocket.recv()
                    data = json.loads(response)

                    if data.get("type") == "connected":
                        self.connected = True
                        self.authenticated = True
                        self.reconnect_attempts = 0

                        # Atualizar fish_count do servidor
                        server_fish_count = data.get("fish_count", 0)
                        with self.lock:
                            self.fish_count = server_fish_count

                        _safe_print("=" * 60)
                        _safe_print(f"✅ WEBSOCKET CONECTADO: {data.get('message', 'Conectado')}")
                        _safe_print(f"📊 Fish count sincronizado: {self.fish_count}")
                        _safe_print(f"🔄 Comunicação ativa - mensagens serão exibidas aqui")
                        _safe_print("=" * 60)

                    elif "error" in data:
                        _safe_print(f"❌ Erro de autenticação: {data['error']}")
                        self.running = False
                        break

                    # 2. LOOP DE MENSAGENS
                    while self.running:
                        try:
                            message = await asyncio.wait_for(
                                websocket.recv(),
                                timeout=1.0
                            )

                            data = json.loads(message)
                            await self._handle_server_message(data)

                        except asyncio.TimeoutError:
                            # Timeout normal, continuar loop
                            continue

                        except websockets.exceptions.ConnectionClosed:
                            _safe_print("🔴 Conexão fechada pelo servidor")
                            self.connected = False
                            break

            except Exception as e:
                self.connected = False
                logger.error(f"❌ Erro na conexão: {e}")

                if self.running:
                    self.reconnect_attempts += 1

                    if self.reconnect_attempts < self.max_reconnect_attempts:
                        wait_time = min(5 * self.reconnect_attempts, 30)
                        _safe_print(f"🔄 Reconectando em {wait_time}s... (tentativa {self.reconnect_attempts}/{self.max_reconnect_attempts})")
                        await asyncio.sleep(wait_time)
                    else:
                        _safe_print(f"❌ Máximo de tentativas de reconexão atingido")
                        self.running = False
                        break

    async def _handle_server_message(self, data: dict):
        """
        Processar mensagem recebida do servidor

        Args:
            data: Dicionário com comando do servidor
        """

        # COMANDO: feed
        if data.get("cmd") == "feed":
            logger.info("🍖 Comando FEED recebido do servidor")
            _safe_print("\n" + "=" * 60)
            _safe_print("🍖 [SERVER→CLIENT] COMANDO FEED RECEBIDO")
            _safe_print(f"   Parâmetros: {data.get('params', {})}")
            _safe_print("=" * 60)

            if "feed" in self.callbacks:
                # Executar callback em thread separada (não bloquear WebSocket)
                threading.Thread(
                    target=self.callbacks["feed"],
                    args=(data.get("params", {}),),
                    daemon=True
                ).start()

        # COMANDO: clean
        elif data.get("cmd") == "clean":
            logger.info("🧹 Comando CLEAN recebido do servidor")
            _safe_print("\n" + "=" * 60)
            _safe_print("🧹 [SERVER→CLIENT] COMANDO CLEAN RECEBIDO")
            _safe_print(f"   Parâmetros: {data.get('params', {})}")
            _safe_print("=" * 60)

            if "clean" in self.callbacks:
                # ✅ CORREÇÃO: Passar params ao callback
                threading.Thread(
                    target=self.callbacks["clean"],
                    args=(data.get("params", {}),),  # ← Passa params!
                    daemon=True
                ).start()

        # COMANDO: break
        elif data.get("cmd") == "break":
            duration = data.get("duration_minutes", 45)
            logger.info(f"☕ Comando BREAK recebido ({duration} min)")
            _safe_print("\n" + "=" * 60)
            _safe_print(f"☕ [SERVER→CLIENT] COMANDO BREAK RECEBIDO")
            _safe_print(f"   Duração: {duration} minutos")
            _safe_print("=" * 60)

            if "break" in self.callbacks:
                threading.Thread(
                    target=self.callbacks["break"],
                    args=(duration,),
                    daemon=True
                ).start()

        # ✅ NOVO: COMANDO: switch_rod_pair (Troca de par de varas)
        elif data.get("cmd") == "switch_rod_pair":
            params = data.get("params", {})
            target_rod = params.get("target_rod", 1)
            logger.info(f"🎣 Comando SWITCH_ROD_PAIR recebido (vara {target_rod})")
            _safe_print("\n" + "=" * 60)
            _safe_print(f"🎣 [SERVER→CLIENT] COMANDO SWITCH_ROD_PAIR RECEBIDO")
            _safe_print(f"   Vara alvo: {target_rod}")
            _safe_print(f"   Parâmetros completos: {params}")
            _safe_print("=" * 60)

            if "switch_rod_pair" in self.callbacks:
                threading.Thread(
                    target=self.callbacks["switch_rod_pair"],
                    args=(params,),
                    daemon=True
                ).start()
            else:
                _safe_print("⚠️ Callback 'switch_rod_pair' não registrado!")
                logger.warning("Callback 'switch_rod_pair' não registrado")

        # ✅ NOVO: COMANDOS GENÉRICOS (sequence, move, click, drag, etc)
        # Estes comandos são executados via ArduinoCommandExecutor
        elif data.get("cmd") in ["sequence", "move", "click", "drag", "key_press", "wait"]:
            cmd_type = data.get("cmd")
            logger.info(f"🤖 Comando GENÉRICO recebido: {cmd_type}")
            _safe_print("\n" + "=" * 60)
            _safe_print(f"🤖 [SERVER→CLIENT] COMANDO {cmd_type.upper()} RECEBIDO")
            _safe_print(f"   Comando completo: {data}")
            _safe_print("=" * 60)

            if self.arduino_executor:
                # Executar comando via ArduinoCommandExecutor em thread separada
                def execute_and_notify():
                    success = self.arduino_executor.execute_command(data)
                    if success:
                        _safe_print(f"✅ [EXECUTOR] Comando {cmd_type} executado com sucesso!")
                    else:
                        _safe_print(f"❌ [EXECUTOR] Falha ao executar comando {cmd_type}!")

                threading.Thread(
                    target=execute_and_notify,
                    daemon=True
                ).start()
            else:
                _safe_print("❌ ArduinoCommandExecutor não registrado!")
                logger.error("ArduinoCommandExecutor não registrado para executar comando genérico")

        # ✅ NOVO: COMANDOS DE DETECÇÃO E EXECUÇÃO (Servidor → Cliente)
        elif data.get("cmd") in ["request_template_detection", "request_inventory_scan", "request_rod_analysis", "execute_sequence", "execute_batch"]:
            cmd_type = data.get("cmd")
            logger.info(f"🔍 Comando {cmd_type} recebido do servidor")
            _safe_print("\n" + "=" * 60)
            _safe_print(f"🔍 [SERVER→CLIENT] COMANDO {cmd_type.upper()} RECEBIDO")
            _safe_print(f"   Comando completo: {data}")
            _safe_print("=" * 60)

            # Encaminhar para fishing_engine via callback genérico
            if "handle_command" in self.callbacks:
                threading.Thread(
                    target=self.callbacks["handle_command"],
                    args=(data,),
                    daemon=True
                ).start()
            else:
                _safe_print("⚠️ Callback 'handle_command' não registrado!")
                logger.warning("Callback 'handle_command' não registrado para processar comando do servidor")

        # PONG (resposta ao ping)
        elif data.get("type") == "pong":
            logger.debug("🏓 Pong recebido")

        else:
            logger.warning(f"⚠️ Mensagem desconhecida do servidor: {data}")

    def is_connected(self) -> bool:
        """Verificar se está conectado"""
        return self.connected and self.authenticated

    def get_fish_count(self) -> int:
        """Obter contador de peixes"""
        with self.lock:
            return self.fish_count


# ═══════════════════════════════════════════════════════
# EXEMPLO DE USO
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import time

    def on_feed(params):
        clicks = params.get("clicks", 5)
        _safe_print(f"[CALLBACK] Executando feeding ({clicks} cliques)...")
        time.sleep(2)  # Simular feeding
        ws_client.send_feeding_done()

    def on_clean():
        _safe_print("[CALLBACK] Executando limpeza...")
        time.sleep(1)  # Simular limpeza
        ws_client.send_cleaning_done()

    def on_break(duration_minutes):
        _safe_print(f"[CALLBACK] Iniciando break de {duration_minutes} minutos...")
        # Pausar fishing engine

    # Criar cliente
    ws_client = WebSocketClient("ws://localhost:8000/ws")

    # Registrar callbacks
    ws_client.register_callback("feed", on_feed)
    ws_client.register_callback("clean", on_clean)
    ws_client.register_callback("break", on_break)

    # Conectar (usar token do /auth/login)
    email = "teste@teste.com"
    token = "teste@teste.com"  # Token simples = email

    if ws_client.connect(email, token):
        _safe_print("\n🎮 Cliente conectado! Simulando capturas de peixe...")

        # Simular capturas
        for i in range(10):
            time.sleep(3)
            _safe_print(f"\n🐟 Peixe #{i+1} capturado!")
            ws_client.send_fish_caught()

        time.sleep(2)
        ws_client.disconnect()
    else:
        _safe_print("❌ Falha na conexão")
