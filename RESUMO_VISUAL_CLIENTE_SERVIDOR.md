# 🎯 Resumo Visual: O que está Onde?

## 📊 Divisão Simples

```
╔════════════════════════════════════════════════════════════════╗
║                     🖥️  CLIENTE (LOCAL)                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  👁️  OLHOS (Detecção)                                          ║
║  ├─ Template matching com OpenCV                               ║
║  ├─ Detecta: peixes, iscas, varas, comida                      ║
║  ├─ Retorna: coordenadas (x, y)                                ║
║  └─ NÃO decide o que fazer                                     ║
║                                                                 ║
║  🤖 MÃOS (Execução)                                             ║
║  ├─ Mouse/Keyboard (PyAutoGUI ou Arduino)                      ║
║  ├─ Executa: click, drag, key press, wait                      ║
║  ├─ Recebe: lista JSON de ações do servidor                    ║
║  └─ NÃO sabe o que está fazendo                                ║
║                                                                 ║
║  📡 COMUNICAÇÃO                                                 ║
║  ├─ Envia: "peguei peixe!", "timeout!", "achei comida aqui"    ║
║  ├─ Recebe: "execute isso", "agora faça aquilo"                ║
║  └─ WebSocket (conexão persistente)                            ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
                              ↕️
                      INTERNET (WSS)
                              ↕️
╔════════════════════════════════════════════════════════════════╗
║                    🌐 SERVIDOR (REMOTO)                         ║
╠════════════════════════════════════════════════════════════════╣
║                                                                 ║
║  🧠 CÉREBRO (Decisões)                                          ║
║  ├─ Sabe: quando alimentar, quando limpar, quando trocar vara  ║
║  ├─ Tracking: fish_count, rod_uses, timeouts                   ║
║  ├─ Regras: a cada 2 peixes → feed, a cada 1 peixe → clean    ║
║  └─ Prioridades: feed > maintenance > clean > break            ║
║                                                                 ║
║  🏗️  CONSTRUTOR (Sequências)                                   ║
║  ├─ Cria: listas completas de ações (50+ ações por operação)   ║
║  ├─ Inclui: coordenadas, timings, sequências                   ║
║  ├─ Exemplo: [stop_fish, open_chest, click(x,y), wait(1.5),...]║
║  └─ Cliente executa cegamente                                   ║
║                                                                 ║
║  🔒 SEGURANÇA                                                   ║
║  ├─ Licenças (Keymaster)                                        ║
║  ├─ HWID binding (1 PC por licença)                            ║
║  ├─ Validação de configs (anti-exploit)                         ║
║  └─ Database (SQLite)                                           ║
║                                                                 ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🎬 Exemplo Prático: Capturar Peixe

### O que acontece quando você pesca um peixe:

```
1️⃣  CLIENTE detecta template 'catch'
    ├─ OpenCV: matchTemplate() → FOUND at (x, y)
    └─ ✅ CLIENTE FAZ: Detectar visualmente

2️⃣  CLIENTE envia evento ao servidor
    ├─ ws_client.send_fish_caught(rod_uses=5, current_rod=1)
    └─ ✅ CLIENTE FAZ: Reportar evento

3️⃣  SERVIDOR recebe e atualiza estado
    ├─ session.fish_count = 23
    ├─ session.rod_uses[1] = 6
    └─ ✅ SERVIDOR FAZ: Tracking de estado

4️⃣  SERVIDOR decide ações necessárias
    ├─ should_feed()? → SIM (23 - 21 = 2 peixes desde último)
    ├─ should_clean()? → SIM (23 - 22 = 1 peixe desde último)
    ├─ should_break()? → NÃO (ainda faltam 27 peixes)
    └─ ✅ SERVIDOR FAZ: Lógica de decisão

5️⃣  SERVIDOR constrói batch de operações
    ├─ operations = ["feeding", "cleaning", "switch_rod"]
    └─ ✅ SERVIDOR FAZ: Definir prioridades

6️⃣  CLIENTE detecta elementos necessários
    ├─ Detecta comida em (1306, 858)
    ├─ Detecta botão "eat" em (1083, 373)
    ├─ Envia coordenadas ao servidor
    └─ ✅ CLIENTE FAZ: Detecção de coordenadas

7️⃣  SERVIDOR constrói sequência completa
    ├─ ActionSequenceBuilder.build_feeding_sequence()
    ├─ Cria lista de 50+ ações:
    │   [
    │     {"type": "stop_continuous_clicking"},
    │     {"type": "key_down", "key": "alt"},
    │     {"type": "wait", "duration": 0.8},
    │     {"type": "move_camera", "dx": 1200, "dy": 200},
    │     {"type": "key_press", "key": "e"},
    │     {"type": "wait", "duration": 1.5},
    │     {"type": "click", "x": 1306, "y": 858},
    │     {"type": "wait", "duration": 1.0},
    │     {"type": "click", "x": 1083, "y": 373},  # Comer 1
    │     {"type": "wait", "duration": 1.5},
    │     {"type": "click", "x": 1083, "y": 373},  # Comer 2
    │     {"type": "wait", "duration": 1.5},
    │     {"type": "key_up", "key": "alt"},
    │     {"type": "key_press", "key": "tab"},
    │     ...
    │   ]
    └─ ✅ SERVIDOR FAZ: Construir sequência

8️⃣  CLIENTE executa sequência cegamente
    ├─ ActionExecutor.execute_sequence(actions)
    ├─ Para cada ação: executa sem entender contexto
    └─ ✅ CLIENTE FAZ: Execução mecânica

9️⃣  CLIENTE confirma conclusão
    ├─ ws_client.send_sequence_completed("feeding")
    └─ ✅ CLIENTE FAZ: Feedback ao servidor

🔟 SERVIDOR atualiza trackers
    ├─ session.last_feed_at = 23
    ├─ session.last_clean_at = 23
    └─ ✅ SERVIDOR FAZ: Atualizar estado
```

---

## 🔍 O que cada um SABE

### 👁️ Cliente SABE:
- ✅ Como detectar templates (OpenCV)
- ✅ Como clicar em coordenadas
- ✅ Como pressionar teclas
- ✅ Como arrastar itens
- ✅ Onde estão os elementos na tela (após detectar)

### ❌ Cliente NÃO SABE:
- ❌ Quando alimentar (servidor decide)
- ❌ Quando limpar (servidor decide)
- ❌ Quando trocar vara (servidor decide)
- ❌ Quantos peixes foram capturados (servidor tracking)
- ❌ Qual vara usar (servidor tracking)
- ❌ Se deve pausar (servidor decide)

### 🧠 Servidor SABE:
- ✅ Quantos peixes foram capturados (fish_count)
- ✅ Quantas vezes cada vara foi usada (rod_uses)
- ✅ Quando alimentar (regra: a cada N peixes)
- ✅ Quando limpar (regra: a cada N peixes ou timeouts)
- ✅ Quando trocar vara (regra: após N usos)
- ✅ Quando pausar (regra: a cada N peixes ou tempo)
- ✅ Como construir sequências completas
- ✅ Prioridades de operações

### ❌ Servidor NÃO SABE:
- ❌ Onde estão os elementos na tela (cliente detecta)
- ❌ Como executar ações no PC (cliente executa)
- ❌ Coordenadas específicas do usuário (cliente envia)

---

## 📁 Principais Arquivos

### 🖥️ CLIENTE

| Arquivo | Responsabilidade |
|---------|------------------|
| `core/template_engine.py` | 👁️ Detectar templates (OpenCV) |
| `client/action_executor.py` | 🤖 Executar sequências JSON |
| `client/ws_client.py` | 📡 Comunicação WebSocket |
| `core/fishing_engine.py` | 🎣 Ciclo de pesca (cast → click → A/D) |
| `core/input_manager.py` | ⌨️ Controle mouse/keyboard |
| `utils/license_manager.py` | 🔐 Validação de licença + HWID |
| `ui/main_window.py` | 🎨 Interface gráfica (configs) |
| `data/config.json` | ⚙️ Coordenadas + configurações locais |

### 🌐 SERVIDOR

| Arquivo | Responsabilidade |
|---------|------------------|
| `server/server.py` | 🏢 FastAPI server + WebSocket |
| `server/server.py (FishingSession)` | 🧠 Lógica de decisão |
| `server/action_sequences.py` | 🏗️ Construtor de sequências |
| `server/fishing_bot.db` | 💾 Database SQLite (HWID bindings) |

---

## 💬 Mensagens Trocadas

### 📤 Cliente → Servidor (Eventos)

```json
{
  "event": "fish_caught",
  "data": {
    "fish_count": 23,
    "rod_uses": 5,
    "current_rod": 1,
    "timestamp": "2025-10-29T14:32:15"
  }
}
```

```json
{
  "event": "timeout",
  "data": {
    "current_rod": 1
  }
}
```

```json
{
  "event": "feeding_locations_detected",
  "data": {
    "food_location": {"x": 1306, "y": 858},
    "eat_location": {"x": 1083, "y": 373}
  }
}
```

```json
{
  "event": "sync_config",
  "data": {
    "feed_interval_fish": 2,
    "clean_interval_fish": 1,
    "rod_switch_limit": 20,
    "maintenance_timeout": 3
  }
}
```

### 📥 Servidor → Cliente (Comandos)

```json
{
  "cmd": "execute_batch",
  "operations": [
    {"type": "feeding", "params": {...}},
    {"type": "cleaning", "params": {...}},
    {"type": "switch_rod", "params": {...}}
  ]
}
```

```json
{
  "cmd": "execute_sequence",
  "actions": [
    {"type": "stop_continuous_clicking"},
    {"type": "key_down", "key": "alt"},
    {"type": "wait", "duration": 0.8},
    {"type": "move_camera", "dx": 1200, "dy": 200},
    {"type": "key_press", "key": "e"},
    {"type": "wait", "duration": 1.5},
    {"type": "click", "x": 1306, "y": 858},
    ...
  ],
  "operation": "feeding"
}
```

```json
{
  "cmd": "request_inventory_scan"
}
```

---

## 🔒 Níveis de Segurança

### Nível 1: Autenticação
```
Cliente → Servidor: login + password + license_key + HWID
Servidor → Keymaster: validate(license_key, HWID)
Keymaster → Servidor: ✅ válida / ❌ inválida
Servidor → Cliente: token (se válida)
```

### Nível 2: HWID Binding
```
Servidor verifica:
- License já vinculada a um HWID?
  - SIM: HWID == atual? → ✅ permitir / ❌ bloquear
  - NÃO: Vincular agora
```

### Nível 3: Lógica Protegida
```
Cliente NÃO tem:
- Regras de quando alimentar
- Regras de quando limpar
- Regras de quando trocar vara
- Tracking de fish_count
- Construção de sequências

Servidor TEM tudo!
```

### Nível 4: Validação de Configs
```
Cliente envia: feed_interval_fish = 999999
Servidor valida: range (1, 100)
Servidor aplica: feed_interval_fish = 100 (max)
```

---

## 📊 Estatísticas

### Distribuição de Código

```
CLIENTE (LOCAL)
├─ Detecção: 100%
├─ Execução: 100%
├─ Lógica: 0%
└─ Decisões: 0%

SERVIDOR (REMOTO)
├─ Detecção: 0%
├─ Execução: 0%
├─ Lógica: 100%
└─ Decisões: 100%
```

### Tráfego de Rede

```
Por Peixe Capturado:
├─ Cliente → Servidor: ~200 bytes (fish_caught event)
├─ Servidor → Cliente: ~5 KB (sequências, se necessário)
└─ Total: ~5.2 KB por peixe

Por Hora (60 peixes/hora):
├─ Upload: ~12 KB
├─ Download: ~300 KB
└─ Total: ~312 KB/hora
```

---

## 🎯 Conclusão

### Cliente = Olhos + Mãos (Burro)
- Vê onde estão as coisas
- Executa o que mandam
- Reporta eventos
- **Não pensa**

### Servidor = Cérebro (Inteligente)
- Decide quando fazer
- Constrói sequências completas
- Valida e protege
- **Controla tudo**

### Comunicação = WebSocket (Tempo Real)
- Cliente envia eventos
- Servidor envia comandos
- Bidirecional e persistente
- Autenticado e seguro

---

## 🚀 Vantagens

1. ✅ **Segurança:** Lógica protegida no servidor
2. ✅ **Controle:** Atualizações sem recompilar cliente
3. ✅ **Escalabilidade:** 100+ usuários simultâneos
4. ✅ **Anti-pirataria:** HWID binding + validação contínua
5. ✅ **Anti-exploit:** Validação server-side de configs
6. ✅ **Manutenibilidade:** Cliente simples, servidor centralizado
