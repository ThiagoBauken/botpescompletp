# ✅ CORREÇÃO CRÍTICA: Contador de Par NÃO Deve Resetar Durante Manutenção

## 🐛 Problema Reportado pelo Usuário

> **Configuração:** `rod_switch_limit = 3` (trocar de par após 3 usos de cada vara)
>
> **Comportamento esperado:**
> - Peixe #1 → Slot 1 (uso: 1/3)
> - Peixe #2 → Slot 2 (uso: 1/3)
> - Peixe #3 → Slot 1 (uso: 2/3)
> - Peixe #4 → Slot 2 (uso: 2/3)
> - Peixe #5 → Slot 1 (uso: 3/3)
> - Peixe #6 → Slot 2 (uso: 3/3) → **TROCA PARA PAR 2 (Slots 3-4)**
>
> **Problema:** Contadores foram RESETADOS durante manutenção, impedindo a troca de par!

**Logs mostrando o bug:**
```
📊 Par 1 (1, 2): Vara 1=2/3, Vara 2=2/3

[MANUTENÇÃO EXECUTADA]

🔄 Resetando contadores de uso após manutenção...
🔧 RESETANDO usos do Par 1 (1, 2) após manutenção
   Vara 1: 2 → 0  ← ❌ BUG: Deveria permanecer 2!
   Vara 2: 2 → 0  ← ❌ BUG: Deveria permanecer 2!
✅ Par 1 resetado - pronto para 3 usos cada

[CONTINUA PESCANDO COM PAR 1, NUNCA TROCA!]
```

---

## 🔍 Análise: Causa Raiz

### Entendendo os Contadores

**Existem DOIS conceitos diferentes:**

1. **Contador de USOS para troca de par** (`rod_uses[slot]`)
   - **Finalidade:** Determinar QUANDO trocar de par
   - **Resetado:** APENAS quando par é **realmente trocado** (não durante manutenção!)
   - **Gerenciado por:** `rod_manager.py` → `confirm_pair_switch()` (linhas 893-894)

2. **Contador de MANUTENÇÃO** (não existe explicitamente!)
   - **Finalidade:** Determinar QUANDO fazer manutenção (recarregar isca)
   - **Deveria ser:** Separado, resetado após manutenção
   - **Problema:** Estava usando o MESMO `rod_uses` e resetando incorretamente!

**Consequência do bug:**
```
rod_uses = contador usado para TROCA DE PAR
         + contador usado para MANUTENÇÃO
         = CONFLITO! ❌

Manutenção resetava rod_uses → quebrava lógica de troca de par!
```

---

## ✅ Correção Aplicada

### Arquivo: `core/rod_maintenance_system.py`

**Linhas modificadas:** 347-364

**ANTES (INCORRETO):**
```python
self.stats['successful_maintenances'] += 1
self.last_maintenance_time = time.time()

# ❌ ERRADO: Resetar contadores durante manutenção
if self.rod_manager:
    _safe_print("\n🔄 Resetando contadores de uso após manutenção...")
    self.rod_manager.reset_pair_uses_after_maintenance()  # ← CHAMADA INCORRETA!

_safe_print("✅ MANUTENÇÃO COMPLETA FINALIZADA COM SUCESSO!")
```

**DEPOIS (CORRETO):**
```python
self.stats['successful_maintenances'] += 1
self.last_maintenance_time = time.time()

# ✅ CORREÇÃO CRÍTICA: NÃO resetar contadores durante manutenção!
# Os contadores (rod_uses) são usados para determinar QUANDO TROCAR DE PAR.
# Eles devem ser resetados APENAS quando o par é realmente trocado (confirm_pair_switch),
# NÃO durante manutenção (que apenas recarrega isca).
#
# Exemplo com rod_switch_limit=3:
# - Peixe #1 slot 1: rod_uses[1]=1
# - Peixe #2 slot 2: rod_uses[2]=1
# - Manutenção (recarrega isca) → rod_uses DEVE permanecer [1]=1, [2]=1
# - Peixe #3 slot 1: rod_uses[1]=2
# - Peixe #4 slot 2: rod_uses[2]=2
# - Peixe #5 slot 1: rod_uses[1]=3 → TROCA PAR → reset apenas NOVO par

_safe_print("✅ MANUTENÇÃO COMPLETA FINALIZADA COM SUCESSO!")
```

---

## 📊 Comportamento CORRETO Agora

### Exemplo com `rod_switch_limit = 3`

```
🎣 INÍCIO - Par 1 (Slots 1, 2) ativo

🐟 Peixe #1 → Slot 1
📊 Vara 1: 1/3, Vara 2: 0/3

🐟 Peixe #2 → Slot 2
📊 Vara 1: 1/3, Vara 2: 1/3

🐟 Peixe #3 → Slot 1
📊 Vara 1: 2/3, Vara 2: 1/3

🐟 Peixe #4 → Slot 2
📊 Vara 1: 2/3, Vara 2: 2/3

[MANUTENÇÃO EXECUTADA - Recarrega isca nas varas]
✅ Manutenção completa
📊 Vara 1: 2/3, Vara 2: 2/3  ← ✅ CONTADORES MANTIDOS!

🐟 Peixe #5 → Slot 1
📊 Vara 1: 3/3, Vara 2: 2/3

🐟 Peixe #6 → Slot 2
📊 Vara 1: 3/3, Vara 2: 3/3

🔄 AMBAS as varas atingiram limite de 3 usos!
🔄 MUDANDO: Par 1 (1, 2) → Par 2 (3, 4)
📊 Vara 3: 0/3, Vara 4: 0/3  ← ✅ NOVO par resetado!

🐟 Peixe #7 → Slot 3
📊 Vara 3: 1/3, Vara 4: 0/3

[CONTINUA COM PAR 2...]
```

---

## 🔧 Quando Cada Contador DEVE Resetar

| Contador | Finalidade | Resetado Quando | Gerenciado Por |
|----------|------------|-----------------|----------------|
| `rod_uses[slot]` | Troca de par | Apenas ao **trocar de par** | `rod_manager.confirm_pair_switch()` |
| `fish_count` | Feeding/Cleaning | Após feeding/cleaning | `fishing_engine.py` |
| `rod_maintenance.last_time` | Próxima manutenção | Após manutenção | `rod_maintenance_system.py` |

**Regra de ouro:**
- ✅ `rod_uses` rastreia PROGRESSO até trocar par → NÃO resetar durante manutenção!
- ✅ Manutenção apenas recarrega isca → NÃO afeta progresso de troca!

---

## 📝 Detalhes Técnicos

### Função `reset_pair_uses_after_maintenance()`

**Localização:** `core/rod_manager.py` (linhas 832-858)

**Status:** Função ainda existe, mas **NÃO é mais chamada** em lugar nenhum!

**Código:**
```python
def reset_pair_uses_after_maintenance(self, pair_index: Optional[int] = None):
    """
    🔧 Resetar contadores de uso após manutenção

    ❌ ATENÇÃO: Esta função NÃO deve ser chamada!
    Os contadores de rod_uses são para TROCA DE PAR, não para manutenção.
    """
    try:
        with self.rod_lock:
            if pair_index is None:
                pair_index = self.current_pair_index

            pair = self.rod_pairs[pair_index]
            vara1, vara2 = pair

            # ❌ INCORRETO: Reseta contadores que NÃO deveriam ser resetados!
            self.rod_uses[vara1] = 0
            self.rod_uses[vara2] = 0
```

**Chamadas:** NENHUMA (comentada em `rod_maintenance_system.py:362`)

---

## 🧪 Como Testar a Correção

### Teste 1: `rod_switch_limit = 3`

```bash
cd C:\Users\Thiago\Desktop\v5
python main.py

# Configurar no GUI:
# - Rod Pair Switch Limit: 3
# - Trigger Catches (feeding): 1 (para forçar manutenção frequente)

# Pressionar F9
# Pescar até 6 peixes
# Verificar logs
```

**Comportamento esperado:**

```
📊 [REGISTRO] Registrando uso da vara...
📊 🐟 Peixe - Vara 1: 1 usos
📊 Par 1 (1, 2): Vara 1=1/3, Vara 2=0/3

[...]

📊 🐟 Peixe - Vara 2: 2 usos
📊 Par 1 (1, 2): Vara 1=2/3, Vara 2=2/3

[MANUTENÇÃO]
✅ MANUTENÇÃO COMPLETA FINALIZADA COM SUCESSO!
(SEM mensagem de "Resetando contadores")

📊 🐟 Peixe - Vara 1: 3 usos
📊 Par 1 (1, 2): Vara 1=3/3, Vara 2=2/3

📊 🐟 Peixe - Vara 2: 3 usos
📊 Par 1 (1, 2): Vara 1=3/3, Vara 2=3/3

🔄 AMBAS as varas do Par 1 atingiram limite de 3 usos!
🔄 MUDANDO: Par 1 (1, 2) → Par 2 (3, 4)
```

---

## 🎯 Resumo da Correção

### Problema
- ❌ `reset_pair_uses_after_maintenance()` era chamado após manutenção
- ❌ Resetava `rod_uses` para 0
- ❌ `rod_uses` é usado para determinar troca de par
- ❌ Resultado: Par nunca trocava se manutenção acontecia antes do limite

### Solução
- ✅ Comentada a chamada em `rod_maintenance_system.py:362`
- ✅ `rod_uses` agora só é resetado ao **realmente trocar de par**
- ✅ Manutenção apenas recarrega isca, não afeta progresso

### Impacto
- ✅ `rod_switch_limit` agora funciona com **QUALQUER valor** (1, 2, 3, 5, 10, etc.)
- ✅ Manutenção pode acontecer a qualquer momento sem afetar troca de par
- ✅ Lógica de rotação de varas preservada

---

## 📌 Observação sobre Contadores Futuros

**Feedback do usuário:**
> "os contadores presisam resetar em momentos diferentes precisa ser contadores diferentes para o timeout das varas, para a limpeza, alimentacao, e troca das varas/pares"

**Situação atual:**
- ✅ Troca de par: `rod_uses` (resetado ao trocar par)
- ✅ Feeding: `fish_count` em `fishing_engine.py` (resetado após feeding)
- ✅ Cleaning: `fish_count` em `fishing_engine.py` (resetado após cleaning)
- ✅ Manutenção: `last_maintenance_time` (resetado após manutenção)

**Todos os sistemas já possuem contadores separados!** O problema era apenas a chamada incorreta de `reset_pair_uses_after_maintenance()`.

---

## ✅ Status

**Correção aplicada:** ✅ COMPLETO

**Arquivo modificado:** `core/rod_maintenance_system.py` (linha 362)

**Função afetada:** `reset_pair_uses_after_maintenance()` (não mais chamada)

**Teste agora:** Configurar `rod_switch_limit = 3` e verificar troca de par após 6 peixes!

---

**Documentos relacionados:**
- [CORRECAO_TECLAS_PRESAS.md](CORRECAO_TECLAS_PRESAS.md)
- [CORRECAO_ALT_REMOVIDO_DA_PESCA.md](CORRECAO_ALT_REMOVIDO_DA_PESCA.md)
- [ANALISE_ROTACAO_VARAS.md](ANALISE_ROTACAO_VARAS.md)
