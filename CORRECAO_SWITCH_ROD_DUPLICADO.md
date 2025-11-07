# 🔧 Correção: Switch Rod Duplicado

## 🐛 Problema Identificado

**Sintoma:**
```
1. ChestOperationCoordinator equipou vara 2 (baseado em usos) ✅
2. _on_batch_complete() executou switch_rod pendente
3. Trocou de volta para vara 1 ❌
4. Cliente pescou com vara errada ❌
```

**Logs do Problema:**
```
✅ Vara 2 equipada e tracking atualizado (botão direito segurado)!
======================================================================

🔔 [CALLBACK] Batch completado - processando finalização...
🔄 [PASSO 1] Executando switch_rod pendente...
📍 Par 1: (1, 2)
   Vara atual: 2 → Próxima: 1
✅ Troca para vara 1 executada (botão direito segurado)!
```

---

## 🎯 Causa Raiz

Quando o batch continha **operações de baú + switch_rod**:

1. **ChestOperationCoordinator** equipava a vara corretamente (baseado em usos)
2. **Mas depois**, `_on_batch_complete()` executava o `switch_rod` pendente
3. Isso **desfazia** a escolha correta do ChestOperationCoordinator!

**Conflito de Responsabilidades:**
- **ChestOperationCoordinator:** Escolhe vara baseado em usos após operações de baú
- **switch_rod:** Troca para próxima vara do par (sem abrir baú)

Ambos executavam, causando troca dupla!

---

## ✅ Solução Implementada

### 1. Nova Flag: `had_chest_operations`

**Arquivo:** `core/fishing_engine.py:233`
```python
self.had_chest_operations = False  # Flag para indicar se batch teve operações de baú
```

### 2. Marcar Flag ao Processar Batch

**Arquivo:** `core/fishing_engine.py:1831-1836`
```python
# ✅ MARCAR: Se houve operações de baú
self.had_chest_operations = (operations_added > 0)
if self.had_chest_operations:
    _safe_print(f"🏪 [FLAG] had_chest_operations = True ({operations_added} operações de baú)")
else:
    _safe_print(f"🏪 [FLAG] had_chest_operations = False (sem operações de baú)")
```

### 3. Decisão Condicional em `_on_batch_complete()`

**Arquivo:** `core/fishing_engine.py:1680-1701`
```python
if self.pending_switch_rod_callback:
    if self.had_chest_operations:
        # ❌ NÃO executar switch_rod - ChestCoordinator JÁ escolheu vara
        _safe_print("   ⚠️ MAS houve operações de baú - ChestCoordinator JÁ escolheu a vara correta!")
        _safe_print("   ❌ NÃO executar switch_rod - vara já foi equipada pelo ChestCoordinator")
    else:
        # ✅ EXECUTAR switch_rod - sem operações de baú
        _safe_print("   ℹ️ SEM operações de baú - switch_rod deve ser executado")
        success = self.pending_switch_rod_callback()
```

---

## 📊 Cenários de Teste

### Cenário 1: Feeding + Cleaning + Switch Rod

**Batch do Servidor:**
```python
[
    {"type": "feeding"},
    {"type": "cleaning"},
    {"type": "switch_rod"}
]
```

**Comportamento Esperado:**
1. Cliente marca: `had_chest_operations = True`
2. ChestCoordinator executa feeding + cleaning
3. ChestCoordinator escolhe vara 2 (baseado em usos)
4. `_on_batch_complete()` detecta `had_chest_operations = True`
5. **NÃO executa** switch_rod pendente
6. Cliente pesca com vara 2 ✅

**Logs Esperados:**
```
🏪 [FLAG] had_chest_operations = True (2 operações de baú)
   ⚠️ IMPORTANTE: switch_rod NÃO será executado (ChestCoordinator escolhe vara)

[ChestCoordinator executa e equipa vara 2]

🔔 [CALLBACK] Batch completado - processando finalização...
🔄 [PASSO 1] switch_rod pendente detectado
   ⚠️ MAS houve operações de baú - ChestCoordinator JÁ escolheu a vara correta!
   ❌ NÃO executar switch_rod - vara já foi equipada pelo ChestCoordinator
   🎯 Mantendo vara escolhida pelo ChestCoordinator (baseado em usos)
```

---

### Cenário 2: Apenas Switch Rod (Sem Operações de Baú)

**Batch do Servidor:**
```python
[
    {"type": "switch_rod"}
]
```

**Comportamento Esperado:**
1. Cliente marca: `had_chest_operations = False`
2. ChestCoordinator NÃO executa (sem operações)
3. `_on_batch_complete()` detecta `had_chest_operations = False`
4. **EXECUTA** switch_rod pendente
5. Cliente troca vara 1 → vara 2 ✅

**Logs Esperados:**
```
🏪 [FLAG] had_chest_operations = False (sem operações de baú)
⚡ [EDGE CASE] Apenas switch_rod no batch - executando imediatamente!

🔔 [CALLBACK] Batch completado - processando finalização...
🔄 [PASSO 1] Executando switch_rod pendente...
   ℹ️ SEM operações de baú - switch_rod deve ser executado
   ✅ Switch rod executado com sucesso
```

---

### Cenário 3: Apenas Operações de Baú (Sem Switch Rod)

**Batch do Servidor:**
```python
[
    {"type": "feeding"},
    {"type": "cleaning"}
]
```

**Comportamento Esperado:**
1. Cliente marca: `had_chest_operations = True`
2. ChestCoordinator executa feeding + cleaning
3. ChestCoordinator escolhe vara
4. `_on_batch_complete()` não tem switch_rod pendente
5. Cliente pesca normalmente ✅

**Logs Esperados:**
```
🏪 [FLAG] had_chest_operations = True (2 operações de baú)

[ChestCoordinator executa e equipa vara]

🔔 [CALLBACK] Batch completado - processando finalização...
ℹ️ [PASSO 1] Nenhum switch_rod pendente
```

---

## 🔒 Lógica de Decisão

### Tabela de Decisão

| Operações de Baú | switch_rod no Batch | Ação do ChestCoordinator | Ação do _on_batch_complete |
|------------------|---------------------|--------------------------|---------------------------|
| ✅ Sim           | ✅ Sim              | Escolhe vara baseado em usos | ❌ NÃO executa switch_rod |
| ✅ Sim           | ❌ Não              | Escolhe vara baseado em usos | ⏭️ Sem switch_rod pendente |
| ❌ Não           | ✅ Sim              | ⏭️ Não executa            | ✅ EXECUTA switch_rod     |
| ❌ Não           | ❌ Não              | ⏭️ Não executa            | ⏭️ Sem switch_rod pendente |

### Fluxograma

```
┌─────────────────────────────────────┐
│ Cliente recebe batch do servidor    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ Separar operações de baú de switch  │
│ - chest_operations = []             │
│ - switch_rod_op = None              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│ operations_added > 0?               │
└─────────────────────────────────────┘
       ↓ SIM              ↓ NÃO
┌──────────────┐   ┌──────────────────┐
│ had_chest_   │   │ had_chest_       │
│ operations   │   │ operations       │
│ = True       │   │ = False          │
└──────────────┘   └──────────────────┘
       ↓                    ↓
┌──────────────┐   ┌──────────────────┐
│ ChestCoord   │   │ _on_batch_       │
│ executa e    │   │ complete()       │
│ escolhe vara │   │ executa          │
│              │   │ switch_rod       │
└──────────────┘   └──────────────────┘
       ↓
┌──────────────┐
│ _on_batch_   │
│ complete()   │
│ NÃO executa  │
│ switch_rod   │
└──────────────┘
       ↓
┌─────────────────────────────────────┐
│ Cliente volta ao estado FISHING     │
│ com vara CORRETA                    │
└─────────────────────────────────────┘
```

---

## ✅ Garantias

1. **ChestOperationCoordinator sempre escolhe vara correta** quando há operações de baú
2. **switch_rod só executa quando NÃO há operações de baú** (troca simples no par)
3. **Sem trocas duplicadas** - apenas UMA escolha de vara por batch
4. **Prioridade para ChestOperationCoordinator** - escolha baseada em usos é mais inteligente

---

## 📝 Arquivos Modificados

1. `core/fishing_engine.py`
   - Linha 233: Adicionada flag `had_chest_operations`
   - Linhas 1680-1721: Modificado `_on_batch_complete()` para verificar flag
   - Linhas 1831-1846: Marcação da flag ao processar batch

---

**Data:** 2025-10-29
**Status:** ✅ CORRIGIDO
**Teste:** Pendente (aguardando próxima captura de peixe)
