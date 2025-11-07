# Sistema de Timeout Migrado para Servidor - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura Antiga vs Nova](#arquitetura-antiga-vs-nova)
3. [Fluxo de Comunicação](#fluxo-de-comunicação)
4. [Implementação Detalhada](#implementação-detalhada)
5. [Configuração](#configuração)
6. [Testes](#testes)
7. [Troubleshooting](#troubleshooting)

---

## Visão Geral

### O que mudou?

**ANTES (v5 antiga - Cliente decide):**
- Cliente detectava timeout (120s sem peixe)
- Cliente contava timeouts consecutivos por vara
- Cliente **DECIDIA** quando limpar (≥3 timeouts)
- Cliente executava limpeza diretamente

**AGORA (v5 atual - Servidor decide):**
- Cliente detecta timeout (120s sem peixe)
- Cliente **REPORTA** timeout ao servidor
- Servidor conta timeouts por vara **por sessão de usuário**
- Servidor **DECIDE** quando limpar (≥ maintenance_timeout)
- Servidor envia comando de limpeza ao cliente
- Cliente apenas **EXECUTA** o comando

### Por que mudou?

**Consistência Arquitetural:**
- Todas as decisões de ações (feed/clean/break/timeout) agora são do **SERVIDOR**
- Cliente vira executor "burro" que apenas reporta eventos e executa comandos
- Permite controle centralizado em ambiente multi-usuário
- Facilita analytics, logging e debugging no servidor

**Benefícios:**
- ✅ Histórico de timeouts armazenado no servidor
- ✅ Decisões consistentes entre múltiplos clientes
- ✅ Logs centralizados de triggers de timeout
- ✅ Possibilidade de ajustar regras sem atualizar cliente
- ✅ Fallback local se servidor indisponível

---

## Arquitetura Antiga vs Nova

### Arquitetura Antiga (Cliente-Side)

```
┌─────────────────────────────────────────┐
│          CLIENTE (fishing_engine.py)     │
│                                          │
│  1. Timeout detectado (120s sem peixe)  │
│         ↓                                │
│  2. Incrementa rod_timeout_history[vara] │
│         ↓                                │
│  3. Verifica se ≥ maintenance_timeout    │
│         ↓                                │
│  4. DECIDE: Precisa limpar? (SIM/NÃO)    │
│         ↓                                │
│  5. SE SIM: trigger_cleaning_operation() │
│         ↓                                │
│  6. Executa limpeza                      │
└─────────────────────────────────────────┘
```

**Problemas:**
- ❌ Decisão local não escalável para multi-usuário
- ❌ Sem histórico centralizado
- ❌ Inconsistente com arquitetura servidor-decide

---

### Arquitetura Nova (Servidor-Side)

```
┌─────────────────────┐              ┌──────────────────────────┐
│      CLIENTE        │              │        SERVIDOR          │
│ (fishing_engine.py) │              │      (server.py)         │
│                     │              │                          │
│  1. Timeout         │   WebSocket  │  1. Recebe evento        │
│     detectado       │─────────────→│     "timeout"            │
│     (120s)          │   {event:    │                          │
│                     │    timeout,  │  2. session.increment    │
│  2. send_timeout()  │    vara: N}  │     _timeout(vara)       │
│                     │              │                          │
│                     │              │  3. Verifica se          │
│                     │              │     should_clean_by      │
│                     │              │     _timeout(vara)       │
│                     │              │                          │
│                     │   WebSocket  │  4. SE SIM:              │
│  3. Recebe comando  │←─────────────│     Envia cmd:           │
│     "clean"         │   {cmd:      │     "clean"              │
│                     │    clean}    │                          │
│  4. Executa         │              │  5. Loga trigger         │
│     limpeza via     │              │     de timeout           │
│     coordinator     │              │                          │
└─────────────────────┘              └──────────────────────────┘

┌─────────────────────────────────────────┐
│      QUANDO PEIXE É CAPTURADO           │
│                                          │
│  Cliente → send_fish_caught()           │
│      ↓                                   │
│  Servidor → session.reset_timeout(vara) │
│      ↓                                   │
│  Contador de timeout da vara → 0        │
└─────────────────────────────────────────┘
```

**Vantagens:**
- ✅ Servidor mantém estado por sessão
- ✅ Decisão centralizada
- ✅ Logs completos no servidor
- ✅ Cliente com fallback local se desconectado

---

## Fluxo de Comunicação

### 1. Configuração Inicial (On Connect)

```python
# client/server_connector.py
def _sync_config_with_server(ws_client):
    """Sincroniza maintenance_timeout do config.json"""

    server_config = {}

    # Lê do config local
    if "timeouts" in local_config:
        timeouts = local_config["timeouts"]
        server_config["maintenance_timeout"] = timeouts.get("maintenance_timeout", 3)

    # Envia ao servidor
    ws_client.send_config_sync(server_config)
```

**Servidor recebe:**
```json
{
  "event": "sync_config",
  "data": {
    "maintenance_timeout": 3,
    "feed_interval_fish": 2,
    "clean_interval_fish": 1,
    "rod_switch_limit": 20
  }
}
```

**Servidor armazena:**
```python
# server/server.py
session.user_config.update(config)
# Agora session.user_config["maintenance_timeout"] = 3
```

---

### 2. Evento de Timeout (Durante Pesca)

**Cliente detecta timeout:**
```python
# core/fishing_engine.py (linha ~1041)

if not peixe_capturado:
    _safe_print(f"⏰ Timeout atingido (120s sem peixe)")

    # ✅ NOVO: Enviar ao servidor
    if self.ws_client:
        _safe_print(f"📡 Enviando timeout ao servidor (vara {current_rod})...")
        self.ws_client.send_timeout(current_rod)
    else:
        # Fallback local se servidor indisponível
        _safe_print("⚠️ WebSocket não disponível - usando lógica local como fallback")
        maintenance_timeout_limit = self.config_manager.get('timeouts.maintenance_timeout', 3)
        if self.rod_timeout_history[current_rod] >= maintenance_timeout_limit:
            trigger_cleaning_operation(self.chest_coordinator, TriggerReason.TIMEOUT_DOUBLE)
            self.rod_timeout_history[current_rod] = 0
```

**Cliente envia via WebSocket:**
```python
# client/ws_client.py (linha ~215)

def send_timeout(self, current_rod: int = 1):
    """Enviar evento de timeout ao servidor"""
    message = {
        "event": "timeout",
        "data": {
            "current_rod": current_rod
        }
    }
    self._send_async(message)
    _safe_print(f"⏰ [WS→SERVER] Evento timeout enviado (vara {current_rod})")
```

**Servidor processa:**
```python
# server/server.py (linha ~735)

elif event == "timeout":
    data = msg.get("data", {})
    current_rod = data.get("current_rod", 1)

    # 1. Incrementa contador de timeout da vara
    session.increment_timeout(current_rod)

    # 2. Verifica se deve limpar
    if session.should_clean_by_timeout(current_rod):
        # 3. Envia comando de limpeza
        await websocket.send_json({
            "cmd": "clean",
            "params": {
                "chest_coords": { /* coordenadas do baú */ },
                "reason": "timeout"
            }
        })
        logger.info(f"🧹 {login}: Comando CLEAN enviado (trigger: timeout vara {current_rod})")
```

---

### 3. Evento de Peixe Capturado (Reset de Timeout)

**Cliente captura peixe:**
```python
# Cliente envia: ws_client.send_fish_caught(fish_id)
```

**Servidor reseta timeout:**
```python
# server/server.py (linha ~646)

elif event == "fish_caught":
    current_rod = data.get("current_rod", 1)

    # Incrementa contador de peixes
    session.increment_fish()

    # ✅ NOVO: Resetar timeout da vara (peixe capturado = vara funcionando)
    session.reset_timeout(current_rod)

    logger.info(f"🐟 {login}: Peixe #{session.fish_count} capturado (vara {current_rod})")
```

**Efeito:**
```python
# session.rod_timeout_history[current_rod] volta para 0
# Contador de timeouts consecutivos é resetado
```

---

## Implementação Detalhada

### 1. Tracking de Timeout no Servidor (FishingSession)

**Estrutura de Dados:**
```python
# server/server.py (linha ~182)

class FishingSession:
    def __init__(self, login: str):
        # Timeout tracking por vara
        self.rod_timeout_history = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.total_timeouts = 0

        # Configurações do usuário
        self.user_config = DEFAULT_RULES.copy()
```

---

### 2. Métodos de Timeout (FishingSession)

**Incrementar Timeout:**
```python
# server/server.py (linha ~230)

def increment_timeout(self, current_rod: int):
    """
    Incrementar contador de timeout para vara específica.

    Chamado quando cliente reporta timeout (120s sem peixe).
    """
    if current_rod not in self.rod_timeout_history:
        self.rod_timeout_history[current_rod] = 0

    self.rod_timeout_history[current_rod] += 1
    self.total_timeouts += 1

    logger.info(
        f"⏰ Timeout incrementado - Vara {current_rod}: "
        f"{self.rod_timeout_history[current_rod]} timeout(s) consecutivo(s)"
    )
```

**Resetar Timeout:**
```python
# server/server.py (linha ~248)

def reset_timeout(self, current_rod: int):
    """
    Resetar contador de timeout quando peixe é capturado.

    Peixe capturado significa vara funcionando = zerar contador.
    """
    if current_rod in self.rod_timeout_history:
        previous_count = self.rod_timeout_history[current_rod]
        self.rod_timeout_history[current_rod] = 0

        if previous_count > 0:
            logger.info(
                f"✅ Timeout resetado - Vara {current_rod} "
                f"(tinha {previous_count} timeout(s))"
            )
```

**Verificar se Deve Limpar:**
```python
# server/server.py (linha ~266)

def should_clean_by_timeout(self, current_rod: int) -> bool:
    """
    Verificar se deve executar limpeza por timeout.

    Lógica: Se timeouts consecutivos >= maintenance_timeout, limpar.
    Automaticamente reseta contador se retornar True.

    Returns:
        bool: True se deve limpar, False caso contrário
    """
    maintenance_timeout_limit = self.user_config.get("maintenance_timeout", 3)
    timeouts = self.rod_timeout_history.get(current_rod, 0)

    should = timeouts >= maintenance_timeout_limit

    if should:
        logger.info(
            f"🧹 Trigger de limpeza por timeout - Vara {current_rod}: "
            f"{timeouts} timeouts >= {maintenance_timeout_limit} (limite)"
        )
        # Resetar contador após trigger
        self.rod_timeout_history[current_rod] = 0

    return should
```

---

### 3. Handler WebSocket no Servidor

**Evento "timeout":**
```python
# server/server.py (linha ~735)

elif event == "timeout":
    data = msg.get("data", {})
    current_rod = data.get("current_rod", 1)

    logger.info(f"⏰ {login}: Recebido evento timeout (vara {current_rod})")

    # Incrementar contador de timeout
    session.increment_timeout(current_rod)

    # Verificar se deve limpar
    if session.should_clean_by_timeout(current_rod):
        # Obter coordenadas do baú do user_config ou usar defaults
        chest_coords = session.user_config.get("chest_coords", {
            "BAU_CENTER_X": 1525,
            "BAU_CENTER_Y": 300,
            "CLICK_X": 1525,
            "CLICK_Y": 300,
            "CLOSE_X": 1817,
            "CLOSE_Y": 125
        })

        # Enviar comando de limpeza
        await websocket.send_json({
            "cmd": "clean",
            "params": {
                "chest_coords": chest_coords,
                "reason": "timeout"
            }
        })

        logger.info(
            f"🧹 {login}: Comando CLEAN enviado "
            f"(trigger: timeout vara {current_rod})"
        )
```

---

### 4. Cliente Envia Timeout

**Método send_timeout():**
```python
# client/ws_client.py (linha ~215)

def send_timeout(self, current_rod: int = 1):
    """
    Enviar evento de timeout ao servidor.

    Quando ciclo de pesca atinge timeout (120s sem peixe), servidor
    decide se precisa executar limpeza baseado em timeouts consecutivos.

    Args:
        current_rod: Número da vara que teve timeout (1-6)
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
```

---

### 5. Integração com FishingEngine

**Detecção e Envio de Timeout:**
```python
# core/fishing_engine.py (linha ~1041)

# Verificar se pescou ou deu timeout
if not peixe_capturado:
    _safe_print(f"⏰ Timeout atingido (120s sem peixe)")
    current_rod = self.rod_manager.current_rod

    # ✅ NOVO: Enviar timeout ao SERVIDOR (servidor decide se limpa)
    if self.ws_client:
        _safe_print(f"📡 Enviando timeout ao servidor (vara {current_rod})...")
        self.ws_client.send_timeout(current_rod)
    else:
        # ⚠️ FALLBACK: Se servidor indisponível, usar lógica local
        _safe_print("⚠️ WebSocket não disponível - usando lógica local como fallback")

        maintenance_timeout_limit = self.config_manager.get('timeouts.maintenance_timeout', 3)

        # Incrementar contador local
        if current_rod not in self.rod_timeout_history:
            self.rod_timeout_history[current_rod] = 0
        self.rod_timeout_history[current_rod] += 1

        # Verificar se precisa limpar
        if self.rod_timeout_history[current_rod] >= maintenance_timeout_limit:
            _safe_print(
                f"🧹 Trigger local de limpeza por timeout "
                f"(vara {current_rod}: {self.rod_timeout_history[current_rod]} timeouts)"
            )
            trigger_cleaning_operation(self.chest_coordinator, TriggerReason.TIMEOUT_DOUBLE)
            self.rod_timeout_history[current_rod] = 0
```

**Envio de Peixe Capturado (Reset Automático):**
```python
# core/fishing_engine.py (já existente, sem modificações)

if peixe_capturado:
    # Enviar ao servidor
    if self.ws_client:
        self.ws_client.send_fish_caught(fish_id=1, current_rod=current_rod)
        # Servidor automaticamente reseta timeout
```

---

## Configuração

### Config Local (config.json)

```json
{
  "timeouts": {
    "maintenance_timeout": 3,  // ← Sincronizado com servidor
    "rod_switch_timeout": 120,
    "fish_catch_timeout": 122
  }
}
```

**Descrição:**
- `maintenance_timeout`: Número de timeouts consecutivos antes de limpar
- Valor padrão: 3 (se não especificado)
- Sincronizado automaticamente ao conectar

---

### Sincronização Automática (On Connect)

```python
# client/server_connector.py (linha ~33)

def _sync_config_with_server(ws_client):
    """
    Sincronizar configurações locais com o servidor.

    Chamado automaticamente ao conectar.
    """
    config_path = "data/config.json"

    with open(config_path, 'r', encoding='utf-8') as f:
        local_config = json.load(f)

    server_config = {}

    # Timeouts (maintenance trigger)
    if "timeouts" in local_config:
        timeouts = local_config["timeouts"]
        server_config["maintenance_timeout"] = timeouts.get("maintenance_timeout", 3)

    # Outras configs...

    # Enviar ao servidor
    ws_client.send_config_sync(server_config)
    _safe_print(f"   ✅ Configs sincronizadas: {list(server_config.keys())}")
```

---

## Testes

### Teste 1: Timeout Único (Não Deve Limpar)

**Cenário:**
- `maintenance_timeout = 3`
- 1 timeout ocorre

**Passos:**
1. Iniciar pesca
2. Deixar vara dar timeout (120s sem peixe)
3. Cliente envia timeout ao servidor
4. Servidor incrementa contador: `rod_timeout_history[vara] = 1`
5. Servidor verifica: `1 < 3` → **NÃO limpa**

**Resultado Esperado:**
```
⏰ Timeout atingido (120s sem peixe)
📡 Enviando timeout ao servidor (vara 1)...
⏰ [WS→SERVER] Evento timeout enviado (vara 1)

# No servidor:
⏰ Timeout incrementado - Vara 1: 1 timeout(s) consecutivo(s)
```

**Comportamento:** Pesca continua normalmente.

---

### Teste 2: Timeout Triplo (Deve Limpar)

**Cenário:**
- `maintenance_timeout = 3`
- 3 timeouts consecutivos na mesma vara

**Passos:**
1. Timeout 1 → contador = 1
2. Timeout 2 → contador = 2
3. Timeout 3 → contador = 3
4. Servidor verifica: `3 >= 3` → **LIMPA**

**Resultado Esperado:**
```
# Timeout 1:
⏰ Timeout incrementado - Vara 1: 1 timeout(s) consecutivo(s)

# Timeout 2:
⏰ Timeout incrementado - Vara 1: 2 timeout(s) consecutivo(s)

# Timeout 3:
⏰ Timeout incrementado - Vara 1: 3 timeout(s) consecutivo(s)
🧹 Trigger de limpeza por timeout - Vara 1: 3 timeouts >= 3 (limite)
🧹 user123: Comando CLEAN enviado (trigger: timeout vara 1)

# Cliente:
🧹 [SERVER→CLIENT] Executando limpeza (trigger: timeout)
```

**Comportamento:** Cliente executa limpeza via ChestOperationCoordinator.

---

### Teste 3: Reset por Peixe Capturado

**Cenário:**
- `maintenance_timeout = 3`
- 2 timeouts, depois peixe capturado

**Passos:**
1. Timeout 1 → contador = 1
2. Timeout 2 → contador = 2
3. **Peixe capturado** → contador = 0
4. Timeout 3 → contador = 1 (resetou!)

**Resultado Esperado:**
```
# Timeout 1:
⏰ Timeout incrementado - Vara 1: 1 timeout(s) consecutivo(s)

# Timeout 2:
⏰ Timeout incrementado - Vara 1: 2 timeout(s) consecutivo(s)

# Peixe capturado:
🐟 user123: Peixe #5 capturado (vara 1)
✅ Timeout resetado - Vara 1 (tinha 2 timeout(s))

# Timeout 3:
⏰ Timeout incrementado - Vara 1: 1 timeout(s) consecutivo(s)
```

**Comportamento:** Contador reseta, pesca continua sem limpeza.

---

### Teste 4: Fallback Local (Servidor Indisponível)

**Cenário:**
- Servidor desconectado
- `maintenance_timeout = 3`

**Passos:**
1. Desconectar servidor
2. Timeout 1, 2, 3
3. Cliente usa lógica local de fallback

**Resultado Esperado:**
```
⏰ Timeout atingido (120s sem peixe)
⚠️ WebSocket não disponível - usando lógica local como fallback
🧹 Trigger local de limpeza por timeout (vara 1: 3 timeouts)
🧹 Executando limpeza localmente...
```

**Comportamento:** Cliente funciona independentemente do servidor.

---

## Troubleshooting

### Problema 1: Timeout não está limpando

**Sintomas:**
- Timeouts ocorrem mas limpeza nunca é executada

**Diagnóstico:**
```python
# Verificar logs do servidor:
grep "Timeout incrementado" server.log
grep "Trigger de limpeza por timeout" server.log

# Verificar configuração:
grep "maintenance_timeout" data/config.json
```

**Possíveis Causas:**
1. `maintenance_timeout` muito alto (ex: 10)
2. Config não sincronizada com servidor
3. Eventos timeout não chegando ao servidor

**Soluções:**
1. Reduzir `maintenance_timeout` no config.json
2. Verificar se `_sync_config_with_server()` foi chamado
3. Verificar conectividade WebSocket

---

### Problema 2: Limpeza executando prematuramente

**Sintomas:**
- Limpeza acontece após 1 ou 2 timeouts (deveria ser 3)

**Diagnóstico:**
```python
# Verificar valor de maintenance_timeout no servidor:
# (adicionar log temporário em server.py)
logger.info(f"maintenance_timeout_limit = {maintenance_timeout_limit}")
```

**Possíveis Causas:**
1. `maintenance_timeout` não sincronizado corretamente
2. Valor padrão (3) não sendo usado
3. Config.json com valor incorreto

**Soluções:**
1. Verificar `data/config.json` → `timeouts.maintenance_timeout`
2. Forçar resync: reconectar cliente
3. Verificar `session.user_config["maintenance_timeout"]` no servidor

---

### Problema 3: Contador não reseta após peixe

**Sintomas:**
- Peixe é capturado mas timeout continua acumulando

**Diagnóstico:**
```python
# Verificar logs:
grep "Peixe.*capturado" server.log
grep "Timeout resetado" server.log

# Se não aparecer "Timeout resetado", problema está no código
```

**Possíveis Causas:**
1. `session.reset_timeout()` não sendo chamado
2. `current_rod` incorreto no evento `fish_caught`

**Soluções:**
1. Verificar handler `fish_caught` no servidor (linha ~646)
2. Verificar se `current_rod` está sendo enviado corretamente

---

### Problema 4: Fallback local não funciona

**Sintomas:**
- Servidor desconectado, mas bot trava sem executar limpeza

**Diagnóstico:**
```python
# Verificar logs do cliente:
grep "WebSocket não disponível" fishing_bot.log
grep "Trigger local de limpeza" fishing_bot.log
```

**Possíveis Causas:**
1. `self.ws_client` não é None mas está desconectado
2. Lógica de fallback não sendo executada

**Soluções:**
1. Verificar `if self.ws_client:` em fishing_engine.py (linha ~1041)
2. Mudar para `if self.ws_client and self.ws_client.connected:`
3. Adicionar log antes do fallback para debug

---

## Resumo de Mudanças

### Arquivos Modificados

1. **server/server.py**
   - Adicionado `rod_timeout_history` e `total_timeouts` em `FishingSession`
   - Métodos: `increment_timeout()`, `reset_timeout()`, `should_clean_by_timeout()`
   - Handler WebSocket para evento `"timeout"`
   - Reset automático de timeout em `fish_caught`

2. **client/ws_client.py**
   - Método `send_timeout(current_rod)` para enviar evento ao servidor

3. **client/server_connector.py**
   - Sincronização de `maintenance_timeout` em `_sync_config_with_server()`

4. **core/fishing_engine.py**
   - Modificado para enviar timeout ao servidor via `ws_client.send_timeout()`
   - Fallback local se servidor indisponível

---

## Diagrama de Estados

```
┌─────────────────────────────────────────────────────┐
│           ESTADO DE TIMEOUT POR VARA                │
└─────────────────────────────────────────────────────┘

      VARA 1: [timeouts=0] ──────┐
                                  │
      120s sem peixe              │ Peixe capturado
                ↓                 ↓
      VARA 1: [timeouts=1] ←──────┘
                │
      120s sem peixe
                ↓
      VARA 1: [timeouts=2]
                │
      120s sem peixe
                ↓
      VARA 1: [timeouts=3] ──→ TRIGGER LIMPEZA ──→ [timeouts=0]
```

---

## Conclusão

O sistema de timeout foi completamente migrado do cliente para o servidor, mantendo:

✅ **Consistência Arquitetural**: Servidor decide todas as ações
✅ **Tracking Centralizado**: Estado armazenado por sessão no servidor
✅ **Fallback Robusto**: Cliente funciona independentemente se desconectado
✅ **Sincronização Automática**: Configurações sincronizadas ao conectar
✅ **Reset Inteligente**: Timeouts resetam quando peixe é capturado
✅ **Logs Completos**: Rastreamento detalhado de timeouts no servidor

**Próximos passos sugeridos:**
- [ ] Testar sistema end-to-end com 3 timeouts consecutivos
- [ ] Testar fallback local desconectando servidor
- [ ] Verificar sincronização de configs em múltiplos clientes
- [ ] Adicionar analytics de timeouts no servidor (média, total por hora, etc.)
