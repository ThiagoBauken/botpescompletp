# 🔧 Plano de Implementação - Arquitetura Coordenada v3-style

**Data:** 2025-10-29
**Objetivo:** Corrigir comunicação cliente-servidor para executar operações de forma coordenada

---

## 🎯 Problema Identificado

### Arquitetura Atual (QUEBRADA):
```
Cliente captura peixe
  ↓
Servidor recebe fish_caught
  ↓
Servidor envia: "request_template_detection" ❌
  ↓
Cliente: DetectionHandler abre baú → detecta → fecha baú → envia coords
  ↓
Servidor: constrói sequence com open_chest
  ↓
Cliente: ActionExecutor abre baú DE NOVO ❌❌
```

**Resultado:** Baú aberto 2 vezes! Operações não coordenadas!

---

## ✅ Solução Proposta (v3-style)

### Arquitetura Corrigida:
```
Cliente captura peixe
  ↓
Servidor recebe fish_caught
  ↓
Servidor decide: [feed, clean, switch_rod_pair] ✅
  ↓
Servidor envia: comando BATCH com todas as operações ✅
  ↓
Cliente: BatchCoordinator executa TUDO em uma sessão:
  - Abre baú 1x
  - Detecta comida NA HORA (baú já aberto)
  - Executa feeding
  - Detecta peixes NA HORA
  - Executa cleaning
  - Executa maintenance se necessário
  - Fecha baú 1x ✅
  ↓
Cliente notifica servidor: operations_completed
```

**Resultado:** Baú aberto apenas 1 vez! Coordenado como v3!

---

## 📋 Mudanças Necessárias

### 1. Servidor (`server/server.py`)

**ANTES:**
```python
if session.should_feed():
    commands.append({
        "cmd": "request_template_detection",
        "templates": ["filefrito", "eat"]
    })

if session.should_clean():
    commands.append({
        "cmd": "request_inventory_scan"
    })
```

**DEPOIS:**
```python
# Coletar todas as operações necessárias
operations = []

if session.should_feed():
    operations.append({
        "type": "feeding",
        "params": {"feeds_per_session": 2}
    })

if session.should_clean():
    operations.append({
        "type": "cleaning",
        "params": {}
    })

if session.should_switch_rod_pair():
    operations.append({
        "type": "switch_rod_pair",
        "params": {"target_rod": session.get_next_pair_rod()}
    })

# Enviar BATCH único
if operations:
    await websocket.send_json({
        "cmd": "execute_batch",
        "operations": operations
    })
```

---

### 2. Cliente - Novo BatchCoordinator (`client/batch_coordinator.py`)

**Criar novo módulo:**

```python
class BatchCoordinator:
    """
    🏪 Coordenador de Operações em Batch (v3-style)

    Recebe lista de operações do servidor e executa TUDO em uma sessão:
    - Abre baú 1x
    - Executa todas as operações
    - Fecha baú 1x

    Operações suportadas:
    - feeding: Detecta comida NA HORA, come
    - cleaning: Detecta peixes NA HORA, transfere
    - switch_rod_pair: Troca para novo par de varas
    - maintenance: Manutenção oportunística
    """

    def execute_batch(self, operations: list):
        """Executar batch coordenado"""
        # 1. Abrir baú 1x
        chest_manager.open_chest()

        # 2. Executar cada operação
        for op in operations:
            if op["type"] == "feeding":
                self._execute_feeding_inline(op["params"])
            elif op["type"] == "cleaning":
                self._execute_cleaning_inline(op["params"])
            elif op["type"] == "switch_rod_pair":
                # Executar APÓS fechar baú
                self.pending_rod_switch = op["params"]

        # 3. Fechar baú 1x
        chest_manager.close_chest()

        # 4. Executar rod switch se pendente
        if self.pending_rod_switch:
            self._execute_rod_switch(self.pending_rod_switch)

    def _execute_feeding_inline(self, params):
        """Feeding com detecção NA HORA"""
        # Baú JÁ ESTÁ ABERTO aqui!
        food_loc = template_engine.detect("filefrito")  # Detecta agora
        eat_loc = template_engine.detect("eat")

        # Transferir comida
        input_manager.click(food_loc)

        # Comer N vezes
        for _ in range(params["feeds_per_session"]):
            input_manager.click(eat_loc)

    def _execute_cleaning_inline(self, params):
        """Cleaning com detecção NA HORA"""
        # Baú JÁ ESTÁ ABERTO aqui!
        fish_locs = self._detect_fish_inline()  # Detecta agora

        # Transferir todos os peixes
        for fish_loc in fish_locs:
            input_manager.ctrl_click(fish_loc)
```

---

### 3. Cliente - FishingEngine

**Modificar handler de comandos:**

```python
# Em handle_server_command():
def handle_server_command(self, cmd_data):
    cmd = cmd_data.get("cmd")

    if cmd == "execute_batch":
        # NOVO: Executar batch coordenado
        operations = cmd_data.get("operations", [])
        self.batch_coordinator.execute_batch(operations)

        # Notificar servidor
        self.ws_client.send({
            "event": "batch_completed",
            "data": {"operations": [op["type"] for op in operations]}
        })

    # Remover handlers antigos:
    # - request_template_detection → DELETAR
    # - request_inventory_scan → DELETAR
    # - execute_sequence → DELETAR (não é mais necessário)
```

---

### 4. DetectionHandler - Remover Abertura de Baú

**ANTES:**
```python
def detect_food_and_eat(self):
    # ❌ Abre baú
    self._open_chest()
    # Detecta
    food_result = self.template_engine.detect_template("filefrito")
    # ❌ Fecha baú
    self._close_chest()
    return coords
```

**DEPOIS:**
```python
def detect_food_and_eat(self):
    # ✅ BAÚ JÁ ESTÁ ABERTO (BatchCoordinator abriu!)
    # Apenas detectar e retornar coords
    food_result = self.template_engine.detect_template("filefrito")
    eat_result = self.template_engine.detect_template("eat")
    return (food_result.location, eat_result.location)
```

---

## 🔄 Fluxo Completo (Após Correção)

### Exemplo: Capturou 1 peixe (triggers: feed + clean)

```
1. 🐟 Cliente captura peixe
   └─> ws_client.send("fish_caught", {rod_uses: {...}, current_rod: 1})

2. 🖥️ Servidor processa:
   └─> session.increment_fish() → 1 peixe
   └─> should_feed() → True (1 peixe ≥ fish_per_feed)
   └─> should_clean() → True (1 peixe ≥ clean_interval)
   └─> should_switch_rod_pair() → False

   └─> Envia BATCH:
       {
         "cmd": "execute_batch",
         "operations": [
           {"type": "feeding", "params": {"feeds_per_session": 2}},
           {"type": "cleaning", "params": {}}
         ]
       }

3. 💻 Cliente recebe batch:
   └─> batch_coordinator.execute_batch(operations)

       ✅ Abre baú 1x

       ✅ Operação 1: Feeding
          - Detecta "filefrito" → (1306, 858)
          - Detecta "eat" → (1083, 373)
          - Click em food
          - Click 2x em eat

       ✅ Operação 2: Cleaning
          - Detecta peixes → [(709, 700), (805, 700)]
          - Ctrl+Click em cada peixe

       ✅ Fecha baú 1x

   └─> ws_client.send("batch_completed", {"operations": ["feeding", "cleaning"]})

4. 🖥️ Servidor recebe confirmação:
   └─> logger.info("✅ user: Batch concluído [feeding, cleaning]")
   └─> session.last_feed_at = session.fish_count
   └─> session.last_clean_at = session.fish_count
```

---

## 📊 Comparação: Antes vs Depois

### Antes (QUEBRADO):
- 🔴 Baú aberto 2x (DetectionHandler + ActionExecutor)
- 🔴 Detecção separada da execução
- 🔴 Servidor envia "request_XXX" → cliente detecta → servidor constrói sequence → cliente executa
- 🔴 3 etapas assíncronas, não coordenadas
- 🔴 Possibilidade de race conditions

### Depois (CORRIGIDO):
- ✅ Baú aberto 1x apenas
- ✅ Detecção NA HORA (durante execução)
- ✅ Servidor envia batch → cliente executa tudo de uma vez
- ✅ 1 etapa síncrona, coordenada
- ✅ Sem race conditions

---

## 🧪 Validação

### Teste 1: Feeding + Cleaning Simultâneos
```
1. Configurar:
   - fish_per_feed = 1
   - clean_interval = 1

2. Apertar F9 e capturar 1 peixe

3. Verificar logs:
   ✅ "Aguardando comandos do servidor (2s)..."
   ✅ "2 comando(s) recebido(s)"
   ✅ "Abrindo baú..."
   ✅ "Executando feeding..."
   ✅ "Executando cleaning..."
   ✅ "Fechando baú..."
   ✅ Baú aberto APENAS 1 vez
```

### Teste 2: Rod Switch Integrado
```
1. Configurar:
   - rod_switch_limit = 2

2. Capturar 4 peixes (esgota par 1)

3. Verificar logs:
   ✅ "Batch: [feeding, cleaning, switch_rod_pair]"
   ✅ "Abrindo baú..."
   ✅ "Executando feeding..."
   ✅ "Executando cleaning..."
   ✅ "Fechando baú..."
   ✅ "Executando switch_rod_pair → Vara 3"
   ✅ Rod switch APÓS fechar baú
```

---

## 📅 Cronograma de Implementação

### Etapa 1: Servidor (30 min)
- [ ] Modificar fish_caught handler para coletar operations
- [ ] Criar comando execute_batch
- [ ] Remover request_template_detection e request_inventory_scan

### Etapa 2: Cliente - BatchCoordinator (45 min)
- [ ] Criar client/batch_coordinator.py
- [ ] Implementar execute_batch()
- [ ] Implementar _execute_feeding_inline()
- [ ] Implementar _execute_cleaning_inline()
- [ ] Implementar _execute_rod_switch()

### Etapa 3: Cliente - Integração (30 min)
- [ ] Modificar FishingEngine.handle_server_command()
- [ ] Remover DetectionHandler._open_chest() e _close_chest()
- [ ] Remover ActionExecutor (não é mais necessário)

### Etapa 4: Testes (30 min)
- [ ] Teste 1: Feeding + Cleaning
- [ ] Teste 2: Rod Switch
- [ ] Teste 3: 10 peixes consecutivos

**Tempo Total Estimado:** ~2 horas

---

## ⚠️ Riscos e Mitigação

### Risco 1: Detecção Falha Durante Execução
**Mitigação:** Retry mechanism com fallback

```python
def _execute_feeding_inline(self, params):
    for attempt in range(3):  # 3 tentativas
        food_loc = template_engine.detect("filefrito")
        if food_loc.found:
            break
        time.sleep(0.5)

    if not food_loc.found:
        logger.error("❌ Comida não encontrada após 3 tentativas")
        # Abortar feeding, continuar com próxima operação
        return False
```

### Risco 2: Servidor e Cliente Dessincronizados
**Mitigação:** Confirmação de batch_completed obrigatória

```python
# Servidor aguarda confirmação com timeout:
async def wait_for_batch_completion(websocket, timeout=30):
    try:
        msg = await asyncio.wait_for(websocket.receive_json(), timeout=timeout)
        if msg.get("event") == "batch_completed":
            return True
    except asyncio.TimeoutError:
        logger.error("❌ Timeout aguardando batch_completed")
        return False
```

---

**Status:** 📝 PLANO PRONTO - AGUARDANDO IMPLEMENTAÇÃO
