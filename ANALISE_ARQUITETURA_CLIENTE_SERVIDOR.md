# 📊 Análise Completa: Arquitetura Cliente-Servidor v5

## 🎯 Resumo Executivo

O v5 implementa uma arquitetura **híbrida com servidor autoritativo**, onde:
- **Servidor**: Detém toda a lógica de negócio e decisões
- **Cliente**: Executa detecções visuais e ações mecânicas

Esta separação protege a lógica do bot contra engenharia reversa e permite controle centralizado.

---

## 🏗️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE LOCAL                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DETECÇÃO (OpenCV)                                    │   │
│  │  • Template matching (peixes, iscas, varas)          │   │
│  │  • Coordenadas de elementos na tela                   │   │
│  │  • Status visual das varas                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  EXECUÇÃO (Input Manager)                             │   │
│  │  • Cliques (mouse)                                     │   │
│  │  • Teclas (keyboard/Arduino)                           │   │
│  │  • Movimentos de câmera                                │   │
│  │  • Sequências de ações atômicas                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                  │
│                     WebSocket Client                          │
└─────────────────────────────────────────────────────────────┘
                             ↕
                      INTERNET (HTTPS/WSS)
                             ↕
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR REMOTO                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AUTENTICAÇÃO (Keymaster)                             │   │
│  │  • Validação de licenças                              │   │
│  │  • HWID binding (anti-compartilhamento)               │   │
│  │  • Gestão de sessões                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LÓGICA DE NEGÓCIO                                     │   │
│  │  • Quando alimentar (a cada N peixes)                 │   │
│  │  • Quando limpar (a cada N peixes ou timeouts)        │   │
│  │  • Quando trocar varas (tracking de uso)               │   │
│  │  • Quando pausar (anti-detecção)                       │   │
│  │  • Regras de prioridade (feed > maint > clean)        │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  CONSTRUÇÃO DE SEQUÊNCIAS                             │   │
│  │  • ActionSequenceBuilder                               │   │
│  │  • Sequências de feeding/cleaning/maintenance          │   │
│  │  • Coordenadas completas + timings                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🖥️ CÓDIGO LOCAL (Cliente)

### ✅ O que o Cliente FAZ

#### 1. **Detecção Visual (Template Matching)**
**Arquivo:** `core/template_engine.py`

```python
# Cliente detecta templates via OpenCV
result = template_engine.detect_template('catch', confidence=0.8)
if result.found:
    # Envia coordenada ao servidor
    ws_client.send_detection('catch', result.location)
```

**Responsabilidades:**
- ✅ Capturar screenshot (MSS)
- ✅ Detectar templates (OpenCV `matchTemplate`)
- ✅ Retornar coordenadas (x, y) e confidence
- ✅ **NÃO** decide o que fazer com a detecção

**Templates detectados:**
- `catch.png` - Peixe capturado
- `VARANOBAUCI.png` - Vara com isca
- `enbausi.png` - Vara sem isca
- `varaquebrada.png` - Vara quebrada
- `filefrito.png` - Comida
- `eat.png` - Botão de comer
- Peixes (salmon, shark, herring, etc.)
- Iscas (carneurso, carnedelobo, grub, minhoca)

---

#### 2. **Execução de Ações Atômicas**
**Arquivo:** `client/action_executor.py`

```python
# Cliente APENAS executa sequência JSON do servidor
executor.execute_sequence([
    {"type": "click", "x": 100, "y": 200},
    {"type": "wait", "duration": 1.5},
    {"type": "key", "key": "esc"}
])
```

**Ações suportadas:**
- ✅ `click` - Clicar em coordenada
- ✅ `click_right` - Clicar direito
- ✅ `wait` - Aguardar N segundos
- ✅ `key` / `key_press` - Pressionar tecla
- ✅ `key_down` / `key_up` - Segurar/soltar tecla
- ✅ `drag` - Arrastar item
- ✅ `move_camera` - Movimento relativo de câmera
- ✅ `mouse_down_relative` / `mouse_up` - Controle de mouse
- ✅ `stop_continuous_clicking` - Parar cliques
- ✅ `stop_camera_movement` - Parar movimentos A/D
- ✅ `template_wait` - Aguardar template aparecer
- ✅ `force_release_key` - Force release (Arduino)

**Características:**
- ❌ **NÃO** decide quais ações executar
- ❌ **NÃO** conhece coordenadas (vêm do servidor)
- ❌ **NÃO** entende o contexto (só executa lista)
- ✅ Executor "burro" e cego

---

#### 3. **Comunicação com Servidor (WebSocket)**
**Arquivo:** `client/ws_client.py`

```python
# Eventos enviados ao servidor
ws_client.send_fish_caught(rod_uses=5, current_rod=1)
ws_client.send_timeout(current_rod=1)
ws_client.send_config_sync(user_config)
ws_client.send_feeding_locations_detected(food_loc, eat_loc)
ws_client.send_fish_locations_detected([...])
ws_client.send_rod_status_detected(status, items)
ws_client.send_sequence_completed("feeding")
ws_client.send_sequence_failed("cleaning", step=5, error="...")
```

**Eventos enviados:**
- `fish_caught` - Peixe capturado + vara atual + usos
- `timeout` - Ciclo sem peixe (120s)
- `sync_config` - Sincronizar configurações locais
- `feeding_locations_detected` - Coordenadas de comida/eat
- `fish_locations_detected` - Lista de peixes no inventário
- `rod_status_detected` - Status das 6 varas + itens disponíveis
- `sequence_completed` - Sequência executada com sucesso
- `sequence_failed` - Erro na execução
- `ping` - Heartbeat (manter conexão)

**Comandos recebidos:**
- `feed` - Executar alimentação
- `clean` - Executar limpeza
- `break` - Pausar bot
- `switch_rod_pair` - Trocar par de varas
- `execute_sequence` - Executar sequência JSON
- `execute_batch` - Executar múltiplas operações
- `request_template_detection` - Solicitar detecção
- `request_inventory_scan` - Solicitar scan de inventário
- `request_rod_analysis` - Solicitar análise de varas

---

#### 4. **Fishing Engine (Ciclo de Pesca)**
**Arquivo:** `core/fishing_engine.py`

```python
# Fishing cycle
def main_fishing_loop():
    while fishing_active:
        # FASE 1: Cast (1.6s right-click)
        # FASE 2: Fast clicking (7.5s)
        # FASE 3: Camera movements (A/D) até catch ou timeout

        # Detectar catch
        result = template_engine.detect_template('catch')
        if result.found:
            # Enviar ao servidor
            ws_client.send_fish_caught(rod_uses, current_rod)
        else:
            # Timeout (120s)
            ws_client.send_timeout(current_rod)
```

**Responsabilidades:**
- ✅ Executar ciclo de pesca (cast → click → A/D)
- ✅ Detectar peixe capturado
- ✅ Reportar eventos ao servidor
- ✅ Processar comandos enfileirados do servidor
- ❌ **NÃO** decide quando alimentar/limpar/trocar vara

---

#### 5. **Input Manager (Controle de Hardware)**
**Arquivo:** `core/input_manager.py` + `core/arduino_input_manager.py`

```python
# Cliente controla mouse/keyboard
input_manager.click(x, y)
input_manager.right_click(x, y)
input_manager.press_key('e')
input_manager.key_down('alt')
input_manager.key_up('alt')

# Ou via Arduino (HID)
arduino_manager.send_command(f"M{x},{y}")  # Move
arduino_manager.send_command("LC")  # Left Click
arduino_manager.send_command("KPe")  # Key Press 'e'
```

**Responsabilidades:**
- ✅ Enviar comandos ao mouse/keyboard
- ✅ Controle via pyautogui OU Arduino Leonardo
- ✅ Timings e delays (anti-detecção)
- ✅ State tracking (botões pressionados)
- ❌ **NÃO** decide quando executar ações

---

#### 6. **Configurações Locais**
**Arquivo:** `data/config.json`

```json
{
  "coordinates": {
    "slot_positions": {
      "1": [709, 1005],
      "2": [805, 1005],
      ...
    },
    "inventory_area": [633, 541, 1233, 953],
    "chest_area": [1214, 117, 1834, 928]
  },
  "rod_system": {
    "rod_switch_limit": 20
  },
  "feeding_system": {
    "trigger_catches": 2,
    "feeds_per_session": 2
  },
  "anti_detection": {
    "break_catches": 50,
    "break_minutes": 45
  },
  "timeouts": {
    "maintenance_timeout": 3
  },
  "chest_side": "left",
  "chest_distance": 1200,
  "bait_priority": {
    "carneurso": 1,
    "carnedelobo": 2,
    "TROUTT": 3,
    "grub": 4,
    "minhoca": 5
  }
}
```

**Sincronização:**
- ✅ Configs locais são sincronizados com servidor via `send_config_sync()`
- ✅ Servidor usa configs do usuário para decisões
- ✅ Cliente mantém configs de coordenadas (resolução específica)

---

#### 7. **UI Local (Interface Gráfica)**
**Arquivo:** `ui/main_window.py`

```python
# UI permite configurar:
- Coordenadas de slots, baú, feeding
- Intervalos de alimentação/limpeza
- Timings de anti-detecção
- Prioridades de isca
- Templates e confidências
- Sistema de varas
```

**Responsabilidades:**
- ✅ Configuração visual das opções
- ✅ Estatísticas em tempo real
- ✅ Controles (Start/Pause/Stop)
- ✅ **NÃO** executa lógica de negócio

---

#### 8. **Sistema de Licenças (Client-side)**
**Arquivo:** `utils/license_manager.py`

```python
# Cliente valida licença com Keymaster
license_manager.validate_license(key)
license_manager.activate_license(key)
license_manager.get_hardware_id()  # HWID fingerprinting
```

**Responsabilidades:**
- ✅ Gerar Hardware ID (fingerprint do PC)
- ✅ Validar licença com servidor Keymaster
- ✅ Salvar licença localmente
- ✅ Binding de HWID (anti-compartilhamento)

---

### ❌ O que o Cliente NÃO FAZ

1. ❌ **Decidir quando alimentar** (servidor decide baseado em fish_count)
2. ❌ **Decidir quando limpar** (servidor decide baseado em fish_count ou timeouts)
3. ❌ **Decidir quando trocar varas** (servidor tracking de rod_uses)
4. ❌ **Decidir quando pausar** (servidor aplica regras anti-ban)
5. ❌ **Conhecer regras de prioridade** (feed > maintenance > clean)
6. ❌ **Construir sequências** (servidor constrói JSON completo)
7. ❌ **Validar limites** (servidor valida configs para prevenir exploits)

---

## 🌐 CÓDIGO SERVIDOR

### ✅ O que o Servidor FAZ

#### 1. **Autenticação e Licenciamento**
**Arquivo:** `server/server.py`

```python
@app.post("/auth/activate")
async def activate_license(request: ActivationRequest):
    # 1. Validar com Keymaster (fonte de verdade)
    keymaster_result = validate_with_keymaster(
        request.license_key,
        request.hwid
    )

    # 2. Verificar HWID binding (anti-compartilhamento)
    binding = check_hwid_binding(request.license_key)
    if binding and binding.hwid != request.hwid:
        return "Licença vinculada a outro PC"

    # 3. Criar sessão e retornar token
    token = generate_token(request)
    return {"token": token, "rules": DEFAULT_RULES}
```

**Responsabilidades:**
- ✅ Validar licenças com Keymaster (https://private-keygen.pbzgje.easypanel.host)
- ✅ HWID binding (1 licença = 1 PC)
- ✅ Gestão de sessões ativas
- ✅ Geração de tokens de autenticação
- ✅ Bloqueio de compartilhamento de contas

**Endpoints:**
- `POST /auth/activate` - Ativar licença
- `GET /` - Health check
- `GET /health` - Status do servidor
- `WebSocket /ws` - Conexão persistente

---

#### 2. **Lógica de Decisão (FishingSession)**
**Arquivo:** `server/server.py` - Classe `FishingSession`

```python
class FishingSession:
    def __init__(self, login: str):
        self.fish_count = 0
        self.rod_uses = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        self.current_rod = 1
        self.current_pair_index = 0
        self.rod_pairs = [(1,2), (3,4), (5,6)]
        self.use_limit = 20
        self.rod_timeout_history = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
        self.user_config = DEFAULT_RULES.copy()
        # ... trackers de última ação ...

    # ═══ REGRAS DE DECISÃO (PROTEGIDAS) ═══

    def should_feed(self) -> bool:
        """Alimentar a cada N peixes"""
        peixes = self.fish_count - self.last_feed_at
        return peixes >= self.user_config["feed_interval_fish"]

    def should_clean(self) -> bool:
        """Limpar a cada N peixes"""
        peixes = self.fish_count - self.last_clean_at
        return peixes >= self.user_config["clean_interval_fish"]

    def should_break(self) -> bool:
        """Pausar a cada N peixes ou tempo"""
        peixes = self.fish_count - self.last_break_at
        tempo = (datetime.now() - self.session_start).seconds / 3600
        return (
            peixes >= self.user_config["break_interval_fish"]
            or tempo >= 2.0
        )

    def should_switch_rod_pair(self) -> bool:
        """Trocar par quando AMBAS varas esgotadas"""
        rod1, rod2 = self.rod_pairs[self.current_pair_index]
        return (
            self.rod_uses[rod1] >= self.use_limit
            and self.rod_uses[rod2] >= self.use_limit
        )

    def should_clean_by_timeout(self, current_rod: int) -> bool:
        """Limpar quando vara atinge N timeouts consecutivos"""
        timeout_limit = self.user_config.get("maintenance_timeout", 3)
        timeouts = self.rod_timeout_history.get(current_rod, 0)
        return timeouts >= timeout_limit
```

**Estado interno (protegido):**
- ✅ `fish_count` - Contador de peixes
- ✅ `rod_uses` - Tracking de uso por vara (1-6)
- ✅ `current_rod` - Vara atual em uso
- ✅ `current_pair_index` - Par atual (0=Par1, 1=Par2, 2=Par3)
- ✅ `rod_timeout_history` - Timeouts consecutivos por vara
- ✅ `user_config` - Configurações sincronizadas do cliente
- ✅ Trackers de última ação (feed/clean/break/rod_switch)

**Regras de negócio:**
- ✅ Quando alimentar (a cada N peixes)
- ✅ Quando limpar (a cada N peixes OU N timeouts)
- ✅ Quando pausar (a cada N peixes OU tempo decorrido)
- ✅ Quando trocar varas (tracking de uso)
- ✅ Prioridades (feed > clean > break)
- ✅ Sistema de 6 varas em 3 pares
- ✅ Validação de configs (anti-exploit)

---

#### 3. **Construção de Sequências (ActionSequenceBuilder)**
**Arquivo:** `server/action_sequences.py`

```python
class ActionSequenceBuilder:
    def build_feeding_sequence(
        self,
        food_location: Dict,
        eat_location: Dict
    ) -> List[Dict]:
        """Constrói sequência COMPLETA de feeding"""
        actions = []

        # 1. Parar fishing
        actions.extend(self._build_stop_fishing())

        # 2. Abrir baú
        actions.extend(self._build_chest_open())

        # 3. Aguardar
        actions.append({"type": "wait", "duration": 1.5})

        # 4. Clicar na comida
        actions.append({
            "type": "click",
            "x": food_location["x"],
            "y": food_location["y"]
        })

        # 5. Clicar em "eat" N vezes
        for i in range(feeds_per_session):
            actions.append({
                "type": "click",
                "x": eat_location["x"],
                "y": eat_location["y"]
            })
            actions.append({"type": "wait", "duration": 1.5})

        # 6. Fechar baú
        actions.extend(self._build_chest_close())

        return actions

    def build_cleaning_sequence(
        self,
        fish_locations: List[Dict]
    ) -> List[Dict]:
        """Constrói sequência COMPLETA de cleaning"""
        # Similar ao feeding, mas com click_right em cada peixe
        ...

    def build_maintenance_sequence(
        self,
        rod_status: Dict,
        available_items: Dict
    ) -> List[Dict]:
        """Constrói sequência COMPLETA de maintenance"""
        # Para cada slot que precisa manutenção:
        # - Drag vara nova se quebrada
        # - Drag isca seguindo prioridade
        ...
```

**Sequências construídas:**
- ✅ **Feeding** - Abrir baú → pegar comida → comer N vezes → fechar
- ✅ **Cleaning** - Abrir baú → transferir peixes → fechar
- ✅ **Maintenance** - Abrir baú → substituir varas → colocar iscas → fechar
- ✅ **Rod Switch** - Segurar direito → trocar vara

**Detalhes das sequências:**
- ✅ Stop fishing (parar cliques/A/D/mouse)
- ✅ Chest open (ALT + movimento câmera + E)
- ✅ Chest close (ALT release + TAB)
- ✅ Coordenadas completas (x, y)
- ✅ Timings (wait, durations)
- ✅ Prioridade de iscas (carneurso > carnedelobo > TROUTT > grub > minhoca)
- ✅ Validação de limites (máx 30 itens por vez)

---

#### 4. **Sistema de Batch Operations (Nova Arquitetura)**
**Arquivo:** `server/server.py` - WebSocket handler

```python
# Quando peixe é capturado
if event == "fish_caught":
    session.increment_fish()
    session.increment_rod_use(current_rod)
    session.reset_timeout(current_rod)

    # Coletar operações necessárias
    operations = []

    # Prioridade 1: Feeding
    if session.should_feed():
        operations.append({
            "type": "feeding",
            "params": {...}
        })

    # Prioridade 2: Cleaning
    if session.should_clean():
        operations.append({
            "type": "cleaning",
            "params": {...}
        })

    # Prioridade 2.5: Switch rod (sempre após peixe)
    operations.append({
        "type": "switch_rod",
        "params": {"will_open_chest": False}
    })

    # Prioridade 3: Switch rod pair
    if session.should_switch_rod_pair():
        target_rod = session.get_next_pair_rod()
        operations.append({
            "type": "switch_rod_pair",
            "params": {"target_rod": target_rod}
        })

    # Prioridade 4: Break
    if session.should_break():
        operations.append({
            "type": "break",
            "params": {"duration_minutes": random.randint(30, 60)}
        })

    # Prioridade 5: Randomize timing (5% chance)
    if session.should_randomize_timing():
        operations.append({
            "type": "adjust_timing",
            "params": {...}
        })

    # Enviar batch único
    await websocket.send_json({
        "cmd": "execute_batch",
        "operations": operations
    })
```

**Batch operations:**
- ✅ Múltiplas operações em um único comando
- ✅ Ordem de prioridade respeitada
- ✅ Cliente executa sequencialmente
- ✅ Feedback de conclusão/falha

---

#### 5. **Validação de Configurações**
**Arquivo:** `server/server.py` - Método `_validate_config`

```python
def _validate_config(self, config: dict) -> dict:
    """Validar configs para prevenir exploits"""
    limits = {
        "fish_per_feed": (1, 100, int),      # Min, Max, Tipo
        "clean_interval": (1, 50, int),
        "rod_switch_limit": (1, 100, int),
        "break_interval": (1, 200, int),
        "break_duration": (1, 3600, int),
        "maintenance_timeout": (1, 20, int),
    }

    validated = {}
    for key, value in config.items():
        if key in limits:
            min_val, max_val, expected_type = limits[key]

            # Validar tipo
            if not isinstance(value, expected_type):
                value = expected_type(value)

            # Validar range
            value = max(min_val, min(value, max_val))

            validated[key] = value

    return validated
```

**Validações:**
- ✅ Tipos corretos (int, float, str)
- ✅ Ranges permitidos (min/max)
- ✅ Prevenir valores negativos
- ✅ Prevenir valores extremos (DoS)
- ✅ Sanitização de entrada

---

#### 6. **Sistema de Timeout Tracking**
**Arquivo:** `server/server.py`

```python
# Quando timeout ocorre
if event == "timeout":
    current_rod = data.get("current_rod", 1)

    # Incrementar contador de timeout da vara
    session.increment_timeout(current_rod)

    # Verificar se precisa limpar
    if session.should_clean_by_timeout(current_rod):
        # Solicitar scan de inventário
        await websocket.send_json({
            "cmd": "request_inventory_scan"
        })
```

**Tracking:**
- ✅ Timeouts consecutivos por vara
- ✅ Reset ao capturar peixe
- ✅ Trigger de limpeza por timeout
- ✅ Estatísticas de timeout

---

#### 7. **Database (SQLite)**
**Arquivo:** `server/server.py` - `DatabasePool`

```python
# Connection pool para 100+ usuários
db_pool = DatabasePool("fishing_bot.db", pool_size=20)

# Tabelas:
# - hwid_bindings: license_key, hwid, bound_at, last_seen, pc_name, login

# Operações:
# - HWID binding (anti-compartilhamento)
# - Tracking de sessões ativas
# - Estatísticas de uso (futuro)
```

**Dados armazenados:**
- ✅ HWID bindings (1 licença = 1 PC)
- ✅ Login associado à licença
- ✅ Nome do PC
- ✅ Last seen (última conexão)
- ❌ **NÃO** armazena senhas (Keymaster cuida disso)

---

### ❌ O que o Servidor NÃO FAZ

1. ❌ **Detectar templates** (cliente detecta via OpenCV)
2. ❌ **Executar ações** (cliente executa via pyautogui/Arduino)
3. ❌ **Capturar screenshots** (cliente captura)
4. ❌ **Controlar mouse/keyboard diretamente** (cliente controla)
5. ❌ **Conhecer coordenadas específicas do cliente** (cliente envia)

---

## 🔄 Fluxo de Comunicação Completo

### Exemplo: Peixe Capturado → Feeding + Cleaning

```
┌─────────── CLIENTE ───────────┐         ┌─────────── SERVIDOR ──────────┐
│                                │         │                                │
│ 1. Template Engine             │         │                                │
│    detect('catch') → FOUND     │         │                                │
│                                │         │                                │
│ 2. WebSocket Client            │─────────▶│ 3. WebSocket Handler          │
│    send_fish_caught(           │ EVENT   │    event == "fish_caught"      │
│      rod_uses=5,               │         │                                │
│      current_rod=1             │         │ 4. FishingSession              │
│    )                           │         │    increment_fish()            │
│                                │         │    fish_count = 23             │
│                                │         │                                │
│                                │         │ 5. Lógica de Decisão           │
│                                │         │    should_feed()? → YES        │
│                                │         │    should_clean()? → YES       │
│                                │         │    should_break()? → NO        │
│                                │         │                                │
│                                │         │ 6. Construir Operations        │
│                                │         │    operations = [              │
│                                │         │      {"type": "feeding"},      │
│                                │         │      {"type": "cleaning"}      │
│                                │         │    ]                           │
│                                │◀─────────│                                │
│ 7. Receber Batch               │ CMD     │ 8. Enviar Batch                │
│    cmd = "execute_batch"       │         │    send_json({                 │
│    operations = [...]          │         │      "cmd": "execute_batch",   │
│                                │         │      "operations": [...]       │
│ 9. Detection Handler           │         │    })                          │
│    • Detecta food + eat        │         │                                │
│    • send_feeding_locations()  │─────────▶│ 10. Recebe Locations          │
│                                │ EVENT   │     event = "feeding_locations"│
│                                │         │                                │
│                                │         │ 11. ActionSequenceBuilder      │
│                                │         │     build_feeding_sequence()   │
│                                │         │     → [click, wait, key...]    │
│                                │◀─────────│                                │
│ 12. Receber Sequência          │ CMD     │ 13. Enviar Sequência           │
│     cmd = "execute_sequence"   │         │     send_json({                │
│     actions = [...]            │         │       "cmd": "execute_sequence"│
│                                │         │       "actions": [50 ações]    │
│ 14. ActionExecutor             │         │     })                         │
│     execute_sequence(actions)  │         │                                │
│     • click(1306, 858)         │         │                                │
│     • wait(1.0)                │         │                                │
│     • click(1083, 373) × 2     │         │                                │
│     • key('esc')               │         │                                │
│     ...                        │         │                                │
│                                │─────────▶│ 15. Confirmar Conclusão        │
│ 16. Enviar Feedback            │ EVENT   │     event = "sequence_completed│
│     send_sequence_completed()  │         │     operation = "feeding"      │
│                                │         │                                │
│ (Repete para cleaning)         │         │                                │
│                                │         │                                │
│ 17. Enviar Batch Completed     │─────────▶│ 18. Atualizar Session          │
│     send_batch_completed([     │ EVENT   │     last_feed_at = fish_count  │
│       "feeding", "cleaning"    │         │     last_clean_at = fish_count │
│     ])                         │         │                                │
│                                │         │                                │
└────────────────────────────────┘         └────────────────────────────────┘
```

---

## 🔒 Níveis de Proteção

### **Nível 1: Licenciamento**
- ✅ Keymaster valida licenças
- ✅ HWID binding (anti-compartilhamento)
- ✅ Token-based authentication
- ✅ WebSocket persistente (validação contínua)

### **Nível 2: Lógica Protegida no Servidor**
- ✅ Regras de decisão no servidor
- ✅ Tracking de estado no servidor (fish_count, rod_uses, etc.)
- ✅ Construção de sequências no servidor
- ✅ Validação de configs no servidor

### **Nível 3: Executor Burro no Cliente**
- ✅ Cliente não conhece lógica
- ✅ Cliente não decide ações
- ✅ Cliente só executa JSON recebido
- ✅ Cliente reporta eventos ao servidor

### **Nível 4: Coordenadas do Servidor**
- ✅ Servidor envia coordenadas completas
- ✅ Cliente detecta (OpenCV) e reporta
- ✅ Servidor constrói sequências com coordenadas
- ✅ Cliente executa sem entender contexto

---

## 📊 Comparação: Local vs Servidor

| Componente | Local (Cliente) | Servidor |
|------------|----------------|----------|
| **Detecção Visual** | ✅ OpenCV | ❌ |
| **Execução de Ações** | ✅ Mouse/Keyboard | ❌ |
| **Regras de Decisão** | ❌ | ✅ Protegidas |
| **Fish Count** | ❌ | ✅ Tracking |
| **Rod Tracking** | ❌ | ✅ 6 varas |
| **Timeout Tracking** | ❌ | ✅ Por vara |
| **Construção de Sequências** | ❌ | ✅ JSON completo |
| **Coordenadas** | ✅ Detecta | ✅ Constrói |
| **Validação de Configs** | ❌ | ✅ Anti-exploit |
| **Licenciamento** | ✅ HWID | ✅ Keymaster |
| **Database** | ❌ | ✅ SQLite Pool |
| **WebSocket** | ✅ Cliente | ✅ Servidor |

---

## 🎯 Vantagens da Arquitetura

### **Segurança**
1. ✅ Lógica protegida no servidor (anti-reverse engineering)
2. ✅ Cliente não conhece regras de negócio
3. ✅ HWID binding (anti-compartilhamento)
4. ✅ Validação server-side (anti-exploit)

### **Controle**
1. ✅ Atualizações centralizadas (sem recompilação)
2. ✅ A/B testing de regras
3. ✅ Ajustes de balanceamento em tempo real
4. ✅ Ban/suspensão remota

### **Escalabilidade**
1. ✅ Servidor FastAPI + Uvicorn
2. ✅ Connection pool SQLite (20 conexões)
3. ✅ WebSocket assíncrono
4. ✅ Suporta 100+ usuários simultâneos

### **Manutenibilidade**
1. ✅ Separação clara de responsabilidades
2. ✅ Cliente simples (só detecção + execução)
3. ✅ Servidor centralizado (toda lógica)
4. ✅ Debug facilitado (logs centralizados)

---

## 📈 Estatísticas de Distribuição

### **Cliente (Local)**
- **Detecção:** 100% (OpenCV)
- **Execução:** 100% (Input)
- **Lógica:** 0%
- **Decisões:** 0%

### **Servidor (Remoto)**
- **Detecção:** 0%
- **Execução:** 0%
- **Lógica:** 100%
- **Decisões:** 100%

---

## 🚀 Tecnologias Utilizadas

### **Cliente**
- Python 3.13+
- OpenCV (template matching)
- MSS (screenshot)
- PyAutoGUI (input fallback)
- Keyboard (teclas)
- WebSockets (websockets lib)
- Tkinter (UI)
- psutil (HWID)
- requests (HTTP API)

### **Servidor**
- Python 3.10+
- FastAPI (framework)
- Uvicorn (ASGI server)
- SQLite (database)
- WebSockets (async)
- Pydantic (validação)
- Requests (Keymaster)

---

## 📝 Resumo Final

O v5 implementa uma **arquitetura cliente-servidor autoritativa híbrida**, onde:

1. **Cliente é "burro":**
   - Detecta elementos visuais (OpenCV)
   - Executa ações mecânicas (mouse/keyboard)
   - Reporta eventos ao servidor
   - **NÃO** toma decisões

2. **Servidor é "inteligente":**
   - Detém toda lógica de negócio
   - Decide quando executar operações
   - Constrói sequências completas
   - Valida e protege contra exploits

3. **Comunicação via WebSocket:**
   - Cliente envia: eventos (fish_caught, timeout, detections)
   - Servidor envia: comandos (feed, clean, execute_sequence)
   - Fluxo bidirecional em tempo real
   - Autenticação com token + HWID

4. **Proteção em múltiplos níveis:**
   - Licenciamento (Keymaster + HWID)
   - Lógica server-side (anti-reverse)
   - Executor burro client-side
   - Validação de configs (anti-exploit)

Essa arquitetura maximiza **segurança**, **controle** e **escalabilidade**, enquanto mantém o cliente simples e responsivo.
