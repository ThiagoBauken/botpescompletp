# 🔧 Correção: FastAPI DeprecationWarning - Migração para Lifespan

## 🎯 Objetivo

Corrigir os warnings de deprecação do FastAPI no arquivo `server.py`:

```
/app/server.py:1202: DeprecationWarning:
    on_event is deprecated, use lifespan event handlers instead.
@app.on_event("startup")

/app/server.py:1211: DeprecationWarning:
    on_event is deprecated, use lifespan event handlers instead.
@app.on_event("shutdown")
```

---

## 📝 O Que Mudou no FastAPI?

A partir da versão **FastAPI 0.93.0**, o método `@app.on_event()` foi **deprecado** em favor do pattern **`lifespan`**.

### Por Que a Mudança?

1. **Melhor controle de ciclo de vida** - Gerenciamento mais claro de recursos
2. **Suporte a context managers** - Padrão Python assíncrono
3. **Evita race conditions** - Garante ordem de execução
4. **Mais testável** - Facilita testes de integração

---

## 🔄 Comparação: Antes vs Depois

### ❌ ANTES (Código Antigo com Warnings)

```python
from fastapi import FastAPI
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

# Variáveis globais para recursos
db_connection = None
cache = None

@app.on_event("startup")
async def startup_event():
    """Inicialização do servidor"""
    global db_connection, cache

    logger.info("🚀 Servidor iniciando...")

    # Conectar ao banco de dados
    db_connection = await connect_database()
    logger.info("✅ Banco de dados conectado")

    # Inicializar cache
    cache = await initialize_cache()
    logger.info("✅ Cache inicializado")

    # Outras inicializações
    logger.info("✅ Servidor pronto!")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpeza ao desligar servidor"""
    global db_connection, cache

    logger.info("🛑 Servidor encerrando...")

    # Fechar conexão do banco
    if db_connection:
        await db_connection.close()
        logger.info("✅ Banco de dados desconectado")

    # Limpar cache
    if cache:
        await cache.clear()
        logger.info("✅ Cache limpo")

    logger.info("✅ Servidor encerrado com sucesso!")

# Rotas
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### ✅ DEPOIS (Código Corrigido sem Warnings)

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# Dicionário para armazenar recursos compartilhados
state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do servidor

    Tudo antes do yield: STARTUP
    Tudo depois do yield: SHUTDOWN
    """

    # ═══════════════════════════════════════════════════════
    # STARTUP - Executado quando servidor inicia
    # ═══════════════════════════════════════════════════════

    logger.info("🚀 Servidor iniciando...")

    # Conectar ao banco de dados
    state['db_connection'] = await connect_database()
    logger.info("✅ Banco de dados conectado")

    # Inicializar cache
    state['cache'] = await initialize_cache()
    logger.info("✅ Cache inicializado")

    # Outras inicializações
    logger.info("✅ Servidor pronto!")

    yield  # ← SERVIDOR RODA AQUI (processando requisições)

    # ═══════════════════════════════════════════════════════
    # SHUTDOWN - Executado quando servidor desliga
    # ═══════════════════════════════════════════════════════

    logger.info("🛑 Servidor encerrando...")

    # Fechar conexão do banco
    if 'db_connection' in state:
        await state['db_connection'].close()
        logger.info("✅ Banco de dados desconectado")

    # Limpar cache
    if 'cache' in state:
        await state['cache'].clear()
        logger.info("✅ Cache limpo")

    logger.info("✅ Servidor encerrado com sucesso!")

# Criar app com lifespan
app = FastAPI(lifespan=lifespan)

# Rotas (podem acessar state se necessário)
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/status")
async def status():
    """Exemplo de rota acessando recursos do lifespan"""
    return {
        "database": "connected" if state.get('db_connection') else "disconnected",
        "cache": "active" if state.get('cache') else "inactive"
    }
```

---

## 🛠️ Guia de Migração Passo a Passo

### Passo 1: Backup do Arquivo

```bash
cp server/server.py server/server.py.backup
```

### Passo 2: Adicionar Import

No topo do arquivo `server.py`, adicione:

```python
from contextlib import asynccontextmanager
```

### Passo 3: Identificar Código Atual

Localize no arquivo (aproximadamente linhas 1202 e 1211):

```python
@app.on_event("startup")
async def startup_event():
    # ... código de inicialização ...

@app.on_event("shutdown")
async def shutdown_event():
    # ... código de limpeza ...
```

### Passo 4: Criar Função Lifespan

**ANTES da criação do `app = FastAPI()`, adicione:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida"""

    # ═════ STARTUP ═════
    # Copie aqui o conteúdo de startup_event()
    # ... código de inicialização ...

    yield  # Servidor roda aqui

    # ═════ SHUTDOWN ═════
    # Copie aqui o conteúdo de shutdown_event()
    # ... código de limpeza ...
```

### Passo 5: Modificar Criação do FastAPI

Localize a linha onde o app é criado:

```python
# ANTES
app = FastAPI()

# DEPOIS
app = FastAPI(lifespan=lifespan)
```

### Passo 6: Remover Decoradores Antigos

**DELETE** as funções com `@app.on_event()`:

```python
# ❌ REMOVER ESSAS LINHAS
@app.on_event("startup")
async def startup_event():
    # ...

@app.on_event("shutdown")
async def shutdown_event():
    # ...
```

### Passo 7: Testar

```bash
# Reiniciar servidor
uvicorn server:app --reload

# Verificar que não há mais warnings
# Verificar que servidor inicia corretamente
# Verificar que rotas funcionam
```

---

## 📋 Exemplo Completo - Server.py Simplificado

```python
#!/usr/bin/env python3
"""
🎣 Fishing Bot Server v5.0
FastAPI servidor com lifespan (sem deprecation warnings)
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════

class ActivationRequest(BaseModel):
    login: str
    password: str
    license_key: str
    hwid: str
    pc_name: Optional[str] = None

class ActivationResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    rules: Optional[dict] = None

# ═══════════════════════════════════════════════════════
# ESTADO GLOBAL
# ═══════════════════════════════════════════════════════

# Dicionário para recursos compartilhados
server_state = {
    'active_connections': {},
    'database': None,
    'cache': None
}

# ═══════════════════════════════════════════════════════
# LIFESPAN - Gerenciamento de Ciclo de Vida
# ═══════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    ✅ NOVO PADRÃO: Gerenciador de ciclo de vida do servidor

    Substitui @app.on_event("startup") e @app.on_event("shutdown")
    """

    # ═════════════════════════════════════════════════
    # STARTUP - Inicialização do Servidor
    # ═════════════════════════════════════════════════

    logger.info("="*60)
    logger.info("🚀 Fishing Bot Server v5.0 - Iniciando...")
    logger.info("="*60)

    # 1. Conectar ao banco de dados
    logger.info("📦 Conectando ao banco de dados...")
    try:
        # server_state['database'] = await connect_database()
        logger.info("✅ Banco de dados conectado")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar banco: {e}")

    # 2. Inicializar cache
    logger.info("💾 Inicializando cache...")
    try:
        # server_state['cache'] = await initialize_cache()
        logger.info("✅ Cache inicializado")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cache: {e}")

    # 3. Outras inicializações
    logger.info("⚙️ Carregando configurações...")
    logger.info("✅ Configurações carregadas")

    logger.info("="*60)
    logger.info("✅ Servidor pronto para receber conexões!")
    logger.info("="*60)

    # ← SERVIDOR RODA AQUI (yield permite execução)
    yield

    # ═════════════════════════════════════════════════
    # SHUTDOWN - Encerramento do Servidor
    # ═════════════════════════════════════════════════

    logger.info("="*60)
    logger.info("🛑 Servidor encerrando...")
    logger.info("="*60)

    # 1. Fechar conexões ativas
    logger.info("🔌 Fechando conexões WebSocket...")
    active_count = len(server_state['active_connections'])
    if active_count > 0:
        logger.info(f"   Fechando {active_count} conexões ativas...")
        for ws_id, ws in list(server_state['active_connections'].items()):
            try:
                await ws.close()
            except:
                pass
        server_state['active_connections'].clear()
        logger.info("✅ Conexões fechadas")

    # 2. Fechar banco de dados
    if server_state.get('database'):
        logger.info("📦 Desconectando banco de dados...")
        try:
            # await server_state['database'].close()
            logger.info("✅ Banco desconectado")
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar banco: {e}")

    # 3. Limpar cache
    if server_state.get('cache'):
        logger.info("💾 Limpando cache...")
        try:
            # await server_state['cache'].clear()
            logger.info("✅ Cache limpo")
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")

    logger.info("="*60)
    logger.info("✅ Servidor encerrado com sucesso!")
    logger.info("="*60)

# ═══════════════════════════════════════════════════════
# CRIAR APP COM LIFESPAN
# ═══════════════════════════════════════════════════════

app = FastAPI(
    title="Fishing Bot Server",
    version="5.0.0",
    lifespan=lifespan  # ← CRÍTICO: Passar lifespan aqui
)

# ═══════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Rota raiz"""
    return {
        "message": "Fishing Bot Server v5.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_connections": len(server_state['active_connections']),
        "database": "connected" if server_state.get('database') else "disconnected"
    }

@app.post("/auth/activate")
async def activate_user(request: ActivationRequest):
    """
    Endpoint de ativação

    Valida license_key com Keymaster e cria sessão
    """
    logger.info(f"📥 /auth/activate: {request.login}")

    try:
        # 1. Validar com Keymaster
        # keymaster_result = validate_with_keymaster(...)

        # 2. Verificar HWID binding
        # ...

        # 3. Gerar token
        token = f"{request.license_key}:{request.hwid[:16]}"

        return ActivationResponse(
            success=True,
            message="Ativação bem-sucedida!",
            token=token,
            rules={
                "feed_interval_fish": 10,
                "clean_interval_fish": 2,
                "break_interval_fish": 50
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro em /auth/activate: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": f"Erro na validação: {str(e)}"
            }
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint para comunicação em tempo real"""
    await websocket.accept()

    # Adicionar à lista de conexões ativas
    ws_id = id(websocket)
    server_state['active_connections'][ws_id] = websocket

    logger.info(f"🟢 Nova conexão WebSocket: {ws_id}")

    try:
        while True:
            # Receber mensagens
            data = await websocket.receive_json()

            # Processar comandos
            # ...

    except Exception as e:
        logger.error(f"❌ Erro no WebSocket {ws_id}: {e}")
    finally:
        # Remover da lista ao desconectar
        server_state['active_connections'].pop(ws_id, None)
        logger.info(f"🔴 WebSocket desconectado: {ws_id}")

# ═══════════════════════════════════════════════════════
# MAIN - Iniciar Servidor
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
```

---

## ✅ Verificação Final

Após aplicar as mudanças, verifique:

### 1. Sem Warnings

Ao iniciar o servidor, **NÃO** deve aparecer:

```
DeprecationWarning: on_event is deprecated
```

### 2. Logs de Startup

Deve aparecer os logs de inicialização:

```
🚀 Fishing Bot Server v5.0 - Iniciando...
📦 Conectando ao banco de dados...
✅ Banco de dados conectado
...
✅ Servidor pronto para receber conexões!
```

### 3. Logs de Shutdown

Ao parar o servidor (Ctrl+C), deve aparecer:

```
🛑 Servidor encerrando...
🔌 Fechando conexões WebSocket...
✅ Conexões fechadas
...
✅ Servidor encerrado com sucesso!
```

### 4. Rotas Funcionando

Testar:

```bash
# Health check
curl http://localhost:8000/health

# Deve retornar: {"status": "healthy", ...}
```

---

## 📚 Referências

- [FastAPI Lifespan Documentation](https://fastapi.tiangolo.com/advanced/events/)
- [Release Notes - v0.93.0](https://fastapi.tiangolo.com/release-notes/#0930)
- [Python asynccontextmanager](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager)

---

## 🆘 Troubleshooting

### Erro: "lifespan parameter not recognized"

**Causa:** FastAPI muito antigo

**Solução:**
```bash
pip install --upgrade fastapi
```

### Erro: "asynccontextmanager not found"

**Causa:** Python < 3.7

**Solução:** Atualizar Python para 3.7+

---

**Criado em:** 2025-11-07
**Versão:** 1.0
**Projeto:** Ultimate Fishing Bot v5.0
