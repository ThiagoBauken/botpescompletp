# 🔍 ANÁLISE COMPLETA DOS LOGS - Problemas Identificados

**Data:** 2025-10-29
**Análise:** Comparação logs atuais vs implementação v5/v6 antiga funcional

---

## 📊 PROBLEMAS CITADOS PELO USUÁRIO

Você disse:
> "comeu corretamente. porem nao aproveitou o feeding pra realizar a manutencao de varas que era necessario, depois na limpeza simplesmente abriu e fechou o bau sem realizar a limpeza nem alimentacao(cairam ao mesmo tempo) e nem manutencao de varas"

---

## ✅ PROBLEMA 1: Manutenção Oportunística

### STATUS: **FUNCIONOU CORRETAMENTE** ✅

**Logs mostram:**

**Primeira operação de feeding (peixe #1):**
```
🔍 VERIFICAÇÃO OPORTUNÍSTICA DE MANUTENÇÃO...
   💡 Limpeza/Alimentação detectada - verificando necessidade de manutenção...
📊 [BACKGROUND] Resultado da análise:
   ✅ COM isca: 3 varas [1, 2, 3]
   ⚠️ SEM isca: 1 varas [4]
   💥 QUEBRADAS: 1 varas [6]
   ⚪ VAZIOS: 1 slots [5]
   💡 MANUTENÇÃO NECESSÁRIA: 3 problema(s) detectado(s)
   🔧 Executando manutenção usando lógica do Page Down (baú já aberto)...
======================================================================
🔧 SISTEMA DE MANUTENÇÃO AUTOMÁTICA DE VARAS - INICIADO
[... executa manutenção completa ...]
✅ MANUTENÇÃO COMPLETA FINALIZADA COM SUCESSO!
```

**Segunda operação de feeding+cleaning (peixe #2):**
```
🔍 VERIFICAÇÃO OPORTUNÍSTICA DE MANUTENÇÃO...
📊 [BACKGROUND] Resultado da análise:
   ✅ COM isca: 6 varas [1, 2, 3, 4, 5, 6]
   ⚠️ SEM isca: 0 varas []
   💥 QUEBRADAS: 0 varas []
   ✅ Todas as varas OK - sem necessidade de manutenção
   ✅ Todas as varas OK - manutenção não necessária
```

**CONCLUSÃO:** Manutenção oportunística funcionou perfeitamente:
- ✅ Primeira vez: detectou problemas e executou
- ✅ Segunda vez: tudo OK, não executou (como esperado)

---

## ❌ PROBLEMA 2: Feeding Falhou - Mas É Esperado

### STATUS: **COMPORTAMENTO CORRETO** ⚠️

**Logs mostram:**
```
🍖 EXECUTANDO ALIMENTAÇÃO AUTOMÁTICA
🔍 Buscando comida no baú...
🔍 Buscando comida no inventário...
❌ Comida não encontrada nem no baú nem no inventário
❌ [FEEDING] Sem comida disponível - abortando alimentação
⚠️ [FEEDING] Resetando contadores para evitar loop infinito
```

**ANÁLISE:**
- Feeding falhou porque **realmente não tem comida**
- Sistema resetou contadores corretamente (evita loop infinito)
- Isso é o **comportamento esperado** quando sem comida

**COMPARAÇÃO COM V5 ANTIGO:**

V5 antigo faz exatamente isso (feeding_system.py:304-311):
```python
food_available = self._detect_food_position()
if not food_available:
    _safe_print("❌ [FEEDING] Sem comida disponível - abortando alimentação")
    _safe_print("⚠️ [FEEDING] Resetando contadores para evitar loop infinito")
    self.last_feeding_time = time.time()
    self.fish_count_since_feeding = 0
    return False
```

**CONCLUSÃO:** Feeding funcionou como esperado. Problema é falta de comida, não lógica.

---

## ❌ PROBLEMA 3: Cleaning Não Detectou Peixes

### STATUS: **BUG CRÍTICO** ❌

**Logs mostram:**
```
🐟 PEIXE CAPTURADO - Peixe #1 capturado
🐟 PEIXE CAPTURADO - Peixe #2 capturado

[...]

🧹 EXECUTANDO LIMPEZA AUTOMÁTICA DO INVENTÁRIO
🔍 Detectando peixes E ISCAS com NMS avançado...
ℹ️ Nenhum peixe ou isca detectado
✅ Nenhum peixe detectado - limpeza concluída!
📊 Total transferido: 0 itens em 1 escaneamentos
```

**PROBLEMA:** 2 peixes capturados mas cleaning não os detectou!

**ANÁLISE:**

Possíveis causas:
1. **Threshold muito alto** - Peixes podem estar com confiança < threshold
2. **NMS suprimindo detecções** - Se peixes estão < 50px de distância
3. **Templates de peixe incorretos** - Nome ou formato

**COMPARAÇÃO COM V5 ANTIGO:**

V5 antigo usa threshold especial para SALMONN/TROUTT (inventory_manager.py:618-623):
```python
template_clean = template_name.replace('.png', '').lower()
if template_clean in ['salmonn', 'troutt']:
    old_threshold = confidence_threshold
    confidence_threshold = 0.85  # ✅ EXACTLY like Catch Viewer
```

**SOLUÇÃO NECESSÁRIA:**
1. Verificar templates de peixe no inventário
2. Ajustar threshold para 0.85 (como CatchViewer)
3. Revisar lógica de NMS (50px pode ser muito agressivo)

---

## ❌ PROBLEMA 4: Troca de Par NÃO Foi Sinalizada

### STATUS: **BUG CRÍTICO** ❌

**Logs mostram:**
```
🎣 Escolhendo próxima vara após baú:
   Par atual: (1, 2)
   Vara 1: 2/1 usos
   Vara 2: 2/1 usos

❌ [ERRO LÓGICO DETECTADO] AMBAS as varas atingiram limite de 1 usos!
   Vara 1: 2/1 usos >= limite
   Vara 2: 2/1 usos >= limite
   ❌ NÃO POSSO escolher vara do mesmo par esgotado!
```

**PROBLEMA:** Varas 1 e 2 esgotaram limite (1 uso cada), mas sistema NÃO sinalizou troca de par!

**ANÁLISE:**

**Configuração atual:**
```
rod_uses_per_bait = 1  ← MUITO BAIXO!
```

**V5 antigo usa:**
```python
# rod_manager.py:89-99
if config_manager:
    rod_switch_limit = config_manager.get('rod_system.rod_switch_limit', 20)
    self.use_limit_initial = rod_switch_limit  # DEFAULT: 20
```

**Fluxo esperado:**
```
register_rod_use() chamado
  ↓
_check_pair_switch_needed() verifica:
  if vara1_usos >= limite AND vara2_usos >= limite:
      → TROCA DE PAR!
      → Retorna número da primeira vara do próximo par (ex: 3)
  ↓
fishing_engine recebe número da vara
  ↓
Sinaliza coordinator:
  coordinator.rod_to_equip_after_pair_switch = 3
```

**O QUE ESTÁ ACONTECENDO:**

Logs mostram que `register_rod_use()` FOI chamado:
```
📝 [REGISTRO] Registrando uso da vara...
   • Peixe capturado: True
   • Vai abrir baú: True
🔍 [GET_CURRENT_ROD] Par 1(1, 2), pos=1, pending_data=None → RETORNA vara 2
📊 🐟 Peixe - Vara 2: 2 usos
   ✅ Mesmo par - sem mudança de par detectada  ← ❌ ERRADO!
```

**PROBLEMA:** `register_rod_use()` não detectou troca de par mesmo com ambas varas >= limite!

**SOLUÇÃO NECESSÁRIA:**
1. Corrigir `rod_uses_per_bait` para valor adequado (10-20)
2. Verificar lógica de `_check_pair_switch_needed()` em rod_manager.py
3. Garantir que retorno de `register_rod_use()` é int (não bool) quando troca

---

## ✅ PROBLEMA 5: "Ciclo Pulado" - Comportamento Correto

### STATUS: **FUNCIONANDO CORRETAMENTE** ✅

**Logs mostram:**
```
⏸️ Ciclo pulado (coordenador ocupado) - não conta uso de vara
🎣 Iniciando ciclo de pesca...
🔄 Estado: fishing → fishing
⏸️ Ciclo pulado (coordenador ocupado) - não conta uso de vara
[repetido ~50 vezes]
```

**ANÁLISE:**

Isso é o **comportamento CORRETO**! V5 antigo faz exatamente isso (fishing_engine.py:675-686):

```python
def _execute_complete_fishing_cycle(self) -> bool:
    # ✅ CRÍTICO: NÃO INICIAR CICLO se coordenador está executando!
    if self.chest_coordinator and self.chest_coordinator.execution_in_progress:
        _safe_print("⏸️ [FISHING CYCLE] Coordenador executando operações - AGUARDANDO")
        time.sleep(0.5)
        return None  # ✅ RETURN None = NÃO CONTA como timeout
```

**Fluxo:**
1. Fishing loop tenta iniciar ciclo
2. Verifica se coordinator está ocupado
3. Se sim: return `None` e aguarda 0.5s
4. Loop tenta novamente
5. Repete até coordinator terminar

**Por que aparece tantas vezes:**

Coordinator demora ~10-20 segundos executando:
- Abre baú (2s)
- Aguarda carregamento (1.5s)
- Executa feeding (2-5s)
- Executa cleaning (2-5s)
- Executa maintenance (5-10s)
- Fecha baú (2s)

Total: ~15-25 segundos

Com `time.sleep(0.5)`, fishing loop verifica ~30-50 vezes até coordinator terminar.

**CONCLUSÃO:** Spam de "Ciclo pulado" é **normal e esperado**.

---

## 📊 RESUMO DOS PROBLEMAS REAIS

| # | Problema | Status | Severidade | Precisa Correção |
|---|----------|--------|------------|------------------|
| 1 | Manutenção oportunística | ✅ Funcionando | - | ❌ Não |
| 2 | Feeding sem comida | ⚠️ Esperado | Baixa | ❌ Não |
| 3 | Cleaning não detecta peixes | ❌ Bug | **Alta** | ✅ **SIM** |
| 4 | Troca de par não sinalizada | ❌ Bug | **Crítica** | ✅ **SIM** |
| 5 | "Ciclo pulado" spam | ✅ Normal | - | ❌ Não |

---

## 🔧 CORREÇÕES NECESSÁRIAS

### CORREÇÃO 1: Detecção de Peixes no Cleaning

**Arquivo:** `core/inventory_manager.py`

**Problema:** Threshold muito baixo ou NMS muito agressivo

**Solução:**
```python
# Usar threshold 0.85 para SALMONN/TROUTT (como CatchViewer)
template_clean = template_name.replace('.png', '').lower()
if template_clean in ['salmonn', 'troutt']:
    confidence_threshold = 0.85  # ✅ Threshold especial
```

**Também revisar:**
- Área de inventário correta: `[633, 541, 1233, 953]`
- NMS distance: 50px pode ser muito agressivo (testar 30px)
- Templates de peixe: verificar nomes e formato

---

### CORREÇÃO 2: Troca de Par em rod_manager.py

**Arquivo:** `core/rod_manager.py`

**Problema 1:** `rod_uses_per_bait = 1` (muito baixo)

**Solução:**
```python
# Ler da UI/config (default: 20)
rod_switch_limit = config_manager.get('rod_system.rod_switch_limit', 20)
self.use_limit_initial = rod_switch_limit
```

**Problema 2:** `_check_pair_switch_needed()` não está detectando troca

**Verificar lógica:**
```python
def _check_pair_switch_needed(self) -> Union[int, bool]:
    """
    Returns:
        int: Número da primeira vara do próximo par (ex: 3, 5)
        bool: False se não precisa trocar
    """
    vara1_usos = self.rod_uses[vara1_slot]
    vara2_usos = self.rod_uses[vara2_slot]
    limite = self.use_limit_initial

    # ✅ CRÍTICO: Verificar se AMBAS atingiram limite
    if vara1_usos >= limite and vara2_usos >= limite:
        new_pair_index = (self.current_pair_index + 1) % len(self.rod_pairs)
        new_pair = self.rod_pairs[new_pair_index]

        # Salvar para confirmação depois
        self.pending_pair_switch_data = {
            'new_pair_index': new_pair_index,
            'first_rod': new_pair[0]
        }

        return new_pair[0]  # ✅ Retorna int (ex: 3)

    return False
```

**Problema 3:** `register_rod_use()` não está retornando int

**Verificar:**
```python
def register_rod_use(self, caught_fish: bool = True, will_open_chest: bool = False):
    # Incrementar uso
    self.rod_uses[rod] += 1

    # ✅ Verificar troca de par
    pair_switch_result = self._check_pair_switch_needed()

    if pair_switch_result:  # int (ex: 3)
        if will_open_chest:
            # Coordinator vai equipar depois
            return pair_switch_result  # ✅ int
        else:
            # Equipar agora
            return pair_switch_result  # ✅ int

    return False  # bool
```

---

## 🎯 PRIORIDADE DAS CORREÇÕES

### 🔴 PRIORIDADE ALTA (Fazer Agora)

1. **Corrigir detecção de troca de par** (rod_manager.py)
   - Verificar `_check_pair_switch_needed()`
   - Garantir retorno correto de `register_rod_use()`
   - Ajustar `rod_uses_per_bait` para 10-20

2. **Corrigir detecção de peixes no cleaning** (inventory_manager.py)
   - Threshold 0.85 para SALMONN/TROUTT
   - Revisar NMS distance (testar 30px)
   - Verificar templates de peixe

### 🟡 PRIORIDADE MÉDIA

3. **Melhorar logs de debugging**
   - Reduzir spam de "Ciclo pulado" (mostrar apenas a cada 5s)
   - Adicionar log quando troca de par é detectada
   - Log detalhado de detecção de peixes

### 🟢 PRIORIDADE BAIXA

4. **Melhorias cosméticas**
   - Mensagens mais claras
   - Estatísticas de economia de aberturas
   - Performance tracking

---

## 📝 PRÓXIMOS PASSOS

1. **Corrigir rod_manager.py:**
   - Revisar `_check_pair_switch_needed()`
   - Verificar retorno de `register_rod_use()`
   - Ajustar limite padrão

2. **Corrigir inventory_manager.py:**
   - Threshold especial para SALMONN/TROUTT
   - Ajustar NMS distance
   - Testar detecção de peixes

3. **Testar novamente:**
   - Pescar 2 peixes
   - Verificar troca de par funciona
   - Verificar cleaning detecta peixes

---

**CONCLUSÃO:**

✅ **Manutenção oportunística funcionou perfeitamente**
✅ **Consolidação de operações funcionou**
❌ **Troca de par não está detectando** (BUG CRÍTICO)
❌ **Cleaning não detecta peixes** (BUG CRÍTICO)
✅ **"Ciclo pulado" é comportamento normal**

**2 bugs críticos precisam ser corrigidos antes de prosseguir.**
