# 🌐 Arquitetura Multi-Usuário - Servidor Centralizado

## 📋 Visão Geral

Sistema de pesca automatizado com arquitetura cliente-servidor onde:
- **CLIENTE** = Executor burro (apenas executa sequências JSON)
- **SERVIDOR** = Cérebro (contém TODA lógica de negócio)

### Princípios Fundamentais

1. **Cliente NÃO decide** - apenas detecta e reporta
2. **Servidor DECIDE** - processa regras e envia sequências completas
3. **Detecção Local** - templates detectados no cliente (latência zero)
4. **Execução Local** - sequências executadas no cliente (latência zero)
5. **Lógica Centralizada** - regras de negócio APENAS no servidor

---

## 🏗️ Componentes da Arquitetura

### Cliente (`client/`)

#### 1. **DetectionHandler** (`detection_handler.py`)
Responsável por detectar templates e reportar coordenadas.

**NÃO SABE:**
- O que fazer com as coordenadas
- Quando executar operações
- Sequências de ações

**APENAS SABE:**
- Detectar templates (filefrito, eat, peixes, varas)
- Aplicar NMS (Non-Maximum Suppression)
- Retornar coordenadas

**Métodos:**
```python
detect_food_and_eat() -> {"food_location": {x, y}, "eat_location": {x, y}}
scan_inventory() -> {"fish_locations": [{x, y}, ...]}
analyze_rod_slots() -> {"rod_status": {...}, "available_items": {...}}
```

#### 2. **ActionExecutor** (`action_executor.py`)
Executor genérico de sequências JSON.

**NÃO SABE:**
- Onde clicar (coordenadas vêm do servidor)
- Quando fazer (decisão do servidor)
- O que está fazendo (apenas executa lista)

**APENAS SABE:**
- Como executar ações atômicas (click, key, wait, drag, template)

**Tipos de Ação Suportados:**
```python
{"type": "click", "x": 100, "y": 200}
{"type": "click_right", "x": 100, "y": 200}
{"type": "wait", "duration": 1.5}
{"type": "key", "key": "esc"}
{"type": "key_down", "key": "alt"}
{"type": "key_up", "key": "alt"}
{"type": "move_camera", "dx": 1200, "dy": -200}
{"type": "drag", "from_x": 100, "from_y": 200, "to_x": 300, "to_y": 400}
{"type": "template_detect", "name": "filefrito", "confidence": 0.75}
{"type": "click_detected"}  # Clica na última detecção
{"type": "stop_continuous_clicking"}
{"type": "stop_camera_movement"}
```

#### 3. **WebSocketClient** (`ws_client.py`)
Comunicação bidirecional cliente↔servidor.

**Eventos Enviados (Cliente → Servidor):**
```python
send_fish_caught(rod_uses, current_rod)
send_feeding_locations_detected(food_location, eat_location)
send_fish_locations_detected(fish_locations)
send_rod_status_detected(rod_status, available_items)
send_sequence_completed(operation)
send_sequence_failed(operation, step_index, error)
send_timeout(current_rod)
```

**Comandos Recebidos (Servidor → Cliente):**
```python
request_template_detection  # Solicita detecção de templates
request_inventory_scan      # Solicita scan de inventário
request_rod_analysis        # Solicita análise de varas
execute_sequence            # Executa sequência JSON
break                       # Pausa o bot
```

---

### Servidor (`server/`)

#### 1. **ActionSequenceBuilder** (`action_sequences.py`)
Construtor de sequências completas de ações.

**RESPONSABILIDADE:**
- Contém TODA lógica de operações de baú
- Constrói sequências JSON atômicas
- Usa coordenadas do cliente + configs do usuário

**Métodos:**
```python
build_feeding_sequence(food_location, eat_location) -> List[Dict]
build_cleaning_sequence(fish_locations) -> List[Dict]
build_maintenance_sequence(rod_status, available_items) -> List[Dict]
build_rod_switch_sequence(target_rod) -> List[Dict]
```

**Exemplo de Sequência Gerada:**
```python
[
    {"type": "stop_continuous_clicking"},
    {"type": "key_down", "key": "alt"},
    {"type": "move_camera", "dx": -1200, "dy": -200},
    {"type": "key_press", "key": "e"},
    {"type": "wait", "duration": 1.5},
    {"type": "click", "x": 1306, "y": 858},  # Comida
    {"type": "wait", "duration": 0.8},
    {"type": "click", "x": 1083, "y": 373, "repeat": 5},  # Eat button
    {"type": "key_press", "key": "esc"},
    {"type": "key_up", "key": "alt"}
]
```

#### 2. **Servidor WebSocket** (`server.py`)
Gerencia sessões de usuários e decisões de lógica de negócio.

**Event Handlers:**
```python
fish_caught → Incrementa contador → Decide operações → Envia comandos
feeding_locations_detected → Constrói sequência → Envia execute_sequence
fish_locations_detected → Constrói sequência → Envia execute_sequence
rod_status_detected → Constrói sequência → Envia execute_sequence
sequence_completed → Atualiza contadores de sessão
sequence_failed → Log de erro
timeout → Incrementa timeout da vara → Decide manutenção
```

---

## 🔄 Fluxo Completo de Operações

### Exemplo 1: Feeding (Alimentação)

```
┌─────────────────────────────────────────────────────────────┐
│ CLIENTE                                                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Detecta peixe capturado (catch.png)                      │
│ 2. Incrementa contador local                                │
│ 3. Envia: send_fish_caught(rod_uses=5, current_rod=1)      │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR                                                    │
├─────────────────────────────────────────────────────────────┤
│ 4. Recebe fish_caught                                       │
│ 5. Incrementa session.fish_count                            │
│ 6. Verifica: session.should_feed() → True (a cada 2 peixes)│
│ 7. Envia: request_template_detection(["filefrito", "eat"]) │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ CLIENTE                                                     │
├─────────────────────────────────────────────────────────────┤
│ 8. Recebe request_template_detection                        │
│ 9. DetectionHandler.detect_food_and_eat()                   │
│ 10. Encontra: filefrito em (1306, 858)                      │
│              eat em (1083, 373)                             │
│ 11. Envia: send_feeding_locations_detected(...)            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR                                                    │
├─────────────────────────────────────────────────────────────┤
│ 12. Recebe feeding_locations_detected                       │
│ 13. builder = ActionSequenceBuilder(user_config)            │
│ 14. sequence = builder.build_feeding_sequence(...)          │
│ 15. Envia: execute_sequence(actions=sequence, op="feeding") │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ CLIENTE                                                     │
├─────────────────────────────────────────────────────────────┤
│ 16. Recebe execute_sequence                                 │
│ 17. ActionExecutor.execute_sequence(actions)                │
│ 18. Para cliques contínuos                                  │
│ 19. Abre baú (ALT + movimento + E)                          │
│ 20. Clica na comida                                         │
│ 21. Clica em "eat" 5 vezes                                  │
│ 22. Fecha baú (ESC)                                         │
│ 23. Envia: send_sequence_completed("feeding")              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVIDOR                                                    │
├─────────────────────────────────────────────────────────────┤
│ 24. Recebe sequence_completed                               │
│ 25. Atualiza: session.last_feed_at = session.fish_count     │
│ 26. LOG: "Feeding concluído com sucesso"                    │
└─────────────────────────────────────────────────────────────┘
```

### Exemplo 2: Cleaning (Limpeza de Inventário)

```
CLIENTE: send_fish_caught()
    ↓
SERVIDOR: should_clean() → True
    ↓
SERVIDOR: send request_inventory_scan
    ↓
CLIENTE: DetectionHandler.scan_inventory()
         Detecta: 15 peixes em diferentes posições
         Aplica NMS (remove duplicatas)
         send_fish_locations_detected([{x,y}, {x,y}, ...])
    ↓
SERVIDOR: ActionSequenceBuilder.build_cleaning_sequence()
          Gera: 15 right-clicks + arrastar para baú
          send execute_sequence(cleaning)
    ↓
CLIENTE: ActionExecutor.execute_sequence()
         Abre baú
         Para cada peixe: right-click + drag para chest_area
         Fecha baú
         send_sequence_completed("cleaning")
    ↓
SERVIDOR: session.last_clean_at = fish_count
```

### Exemplo 3: Rod Maintenance (Manutenção de Varas)

```
CLIENTE: Timeout detectado (122s sem peixe)
         send_timeout(current_rod=1)
    ↓
SERVIDOR: session.increment_timeout(rod=1)
          Timeout count = 3 (limite atingido)
          send request_rod_analysis
    ↓
CLIENTE: DetectionHandler.analyze_rod_slots()
         Detecta: Slot 1: QUEBRADA
                 Slot 2: SEM_ISCA
                 Baú: 5 varas disponíveis, 10 iscas
         send_rod_status_detected(...)
    ↓
SERVIDOR: ActionSequenceBuilder.build_maintenance_sequence()
          Decide: Substituir vara quebrada (slot 1)
                 Adicionar isca (slot 2)
          Gera sequência completa
          send execute_sequence(maintenance)
    ↓
CLIENTE: ActionExecutor.execute_sequence()
         Abre baú
         Arrasta vara nova para slot 1
         Arrasta isca para slot 2
         Fecha baú
         send_sequence_completed("maintenance")
    ↓
SERVIDOR: session.reset_timeout(rod=1)
```

---

## 🔀 Modo Offline (Fallback)

Quando servidor não está disponível ou desconectado:

```python
# fishing_engine.py - increment_fish_count()

if self.ws_client and self.ws_client.is_connected():
    # MODO ONLINE: Envia ao servidor
    self.ws_client.send_fish_caught(...)
else:
    # MODO OFFLINE: Usa lógica local
    self.feeding_system.increment_fish_count()
    self.inventory_manager.increment_fish_count()
    self.rod_manager.increment_fish_count(current_rod)
    # Os managers executam suas próprias lógicas localmente
```

**Offline Mode:**
- Cliente usa `feeding_system`, `inventory_manager`, `rod_manager` localmente
- Não envia eventos ao servidor
- Não espera comandos do servidor
- 100% funcional sem servidor

---

## 📊 Prioridades de Operações

### No Servidor (`server.py` - fish_caught handler)

```python
# Ordem de prioridades (executadas em sequência)
1. switch_rod_pair   # Trocar par de varas (se ambas esgotadas)
2. feeding           # Alimentar (a cada N peixes)
3. cleaning          # Limpar (a cada N peixes)
4. break             # Pausar (a cada N peixes ou tempo)
5. adjust_timing     # Randomizar timing (5% chance - anti-ban)
```

### No Cliente (Execução)

Todas operações de baú são **coordenadas** para evitar conflitos:
- Apenas UMA operação de baú por vez
- Agrupamento de 2 segundos (batch operations)
- Prioridade: feeding > maintenance > cleaning

---

## 🧪 Testing Checklist

### Teste 1: Feeding Online
1. Conectar ao servidor
2. Pescar 2 peixes
3. Verificar:
   - [ ] Cliente envia fish_caught
   - [ ] Servidor envia request_template_detection
   - [ ] Cliente detecta comida e eat
   - [ ] Servidor envia execute_sequence
   - [ ] Cliente executa feeding
   - [ ] Cliente envia sequence_completed

### Teste 2: Cleaning Online
1. Conectar ao servidor
2. Pescar 1 peixe
3. Verificar:
   - [ ] Servidor envia request_inventory_scan
   - [ ] Cliente detecta peixes
   - [ ] Servidor envia execute_sequence (cleaning)
   - [ ] Cliente limpa inventário
   - [ ] sequence_completed enviado

### Teste 3: Offline Mode
1. Iniciar sem servidor
2. Pescar 3 peixes
3. Verificar:
   - [ ] Feeding executado localmente
   - [ ] Cleaning executado localmente
   - [ ] Logs mostram "modo offline"

### Teste 4: Múltiplos Clientes
1. Conectar 3 clientes simultaneamente
2. Pescar em paralelo
3. Verificar:
   - [ ] Cada cliente tem sessão isolada
   - [ ] Contadores independentes
   - [ ] Sem conflitos de comandos

---

## 📝 Configurações Sincronizadas

### Cliente → Servidor (na conexão)

```python
# client/server_connector.py - _sync_config_with_server()

server_config = {
    "feed_interval_fish": 2,           # Alimentar a cada 2 peixes
    "clean_interval_fish": 1,          # Limpar a cada 1 peixe
    "rod_switch_limit": 20,            # Trocar vara após 20 usos
    "break_interval_fish": 50,         # Break a cada 50 peixes
    "break_duration_minutes": 45,      # Duração do break
    "maintenance_timeout": 3,          # Limite de timeouts
    "chest_side": "left",              # Lado do baú
    "chest_distance": 1200,            # Distância para abrir
    "chest_vertical_offset": 200,      # Offset vertical
    "slot_positions": {...},           # Posições dos slots de vara
    "inventory_area": [...],           # Área de scan do inventário
    "chest_area": [...],               # Área de scan do baú
    "bait_priority": [...],            # Prioridade de iscas
    "feeds_per_session": 2             # Quantas vezes comer
}

ws_client.send_config_sync(server_config)
```

---

## 🚀 Performance

### Latência Esperada

- **Detecção de Template:** <50ms (local)
- **Envio ao Servidor:** <100ms (WebSocket)
- **Construção de Sequência:** <10ms (servidor)
- **Execução de Sequência:** Depende da sequência (3-15s típico)

### Escalabilidade

**Servidor pode suportar 100+ clientes simultâneos:**
- 3.3 operações/segundo TOTAL (0.033 ops/s por cliente)
- <1% CPU por cliente
- ~10MB RAM por sessão

---

## 🔒 Segurança e Validação

### Servidor Valida

1. **Licença Keymaster** - Toda conexão validada com Keymaster
2. **HWID Binding** - Anti-compartilhamento de licença
3. **Session Token** - JWT token por sessão
4. **Heartbeat** - Validação contínua (a cada 30s)

### Cliente Nunca

- Não toma decisões de lógica de negócio
- Não pode burlar regras do servidor
- Não compartilha dados entre sessões

---

## 📚 Arquivos Importantes

### Cliente
```
client/
├── detection_handler.py       # Detecções de templates
├── action_executor.py         # Executor de sequências
├── ws_client.py               # Cliente WebSocket
└── server_connector.py        # Conexão e callbacks
```

### Servidor
```
server/
├── action_sequences.py        # Construtor de sequências
├── server.py                  # WebSocket server + lógica
└── session.py                 # Gerenciamento de sessões
```

### Core
```
core/
└── fishing_engine.py          # Motor principal
    ├── handle_server_command()    # Handler de comandos
    └── increment_fish_count()     # Online/offline mode
```

---

## 🎯 Próximos Passos

1. ✅ Implementação completa (DONE)
2. ⏳ Testes end-to-end
3. ⏳ Deploy do servidor em produção
4. ⏳ Teste com múltiplos usuários reais

---

## 🐛 Debugging

### Cliente
```bash
# Ver logs de detecção
tail -f data/logs/fishing_bot_*.log | grep "🔍"

# Ver logs de execução
tail -f data/logs/fishing_bot_*.log | grep "⚡"

# Ver logs de WebSocket
tail -f data/logs/fishing_bot_*.log | grep "🌐"
```

### Servidor
```bash
# Ver eventos recebidos
tail -f logs/server.log | grep "EVENTO"

# Ver sequências enviadas
tail -f logs/server.log | grep "Sequência"

# Ver erros
tail -f logs/server.log | grep "❌"
```

---

**Última Atualização:** 2025-10-29
**Versão:** v5.0 (Multi-User Architecture)
