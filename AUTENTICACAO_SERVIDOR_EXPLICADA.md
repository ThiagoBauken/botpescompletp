# 🔐 Como Funciona a Autenticação no Servidor WebSocket

## 🎯 Resposta Rápida

**Login e senha são OBRIGATÓRIOS para enviar ao servidor, MAS:**

- ✅ **License Key** = Validada pelo Keymaster (REAL)
- ⚠️ **Login** = Apenas identificação visual (NÃO validado)
- ⚠️ **Senha** = NÃO é validada (aceita qualquer valor)

**Em resumo:** A **ÚNICA** autenticação REAL é a **license_key**. Login/senha são apenas "labels" para identificar o usuário no painel.

---

## 📋 Campos Enviados ao Servidor

### Código: [server.py:417-423](server/server.py#L417-L423)

```python
class ActivationRequest(BaseModel):
    login: str                  # ⚠️ Obrigatório, MAS não validado
    password: str               # ⚠️ Obrigatório, MAS não validado
    license_key: str            # ✅ Validado pelo Keymaster (REAL)
    hwid: str                   # ✅ Validado (anti-compartilhamento)
    pc_name: str = None         # 📝 Opcional (apenas info)
```

---

## 🔄 Fluxo de Autenticação Completo

### Etapa 1: Cliente Envia Credenciais

O cliente envia via HTTP POST `/auth/activate`:

```json
{
  "login": "usuario@email.com",
  "password": "qualquer_senha_123",
  "license_key": "XXXX-XXXX-XXXX-XXXX",
  "hwid": "ABC123...",
  "pc_name": "DESKTOP-WIN11"
}
```

---

### Etapa 2: Servidor Valida APENAS a License Key

**Código:** [server.py:468-476](server/server.py#L468-L476)

```python
# 1. VALIDAR COM KEYMASTER (OBRIGATÓRIO)
keymaster_result = validate_with_keymaster(request.license_key, request.hwid)

if not keymaster_result["valid"]:
    logger.warning(f"❌ Keymaster rejeitou: {request.license_key[:10]}...")
    return ActivationResponse(
        success=False,
        message=keymaster_result["message"]
    )
```

**O que acontece:**
- ✅ Servidor chama o Keymaster com a `license_key` + `hwid`
- ✅ Keymaster valida se a chave é válida
- ✅ Keymaster valida se HWID está permitido
- ❌ **Login e senha NÃO são validados!**

---

### Etapa 3: Servidor Verifica HWID Binding

**Código:** [server.py:486-522](server/server.py#L486-L522)

```python
# 2. VERIFICAR HWID BINDING (Anti-compartilhamento)
cursor.execute("""
    SELECT hwid, pc_name, bound_at, login
    FROM hwid_bindings
    WHERE license_key=?
""", (request.license_key,))

binding = cursor.fetchone()

if binding:
    bound_hwid, bound_pc_name, bound_at, bound_login = binding

    if request.hwid == bound_hwid:
        # ✅ MESMO PC - permitir
        logger.info(f"✅ HWID válido: {request.login} (PC: {request.pc_name})")
    else:
        # ❌ PC DIFERENTE - bloquear
        return ActivationResponse(
            success=False,
            message=f"Licença vinculada a outro PC ({bound_pc_name})"
        )
else:
    # PRIMEIRA VEZ → vincular HWID + login
    cursor.execute("""
        INSERT INTO hwid_bindings (license_key, hwid, pc_name, login)
        VALUES (?, ?, ?, ?)
    """, (request.license_key, request.hwid, request.pc_name, request.login))
```

**O que acontece:**
- ✅ Se license_key nunca foi usada → vincula HWID + login ao PC
- ✅ Se license_key já foi usada → verifica se é o mesmo PC
- ❌ **Senha nunca é verificada!**

---

### Etapa 4: Servidor Retorna Token

**Código:** [server.py:544-553](server/server.py#L544-L553)

```python
# 3. GERAR TOKEN E RETORNAR REGRAS
token = f"{request.license_key}:{request.hwid[:16]}"  # Token simples

return ActivationResponse(
    success=True,
    message="Ativação bem-sucedida!",
    token=token,
    rules=DEFAULT_RULES
)
```

**O que acontece:**
- ✅ Token = `license_key:hwid_prefix`
- ✅ Token usado para conectar ao WebSocket
- ✅ Cliente salva token localmente

---

## 🤔 Por Que Login/Senha Se Não São Validados?

### Motivo 1: Identificação Visual no Dashboard

Quando você acessa o painel web do servidor, você vê:

```
┌─────────────────────────────────────────┐
│ Usuários Ativos                         │
├─────────────────────────────────────────┤
│ usuario@email.com (DESKTOP-WIN11)       │ ← Login salvo
│ outro@email.com (LAPTOP-MAC)            │
│ admin@test.com (SERVER-LINUX)           │
└─────────────────────────────────────────┘
```

O **login** ajuda a identificar visualmente quem está conectado.

---

### Motivo 2: Preparação para Futuro Sistema de Usuários

**Atualmente:**
- 1 license_key = 1 PC (HWID binding)
- Login é apenas "label"

**Futuro possível:**
- 1 license_key = N PCs (plano premium)
- Login + senha = autenticação real
- Sistema de usuários com permissões

**Mas hoje:** Senha não é usada!

---

### Motivo 3: Compatibilidade com Outros Sistemas

Se você quiser integrar com:
- Discord OAuth
- Google Login
- Keymaster OAuth (se existir)

Já tem os campos `login` e `password` prontos.

---

## 📊 Tabela Comparativa: O Que É Validado?

| Campo | Obrigatório? | Validado? | Onde? | Função |
|-------|--------------|-----------|-------|--------|
| **license_key** | ✅ Sim | ✅ SIM | Keymaster | **AUTENTICAÇÃO REAL** |
| **hwid** | ✅ Sim | ✅ SIM | Servidor | **Anti-compartilhamento** |
| **login** | ✅ Sim | ❌ NÃO | - | Identificação visual |
| **password** | ✅ Sim | ❌ NÃO | - | Não usado |
| **pc_name** | ❌ Não | ❌ NÃO | - | Info adicional |

---

## 🔐 Sistema de Segurança Atual

```
┌─────────────────────────────────────────────────────┐
│  CAMADAS DE SEGURANÇA                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1️⃣ License Key (Keymaster)                         │
│     ✅ Valida se chave é válida                     │
│     ✅ Verifica plano (Basic/Pro/Enterprise)        │
│     ✅ Verifica expiração                           │
│                                                     │
│  2️⃣ HWID Binding (Servidor)                         │
│     ✅ Vincula license_key a 1 PC                   │
│     ✅ Bloqueia uso em múltiplos PCs                │
│     ✅ Impede compartilhamento de licença           │
│                                                     │
│  3️⃣ Token WebSocket                                 │
│     ✅ Token = license_key:hwid_prefix              │
│     ✅ Validado a cada conexão                      │
│     ✅ Heartbeat mantém sessão ativa                │
│                                                     │
│  ❌ Login/Senha (NÃO USADO ATUALMENTE)              │
│     ⚠️ Apenas para identificação visual             │
│     ⚠️ Não há validação real                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## ❓ FAQ

### Q1: Posso usar qualquer login/senha?
**A:** SIM! O servidor aceita qualquer valor. Exemplos válidos:
- Login: `"test@test.com"`, Senha: `"123"`
- Login: `"usuario"`, Senha: `"qualquer"`
- Login: `"admin"`, Senha: `""`

O servidor NÃO valida esses campos.

### Q2: Então por que o ActivationDialog pede senha?
**A:** Por dois motivos:
1. **UI/UX** - Usuário espera um formulário de login completo
2. **Preparação futura** - Se você implementar autenticação real depois, já tem o campo

### Q3: Posso REMOVER o campo senha?
**A:** Tecnicamente SIM, mas:
- ❌ Quebra compatibilidade com o servidor atual (campo obrigatório no modelo Pydantic)
- ⚠️ Melhor: Marcar como opcional (`password: str = "default"`)

### Q4: O servidor salva a senha?
**A:** NÃO! O servidor:
- ✅ Recebe a senha no request
- ❌ NÃO salva no banco de dados
- ❌ NÃO valida contra nada
- ✅ Apenas descarta

Veja o banco de dados:

```sql
CREATE TABLE hwid_bindings (
    id INTEGER PRIMARY KEY,
    license_key TEXT NOT NULL,
    hwid TEXT NOT NULL,
    pc_name TEXT,
    login TEXT,              -- ✅ Salva login
    -- password TEXT,        -- ❌ NÃO salva senha!
    bound_at TIMESTAMP,
    last_seen TIMESTAMP
);
```

### Q5: Então a senha é apenas "decorativa"?
**A:** EXATAMENTE! É como um campo de "comentário". Você pode digitar:
- `"123"` ✅ Funciona
- `"minha_senha_secreta"` ✅ Funciona
- `""` (vazio) ✅ Funciona (servidor vai rejeitar apenas se NULL)

### Q6: Como faço autenticação REAL então?
**A:** A autenticação REAL é:
1. **License Key** validada pelo Keymaster
2. **HWID** vinculado ao PC

Se ambos passarem, você está autenticado! Login/senha são irrelevantes.

---

## 🎯 Recomendação: Simplificar o ActivationDialog?

### Opção 1: Manter Como Está (Atual)
```python
# client/activation_dialog.py
login = input("Login: ")          # Obrigatório (qualquer valor)
password = input("Senha: ")       # Obrigatório (qualquer valor)
license_key = input("License: ")  # Obrigatório (VALIDADO)
```

**Prós:**
- ✅ Usuário espera formulário completo
- ✅ Preparado para futuro sistema de usuários
- ✅ Compatível com servidor atual

**Contras:**
- ❌ Confuso (usuário pensa que senha é validada)
- ❌ Campos desnecessários

---

### Opção 2: Senha Opcional com Tooltip

```python
tk.Label(form_frame, text="Senha (não validada - apenas identificação):").pack()
password_entry = tk.Entry(form_frame, show="●")
password_entry.insert(0, "default")  # Pré-preenchido
```

**Prós:**
- ✅ Transparente (usuário sabe que senha não é validada)
- ✅ Ainda compatível com servidor

**Contras:**
- ⚠️ Pode confundir ainda mais

---

### Opção 3: Apenas License Key (Mais Simples)

**Modificar servidor:**
```python
class ActivationRequest(BaseModel):
    license_key: str            # ✅ Validado
    hwid: str                   # ✅ Validado
    login: str = "user"         # ⚠️ Opcional (gerado automaticamente)
    password: str = "default"   # ⚠️ Opcional (não usado)
    pc_name: str = None
```

**Cliente:**
```python
# Apenas pede license_key
license_key = input("License Key: ")

# Gera login automaticamente
login = f"user_{license_key[:8]}"
password = "default"  # Não usado

# Envia ao servidor
activate(login, password, license_key, hwid, pc_name)
```

**Prós:**
- ✅ Muito mais simples para o usuário
- ✅ Apenas pede o que é realmente necessário
- ✅ Menos confusão

**Contras:**
- ❌ Requer modificação no servidor (tornar login/senha opcionais)
- ❌ Perde flexibilidade futura

---

## 📝 Conclusão

### Estado Atual:
```
Login/Senha: Obrigatórios no código, mas NÃO validados
License Key: Obrigatória e VALIDADA pelo Keymaster
HWID: Obrigatório e validado pelo servidor (anti-compartilhamento)
```

### A Verdade Brutal:
**Você pode usar `login="a"` e `password="b"` que funciona perfeitamente!**

O que realmente importa é:
1. ✅ License Key válida no Keymaster
2. ✅ HWID do PC compatível com a licença

Login/senha são apenas "etiquetas" para o painel web.

---

## 🚀 Teste Você Mesmo

Execute este teste:

```python
# teste_autenticacao_fake.py
from client.server_connector import connect_to_server

# Teste 1: Credenciais "fake" + license key VÁLIDA
ws_client = connect_to_server(
    login="usuario_fake",
    password="123",  # Qualquer senha
    license_key="SUA-LICENSE-KEY-REAL",
    server_url="wss://seu-servidor.com/ws"
)

# Se license_key for válida → ✅ Conecta!
# Senha não importa!

# Teste 2: Credenciais "reais" + license key INVÁLIDA
ws_client = connect_to_server(
    login="admin@real.com",
    password="senha_super_segura_123!@#",  # Senha "real"
    license_key="INVALID-KEY",
    server_url="wss://seu-servidor.com/ws"
)

# License_key inválida → ❌ Rejeita!
# Mesmo com senha "real"!
```

---

**TL;DR:** 📌
- **Login/Senha:** Obrigatórios, mas **NÃO validados** (aceita qualquer valor)
- **License Key:** Obrigatória e **VALIDADA** pelo Keymaster (autenticação REAL)
- **HWID:** Obrigatório e **VALIDADO** pelo servidor (anti-compartilhamento)

**A senha é apenas decorativa!** 🎨
