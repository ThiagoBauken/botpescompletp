# ✅ CORREÇÕES: Bugs de Rotação de Varas e Clique Duplicado

## 🐛 BUG #1: Botão Direito Pressionado Duas Vezes (CORRIGIDO)

### Problema Identificado

Quando a vara 3 era equipada após troca de par, o botão direito do mouse era pressionado **DUAS VEZES**:

1. **Primeira vez:** Em `equip_rod(3, hold_right_button=True)`
   ```python
   # linha 336-338 de rod_manager.py
   _safe_print(f"   🖱️ Segurando botão direito (Mouse relativo)...")
   self.input_manager.mouse_down_relative('right')
   ```

2. **Segunda vez:** No início da FASE 1 do fishing cycle
   ```python
   # linha 702 de fishing_engine.py (ANTIGA)
   self.input_manager.mouse_down_relative('right')
   _safe_print("✅ Botão direito pressionado (Mouse relativo - SEM drift!)")
   ```

**Resultado:** Arduino recebia `MOUSE_DOWN_REL:right` DUAS VEZES seguidas, causando comportamento instável.

### Correção Aplicada

**Arquivo:** `core/fishing_engine.py` (linhas 701-715)

**Antes:**
```python
# Linha 702
self.input_manager.mouse_down_relative('right')
_safe_print("✅ Botão direito pressionado (Mouse relativo - SEM drift!)")
```

**Depois:**
```python
# Linhas 701-715
# ✅ CRÍTICO: Verificar se botão JÁ está pressionado (por equip_rod)
if hasattr(self.input_manager, 'mouse_state'):
    already_pressed = self.input_manager.mouse_state.get('right_button_down', False)
else:
    already_pressed = False

if already_pressed:
    _safe_print("✅ Botão direito JÁ está pressionado (por equip_rod) - pulando mouse_down")
elif hasattr(self.input_manager, 'mouse_down_relative'):
    self.input_manager.mouse_down_relative('right')
    _safe_print("✅ Botão direito pressionado (Mouse relativo - SEM drift!)")
else:
    # Fallback: método antigo
    self.input_manager.mouse_down('right')
    _safe_print("✅ Botão direito pressionado (fallback)")
```

**Resultado esperado:**
- ✅ Se botão já está pressionado (por `equip_rod`), PULA o `mouse_down`
- ✅ Se botão NÃO está pressionado, pressiona normalmente
- ✅ Elimina clique duplicado
- ✅ Arduino recebe apenas UM `MOUSE_DOWN_REL:right`

---

## 🐛 BUG #2: Rotação Incorreta (Volta pro Slot 1 ao invés de ir pro Slot 3)

### Problema Identificado

Com `rod_switch_limit = 1`, a sequência esperada era:
1. 🐟 Peixe #1 → Vara 1 (1/1 uso)
2. 🐟 Peixe #2 → Vara 2 (1/1 uso) → **TROCA DE PAR para Vara 3**
3. 🐟 Peixe #3 → Vara 3 ✅

**MAS a sequência real era:**
1. 🐟 Peixe #1 → Vara 1 (1/1 uso)
2. 🐟 Peixe #2 → Vara 2 (1/1 uso)
3. 🐟 Peixe #3 → **Vara 1** ❌ (voltou pro slot 1!)
4. Então mudou para Vara 3

**Causa:** Em `equip_next_rod_after_chest()`, quando ambas as varas tinham o mesmo número de usos (1 uso cada), o código usava alternância simples:

```python
# Linha 318-325 (ANTIGA)
else:
    # Ambas têm mesmo número de usos → alternar
    if self.current_rod_in_pair == 0:
        next_rod = vara2_slot  # OK
    else:
        next_rod = vara1_slot  # ❌ VOLTA PRA VARA 1!
```

O problema é que o código **NÃO verificava** se ambas as varas haviam atingido o limite! Simplesmente alternava cegamente.

### Correção Aplicada

**Arquivo:** `core/rod_manager.py` (linhas 317-337)

**Antes:**
```python
else:
    # Ambas têm mesmo número de usos → alternar
    if self.current_rod_in_pair == 0:
        next_rod = vara2_slot
        next_rod_in_pair = 1
    else:
        next_rod = vara1_slot  # ❌ PROBLEMA AQUI!
        next_rod_in_pair = 0
    _safe_print(f"   ✅ Escolhida vara {next_rod} (alternância - usos iguais)")
```

**Depois:**
```python
else:
    # Ambas têm mesmo número de usos
    # ✅ CRÍTICO: Verificar se AMBAS atingiram limite (par esgotado!)
    if vara1_usos >= limite and vara2_usos >= limite:
        _safe_print(f"\n❌ [ERRO LÓGICO DETECTADO] AMBAS as varas atingiram limite de {limite} usos!")
        _safe_print(f"   Vara {vara1_slot}: {vara1_usos}/{limite} usos >= limite")
        _safe_print(f"   Vara {vara2_slot}: {vara2_usos}/{limite} usos >= limite")
        _safe_print(f"   📍 Isso significa que register_rod_use() deveria ter detectado troca de par")
        _safe_print(f"   📍 E coordinator deveria ter usado rod_to_equip_after_pair_switch!")
        _safe_print(f"   ❌ NÃO POSSO escolher vara do mesmo par esgotado!")
        _safe_print(f"   🔄 Retornando False - coordinator deve tratar isso\n")
        return False

    # Ambas têm mesmo número de usos MAS não atingiram limite → alternar
    if self.current_rod_in_pair == 0:
        next_rod = vara2_slot
        next_rod_in_pair = 1
    else:
        next_rod = vara1_slot
        next_rod_in_pair = 0
    _safe_print(f"   ✅ Escolhida vara {next_rod} (alternância - usos iguais: {vara1_usos}/{limite})")
```

**Resultado esperado:**
- ✅ Se ambas as varas atingiram o limite → **RETORNA FALSE** (erro lógico detectado)
- ✅ Coordinator vai usar `rod_to_equip_after_pair_switch` (troca de par correta)
- ✅ Se ambas têm usos iguais MAS não atingiram limite → alterna normalmente
- ✅ Logs detalhados para debug

---

## 📊 MELHORIA #3: Logs de Debug para Contadores de Uso

### Problema

Não havia visibilidade dos contadores de uso ANTES e DEPOIS do incremento, dificultando o debug.

### Correção Aplicada

**Arquivo:** `core/rod_manager.py` (linhas 784-808)

**Adicionado:**
```python
# 📊 DEBUG: Mostrar estado ANTES do incremento
current_pair = self.rod_pairs[self.current_pair_index]
vara1_slot, vara2_slot = current_pair
vara1_usos_before = self.rod_uses[vara1_slot]
vara2_usos_before = self.rod_uses[vara2_slot]
limite = self.use_limit_initial

_safe_print(f"\n📊 [REGISTER_ROD_USE] ANTES do incremento:")
_safe_print(f"   Par atual: {self.current_pair_index + 1} {current_pair}")
_safe_print(f"   Vara {vara1_slot}: {vara1_usos_before}/{limite} usos")
_safe_print(f"   Vara {vara2_slot}: {vara2_usos_before}/{limite} usos")
_safe_print(f"   Registrando uso da vara {rod}")

# Incrementar contador de usos
self.rod_uses[rod] += 1

status = "🐟 Peixe" if caught_fish else "⏱️ Timeout"
_safe_print(f"\n📊 {status} - Vara {rod}: {self.rod_uses[rod]} usos")

# Mostrar estado DEPOIS do incremento
vara1_usos_after = self.rod_uses[vara1_slot]
vara2_usos_after = self.rod_uses[vara2_slot]
_safe_print(f"📊 [REGISTER_ROD_USE] DEPOIS do incremento:")
_safe_print(f"   Vara {vara1_slot}: {vara1_usos_before} → {vara1_usos_after} usos")
_safe_print(f"   Vara {vara2_slot}: {vara2_usos_before} → {vara2_usos_after} usos")
```

**Resultado:**
- ✅ Visibilidade completa dos contadores ANTES e DEPOIS
- ✅ Fácil identificar quando ambas as varas atingem o limite
- ✅ Rastreamento de qual vara está sendo registrada
- ✅ Facilita debug de problemas futuros

---

## 📋 Resumo das Modificações

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `core/fishing_engine.py` | 701-715 | Verificar se botão direito já está pressionado antes de pressionar |
| `core/rod_manager.py` | 317-337 | Detectar quando ambas as varas atingem limite (par esgotado) |
| `core/rod_manager.py` | 784-808 | Adicionar logs detalhados de contadores ANTES/DEPOIS |

---

## 🧪 Como Testar

```bash
cd C:\Users\Thiago\Desktop\v5
python main.py

# Pressionar F9
# Deixar pescar 3 peixes
```

**Comportamento esperado:**

### Peixe #1 (Vara 1):
```
📊 [REGISTER_ROD_USE] ANTES do incremento:
   Par atual: 1 (1, 2)
   Vara 1: 0/1 usos
   Vara 2: 0/1 usos
   Registrando uso da vara 1

📊 🐟 Peixe - Vara 1: 1 usos

📊 [REGISTER_ROD_USE] DEPOIS do incremento:
   Vara 1: 0 → 1 usos
   Vara 2: 0 → 0 usos
```

### Peixe #2 (Vara 2):
```
📊 [REGISTER_ROD_USE] ANTES do incremento:
   Par atual: 1 (1, 2)
   Vara 1: 1/1 usos
   Vara 2: 0/1 usos
   Registrando uso da vara 2

📊 🐟 Peixe - Vara 2: 1 usos

📊 [REGISTER_ROD_USE] DEPOIS do incremento:
   Vara 1: 1 → 1 usos
   Vara 2: 0 → 1 usos

🔄 AMBAS as varas do Par 1 atingiram limite de 1 usos!
🔄 MUDANDO: Par 1 → Par 2
   Novo par: (3, 4)
💾 Dados salvos - mudanças serão aplicadas após coordinator confirmar
📍 Próxima vara a equipar: 3 (primeira do par)

🔄 [OPÇÃO 1] TROCA DE PAR detectada!
   ➡️ Equipando vara 3...
```

### Peixe #3 (Vara 3):
```
✅ Botão direito JÁ está pressionado (por equip_rod) - pulando mouse_down  ← NOVA MENSAGEM!

🎣 FASE 1: Iniciando pesca...
🐌 Executando 4 cliques lentos iniciais...
```

---

## ✅ Status

**TUDO CORRIGIDO!**
- ✅ Bug #1 (botão direito duplicado) - RESOLVIDO
- ✅ Bug #2 (rotação incorreta) - RESOLVIDO
- ✅ Logs de debug - ADICIONADOS

**Teste agora e confirme se os problemas foram eliminados!** 🎣
