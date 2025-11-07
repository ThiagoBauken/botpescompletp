# 🐛 Bug Crítico: active_users = 0 Permanente

## 🚨 Descrição do Problema

O servidor **valida corretamente** a autenticação HTTP mas **não registra** os usuários como ativos no WebSocket, resultando em `"active_users": 0` mesmo quando há conexões ativas.

### Sintomas Observados

1. ✅ **HTTP /auth/activate funciona** - Retorna 200 OK com token
2. ✅ **Keymaster valida** - License aprovada
3. ❌ **WebSocket não conecta** - Cliente recebe erro HTTP 400
4. ❌ **active_users permanece em 0** - Contador não incrementa

---

## 📊 Evidências

### Logs do Servidor (Funcionamento Parcial)

```
INFO:server:🔍 Validando com Keymaster: OF5Y-ZPOI-...
INFO:server:✅ Keymaster: License válida!
INFO:server:✅ Keymaster validou: OF5Y-ZPOI-... (Plan: basic)
INFO:server:🔗 HWID vinculado pela primeira vez:
INFO:server:   License: OF5Y-ZPOI-...
INFO:server:   Login: BALINHA
INFO:server:   PC: DESKTOP-Q5GCMOD
INFO:server:   HWID: be10ce58a64d16ce...
INFO:server:✅ Ativação bem-sucedida: BALINHA
INFO:     10.11.0.61:33184 - "POST /auth/activate HTTP/1.1" 200 OK  ← ✅ HTTP OK
```

### Health Check (Bug Evidente)

```json
{
  "service": "Fishing Bot Server",
  "version": "2.0.0",
  "status": "online",
  "active_users": 0,  ← ❌ ZERO mesmo após autenticação!
  "keymaster_integration": true
}
```

### Cliente (Erro na Conexão WebSocket)

```
🌐 Conectando ao servidor multi-usuário...
   URL: https://private-serverpesca.pbzgje.easypanel.host
   Login: thiago
   🔐 Autenticando (servidor valida com Keymaster)...
   ❌ Falha na ativação: Erro na validação (HTTP 400)  ← Cliente recebe 400
```

---

## 🔍 Análise da Causa Raiz

### Fluxo Esperado (Como Deveria Funcionar)

```
1. Cliente → HTTP POST /auth/activate
   ↓
2. Servidor valida com Keymaster ✅
   ↓
3. Servidor retorna token + rules ✅
   ↓
4. Cliente conecta WebSocket com token
   ↓
5. Servidor autentica WebSocket
   ↓
6. Servidor incrementa active_users
   ↓
7. Cliente recebe "connected"
```

### Fluxo Atual (O Que Está Acontecendo)

```
1. Cliente → HTTP POST /auth/activate
   ↓
2. Servidor valida com Keymaster ✅
   ↓
3. Servidor retorna token + rules ✅
   ↓
4. Cliente conecta WebSocket com token
   ↓
5. ❌ FALHA AQUI - WebSocket rejeita conexão
   ↓
6. ❌ active_users não incrementa
   ↓
7. Cliente recebe HTTP 400
```

### Possíveis Causas do Bug

#### 1. **WebSocket Não Validando Token Corretamente**

O endpoint WebSocket (`/ws`) pode estar rejeitando tokens válidos.

**Código problemático (server.py linha ~600):**

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        # Receber token
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")

        # ❌ PROBLEMA: Validação de token pode estar falhando
        if not token or not validate_token(token):
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close()
            return  # ← Sai sem incrementar active_users

        # Se chegar aqui, deveria incrementar
        active_users[token] = websocket
        logger.info(f"✅ Usuário conectado: {len(active_users)} ativos")

    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}")
        await websocket.close()
```

**Problemas possíveis:**
- `validate_token()` pode estar rejeitando tokens válidos
- Token pode estar expirando muito rápido
- Formato do token pode estar incorreto

#### 2. **Desconexão Imediata Após Aceitar**

WebSocket aceita conexão mas fecha imediatamente devido a erro.

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # ← Aceita

    try:
        # Algo falha aqui
        user_session = create_session(...)  # ← Erro
    except Exception:
        await websocket.close()  # ← Fecha sem logar
        return
```

#### 3. **CORS ou Headers Incorretos no WebSocket**

Cliente não consegue estabelecer handshake WebSocket devido a CORS.

```python
# Faltando configuração CORS para WebSocket
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Pode não estar incluindo WSS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. **Problema com SSL/TLS (WSS)**

Servidor pode estar rejeitando conexões WSS por certificado inválido.

#### 5. **Timeout na Autenticação WebSocket**

Cliente pode estar demorando muito para enviar token.

```python
# Servidor espera apenas 1s para autenticação
auth_data = await asyncio.wait_for(
    websocket.receive_json(),
    timeout=1.0  # ← Muito curto!
)
```

---

## 🛠️ Soluções Propostas

### Solução 1: Adicionar Logging Detalhado no WebSocket

**Modificar `server.py` linha ~600:**

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"🔵 Nova conexão WebSocket de {websocket.client}")

    try:
        await websocket.accept()
        logger.info(f"✅ WebSocket aceito: {websocket.client}")

        # Receber token
        logger.info(f"⏳ Aguardando autenticação...")
        auth_data = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=5.0  # ← Aumentar timeout
        )
        logger.info(f"📥 Dados recebidos: {auth_data}")

        token = auth_data.get("token")
        logger.info(f"🔑 Token recebido: {token[:20]}...")

        # Validar token
        logger.info(f"🔍 Validando token...")
        if not token:
            logger.error("❌ Token vazio!")
            await websocket.send_json({"error": "Token missing"})
            await websocket.close()
            return

        if not validate_token(token):
            logger.error(f"❌ Token inválido: {token[:20]}...")
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close()
            return

        logger.info(f"✅ Token válido!")

        # Registrar usuário
        user_id = extract_user_from_token(token)
        active_users[user_id] = websocket
        logger.info(f"✅ Usuário {user_id} adicionado aos ativos: {len(active_users)} total")

        # Enviar confirmação
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado com sucesso!",
            "fish_count": 0
        })

        # Loop de mensagens
        while True:
            message = await websocket.receive_json()
            logger.info(f"📨 Mensagem de {user_id}: {message.get('event')}")
            # Processar mensagem...

    except asyncio.TimeoutError:
        logger.error(f"❌ Timeout aguardando autenticação de {websocket.client}")
        await websocket.close()

    except WebSocketDisconnect:
        logger.info(f"🔴 Cliente desconectou: {websocket.client}")
        # Remover dos ativos
        for uid, ws in list(active_users.items()):
            if ws == websocket:
                del active_users[uid]
                logger.info(f"🗑️ Usuário {uid} removido: {len(active_users)} ativos")
                break

    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}", exc_info=True)
        await websocket.close()
```

### Solução 2: Verificar Função `validate_token()`

**Adicionar logs na validação:**

```python
def validate_token(token: str) -> bool:
    """
    Validar token do formato: license_key:hwid_prefix
    """
    logger.info(f"🔍 Validando token: {token[:20]}...")

    try:
        # Parse token
        parts = token.split(":")
        if len(parts) != 2:
            logger.error(f"❌ Token formato inválido: esperado 'license:hwid', recebido '{token}'")
            return False

        license_key, hwid_prefix = parts
        logger.info(f"   License: {license_key[:10]}...")
        logger.info(f"   HWID: {hwid_prefix}...")

        # Verificar se license existe no banco
        cursor.execute("""
            SELECT license_key, hwid, login
            FROM hwid_bindings
            WHERE license_key=?
        """, (license_key,))

        binding = cursor.fetchone()

        if not binding:
            logger.error(f"❌ License não encontrada no banco: {license_key[:10]}...")
            return False

        stored_license, stored_hwid, login = binding
        stored_hwid_prefix = stored_hwid[:16]

        logger.info(f"   Binding encontrado: login={login}")
        logger.info(f"   HWID stored: {stored_hwid_prefix}")
        logger.info(f"   HWID token: {hwid_prefix}")

        # Comparar HWID
        if hwid_prefix != stored_hwid_prefix:
            logger.error(f"❌ HWID não corresponde!")
            logger.error(f"   Esperado: {stored_hwid_prefix}")
            logger.error(f"   Recebido: {hwid_prefix}")
            return False

        logger.info(f"✅ Token válido para {login}")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao validar token: {e}", exc_info=True)
        return False
```

### Solução 3: Aumentar Timeout de Autenticação

**Aumentar de 1s para 10s:**

```python
# Antes
auth_data = await asyncio.wait_for(websocket.receive_json(), timeout=1.0)

# Depois
auth_data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
```

### Solução 4: Verificar CORS para WebSocket

**Adicionar middleware CORS corretamente:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Solução 5: Health Check Corrigido

**Retornar contagem real de usuários ativos:**

```python
@app.get("/health")
async def health_check():
    """Health check com contagem correta de usuários"""
    active_count = len(active_users)

    logger.info(f"📊 Health check: {active_count} usuários ativos")

    # Listar usuários (debug)
    for user_id in active_users.keys():
        logger.info(f"   - {user_id}")

    return {
        "service": "Fishing Bot Server",
        "version": "2.0.0",
        "status": "online",
        "active_users": active_count,
        "keymaster_integration": True,
        "users": list(active_users.keys())  # ← Debug: listar IDs
    }
```

---

## 🧪 Teste de Diagnóstico

### Script de Teste Completo

Criar arquivo `test_websocket_detailed.py`:

```python
#!/usr/bin/env python3
"""
Teste detalhado de conexão WebSocket
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Testar conexão WebSocket com logs detalhados"""

    server_url = "wss://private-serverpesca.pbzgje.easypanel.host/ws"
    token = "MAMZ-LQCC-...:26ac9cc77f1aa50a"  # Seu token

    print(f"🔌 Conectando a {server_url}...")

    try:
        async with websockets.connect(server_url) as websocket:
            print("✅ WebSocket conectado!")

            # Enviar autenticação
            auth_msg = {"token": token}
            print(f"📤 Enviando autenticação: {auth_msg}")
            await websocket.send(json.dumps(auth_msg))

            # Aguardar resposta
            print("⏳ Aguardando resposta...")
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            print(f"📥 Resposta: {response}")

            data = json.loads(response)
            if data.get("type") == "connected":
                print("✅ AUTENTICAÇÃO BEM-SUCEDIDA!")
                print(f"   Message: {data.get('message')}")
            elif "error" in data:
                print(f"❌ ERRO: {data['error']}")

    except asyncio.TimeoutError:
        print("❌ Timeout aguardando resposta do servidor")
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ Status code inválido: {e.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
```

---

## 📋 Checklist de Correção

- [ ] Adicionar logs detalhados no endpoint WebSocket
- [ ] Adicionar logs na função `validate_token()`
- [ ] Aumentar timeout de autenticação (1s → 10s)
- [ ] Verificar middleware CORS está configurado
- [ ] Corrigir health check para mostrar usuários reais
- [ ] Testar com script `test_websocket_detailed.py`
- [ ] Verificar logs do servidor após cada tentativa
- [ ] Confirmar que active_users incrementa corretamente

---

## 🎯 Conclusão

**Problema:** Servidor aceita autenticação HTTP mas **rejeita conexões WebSocket**, causando `active_users = 0` permanente.

**Causa Provável:** Erro na validação de token no WebSocket ou timeout muito curto.

**Ação Imediata:** Adicionar logs detalhados para identificar onde exatamente a conexão WebSocket está falhando.

---

**Criado em:** 2025-11-07
**Versão:** 1.0
**Projeto:** Ultimate Fishing Bot v5.0
**Prioridade:** 🔴 CRÍTICA
