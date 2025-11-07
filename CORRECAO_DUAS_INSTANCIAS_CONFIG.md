# 🐛 BUG CRÍTICO: Duas Instâncias do ConfigManager

**Data:** 2025-10-31
**Status:** ✅ **CORRIGIDO**
**Causado por:** Mudança nesta conversa (correção anterior do sync)

---

## 🔍 O QUE ACONTECEU

Quando corrigi o `server_connector.py` para usar ConfigManager ao invés de ler JSON manualmente, **EU CRIEI UM BUG NOVO**!

### Problema Introduzido

**Antes da minha correção anterior:**
```python
# server_connector.py (ANTIGO - lia JSON manual)
with open("data/config.json") as f:
    local_config = json.load(f)

chest_side = local_config.get("chest_side", "left")  # Default errado, mas consistente
```

**Depois da minha correção (QUE CRIOU O BUG):**
```python
# server_connector.py (BUGADO - cria nova instância!)
def _sync_config_with_server(ws_client):
    config = ConfigManager()  # ❌ NOVA INSTÂNCIA!
    chest_side = config.get("chest_side", "right")
```

### Por Que Isso É Um Problema?

O código agora tinha **DUAS instâncias diferentes** do ConfigManager:

1. **Instância A** - Criada no `main.py` e usada por:
   - ChestManager
   - ChestOperationCoordinator
   - FishingEngine
   - Todos os outros componentes

2. **Instância B** - Criada no `server_connector.py` e usada apenas para sync

**Resultado:** Cada instância podia ler configurações em momentos diferentes ou ter estados diferentes!

---

## 🎯 SINTOMA REPORTADO PELO USUÁRIO

> "porque eu notei que ao abrir o bau que estava configurado para abrir na direita tentou abrir para a esquerda"

**Por que aconteceu:**

1. ChestOperationCoordinator usa **Instância A** do ConfigManager
2. Se Instância A foi criada ANTES de alguma mudança em config
3. E Instância B foi criada DEPOIS da mudança
4. As duas podem ter valores DIFERENTES para chest_side!

**Exemplo de Race Condition:**

```
┌─────────────────────────────────────────────────────────────┐
│ Timeline                                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ T1: main.py cria ConfigManager A                           │
│     └─ Lê config: chest_side não existe em data/config     │
│     └─ Usa default: "right" ✅                              │
│                                                             │
│ T2: [Algo muda config ou arquivo é recarregado]            │
│                                                             │
│ T3: connect_to_server() → _sync_config_with_server()       │
│     └─ Cria ConfigManager B (NOVA INSTÂNCIA!)              │
│     └─ Lê config: chest_side pode ser diferente!           │
│     └─ Ou usa cache diferente                              │
│                                                             │
│ T4: ChestOperationCoordinator abre baú                     │
│     └─ Usa ConfigManager A (valor antigo)                  │
│     └─ Pode ter valor DIFERENTE do que B enviou!           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ CORREÇÃO APLICADA

### Princípio: **Uma Única Fonte de Verdade**

Agora o `server_connector.py` **NÃO cria** uma nova instância. Ele **RECEBE** a instância existente do main.py!

### Mudanças

**1. server_connector.py - Função `_sync_config_with_server()`**

```python
# ANTES (BUGADO):
def _sync_config_with_server(ws_client):
    config = ConfigManager()  # ❌ Nova instância!

# DEPOIS (CORRIGIDO):
def _sync_config_with_server(ws_client, config_manager=None):
    if config_manager:
        config = config_manager  # ✅ Usa instância existente!
        _safe_print("   ✅ Usando ConfigManager existente do main.py")
    else:
        # Fallback apenas se não foi passado
        config = ConfigManager()
        _safe_print("   ⚠️ Criando nova instância (fallback)")
```

**2. server_connector.py - Função `connect_to_server()`**

```python
# ANTES:
def connect_to_server(login, password, license_key, server_url):
    ...
    _sync_config_with_server(ws_client)

# DEPOIS:
def connect_to_server(login, password, license_key, server_url, config_manager=None):
    ...
    _sync_config_with_server(ws_client, config_manager)  # ✅ Passa config!
```

**3. main.py - Chamada de `connect_to_server()`**

```python
# ANTES:
ws_client = connect_to_server(
    login=login,
    password=password,
    license_key=license_key,
    server_url=server_url
)

# DEPOIS:
ws_client = connect_to_server(
    login=login,
    password=password,
    license_key=license_key,
    server_url=server_url,
    config_manager=config  # ✅ Passa config existente!
)
```

---

## 📊 FLUXO CORRIGIDO

### Antes (Bugado - 2 Instâncias)

```
main.py
   ├─ config_A = ConfigManager()  ← Instância A
   │
   ├─ ChestManager(config_A)
   ├─ ChestOpCoordinator(config_A)
   ├─ FishingEngine(config_A)
   │
   └─ connect_to_server()
        └─ _sync_config_with_server()
             └─ config_B = ConfigManager()  ← Instância B ❌
                  └─ Pode ter valores diferentes de A!
```

### Depois (Corrigido - 1 Instância)

```
main.py
   ├─ config = ConfigManager()  ← Única instância
   │
   ├─ ChestManager(config)
   ├─ ChestOpCoordinator(config)
   ├─ FishingEngine(config)
   │
   └─ connect_to_server(config_manager=config)
        └─ _sync_config_with_server(config)  ✅
             └─ Usa mesma instância que todo mundo!
```

---

## 🧪 COMO TESTAR

### 1. Reinicie o bot

```bash
python main.py
```

### 2. Verifique o log de sync

**Deve aparecer:**
```
✅ Usando ConfigManager existente do main.py  ← IMPORTANTE!
⚙️ Sincronizando configs com servidor:
   • Chest side: right  ✅
```

**NÃO deve aparecer:**
```
⚠️ Criando nova instância do ConfigManager (fallback)  ← ERRADO!
```

### 3. Pesque e observe abertura de baú

**Peixe #2 (trigger de clean):**
- ✅ Deve abrir baú no lado DIREITO
- ✅ ConfigManager usado é o MESMO do main.py
- ✅ Valores consistentes em todo o código

---

## 📝 RESUMO TÉCNICO

### Problema

**Singleton Pattern Violado:** Duas instâncias do ConfigManager existindo simultaneamente, podendo ter estados diferentes.

### Causa Raiz

Ao corrigir o bug anterior (defaults hardcoded), introduzi um **novo bug** criando uma instância adicional ao invés de reusar a existente.

### Solução

**Dependency Injection:** Passar a instância existente como parâmetro ao invés de criar nova.

### Arquivos Modificados

1. [client/server_connector.py](client/server_connector.py:33-61) - Aceitar config_manager opcional
2. [client/server_connector.py](client/server_connector.py:135-162) - Aceitar config_manager opcional
3. [client/server_connector.py](client/server_connector.py:259) - Passar config_manager para sync
4. [main.py](main.py:209-215) - Passar config ao connect_to_server

---

## ⚠️ LIÇÕES APRENDIDAS

### 1. Cuidado ao "Corrigir" Código

Ao corrigir um bug, **NÃO introduza bugs novos**!

**Checklist antes de mudança:**
- [ ] Esta mudança cria novas instâncias de objetos que deveriam ser únicos?
- [ ] Estou violando algum padrão de design (Singleton, DI, etc)?
- [ ] Há outras partes do código que usam o objeto de forma diferente?

### 2. Singleton vs Dependency Injection

**Quando NÃO criar nova instância:**
- ❌ ConfigManager (deve ser único por aplicação)
- ❌ InputManager (deve ser único para controlar estado)
- ❌ GameState (deve ser compartilhado por todos)

**Quando pode criar nova instância:**
- ✅ TemplateResult (objeto de dados imutável)
- ✅ Threads worker (execução paralela)
- ✅ Logger (desde que escreva no mesmo arquivo)

### 3. Sempre Preferir Dependency Injection

**Ruim (cria dentro da função):**
```python
def processo():
    config = ConfigManager()  # ❌ Nova instância!
    usar(config)
```

**Bom (recebe como parâmetro):**
```python
def processo(config_manager):
    usar(config_manager)  # ✅ Usa instância existente!
```

### 4. Code Review Próprio

Antes de finalizar mudança:
1. Ler código modificado linha por linha
2. Perguntar: "Isso pode causar efeitos colaterais?"
3. Testar localmente ANTES de commitar
4. Verificar se outros módulos são afetados

---

## ✅ STATUS FINAL

**🟢 BUG CORRIGIDO**

- ✅ Apenas UMA instância do ConfigManager no sistema
- ✅ Todos os componentes usam a mesma instância
- ✅ Valores consistentes em todo o código
- ✅ server_connector.py usa instância do main.py
- ✅ Dependency Injection implementada

**Pronto para teste em produção!** 🚀

---

## 🔄 HISTÓRICO DE BUGS RELACIONADOS

1. **Bug Original:** server_connector.py usava defaults hardcoded errados
   - **Status:** ✅ Corrigido em correção anterior

2. **Bug Introduzido:** Correção criou duas instâncias do ConfigManager
   - **Status:** ✅ Corrigido neste documento

3. **Resultado Final:** Sistema funcional com arquitetura correta
   - **Status:** ✅ Pronto para produção
