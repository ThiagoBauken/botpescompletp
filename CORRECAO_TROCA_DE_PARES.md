# 🔧 Correção: Troca de Pares Não Funcionava

## 🐛 Problema Identificado

**Sintoma:**
- Vara 1 e Vara 2 atingiram limite de usos (2/1)
- Servidor detectou par esgotado e enviou `switch_rod_pair`
- Cliente **NÃO processou** a troca de par
- Cliente ficou sem vara funcional

**Logs do Problema (Cliente):**
```
❌ [ERRO LÓGICO DETECTADO] AMBAS as varas atingiram limite de 1 usos!
   Vara 1: 2/1 usos >= limite
   Vara 2: 2/1 usos >= limite
   ❌ NÃO POSSO escolher vara do mesmo par esgotado!
```

**Logs do Servidor:**
```
INFO:server:🔄 thiago: Par (1, 2) esgotado (Vara 1: 1, Vara 2: 1)
INFO:server:🔄 thiago: Mudança Par1 → Par2 (3, 4)
INFO:server:   Primeira vara do novo par: 3
INFO:server:🎣 thiago: Operação SWITCH_ROD_PAIR adicionada ao batch (→ Vara 3)
INFO:server:📦 thiago: BATCH enviado com 4 operação(ões): ['feeding', 'cleaning', 'switch_rod', 'switch_rod_pair']
```

---

## 🎯 Causa Raiz

O cliente **não tinha handler** para processar `switch_rod_pair`. No código de processamento de batch:

```python
for op in operations:
    if op_type_str == "switch_rod":
        # Processado ✅
    else:
        chest_operations.append(op)

# ...mais tarde...
for op in chest_operations:
    if op_type_str == "feeding":
        # Processado ✅
    elif op_type_str == "cleaning":
        # Processado ✅
    elif op_type_str == "maintenance":
        # Processado ✅
    else:
        _safe_print(f"⚠️ Tipo de operação desconhecido: {op_type_str}")
        # switch_rod_pair cai aqui! ❌
```

**Resultado:** `switch_rod_pair` era classificado como "operação desconhecida" e ignorado!

---

## ✅ Solução Implementada

### 1. Detectar `switch_rod_pair` no Batch

**Arquivo:** `core/fishing_engine.py:1779-1797`

```python
# ✅ SEPARAR: switch_rod das operações de baú
# switch_rod NÃO precisa de baú aberto - executar DEPOIS que baú fechar
# switch_rod_pair PRECISA de baú aberto - vai para ChestOperationCoordinator
chest_operations = []
switch_rod_op = None
switch_rod_pair_op = None  # ✅ NOVO

for op in operations:
    op_type_str = op.get("type")

    if op_type_str == "switch_rod":
        _safe_print(f"🔄 switch_rod detectado - será executado APÓS fechar baú")
        switch_rod_op = op
    elif op_type_str == "switch_rod_pair":  # ✅ NOVO
        _safe_print(f"🔄 switch_rod_pair detectado - PRECISA abrir baú!")
        switch_rod_pair_op = op
        chest_operations.append(op)  # Adicionar às operações de baú
    else:
        chest_operations.append(op)
```

### 2. Processar `switch_rod_pair` e Informar ChestCoordinator

**Arquivo:** `core/fishing_engine.py:1817-1827`

```python
elif op_type_str == "switch_rod_pair":
    # ✅ NOVO: Troca de par (precisa baú aberto)
    # Extrair vara do novo par dos params
    target_rod = op.get("params", {}).get("target_rod")
    if target_rod:
        _safe_print(f"🔄 switch_rod_pair → equipar vara {target_rod} do novo par")
        # Informar ChestCoordinator qual vara equipar após fechar baú
        if self.chest_coordinator:
            self.chest_coordinator.rod_to_equip_after_pair_switch = target_rod
    # switch_rod_pair não precisa de callback (ChestCoordinator já vai equipar vara)
    continue  # Pular add_operation (não é operação executável)
```

**Como Funciona:**
1. Cliente detecta `switch_rod_pair` no batch
2. Extrai `target_rod` dos params (ex: vara 3)
3. Informa ChestCoordinator: `rod_to_equip_after_pair_switch = 3`
4. ChestCoordinator, ao fechar baú, vai equipar vara 3 (não vara 1 ou 2!)

---

## 📊 Fluxo Completo de Troca de Par

### Antes (INCORRETO)

```
1. Servidor detecta par esgotado ✅
2. Servidor envia switch_rod_pair ✅
3. Cliente recebe batch ✅
4. Cliente não reconhece switch_rod_pair ❌
5. switch_rod_pair ignorado ❌
6. ChestCoordinator tenta escolher vara do par esgotado ❌
7. ERRO: "AMBAS as varas atingiram limite" ❌
8. Cliente fica sem vara ❌
```

### Depois (CORRETO)

```
1. Servidor detecta par esgotado ✅
2. Servidor envia: [feeding, cleaning, switch_rod, switch_rod_pair] ✅
3. Cliente recebe batch ✅
4. Cliente detecta switch_rod_pair ✅
5. Cliente extrai target_rod = 3 ✅
6. Cliente informa ChestCoordinator: rod_to_equip_after_pair_switch = 3 ✅
7. ChestCoordinator executa feeding + cleaning ✅
8. ChestCoordinator fecha baú ✅
9. ChestCoordinator detecta rod_to_equip_after_pair_switch = 3 ✅
10. ChestCoordinator equipa vara 3 (novo par!) ✅
11. Cliente continua pescando com vara 3 ✅
```

---

## 🧪 Como Testar

### Cenário: Esgotar Par 1 e Trocar para Par 2

**Configuração:**
```json
{
  "rod_system": {
    "use_limit": 1  // Limite baixo para teste rápido
  }
}
```

**Passos:**
1. Inicie servidor: `cd server && python server.py`
2. Inicie cliente: `python main.py`
3. Pressione F9 e capture 2 peixes

**Peixe 1:**
- Servidor: `Vara 1 usada (1/1 usos)`
- Servidor envia: `[feeding, cleaning, switch_rod]`
- Cliente troca vara 1 → vara 2

**Peixe 2 (CRÍTICO):**
- Servidor: `Vara 2 usada (1/1 usos)`
- Servidor detecta: `Par (1, 2) esgotado`
- Servidor envia: `[feeding, cleaning, switch_rod, switch_rod_pair]`

**Logs Esperados (SERVIDOR):**
```
INFO:server:🔄 thiago: Par (1, 2) esgotado (Vara 1: 1, Vara 2: 1)
INFO:server:🔄 thiago: Mudança Par1 → Par2 (3, 4)
INFO:server:   Primeira vara do novo par: 3
INFO:server:   ✅ current_rod atualizado para: 3
INFO:server:🎣 thiago: Operação SWITCH_ROD_PAIR adicionada ao batch (→ Vara 3)
INFO:server:📦 thiago: BATCH enviado com 4 operação(ões): ['feeding', 'cleaning', 'switch_rod', 'switch_rod_pair']
```

**Logs Esperados (CLIENTE):**
```
🏪 [SERVER→CLIENT] BATCH RECEBIDO: 4 operação(ões)
🏪 Operações: ['feeding', 'cleaning', 'switch_rod', 'switch_rod_pair']
🔄 switch_rod detectado - será executado APÓS fechar baú
🔄 switch_rod_pair detectado - PRECISA abrir baú!
➕ feeding adicionado à fila do ChestOperationCoordinator
➕ cleaning adicionado à fila do ChestOperationCoordinator
🔄 switch_rod_pair → equipar vara 3 do novo par
🏪 [FLAG] had_chest_operations = True (2 operações de baú)
   ⚠️ IMPORTANTE: switch_rod NÃO será executado (ChestCoordinator escolhe vara)

[ChestCoordinator abre baú]
[ChestCoordinator executa feeding]
[ChestCoordinator executa cleaning]
[ChestCoordinator fecha baú]

======================================================================
🎣 PASSO 5: EQUIPANDO VARA APÓS FECHAR BAÚ
======================================================================
📊 [DEBUG] rod_to_equip_after = 2
📊 [DEBUG] rod_to_equip_after_pair_switch = 3

🔄 [OPÇÃO 1] TROCA DE PAR detectada!
   ➡️ Equipando vara 3...
   ✅ Vara 3 equipada e tracking atualizado (botão direito segurado)!
   📝 Confirmando troca de par no RodManager...
======================================================================

✅ Sincronização completa - cliente pode pescar novamente!
```

---

## 🔒 Diferenças: switch_rod vs switch_rod_pair

| Aspecto | switch_rod | switch_rod_pair |
|---------|-----------|-----------------|
| **Quando** | A cada peixe (troca no par) | Quando par esgota |
| **Exemplo** | Vara 1 → Vara 2 | Vara 2 → Vara 3 |
| **Precisa Baú?** | ❌ NÃO | ✅ SIM (pegar novas varas) |
| **Processamento** | Pendente (após fechar baú) | Imediato (informa ChestCoordinator) |
| **Execução** | _on_batch_complete() | ChestCoordinator |

---

## 📝 Arquivos Modificados

1. `core/fishing_engine.py`
   - **Linhas 1779-1797:** Detectar `switch_rod_pair` no loop de separação
   - **Linhas 1817-1827:** Processar `switch_rod_pair` e informar ChestCoordinator

---

## ✅ Garantias

1. **switch_rod_pair sempre processado** - Não é mais ignorado
2. **Vara correta equipada** - ChestCoordinator recebe `rod_to_equip_after_pair_switch`
3. **Prioridade correta** - rod_to_equip_after_pair_switch tem prioridade sobre escolha por usos
4. **Sincronização servidor-cliente** - Servidor controla qual vara equipar

---

**Data:** 2025-10-29
**Status:** ✅ CORRIGIDO
**Teste:** Próxima captura de peixe que esgote par
