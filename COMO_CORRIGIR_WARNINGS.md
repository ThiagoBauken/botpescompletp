# 🚀 Como Corrigir os Warnings do FastAPI - Guia Rápido

## ⚡ Método Automático (Recomendado)

### Passo 1: Copiar o script para o servidor

Se o servidor está no Docker/Easypanel:

```bash
# Fazer SSH no servidor
ssh usuario@seu-servidor

# Ou acessar terminal do container no Easypanel
```

### Passo 2: Executar o script de correção

```bash
# Baixar o script
wget https://raw.githubusercontent.com/ThiagoBauken/botpescompletp/claude/debug-and-analyze-011CUtzVUpPtyKB2FUopKuVP/fix_fastapi_deprecation.py

# Ou copiar manualmente o arquivo fix_fastapi_deprecation.py para o servidor

# Executar correção
python fix_fastapi_deprecation.py /app/server.py

# Ou se estiver em outro local:
python fix_fastapi_deprecation.py /caminho/para/server.py
```

### Passo 3: Reiniciar servidor

```bash
# Docker
docker restart nome-do-container

# Ou no Easypanel: Services → Seu serviço → Restart
```

### Passo 4: Verificar

Logs devem mostrar:
```
✅ Banco de dados inicializado (HWID bindings)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**SEM** warnings de DeprecationWarning!

---

## 🔧 Método Manual (Se preferir)

### Passo 1: Backup

```bash
cp /app/server.py /app/server.py.backup
```

### Passo 2: Editar server.py

Abrir `/app/server.py` e fazer as seguintes mudanças:

#### 2.1. Adicionar import (próximo aos outros imports do FastAPI)

```python
from contextlib import asynccontextmanager
```

#### 2.2. Localizar as linhas 1202-1211 e substituir

**REMOVER (linhas ~1202-1211):**

```python
@app.on_event("startup")
async def startup_event():
    # ... código de inicialização ...
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # ... código de limpeza ...
    pass
```

**ADICIONAR no lugar:**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciador de ciclo de vida do servidor"""

    # ═══════ STARTUP ═══════
    # Copiar aqui o código que estava em startup_event()
    # ... código de inicialização ...

    yield  # Servidor roda aqui

    # ═══════ SHUTDOWN ═══════
    # Copiar aqui o código que estava em shutdown_event()
    # ... código de limpeza ...
```

#### 2.3. Modificar criação do FastAPI

Localizar linha onde `app = FastAPI(...)` é criado e adicionar `lifespan=lifespan`:

**ANTES:**
```python
app = FastAPI()
```

**DEPOIS:**
```python
app = FastAPI(lifespan=lifespan)
```

Ou se já tem outros parâmetros:

**ANTES:**
```python
app = FastAPI(
    title="Fishing Bot Server",
    version="2.0.0"
)
```

**DEPOIS:**
```python
app = FastAPI(
    title="Fishing Bot Server",
    version="2.0.0",
    lifespan=lifespan
)
```

### Passo 3: Salvar e reiniciar

```bash
# Salvar arquivo (Ctrl+O no nano, :wq no vim)

# Reiniciar servidor
docker restart nome-do-container
```

---

## ✅ Como Verificar que Funcionou

### 1. Logs do Servidor

**ANTES (com warnings):**
```
INFO:__main__:✅ Banco de dados inicializado (HWID bindings)
/app/server.py:1202: DeprecationWarning:  ← ❌ Aparece aqui
        on_event is deprecated, use lifespan event handlers instead.
  @app.on_event("startup")
/app/server.py:1211: DeprecationWarning:  ← ❌ Aparece aqui
        on_event is deprecated, use lifespan event handlers instead.
  @app.on_event("shutdown")
```

**DEPOIS (sem warnings):**
```
INFO:__main__:✅ Banco de dados inicializado (HWID bindings)
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000  ← ✅ Sem warnings!
```

### 2. Servidor Continua Funcionando

```bash
# Testar health check
curl http://localhost:8000/health

# Deve retornar:
{"service":"Fishing Bot Server","version":"2.0.0","status":"online",...}
```

---

## 🆘 Se Algo Der Errado

### Restaurar Backup

```bash
# Restaurar arquivo original
cp /app/server.py.backup /app/server.py

# Reiniciar
docker restart nome-do-container
```

### Verificar Erros

```bash
# Ver logs completos
docker logs nome-do-container

# Procurar por:
# - SyntaxError
# - IndentationError
# - Import errors
```

### Pedir Ajuda

Se não funcionar, compartilhe:
1. Saída completa do script (se usou método automático)
2. Logs do servidor após reiniciar
3. Qual método usou (automático ou manual)

---

## 📋 Checklist

- [ ] Backup criado (`server.py.backup`)
- [ ] Script executado OU mudanças manuais aplicadas
- [ ] Arquivo salvo
- [ ] Servidor reiniciado
- [ ] Logs verificados (sem DeprecationWarning)
- [ ] Health check funcionando
- [ ] Cliente conecta normalmente

---

## 🎯 Resultado Esperado

Após a correção:
- ✅ Warnings desaparecem completamente
- ✅ Servidor inicia normalmente
- ✅ Funcionalidade permanece idêntica
- ✅ Código preparado para futuras versões do FastAPI

---

**Tempo estimado:** 2-5 minutos
**Dificuldade:** Baixa
**Risco:** Baixo (backup criado automaticamente)
