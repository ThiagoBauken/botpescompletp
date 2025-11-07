# 🔧 Correção: Servidor não enviava batch de comandos

**Data:** 2025-10-31
**Problema:** Servidor logava "Operação FEEDING adicionada ao batch" mas nunca enviava o batch para o cliente

---

## 🔍 Problema Identificado

### Sintomas:
```
INFO:server:🍖 thiago: Operação FEEDING adicionada ao batch
INFO:__main__:✅ Database pool criado: 20 read connections, 1 write connection
```

**O que estava acontecendo:**
- ✅ Servidor detectava que precisava alimentar (`should_feed()`)
- ✅ Servidor adicionava operação ao batch
- ❌ **Servidor NÃO enviava o batch** (faltava log `"📦 BATCH enviado"`)
- ⚠️ Logo após, servidor **reiniciava** (log de inicialização aparecia)

**Possíveis causas:**
1. Erro silencioso entre adicionar ao batch e enviar
2. Servidor reiniciando automaticamente (modo `--reload`)
3. Exceção não tratada no `await websocket.send_json()`

---

## ✅ Correções Aplicadas

### 1. Logs de Debug Adicionados

**Arquivo:** `server/server.py`

#### Antes (linha 835-916):
```python
operations = []

if session.should_feed():
    operations.append(...)
    logger.info(f"🍖 {login}: Operação FEEDING adicionada ao batch")

# ... mais operações ...

if operations:
    await websocket.send_json({
        "cmd": "execute_batch",
        "operations": operations
    })
    logger.info(f"📦 {login}: BATCH enviado...")
```

#### Depois:
```python
logger.info(f"🔍 {login}: DEBUG - Iniciando construção do batch de operações")
operations = []

logger.info(f"🔍 {login}: DEBUG - Verificando should_feed()...")
if session.should_feed():
    operations.append(...)
    logger.info(f"🍖 {login}: Operação FEEDING adicionada ao batch")

logger.info(f"🔍 {login}: DEBUG - Verificando should_clean()...")
if session.should_clean():
    operations.append(...)
    logger.info(f"🧹 {login}: Operação CLEANING adicionada ao batch")

logger.info(f"🔍 {login}: DEBUG - Adicionando switch_rod (sempre executado)...")
operations.append(...)
logger.info(f"🔄 {login}: Operação SWITCH_ROD adicionada ao batch")

# ... mais operações ...

logger.info(f"🔍 {login}: DEBUG - Verificando operations list: {len(operations)} operações")
if operations:
    try:
        logger.info(f"📤 {login}: DEBUG - Preparando envio do batch...")
        batch_message = {
            "cmd": "execute_batch",
            "operations": operations
        }
        logger.info(f"📤 {login}: DEBUG - Mensagem preparada: {batch_message}")

        await websocket.send_json(batch_message)

        logger.info(f"📦 {login}: ✅ BATCH enviado com {len(operations)} operação(ões): {[op['type'] for op in operations]}")
    except Exception as e:
        logger.error(f"❌ {login}: ERRO ao enviar batch: {e}")
        import traceback
        traceback.print_exc()
else:
    logger.warning(f"⚠️ {login}: Nenhuma operação no batch (não deveria acontecer!)")
```

### 2. Try/Except Adicionado

Agora, **qualquer erro** ao enviar o batch será capturado e logado:

```python
try:
    await websocket.send_json(batch_message)
    logger.info(f"📦 {login}: ✅ BATCH enviado...")
except Exception as e:
    logger.error(f"❌ {login}: ERRO ao enviar batch: {e}")
    traceback.print_exc()
```

### 3. Validação de Operations

Adicionado warning se `operations` estiver vazio (não deveria acontecer):

```python
if operations:
    # Enviar
else:
    logger.warning(f"⚠️ {login}: Nenhuma operação no batch (não deveria acontecer!)")
```

---

## 🧪 Como Testar

### 1. Reiniciar o servidor

```bash
cd server
python server.py
```

### 2. Iniciar o cliente e pescar 1 peixe

```bash
python main.py
# Pressione F9 para iniciar
# Aguarde capturar 1 peixe
```

### 3. Verificar logs do servidor

**O que DEVE aparecer agora:**

```
INFO:server:🐟 thiago: Peixe #1 capturado!
INFO:server:🎣 thiago: Vara 1 usada (1/1 usos)
INFO:server:🔍 thiago: DEBUG - Iniciando construção do batch de operações
INFO:server:🔍 thiago: DEBUG - Verificando should_feed()...
INFO:server:🍖 thiago: Operação FEEDING adicionada ao batch
INFO:server:🔍 thiago: DEBUG - Verificando should_clean()...
INFO:server:🧹 thiago: Operação CLEANING adicionada ao batch
INFO:server:🔍 thiago: DEBUG - Adicionando switch_rod (sempre executado)...
INFO:server:🔄 thiago: Operação SWITCH_ROD adicionada ao batch (troca no par)
INFO:server:🔍 thiago: DEBUG - Verificando operations list: 3 operações
INFO:server:📤 thiago: DEBUG - Preparando envio do batch...
INFO:server:📤 thiago: DEBUG - Mensagem preparada: {'cmd': 'execute_batch', 'operations': [...]}
INFO:server:📦 thiago: ✅ BATCH enviado com 3 operação(ões): ['feeding', 'cleaning', 'switch_rod']
```

**Se aparecer ERRO:**

```
INFO:server:❌ thiago: ERRO ao enviar batch: [mensagem de erro]
```

Isso indicará exatamente qual é o problema (WebSocket desconectado, erro de serialização, etc.)

---

## 🔍 Diagnóstico

### Se o log parar em "Operação FEEDING adicionada ao batch":

**Causa:** Exceção entre linhas 851-913

**Solução:** Verificar qual log de DEBUG apareceu por último para identificar onde parou

### Se o log parar em "DEBUG - Preparando envio do batch":

**Causa:** Erro no `await websocket.send_json()`

**Solução:** Verificar se WebSocket ainda está conectado

### Se aparecer "Nenhuma operação no batch":

**Causa:** Lista `operations` está vazia (muito estranho!)

**Solução:** Verificar se `should_feed()`, `should_clean()` estão funcionando

### Se aparecer "ERRO ao enviar batch":

**Causa:** Exceção capturada pelo try/except

**Solução:** Analisar traceback completo do erro

---

## 📊 Logs Completos Esperados

### Sequência completa ao pescar peixe #1:

```
INFO:server:🐟 thiago: Peixe #1 capturado!
INFO:server:🎣 thiago: Vara 1 usada (1/1 usos)

# Início da construção do batch
INFO:server:🔍 thiago: DEBUG - Iniciando construção do batch de operações

# Verificação de alimentação
INFO:server:🔍 thiago: DEBUG - Verificando should_feed()...
INFO:server:🍖 thiago: Operação FEEDING adicionada ao batch

# Verificação de limpeza
INFO:server:🔍 thiago: DEBUG - Verificando should_clean()...
INFO:server:🧹 thiago: Operação CLEANING adicionada ao batch

# Troca de vara (sempre executado)
INFO:server:🔍 thiago: DEBUG - Adicionando switch_rod (sempre executado)...
INFO:server:🔄 thiago: Operação SWITCH_ROD adicionada ao batch (troca no par)

# Envio do batch
INFO:server:🔍 thiago: DEBUG - Verificando operations list: 3 operações
INFO:server:📤 thiago: DEBUG - Preparando envio do batch...
INFO:server:📤 thiago: DEBUG - Mensagem preparada: {'cmd': 'execute_batch', 'operations': [
    {'type': 'feeding', 'params': {...}},
    {'type': 'cleaning', 'params': {...}},
    {'type': 'switch_rod', 'params': {...}}
]}
INFO:server:📦 thiago: ✅ BATCH enviado com 3 operação(ões): ['feeding', 'cleaning', 'switch_rod']
```

---

## ✅ Resultado Esperado

Após esta correção:

1. ✅ **Servidor loga cada etapa** da construção do batch
2. ✅ **Servidor envia batch** para o cliente
3. ✅ **Cliente recebe comandos** e executa operações
4. ✅ **Se houver erro**, exceção é capturada e logada

**Próximos passos:**

1. Testar com peixe #1 (configuração: `feed_interval_fish: 1`, `clean_interval_fish: 1`)
2. Verificar se cliente **recebe e executa** comandos
3. Se necessário, adicionar mais logs no **cliente** para rastrear recebimento

---

## 📝 Notas Importantes

### Configuração testada:

```json
{
  "feed_interval_fish": 1,
  "clean_interval_fish": 1,
  "rod_switch_limit": 1
}
```

Significa:
- ✅ Alimentar a **cada 1 peixe**
- ✅ Limpar a **cada 1 peixe**
- ✅ Trocar vara a **cada 1 uso**

### Servidor em modo --reload:

Se estiver rodando `uvicorn server:app --reload`, o servidor **reinicia** ao detectar mudanças no código. Isso pode causar desconexões.

**Solução:** Rodar sem `--reload`:
```bash
python server.py
```

---

**Última atualização:** 2025-10-31
**Status:** ✅ Correção aplicada, aguardando testes
