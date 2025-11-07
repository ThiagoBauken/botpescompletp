# 📁 O Que É a Pasta `client/`?

## 🎯 Resumo Executivo

A pasta `client/` contém o **novo sistema de cliente-servidor** (v5) que permite:
- **Múltiplos bots** conectados a um servidor central
- **Controle remoto** via WebSocket
- **Arduino remoto** para anti-detecção avançada
- **Autenticação** com login/senha/license key

---

## 🔄 Evolução do Projeto

### v3 e v4: Bot Standalone (Tradicional)

```
┌─────────────────────┐
│   Fishing Bot v3/v4  │
│                     │
│  ┌───────────────┐  │
│  │ Template Eng. │  │
│  │ Input Manager │  │
│  │ Fishing Eng.  │  │
│  │ UI (GUI)      │  │
│  └───────────────┘  │
│                     │
│  Tudo em 1 PC       │
└─────────────────────┘
```

**Características:**
- ✅ Simples e funcional
- ✅ Não precisa de servidor
- ❌ Um bot por PC
- ❌ Sem controle remoto
- ❌ Detecção de input pelo jogo

---

### v5: Sistema Cliente-Servidor (NOVO)

```
┌──────────────────┐         WebSocket        ┌──────────────────┐
│   Fishing Bot    │◄─────────────────────────►│  Servidor        │
│   (Client)       │     wss://servidor.com    │  (Cerebro)       │
│                  │                            │                  │
│  ┌────────────┐  │                            │  ┌────────────┐  │
│  │ Template   │  │                            │  │ Gerencia   │  │
│  │ Detection  │  │    📤 Envia comandos       │  │ N clientes │  │
│  │            │  │    📥 Recebe ações         │  │            │  │
│  └────────────┘  │                            │  │ Orquestra  │  │
│                  │                            │  │ bots       │  │
│  ┌────────────┐  │                            │  │            │  │
│  │ Arduino    │  │                            │  │ Salva logs │  │
│  │ USB HID    │  │                            │  │ Analytics  │  │
│  └────────────┘  │                            │  └────────────┘  │
│                  │                            │                  │
│  Input via       │                            │  Multi-usuário   │
│  Arduino físico  │                            │  Multi-bot       │
└──────────────────┘                            └──────────────────┘
         ▲                                               ▲
         │                                               │
         └───────────── 100% indetectável ───────────────┘
         (Arduino = hardware USB real)
```

**Características:**
- ✅ **Múltiplos bots** em múltiplos PCs
- ✅ **Controle centralizado** via servidor
- ✅ **Arduino físico** = inputs 100% naturais
- ✅ **Dashboard web** para monitorar tudo
- ✅ **Login/senha** para segurança
- ⚠️ Mais complexo de configurar

---

## 📂 Arquivos da Pasta `client/`

### 1. **activation_dialog.py** (🔐 Login)
```python
# Diálogo de autenticação
# Campos:
# - Login (email/username)
# - Senha (opcional)
# - License Key (Keymaster)
# - Checkbox: Manter conectado
```

**Função:** Tela de login para conectar ao servidor multi-usuário.

**Quando aparece:**
- Primeira conexão ao servidor
- Quando `data/credentials.json` não existe
- Após licença válida

---

### 2. **credential_manager.py** (💾 Salvar Credenciais)
```python
# Gerencia credenciais locais
# Salva em: data/credentials.json
# Criptografa senha localmente
```

**Função:** Salva login/senha/license_key para auto-login.

**Arquivo gerado:** `data/credentials.json`

---

### 3. **ws_client.py** (🌐 WebSocket)
```python
# Cliente WebSocket assíncrono
# Conecta ao servidor via wss://
# Mantém conexão persistente
# Auto-reconecta em caso de queda
```

**Função:** Comunicação bidirecional com servidor.

**Protocolo:**
```json
// Cliente envia:
{
  "type": "status",
  "data": {
    "fishing_active": true,
    "fish_count": 42,
    "rod_durability": 80
  }
}

// Servidor envia:
{
  "type": "command",
  "command": "start_fishing",
  "params": {}
}
```

---

### 4. **server_connector.py** (🔗 Conexão)
```python
# Camada de abstração sobre ws_client
# Gerencia autenticação
# Registra callbacks
# Trata erros de conexão
```

**Função:** Facilita uso do WebSocket no main.py

**Exemplo de uso:**
```python
from client.server_connector import connect_to_server

ws_client = connect_to_server(
    server_url="wss://servidor.com/ws",
    login="user@email.com",
    password="senha123",
    license_key="XXXX-YYYY-ZZZZ"
)
```

---

### 5. **action_executor.py** (⚡ Executor)
```python
# Executa comandos recebidos do servidor
# Mapeia comandos → ações do bot
# Exemplos:
#   "start_fishing" → fishing_engine.start()
#   "stop_fishing"  → fishing_engine.stop()
#   "feed"          → feeding_system.feed_now()
```

**Função:** Traduz comandos do servidor em ações do bot.

**Fluxo:**
```
Servidor envia: {"command": "start_fishing"}
       ↓
action_executor recebe
       ↓
Chama: fishing_engine.start_fishing()
       ↓
Bot começa a pescar
       ↓
Cliente envia status atualizado ao servidor
```

---

### 6. **arduino_command_executor.py** (🔌 Arduino)
```python
# Executa comandos via Arduino USB
# Envia inputs físicos (mouse/teclado)
# 100% indetectável (hardware real)
```

**Função:** Envia comandos para Arduino Leonardo/Pro Micro via USB.

**Protocolo Serial:**
```
MOVE:100:200       → Move mouse para (100, 200)
CLICK:1            → Clique esquerdo
PRESS:F9           → Pressiona F9
TYPE:hello         → Digita "hello"
```

**Hardware necessário:**
- Arduino Leonardo ou Pro Micro
- Firmware HID (Mouse+Keyboard)
- Porta COM configurada

---

## 🔄 Fluxo Completo: Bot Standalone vs Cliente-Servidor

### Modo Standalone (v3/v4 - SEM pasta `client/`)

```
1. Usuario pressiona F9
2. HotkeyManager captura
3. FishingEngine inicia
4. InputManager clica (pyautogui)
5. TemplateEngine detecta peixe
6. Loop continua...
```

**Detecção de input:** Jogo pode detectar pyautogui/pynput (software).

---

### Modo Cliente-Servidor (v5 - COM pasta `client/`)

```
1. Usuario pressiona F9 na GUI
   ↓
2. main.py envia comando ao servidor via ws_client
   {
     "type": "command",
     "command": "start_fishing"
   }
   ↓
3. Servidor valida e retorna confirmação
   ↓
4. server_connector registra callback
   ↓
5. action_executor executa localmente:
   fishing_engine.start_fishing()
   ↓
6. InputManager clica via ARDUINO (arduino_command_executor)
   Serial: "CLICK:1" → Arduino emula clique FÍSICO
   ↓
7. TemplateEngine detecta peixe
   ↓
8. Cliente envia status ao servidor:
   {
     "type": "status",
     "fish_count": 1
   }
   ↓
9. Servidor salva em banco de dados
10. Dashboard web atualiza em tempo real
```

**Detecção de input:** Impossível detectar (Arduino = hardware USB HID real).

---

## ❓ FAQ

### Q: Preciso da pasta `client/` para o bot funcionar?
**A:** NÃO. O bot funciona standalone sem `client/`. A pasta `client/` é apenas para o modo servidor avançado.

### Q: O que acontece se eu deletar `client/`?
**A:** Bot funciona normalmente em modo standalone (v3/v4). Você perde:
- Controle remoto
- Arduino HID
- Multi-bot
- Dashboard web

### Q: Como ativar o modo cliente-servidor?
**A:** Precisa de:
1. Licença válida (`license_manager.is_licensed()`)
2. Servidor rodando (FastAPI WebSocket)
3. Credenciais (login/senha/license_key)
4. `server.url` configurado em `config.json`

### Q: Preciso de Arduino?
**A:** NÃO. O `arduino_command_executor` é opcional. Você pode usar pyautogui normalmente (modo standalone).

### Q: A pasta `server/` é necessária?
**A:** Apenas se você quer rodar o SERVIDOR. A pasta `client/` é para conectar a um servidor existente.

---

## 🎯 Decisão: Usar ou Não Usar `client/`?

### Use `client/` SE:
- ✅ Você tem múltiplos PCs rodando bots
- ✅ Quer controle centralizado
- ✅ Quer usar Arduino para anti-detecção
- ✅ Quer dashboard web para analytics
- ✅ Tem servidor FastAPI rodando

### NÃO use `client/` SE:
- ✅ Quer apenas pescar em 1 PC
- ✅ Não tem servidor
- ✅ Prefere simplicidade
- ✅ Bot standalone v3/v4 é suficiente

---

## 📦 Compilar .exe: Incluir ou Não `client/`?

### Opção 1: .exe Standalone (Simples)
```python
# FishingBot.spec
hiddenimports=[
    'core',
    'ui',
    'utils',
    # NÃO incluir 'client'
]
```

**Resultado:** .exe menor, sem dependências de WebSocket/servidor.

---

### Opção 2: .exe com Cliente-Servidor (Completo)
```python
# FishingBot.spec
hiddenimports=[
    'core',
    'ui',
    'utils',
    'client',  # ← Incluir
    'websockets',
    'asyncio',
]
```

**Resultado:** .exe maior, com suporte a servidor remoto.

---

## 📊 Comparação Final

| Recurso | Standalone (sem client/) | Cliente-Servidor (com client/) |
|---------|--------------------------|-------------------------------|
| Simplicidade | ✅ Muito simples | ⚠️ Complexo |
| Multi-bot | ❌ 1 bot por PC | ✅ N bots centralizados |
| Controle remoto | ❌ Não | ✅ Sim (via servidor) |
| Arduino HID | ❌ Não | ✅ Sim |
| Dashboard | ❌ Não | ✅ Sim (web) |
| Tamanho .exe | ✅ ~50-80 MB | ⚠️ ~80-120 MB |
| Dependências | ✅ Poucas | ⚠️ Muitas (websockets, asyncio) |
| Servidor necessário | ✅ Não | ❌ Sim |

---

## 🚀 Conclusão

**A pasta `client/` é um módulo OPCIONAL para modo avançado cliente-servidor.**

- Se você quer apenas pescar em 1 PC → **IGNORE `client/`**
- Se você quer orquestrar múltiplos bots → **USE `client/`**

O código atual em `main.py` **já suporta ambos os modos**:
1. Se licença válida + servidor configurado → Conecta via `client/`
2. Se não → Roda standalone normal

**Recomendação:** Para distribuir o .exe, compile **SEM** a pasta `client/` (mais simples). Se o usuário quiser servidor depois, pode baixar versão completa separadamente.
