# Análise: Vara Não Equipando Após Fechar Baú

**Data:** 2025-10-26
**Problema Relatado:** Vara diz que equipou mas não está indo para a mão

---

## Problemas Identificados pelo Usuário

1. ✅ **ALT sendo solto antes dos arrastos** - ❌ FALSO!
   - Código ESTÁ mantendo ALT pressionado durante toda manutenção
   - Linha 224 `rod_maintenance_system.py`: "ALT permanece pressionado durante manutenção"
   - ALT só é solto em `_close_chest()` ANTES do TAB

2. ✅ **ALT deve ser solto antes de TAB** - ✅ CORRETO!
   - Linha 626 `chest_operation_coordinator.py`: "Liberando ALT antes de TAB"
   - Funcionando corretamente

3. ✅ **Botão direito deve estar pressionado** - ✅ CORRETO!
   - Linha 234-237 `rod_manager.py`: Segura botão direito ANTES de pressionar slot
   - Sequência: `mouse_down('right')` → `sleep(0.3)` → `press_key(str(slot))`

4. ❌ **Vara não está equipando** - PROBLEMA REAL!
   - Código executa: "✅ Vara do slot 1 equipada"
   - MAS vara não vai para mão no jogo

---

## Fluxo Atual (Código)

### Sequência de Equipar Vara (rod_manager.py:211-253)

```python
def equip_rod(self, slot: int, hold_right_button: bool = False):
    # PASSO 1: Segurar botão direito (se solicitado)
    if hold_right_button:
        self.input_manager.mouse_down('right')  # ✅
        time.sleep(0.3)

    # PASSO 2: Pressionar número do slot via Arduino
    self.input_manager.press_key(str(slot))  # ❓ PODE SER O PROBLEMA
    time.sleep(0.5)
```

### Como press_key() Funciona (arduino_input_manager.py:360-392)

```python
def press_key(self, key: str, duration: float = 0.05):
    # PASSO 1: Pressionar tecla
    self.key_down(key_lower)  # Envia: KEY_DOWN:1

    # PASSO 2: Segurar
    time.sleep(duration)  # 0.05s (50ms)

    # PASSO 3: Soltar
    self.key_up(key_lower)  # Envia: KEY_UP:1
```

### Arduino Processamento (arduino sketch:367-427)

```cpp
// handleKeyDown para números:
void handleKeyDown(String key) {
  // ... teclas especiais ...

  else {
    // Tecla normal (letra ou número)
    char keyChar = key.charAt(0);  // '1' → char '1'
    NKROKeyboard.press(keyChar);   // ❓ PODE SER O PROBLEMA
  }
}
```

---

## Possíveis Causas

### Hipótese 1: Botão Direito Interferindo

**Problema:** Botão direito pressionado pode impedir que o jogo registre a tecla do slot?

**Teste Sugerido:**
```python
# OPÇÃO A: Soltar botão direito → pressionar slot → segurar novamente
mouse_down('right')
sleep(0.3)
mouse_up('right')       # ← NOVO: Soltar antes
press_key(str(slot))
sleep(0.2)
mouse_down('right')     # ← NOVO: Segurar novamente

# OPÇÃO B: Não segurar botão direito antes
press_key(str(slot))
sleep(0.2)
mouse_down('right')     # ← Segurar DEPOIS
```

### Hipótese 2: Duration Muito Curto

**Problema:** `press_key()` segura tecla por apenas 50ms (0.05s). Jogo pode não registrar.

**Teste Sugerido:**
```python
# Aumentar duração do press
self.input_manager.press_key(str(slot), duration=0.2)  # 200ms
```

### Hipótese 3: Arduino NKROKeyboard com Números

**Problema:** `NKROKeyboard.press(keyChar)` pode não funcionar corretamente para caracteres numéricos '1'-'6'.

**Teste Sugerido:**
```cpp
// No Arduino, trocar:
NKROKeyboard.press(keyChar);

// Por:
switch(keyChar) {
  case '1': NKROKeyboard.press(KEY_1); break;
  case '2': NKROKeyboard.press(KEY_2); break;
  case '3': NKROKeyboard.press(KEY_3); break;
  case '4': NKROKeyboard.press(KEY_4); break;
  case '5': NKROKeyboard.press(KEY_5); break;
  case '6': NKROKeyboard.press(KEY_6); break;
  default: NKROKeyboard.press(keyChar); break;
}
```

### Hipótese 4: Timing Entre Fechar Baú e Equipar

**Problema:** Não está aguardando tempo suficiente após fechar baú?

**Código Atual:**
```python
# _close_chest()
time.sleep(0.6)  # Aguarda baú fechar
_safe_print("⏳ Aguardando baú fechar completamente...")

# _equip_specific_rod_after_chest()
# IMEDIATAMENTE equipa vara
```

**Teste Sugerido:**
```python
# Adicionar delay antes de equipar
time.sleep(1.0)  # Aguardar 1s após fechar baú
```

---

## Sequência Correta (Segundo Usuário)

Usuário explicou:
> "pra vara ir para mao e necessario apertar o botao do slot 1,2,3,4,5,6"
> "no caso o botao direito se segura ate apertar o slot"

**Interpretação:**
1. Segurar botão direito
2. Apertar slot (1-6)
3. Botão direito continua pressionado
4. Vara vai para mão

**Código atual JÁ FAZ ISSO!** Mas não funciona...

---

## Logs do Usuário (Evidência)

```
🎣 PASSO 5: Equipando vara APÓS fechar baú...
   📊 rod_to_equip_after = 1
   🎣 Equipando vara 1 com botão direito...
   📍 Chamando rod_manager.equip_rod(1, hold_right_button=True)
🎣 Equipando vara do slot 1...
   🖱️ Segurando botão direito...                    ← ✅ Botão direito pressionado
🔢 [LOG BOTÃO 1] Chamado por: _equip_specific_rod_after_chest
🔢 [LOG BOTÃO 1] Ação: EQUIPAR vara (hold_right=True)
✅ Vara do slot 1 equipada                          ← ✅ Código executou
   ✅ Vara 1 equipada - botão direito pressionado!  ← ✅ Confirmação
```

**MAS:** Vara não está na mão no jogo!

---

## Perguntas para Usuário

1. **O baú fecha completamente antes de tentar equipar?**
   - Se ainda estiver aberto, pode não funcionar

2. **Manualmente funciona?**
   - Teste manual: Fechar baú → Segurar botão direito → Apertar '1'
   - Vara equipa?

3. **Sem botão direito funciona?**
   - Teste manual: Fechar baú → Apertar '1' (SEM botão direito)
   - Vara equipa?

4. **Qual o delay correto?**
   - Após fechar baú, quanto tempo precisa esperar antes de equipar?

5. **Serial Monitor mostra o comando?**
   - Ver no Serial Monitor se `KEY_DOWN:1` e `KEY_UP:1` estão chegando
   - Arduino está respondendo OK?

---

## Testes Propostos

### Teste 1: Aumentar Delays

```python
# Em rod_manager.py, linha 245:
# ANTES:
self.input_manager.press_key(str(slot))
time.sleep(0.5)

# DEPOIS:
time.sleep(0.5)  # ← NOVO: Aguardar antes
self.input_manager.press_key(str(slot), duration=0.3)  # ← Aumentar duração
time.sleep(1.0)  # ← Aumentar delay após
```

### Teste 2: Soltar e Segurar Botão Direito

```python
# Em rod_manager.py, linha 233-246:
if hold_right_button:
    _safe_print("   🖱️ Segurando botão direito...")
    self.input_manager.mouse_down('right')
    time.sleep(0.3)

    # ← NOVO: Soltar antes de pressionar slot
    self.input_manager.mouse_up('right')
    time.sleep(0.1)

# Pressionar slot
self.input_manager.press_key(str(slot), duration=0.2)
time.sleep(0.3)

# ← NOVO: Segurar novamente após pressionar
if hold_right_button:
    self.input_manager.mouse_down('right')
    time.sleep(0.2)
```

### Teste 3: Usar KEY_PRESS Direto

```python
# Em arduino_input_manager.py, criar método especial:
def press_number_slot(self, slot: int) -> bool:
    """Pressionar slot usando KEY_PRESS direto (não KEY_DOWN+KEY_UP)"""
    response = self._send_command(f"KEY_PRESS:{slot}")
    return response and "OK" in response

# Em rod_manager.py:
# self.input_manager.press_key(str(slot))
self.input_manager.press_number_slot(slot)  # ← Usar comando direto
```

### Teste 4: Verificar Estado do Baú

```python
# Em chest_operation_coordinator.py, após _close_chest():
def _ensure_chest_closed(self) -> bool:
    """Garantir que baú fechou COMPLETAMENTE"""
    _safe_print("🔍 Verificando se baú fechou...")

    for i in range(5):
        # Detectar se interface de inventário sumiu
        result = self.template_engine.detect_template('inventory', confidence=0.7)
        if not result.found:
            _safe_print(f"   ✅ Baú confirmado fechado (tentativa {i+1})")
            return True

        _safe_print(f"   ⏳ Baú ainda aberto, aguardando... ({i+1}/5)")
        time.sleep(0.5)

    _safe_print("   ⚠️ Baú pode não ter fechado completamente!")
    return False
```

---

## Próximos Passos

1. ✅ Usuário confirmar comportamento manual
2. ✅ Verificar Serial Monitor para comandos chegando
3. ✅ Testar aumentar delays
4. ✅ Testar soltar/segurar botão direito
5. ✅ Implementar verificação de baú fechado

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-26
**Status:** INVESTIGANDO
