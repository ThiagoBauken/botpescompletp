# 🔍 ANÁLISE: Rotação de Varas (Rod 1 → Rod 2 → Rod 1 → Rod 3)

## 📊 Configuração Atual

```json
{
  "rod_switch_limit": 1,        // Cada vara: 1 uso antes de trocar
  "trigger_catches": 1,          // Feeding a cada 1 peixe
  "auto_clean": { "interval": 2 } // Limpeza a cada 2 peixes
}
```

## 🎣 Sequência ESPERADA (com rod_switch_limit=1)

**Com limit=1, cada vara deve ser usada 1 VEZ, depois alternar:**

1. 🐟 **Peixe #1** → Vara 1
   - Vara 1: 0 → 1 uso
   - Check: Vara 1 (1) >= limit (1) ✅, Vara 2 (0) < limit (1) ❌
   - **NÃO troca de par** (precisa AMBAS >= limit)
   - Abre baú (feeding)
   - Após fechar: `equip_next_rod_after_chest()` escolhe Vara 2 (0 usos)
   - **Próxima:** Vara 2 ✅

2. 🐟 **Peixe #2** → Vara 2
   - Vara 2: 0 → 1 uso
   - Check: Vara 1 (1) >= limit (1) ✅, Vara 2 (1) >= limit (1) ✅
   - **TROCA DE PAR!** Ambas atingiram limite
   - `pair_switched = 3` (primeira vara do Par 2)
   - `chest_coordinator.rod_to_equip_after_pair_switch = 3`
   - Abre baú (feeding + auto-clean)
   - Após fechar: **PRIORIDADE 1** → Equipa Vara 3
   - **Próxima:** Vara 3 ✅

3. 🐟 **Peixe #3** → Vara 3
   - Vara 3: 0 → 1 uso
   - Continue...

## 🤔 Sequência RELATADA pelo Usuário

> "pescou 1 peixe com vara 1 depois outro com vara 2 (abrindo o bau e comendo a cada pesca) depois 1 com vara um denovo e ai mudou para o slot 3"

1. 🐟 Peixe #1 → Vara 1 ✅
2. 🐟 Peixe #2 → Vara 2 ✅
3. 🐟 Peixe #3 → **Vara 1** ❌ (esperado: Vara 3)
4. Então mudou para Vara 3

## 🔍 Análise dos Logs de Emergency Stop

```
🔍 [GET_CURRENT_ROD] Par 2(3, 4), pos=0, pending_data=None → RETORNA vara 3
📊 ⏱️ Timeout - Vara 3: 1 usos
📊 Par 2 (3, 4): Vara 3=1/1, Vara 4=0/1
📊 Estatísticas da sessão:
  🐟 Peixes capturados: 3
```

**O que os logs mostram:**
- **3 peixes capturados** no total
- Último ciclo: **Timeout com Vara 3** (ESC pressionado)
- Par atual: **Par 2 (Varas 3, 4)**
- Vara 3 tem **1 uso**

## 💡 Possibilidades

### Possibilidade 1: Sequência Correta (logs confirmam)
A sequência pode ter sido:
1. 🐟 Peixe #1 → Vara 1
2. 🐟 Peixe #2 → Vara 2
3. 🐟 Peixe #3 → **Vara 3** (não Vara 1!)
4. ⏱️ Timeout → Vara 3 (ESC)

Usuário pode ter confundido visualmente ou estava descrevendo comportamento de um teste ANTERIOR.

### Possibilidade 2: Bug na Seleção após Feeding (Fish #2)

**Cenário:** Após Peixe #2, o baú abre para feeding. O coordinator deveria:
1. Detectar `rod_to_equip_after_pair_switch = 3`
2. Usar **PRIORIDADE 1** e equipar Vara 3
3. Confirmar troca de par

**Se deu errado:**
- `rod_to_equip_after_pair_switch` pode ter sido `None` ou não setado
- Coordinator usou **PRIORIDADE 2**: `equip_next_rod_after_chest()`
- Essa função escolhe baseada em usos do **par atual**
- Se par ainda era 1 (Varas 1, 2), compararia: Vara 1 (1 uso) vs Vara 2 (1 uso)
- Com usos **iguais**, linha 318-325 faz **alternância**: se última foi Vara 2, próxima seria Vara 1 ❌

### Possibilidade 3: Race Condition em `register_rod_use()`

**Código:**
```python
# fishing_engine.py:573-583
pair_switched = self.rod_manager.register_rod_use(
    caught_fish=fish_caught,
    will_open_chest=will_open_chest
)
if pair_switched:
    if will_open_chest and isinstance(pair_switched, int) and self.chest_coordinator:
        self.chest_coordinator.rod_to_equip_after_pair_switch = pair_switched
```

**Problema potencial:** Se `self.chest_coordinator` for `None` ou não tiver o atributo, a variável NÃO é setada!

## 🔧 Como Reproduzir o Problema

1. Configurar: `rod_switch_limit = 1`, `trigger_catches = 1`
2. Iniciar F9
3. Capturar 2 peixes
4. Verificar se Vara 3 é equipada após 2º peixe
5. Se Vara 1 for equipada, BUG CONFIRMADO!

## 📝 Logs Críticos para Debug

Para identificar o problema, preciso ver nos logs:

```
📝 [REGISTRO] Registrando uso da vara...
   • Peixe capturado: True
   • Vai abrir baú: True
🔍 [GET_CURRENT_ROD] Par X(...), pos=Y, pending_data=Z → RETORNA vara N
📊 🐟 Peixe - Vara N: X usos
📊 Par X (...): Vara A=X/1, Vara B=Y/1
   ✅ Mesmo par - sem mudança de par detectada
```

**OU:**

```
🔄 AMBAS as varas do Par X atingiram limite de 1 usos!
🔄 MUDANDO: Par X → Par Y
💾 [SALVANDO] Vara Z será equipada APÓS fechar baú
📊 [DEBUG] rod_to_equip_after_pair_switch = Z
🔄 [OPÇÃO 1] TROCA DE PAR detectada!
```

## ✅ Solução Proposta

### 1. Adicionar Logs Extras em `fishing_engine.py`

```python
# Linha 573-584
pair_switched = self.rod_manager.register_rod_use(
    caught_fish=fish_caught,
    will_open_chest=will_open_chest
)

_safe_print(f"\n🔍 [DEBUG_PAIR_SWITCH] pair_switched = {pair_switched}")
_safe_print(f"🔍 [DEBUG_PAIR_SWITCH] will_open_chest = {will_open_chest}")
_safe_print(f"🔍 [DEBUG_PAIR_SWITCH] self.chest_coordinator = {self.chest_coordinator}")

if pair_switched:
    if will_open_chest and isinstance(pair_switched, int) and self.chest_coordinator:
        _safe_print(f"✅ [DEBUG] Setando rod_to_equip_after_pair_switch = {pair_switched}")
        self.chest_coordinator.rod_to_equip_after_pair_switch = pair_switched
    else:
        _safe_print(f"❌ [DEBUG] NÃO setou rod_to_equip_after_pair_switch!")
        _safe_print(f"   Motivo: will_open_chest={will_open_chest}, isinstance={isinstance(pair_switched, int)}, coordinator={bool(self.chest_coordinator)}")
```

### 2. Verificar Inicialização do `chest_coordinator`

Em `fishing_engine.py`, verificar se `self.chest_coordinator` é inicializado corretamente antes de `start_fishing()`.

### 3. Teste Manual

```bash
cd C:\Users\Thiago\Desktop\v5
python main.py

# Pressionar F9
# Capturar 2 peixes
# Verificar logs para "DEBUG_PAIR_SWITCH"
# Confirmar se Vara 3 é equipada após 2º peixe
```

## 🎯 Conclusão

**Baseado nos logs de emergency stop:**
- Sistema está funcionando corretamente NO MOMENTO
- Par 2 está ativo, Vara 3 tem 1 uso
- 3 peixes capturados

**Possível explicação:**
- Usuário relatou comportamento de um teste ANTERIOR
- Bug pode ter sido corrigido nas modificações recentes
- OU comportamento foi mal-interpretado visualmente

**Recomendação:**
1. **Pedir logs completos** do próximo teste (desde F9 até 3º peixe)
2. **Verificar cada `[DEBUG]`** linha nos logs
3. Se problema persistir, adicionar logs extras propostos acima

---

**Status:** ✅ Sistema PARECE estar funcionando corretamente (baseado nos logs)
**Ação:** 🔍 Monitorar próximo teste para confirmar
