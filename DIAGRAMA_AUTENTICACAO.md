# 🔐 Diagrama: Como o Servidor Distingue Usuários

## 🎯 Visão Geral

```
┌─────────────────────────────────────────────────────────────────┐
│                   SERVIDOR WEBSOCKET                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  active_sessions = {                                            │
│                                                                 │
│    "LICENSE-KEY-AAA": {    ← Chave única (identifica usuário)  │
│       "login": "user1@email.com",   ← Apenas para logs         │
│       "session": FishingSession("user1@email.com")             │
│    },                                                           │
│                                                                 │
│    "LICENSE-KEY-BBB": {    ← Outra chave única                 │
│       "login": "user2@email.com",   ← Outro login              │
│       "session": FishingSession("user2@email.com")             │
│    },                                                           │
│                                                                 │
│    "LICENSE-KEY-CCC": {    ← Mais uma chave única              │
│       "login": "user1@email.com",   ← MESMO LOGIN que AAA!    │
│       "session": FishingSession("user1@email.com")             │
│    }                                                            │
│  }                                                              │
│                                                                 │
│  ✅ Servidor distingue pelos 3 usuários diferentes!            │
│  ✅ Mesmo com 2 tendo o mesmo login!                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo Completo: Cliente → Servidor

### 1️⃣ Cliente Envia Credenciais

```
┌──────────────────┐
│  CLIENTE 1       │
│                  │
│  Login: user1@   │  POST /auth/activate
│  Senha: 123      │  ─────────────────────►
│  Key: KEY-AAA    │  {
│  HWID: ABC123    │    "login": "user1@email.com",
└──────────────────┘    "password": "123",
                        "license_key": "KEY-AAA",
                        "hwid": "ABC123"
                      }
```

### 2️⃣ Servidor Valida License Key

```
┌──────────────────────────────────────┐
│  SERVIDOR                            │
├──────────────────────────────────────┤
│                                      │
│  1. Validar KEY-AAA no Keymaster     │
│     ✅ Chave válida                  │
│                                      │
│  2. Verificar HWID ABC123            │
│     ✅ HWID permitido                │
│                                      │
│  3. ❌ NÃO valida login "user1@"     │
│     ❌ NÃO valida senha "123"        │
│                                      │
│  4. Vincular no banco:               │
│     license_key=KEY-AAA              │
│     hwid=ABC123                      │
│     login=user1@email.com  ← Salvo! │
│                                      │
│  5. Retornar token                   │
│     token = "KEY-AAA:ABC123"         │
│                                      │
└──────────────────────────────────────┘
```

### 3️⃣ Cliente Conecta WebSocket

```
┌──────────────────┐
│  CLIENTE 1       │  WebSocket /ws
│                  │  ─────────────────────►
│  Token:          │  {
│  KEY-AAA:ABC123  │    "token": "KEY-AAA:ABC123"
└──────────────────┘  }
```

### 4️⃣ Servidor Registra Sessão

```
┌──────────────────────────────────────┐
│  SERVIDOR                            │
├──────────────────────────────────────┤
│                                      │
│  active_sessions["KEY-AAA"] = {      │
│     "login": "user1@email.com",      │
│     "websocket": <conexão>,          │
│     "session": FishingSession(...)   │
│  }                                   │
│                                      │
│  logger.info("Cliente conectado:     │
│               user1@email.com")      │
│               ↑ Login usado aqui!    │
│                                      │
└──────────────────────────────────────┘
```

---

## 🎭 Cenário: 2 Usuários, Mesmo Login

### Cliente 1

```
Login: usuario@email.com
Senha: abc123
License: KEY-AAA
HWID: HWID-PC-1
```

### Cliente 2

```
Login: usuario@email.com  ← MESMO LOGIN!
Senha: xyz789
License: KEY-BBB          ← CHAVE DIFERENTE
HWID: HWID-PC-2
```

### Resultado no Servidor

```python
active_sessions = {
    "KEY-AAA": {
        "login": "usuario@email.com",    # Cliente 1
        "pc_name": "DESKTOP-WIN11",
        "fish_count": 42
    },
    "KEY-BBB": {
        "login": "usuario@email.com",    # Cliente 2 (MESMO LOGIN!)
        "pc_name": "LAPTOP-MAC",
        "fish_count": 15
    }
}
```

**✅ Servidor distingue corretamente os dois!**

**Logs:**
```
🟢 Cliente conectado: usuario@email.com (PC: DESKTOP-WIN11)
🟢 Cliente conectado: usuario@email.com (PC: LAPTOP-MAC)
   ↑ Mesmo login, mas PCs diferentes = OK!
```

---

## 🚫 Cenário: 1 Usuário, 2 PCs (BLOQUEADO)

### Tentativa 1 (PC 1)

```
Login: usuario@email.com
License: KEY-AAA
HWID: HWID-PC-1
→ ✅ ACEITO (primeira vez)
→ Vincula KEY-AAA → HWID-PC-1
```

### Tentativa 2 (PC 2 - MESMO USUÁRIO)

```
Login: usuario@email.com  ← Mesmo login
License: KEY-AAA          ← Mesma chave
HWID: HWID-PC-2          ← ❌ HWID DIFERENTE!
→ ❌ BLOQUEADO
→ Mensagem: "Licença vinculada ao PC: DESKTOP-WIN11"
```

**❌ Servidor bloqueia pela HWID, não pelo login!**

---

## 📊 Tabela: O Que Identifica o Usuário?

| Campo | Usado para Identificar? | Único? | Validado? |
|-------|-------------------------|--------|-----------|
| **license_key** | ✅ SIM (chave principal) | ✅ SIM | ✅ SIM (Keymaster) |
| **hwid** | ✅ SIM (anti-share) | ✅ SIM (por license) | ✅ SIM (binding) |
| **login** | ❌ NÃO (apenas label) | ❌ NÃO (pode repetir) | ❌ NÃO |
| **password** | ❌ NÃO (ignorada) | ❌ NÃO | ❌ NÃO |
| **pc_name** | ❌ NÃO (info adicional) | ❌ NÃO | ❌ NÃO |

---

## 🎯 Como o Servidor Decide Quem É Quem?

### Pergunta: "Qual cliente enviou este fish_caught?"

```python
# Mensagem recebida via WebSocket:
{
    "event": "fish_caught",
    "fish_count": 42
}

# Servidor identifica pelo WebSocket:
for license_key, data in active_sessions.items():
    if data["websocket"] == sender_websocket:
        login = data["login"]  # ← Pega login para logs
        session = data["session"]

        logger.info(f"[{login}] Peixe #{session.fish_count} capturado!")
        #            ↑ Login usado APENAS para logging!

        session.increment_fish()
        break
```

**Identificação real:** WebSocket → license_key
**Login usado:** Apenas para mensagem de log

---

## 💡 Analogia: Sistema de Hotéis

```
Hotel = Servidor
Quarto = active_sessions[license_key]
Número do Quarto = license_key (ÚNICO)
Nome do Hóspede = login (pode repetir)
```

**Cenário:**

```
Quarto 101: Sr. João Silva
Quarto 102: Sr. João Silva  ← Mesmo nome!
Quarto 103: Sra. Maria Santos
```

**Como o hotel identifica?**
- ✅ Pelo NÚMERO DO QUARTO (101, 102, 103)
- ❌ NÃO pelo nome (pode ter 2 "João Silva")

**Como o hotel chama os hóspedes?**
- 📢 "Sr. João Silva do quarto 101, sua encomenda chegou!"
- ↑ Usa o NOME para comunicação (mais humano)

**Mesma lógica no servidor:**
- ✅ Identifica por `license_key` (chave única)
- 📢 Exibe `login` nos logs (mais humano)

---

## ✅ Conclusão

```
┌─────────────────────────────────────────────┐
│  HIERARQUIA DE IDENTIFICAÇÃO:               │
├─────────────────────────────────────────────┤
│                                             │
│  1. license_key (PRIMÁRIO)                  │
│     ↓ Identifica tecnicamente o usuário    │
│                                             │
│  2. hwid (SECUNDÁRIO)                       │
│     ↓ Valida que é o mesmo PC              │
│                                             │
│  3. login (TERCIÁRIO)                       │
│     ↓ Apenas para exibição/logs            │
│                                             │
│  4. password (NÃO USADO)                    │
│     ↓ Ignorado completamente               │
│                                             │
└─────────────────────────────────────────────┘
```

**Resposta direta:**

✅ **Login é necessário?** SIM, para identificação visual
✅ **Login distingue usuários?** NÃO, isso é feito pela license_key
✅ **O que distingue usuários?** license_key + hwid
✅ **Login pode repetir?** SIM, mas dificulta debugging

**Recomendação:** Use logins únicos para facilitar os logs! 🎯
