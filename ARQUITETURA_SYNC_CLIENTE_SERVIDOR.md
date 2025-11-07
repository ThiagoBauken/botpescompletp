# 🔄 ARQUITETURA: Sincronização Cliente-Servidor

**Data:** 2025-10-31
**Versão:** v5.0

---

## 📋 ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Fluxo Completo](#fluxo-completo)
3. [Sincronização Inicial](#sincronização-inicial)
4. [Ciclo de Pesca](#ciclo-de-pesca)
5. [Execução de Batch](#execução-de-batch)
6. [Debugging](#debugging)

---

## 🎯 VISÃO GERAL

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENTE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Config     │      │   Fishing    │      │  WebSocket   │  │
│  │   Manager    │─────▶│   Engine     │◀────▶│   Client     │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                     │                      │          │
│         │                     │                      │          │
│         ▼                     ▼                      ▼          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ default.json │      │  Templates   │      │   Callbacks  │  │
│  │ + user.json  │      │  Detection   │      │   (feed/etc) │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                          SERVIDOR                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Session    │      │    Batch     │      │   WebSocket  │ │
│  │   Manager    │◀────▶│   Builder    │◀────▶│   Handler    │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│         │                     │                      │         │
│         │                     │                      │         │
│         ▼                     ▼                      ▼         │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │ user_config  │      │   Logic      │      │   Events     │ │
│  │ fish_count   │      │   (triggers) │      │   (msgs)     │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Princípios

1. **Cliente Obedece, Servidor Decide:**
   - Cliente executa ações locais (pesca, detecção)
   - Servidor decide quando fazer operações (feed, clean, maintenance)
   - Cliente notifica servidor de eventos (fish_caught, timeout)
   - Servidor responde com batches de comandos

2. **Sincronização de Estado:**
   - Cliente envia configurações na conexão
   - Servidor armazena configurações por sessão
   - Servidor usa configurações para calcular triggers
   - Cliente executa comandos do servidor

3. **Comunicação WebSocket:**
   - Bidirecional, tempo real
   - Cliente → Servidor: Eventos (fish_caught, rod_broken)
   - Servidor → Cliente: Comandos (feed, clean, maintenance, switch_rod)

---

## 🔄 FLUXO COMPLETO

### Fase 1: Inicialização

```
┌──────────┐
│ CLIENTE  │
└────┬─────┘
     │
     │ 1. Carregar configurações
     ▼
┌─────────────────────────────────────┐
│ ConfigManager.load_configs()        │
├─────────────────────────────────────┤
│ • Ler default_config.json           │
│ • Ler data/config.json              │
│ • Merge profundo                    │
│ • merged_config pronto              │
└────┬────────────────────────────────┘
     │
     │ 2. Conectar ao servidor
     ▼
┌─────────────────────────────────────┐
│ connect_to_server()                 │
├─────────────────────────────────────┤
│ • Autenticar (login/senha/license)  │
│ • Receber token                     │
│ • Conectar WebSocket                │
└────┬────────────────────────────────┘
     │
     │ 3. Sincronizar configurações
     ▼
┌─────────────────────────────────────┐
│ _sync_config_with_server()          │
├─────────────────────────────────────┤
│ • config.get("chest_side")          │
│ • config.get("auto_clean.interval") │
│ • config.get("feeding_system....")  │
│ • Enviar via WebSocket              │
└────┬────────────────────────────────┘
     │
     │ WebSocket: {"event": "config_sync", "config": {...}}
     ▼
┌──────────┐
│ SERVIDOR │
└────┬─────┘
     │
     │ 4. Receber e armazenar
     ▼
┌─────────────────────────────────────┐
│ handle_config_sync()                │
├─────────────────────────────────────┤
│ session.user_config = {             │
│   "chest_side": "right",            │
│   "clean_interval_fish": 2,         │
│   "feed_interval_fish": 10,         │
│   ...                               │
│ }                                   │
└─────────────────────────────────────┘
```

### Fase 2: Ciclo de Pesca

```
┌──────────┐
│ CLIENTE  │
└────┬─────┘
     │
     │ 1. Executar ciclo de pesca
     ▼
┌─────────────────────────────────────┐
│ FishingEngine.main_fishing_loop()   │
├─────────────────────────────────────┤
│ • Phase 1: Cast (1.6s)              │
│ • Phase 2: Fast clicking (7.5s)     │
│ • Phase 3: A/D movements (até 122s) │
│ • Detectar catch.png                │
└────┬────────────────────────────────┘
     │
     │ 2. Peixe capturado!
     ▼
┌─────────────────────────────────────┐
│ Incrementar fish_count              │
│ Registrar uso da vara               │
└────┬────────────────────────────────┘
     │
     │ 3. Notificar servidor
     │ WebSocket: {"event": "fish_caught", "rod_id": 1, ...}
     ▼
┌──────────┐
│ SERVIDOR │
└────┬─────┘
     │
     │ 4. Processar fish_caught
     ▼
┌─────────────────────────────────────┐
│ handle_fish_caught()                │
├─────────────────────────────────────┤
│ • session.fish_count += 1           │
│ • Atualizar rod_usage_history       │
│ • Calcular triggers                 │
└────┬────────────────────────────────┘
     │
     │ 5. Construir batch de comandos
     ▼
┌─────────────────────────────────────┐
│ Verificar triggers (em ordem):      │
├─────────────────────────────────────┤
│ 🍖 PRIORIDADE 1: Feeding?           │
│    if fish_count % feed_interval:   │
│       operations.append("feed")     │
│                                     │
│ 🔧 PRIORIDADE 2: Maintenance?       │
│    if rod_timeout_count >= 1:       │
│       operations.append("maint")    │
│                                     │
│ 🧹 PRIORIDADE 3: Cleaning?          │
│    if fish_count % clean_interval:  │
│       operations.append("clean")    │
│                                     │
│ 🔄 PRIORIDADE 4: Switch rod         │
│    (SEMPRE após cada peixe)         │
│    operations.append("switch_rod")  │
└────┬────────────────────────────────┘
     │
     │ 6. Enviar batch ao cliente
     │ WebSocket: {"event": "execute_batch", "operations": [...]}
     ▼
┌──────────┐
│ CLIENTE  │
└────┬─────┘
     │
     │ 7. Receber e processar batch
     ▼
┌─────────────────────────────────────┐
│ handle_execute_batch(operations)    │
├─────────────────────────────────────┤
│ • Marcar waiting_batch = True       │
│ • Detectar tipo de operações        │
│ • Executar conforme necessário      │
└─────────────────────────────────────┘
```

---

## 🔧 SINCRONIZAÇÃO INICIAL

### Cliente: _sync_config_with_server()

**Localização:** `client/server_connector.py` linhas 33-138

**Processo:**

```python
# 1. Criar ConfigManager (faz merge automático)
config = ConfigManager()

# 2. Ler valores do merged_config
server_config = {
    # Feeding
    "feed_interval_fish": config.get("feeding_system.trigger_catches", 10),

    # Cleaning
    "clean_interval_fish": config.get("auto_clean.interval", 2),

    # Chest
    "chest_side": config.get("chest_side", "right"),
    "chest_distance": config.get("chest_distance", 1200),

    # Maintenance
    "maintenance_timeout": config.get("timeouts.maintenance_timeout", 1),

    # Bait priority
    "bait_priority": config.get("bait_system.priority"),

    # Etc...
}

# 3. Enviar ao servidor
ws_client.send_config_sync(server_config)
```

**Payload WebSocket:**

```json
{
  "event": "config_sync",
  "config": {
    "chest_side": "right",
    "clean_interval_fish": 2,
    "feed_interval_fish": 10,
    "maintenance_timeout": 1,
    "rod_switch_limit": 2,
    "bait_priority": {
      "crocodilo": 1,
      "bigcat": 2,
      "carneurso": 3,
      "carnedelobo": 4,
      "TROUTT": 5,
      "grub": 6,
      "minhoca": 7
    }
  }
}
```

### Servidor: handle_config_sync()

**Localização:** `server/server.py` (handler WebSocket)

**Processo:**

```python
async def handle_config_sync(login, config):
    """Armazenar configurações do cliente na sessão"""

    if login not in sessions:
        return

    session = sessions[login]

    # Armazenar configurações
    session.user_config.update(config)

    logger.info(f"⚙️ {login}: Configurações sincronizadas")
    logger.debug(f"   Config: {config}")
```

**Resultado:**

Cada sessão agora tem:
```python
session.user_config = {
    "chest_side": "right",
    "clean_interval_fish": 2,
    "feed_interval_fish": 10,
    "maintenance_timeout": 1,
    ...
}
```

---

## 🎣 CICLO DE PESCA

### Cliente: fish_caught Event

**Localização:** `core/fishing_engine.py` (após catch.png detectado)

**Processo:**

```python
# 1. Peixe capturado
_safe_print(f"🐟 Peixe #{fish_count} capturado!")

# 2. Incrementar contador
self.fish_count += 1

# 3. Registrar uso da vara
current_rod = self._get_current_rod()
self.rod_usage[current_rod] += 1

# 4. Notificar servidor
if self.ws_client:
    self.ws_client.send_fish_caught(
        fish_count=self.fish_count,
        rod_id=current_rod,
        rod_usage=self.rod_usage[current_rod]
    )
```

**Payload WebSocket:**

```json
{
  "event": "fish_caught",
  "fish_count": 1,
  "rod_id": 1,
  "rod_usage": 1
}
```

### Servidor: handle_fish_caught()

**Localização:** `server/server.py` linhas 800-950

**Processo Completo:**

```python
async def handle_fish_caught(login, data):
    """Processar captura de peixe e gerar batch"""

    session = sessions[login]

    # 1. Atualizar contadores
    session.fish_count += 1
    fish_count = session.fish_count

    rod_id = data.get("rod_id", 1)
    rod_usage = data.get("rod_usage", 1)

    # 2. Atualizar histórico de uso
    session.rod_usage_history[rod_id] = rod_usage

    logger.info(f"🐟 {login}: Peixe #{fish_count} (vara {rod_id}, uso {rod_usage})")

    # 3. Construir batch de operações
    operations = []

    # 🍖 PRIORIDADE 1: Feeding?
    feed_interval = session.user_config.get("feed_interval_fish", 10)
    if fish_count % feed_interval == 0:
        operations.append({
            "type": "feed",
            "params": {}
        })
        logger.info(f"🍖 {login}: Trigger de feeding ({fish_count} peixes)")

    # 🔧 PRIORIDADE 2: Maintenance?
    maintenance_timeout_limit = session.user_config.get("maintenance_timeout", 1)
    needs_maintenance = False

    for rod, timeouts in session.rod_timeout_history.items():
        if timeouts >= 1:
            needs_maintenance = True
            break

    if needs_maintenance:
        operations.append({
            "type": "maintenance",
            "params": {}
        })
        logger.info(f"🔧 {login}: Operação MAINTENANCE adicionada ao batch")

    # 🧹 PRIORIDADE 3: Cleaning?
    clean_interval = session.user_config.get("clean_interval_fish", 2)
    if fish_count % clean_interval == 0:
        operations.append({
            "type": "clean",
            "params": {
                "chest_side": session.user_config.get("chest_side", "right")
            }
        })
        logger.info(f"🧹 {login}: Trigger de cleaning ({fish_count} peixes)")

    # 🔄 PRIORIDADE 4: Switch rod (SEMPRE)
    operations.append({
        "type": "switch_rod",
        "params": {
            "will_open_chest": len(operations) > 0
        }
    })
    logger.info(f"🔄 {login}: Switch rod adicionado (will_open_chest={len(operations) > 0})")

    # 4. Enviar batch ao cliente
    await send_execute_batch(login, operations)
```

**Exemplo de Batch (2º peixe, clean_interval=2):**

```json
{
  "event": "execute_batch",
  "operations": [
    {
      "type": "clean",
      "params": {
        "chest_side": "right"
      }
    },
    {
      "type": "switch_rod",
      "params": {
        "will_open_chest": true
      }
    }
  ]
}
```

---

## ⚙️ EXECUÇÃO DE BATCH

### Cliente: handle_execute_batch()

**Localização:** `core/fishing_engine.py` linhas 1790-1920

**Processo:**

```python
def handle_execute_batch(self, operations):
    """Executar batch de operações do servidor"""

    # 1. Marcar flag de espera
    self.waiting_for_batch_completion = True

    # 2. Analisar operações
    has_chest_ops = False
    has_switch_rod = False

    for op in operations:
        if op["type"] in ["feed", "clean", "maintenance"]:
            has_chest_ops = True
        if op["type"] == "switch_rod":
            has_switch_rod = True

    # 3. Edge case: Apenas switch_rod (sem operações de baú)
    if has_switch_rod and not has_chest_ops:
        _safe_print("⚡ [EDGE CASE] Apenas switch_rod - executando imediatamente!")

        # Executar callback de conclusão
        self._on_batch_complete(operations)
        return

    # 4. Caso normal: Executar operações de baú
    if has_chest_ops:
        # Enfileirar para execução após fechar baú
        self.pending_batch_operations = operations

        # ChestOperationCoordinator vai executar
        _safe_print("📋 Batch com operações de baú enfileirado")
```

### Cliente: _on_batch_complete()

**Callback executado após batch completo**

**Localização:** `core/fishing_engine.py` linhas 1620-1750

```python
def _on_batch_complete(self, operations):
    """Callback de conclusão de batch"""

    _safe_print("=" * 60)
    _safe_print("🔄 [BATCH COMPLETE CALLBACK] Sincronizando cliente após batch")
    _safe_print("=" * 60)

    # 1. Executar switch_rod se presente
    for op in operations:
        if op["type"] == "switch_rod":
            will_open_chest = op["params"].get("will_open_chest", False)

            if not will_open_chest:
                # Não teve operações de baú - executar switch_rod
                _safe_print("🔄 [PASSO 1] Executando switch_rod pendente...")
                self._perform_rod_switch()
                _safe_print("   ✅ Switch rod executado com sucesso")

    # 2. Resetar flag de espera
    _safe_print("🔓 [PASSO 2] Resetando flag waiting_for_batch_completion...")
    self.waiting_for_batch_completion = False

    # 3. Retornar ao estado FISHING
    _safe_print("🎣 [PASSO 3] Retornando ao estado FISHING...")
    self.state = FishingState.FISHING

    _safe_print("✅ Sincronização completa - cliente pode pescar novamente!")
    _safe_print("=" * 60)
```

---

## 🐛 DEBUGGING

### Logs de Sincronização

**Cliente (Startup):**
```
⚙️ ConfigManager inicializado
✅ Configurações carregadas com sucesso
🌐 Conectando ao servidor multi-usuário...
✅ Ativação bem-sucedida!
🔗 Conectando ao WebSocket...
✅ Conectado ao servidor!

⚙️ Sincronizando configs com servidor:
   • Alimentar a cada: 10 peixes
   • Limpar a cada: 2 peixe(s)        ← IMPORTANTE: Deve ser 2!
   • Rod switch limit: 2 usos
   • Chest side: right                ← IMPORTANTE: Deve ser right!
   • Feeds per session: 2
   • Prioridade de iscas: {...}
```

**Servidor (Recebendo config):**
```
⚙️ thiago: Configurações sincronizadas
DEBUG: Config recebido:
{
    'chest_side': 'right',              ← Verificar!
    'clean_interval_fish': 2,           ← Verificar!
    'feed_interval_fish': 10,
    'maintenance_timeout': 1,
    'rod_switch_limit': 2
}
```

### Logs de Fish Caught

**Cliente:**
```
🐟 Peixe #1 capturado!
📤 Cliente → Servidor: fish_caught (vara 1: 1 uso)
```

**Servidor:**
```
🐟 thiago: Peixe #1 (vara 1, uso 1)

🍖 thiago: Verificando trigger de feeding...
   • fish_count=1, interval=10
   • 1 % 10 = 1 (NÃO dispara)

🔧 thiago: Verificando trigger de maintenance...
   • rod_timeout_history = {}
   • needs_maintenance = False

🧹 thiago: Verificando trigger de cleaning...
   • fish_count=1, interval=2          ← IMPORTANTE: Interval!
   • 1 % 2 = 1 (NÃO dispara)           ← Não limpa no 1º peixe ✅

🔄 thiago: Switch rod adicionado (will_open_chest=False)

📦 thiago: Enviando batch: [{"type": "switch_rod", ...}]
```

**Cliente:**
```
📦 Servidor → Cliente: execute_batch [{"type": "switch_rod"}]

⚡ [EDGE CASE] Apenas switch_rod - executando imediatamente!

🔄 [BATCH COMPLETE CALLBACK] Sincronizando cliente após batch
🔄 [PASSO 1] Executando switch_rod pendente...
   ✅ Switch rod executado com sucesso
🔓 [PASSO 2] Resetando flag waiting_for_batch_completion...
🎣 [PASSO 3] Retornando ao estado FISHING...
✅ Sincronização completa - cliente pode pescar novamente!

🎣 Iniciando ciclo de pesca...  ← Bot retoma!
```

### Segundo Peixe (Trigger de Clean)

**Servidor:**
```
🐟 thiago: Peixe #2 (vara 2, uso 1)

🧹 thiago: Verificando trigger de cleaning...
   • fish_count=2, interval=2
   • 2 % 2 = 0 (DISPARA!) ✅           ← Limpa no 2º peixe!

📋 thiago: Operação CLEAN adicionada ao batch
   • chest_side: right                 ← IMPORTANTE: Side correto!

🔄 thiago: Switch rod adicionado (will_open_chest=True)

📦 thiago: Enviando batch: [
    {"type": "clean", "params": {"chest_side": "right"}},
    {"type": "switch_rod", "params": {"will_open_chest": true}}
]
```

**Cliente:**
```
📦 Servidor → Cliente: execute_batch

🧹 [CLEAN] Detectado no batch
🔄 [SWITCH_ROD] Detectado no batch (será executado APÓS baú)

📋 Batch com operações de baú enfileirado
🔒 [SYNC] Marcando waiting_for_batch_completion = True

[ChestOperationCoordinator executa clean]
   🧹 Abrindo baú no lado: right      ← IMPORTANTE: Side correto!
   🧹 Executando limpeza...
   ✅ Limpeza concluída

[Callback de conclusão do baú]
   🔄 Executando switch_rod...
   ✅ Switch rod executado
   🔓 Resetando flag...
   🎣 Retornando ao estado FISHING...

🎣 Iniciando ciclo de pesca...  ← Bot retoma!
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### Sincronização Inicial

- [ ] ConfigManager carrega default_config.json
- [ ] ConfigManager carrega data/config.json
- [ ] ConfigManager faz merge correto
- [ ] `_sync_config_with_server()` usa config.get()
- [ ] Valores enviados ao servidor estão corretos
- [ ] Servidor armazena em session.user_config
- [ ] Logs mostram valores corretos

### Primeiro Peixe (Sem Clean)

- [ ] Cliente detecta peixe
- [ ] Cliente notifica servidor (fish_caught)
- [ ] Servidor incrementa fish_count
- [ ] Servidor verifica triggers (feed: NÃO, clean: NÃO, maintenance: NÃO)
- [ ] Servidor adiciona apenas switch_rod ao batch
- [ ] Cliente recebe batch
- [ ] Cliente detecta edge case (apenas switch_rod)
- [ ] Cliente executa switch_rod imediatamente
- [ ] Cliente reseta flag waiting_for_batch_completion
- [ ] Bot retoma pesca

### Segundo Peixe (Com Clean)

- [ ] Cliente detecta peixe
- [ ] Cliente notifica servidor (fish_caught)
- [ ] Servidor incrementa fish_count (agora = 2)
- [ ] Servidor verifica triggers (clean: SIM!)
- [ ] Servidor adiciona clean E switch_rod ao batch
- [ ] Cliente recebe batch
- [ ] Cliente detecta operações de baú
- [ ] Cliente enfileira batch
- [ ] ChestOperationCoordinator abre baú (lado correto!)
- [ ] Limpeza executada
- [ ] Callback executa switch_rod
- [ ] Cliente reseta flag
- [ ] Bot retoma pesca

---

## 📝 RESUMO

### Fluxo Funcional

1. **Startup:** ConfigManager faz merge → Sync envia configs → Servidor armazena
2. **Pesca:** Cliente pesca → Notifica servidor → Servidor calcula triggers → Envia batch
3. **Execução:** Cliente recebe batch → Executa operações → Callback reseta → Retoma pesca

### Pontos Críticos

✅ **ConfigManager sempre retorna merged config** (default + user)
✅ **Servidor usa user_config para calcular triggers**
✅ **Cliente executa comandos com parâmetros do servidor**
✅ **Callback reseta flag para permitir retomada**

### Debugging

- Verificar logs de sync (chest_side, clean_interval_fish)
- Verificar logs de triggers no servidor (% operations)
- Verificar batch enviado (tipos e params)
- Verificar execução no cliente (edge cases, callbacks)

---

**STATUS:** 🟢 **SISTEMA FUNCIONAL**
