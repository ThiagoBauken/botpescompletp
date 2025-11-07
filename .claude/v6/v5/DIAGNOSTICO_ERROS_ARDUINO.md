# 🔧 Diagnóstico Completo: Erros no Sistema Arduino

**Data:** 2025-10-14
**Status:** BAÚ NÃO ABRE - Arduino envia comandos mas jogo não responde

---

## 🔴 ERROS ENCONTRADOS

### 1. ✅ CORRIGIDO: `_safe_print()` sem argumento

**Erro:**
```
⚠️ Erro ao logar elementos: _safe_print() missing 1 required positional argument: 'text'
```

**Localização:** `core/rod_maintenance_system.py:1621`

**Correção aplicada:**
```python
# ANTES:
_safe_print()  # ❌ ERRO

# DEPOIS:
_safe_print("")  # ✅ Passa string vazia
```

---

### 2. ❌ NÃO RESOLVIDO: ESC sendo acionado automaticamente

**Sintoma:**
```
🚨 [ESC] PARADA DE EMERGÊNCIA ATIVADA!
```

Acontece **múltiplas vezes** durante a operação do baú sem o usuário pressionar ESC.

**Hipóteses:**
1. **Keyboard library** está capturando ESC globalmente
2. **Alguma thread** está chamando `emergency_stop()` automaticamente
3. **Hook do sistema** está interceptando ALT e disparando ESC

**Precisa investigar:**
- Logs de captura de teclas
- Verificar se ALT+E está sendo interpretado como ESC
- Conferir se `keyboard.on_press_key('esc', ...)` está registrado

---

### 3. ❌ NÃO RESOLVIDO: Baú não abre - Arduino envia mas jogo não detecta

**Logs mostram:**
```
[2/5] Pressionando ALT...
   ✅ ALT pressionado via Arduino

[5/5] Pressionando E...
   ✅ E pressionado via Arduino

✅ BAÚ ABERTO COM SUCESSO!  # ❌ MENTIRA - Baú NÃO abre!
```

**Problema real:**
- Arduino **ENVIA** os comandos
- Serial Monitor confirma: `OK:KEYDOWN:ALT`, `OK:KEYPRESS:e`
- Mas o **JOGO RUST NÃO DETECTA** os inputs

**Possíveis causas:**

#### A. Jogo em Fullscreen (mais provável)
- Jogos fullscreen muitas vezes **ignoram inputs USB HID**
- Solução: **Mudar jogo para modo Janela (Borderless)**

#### B. Jogo sem foco
- Jogo precisa ter foco para receber inputs
- Solução: Garantir que jogo está ativo antes de enviar comandos

#### C. Anti-cheat bloqueando HID
- Rust pode ter anti-cheat que bloqueia inputs HID
- Solução: Tentar com PyAutoGUI em paralelo

#### D. Timing errado
- ALT pressionado mas movimento de câmera muito rápido
- E pressionado antes do movimento completar
- Solução: Aumentar delays

---

### 4. ❌ NÃO RESOLVIDO: Detecção de templates retorna 0 itens

**Logs mostram:**
```
🔍 [BACKGROUND] Detectando TODAS as ocorrências de 14 templates...
📊 [BACKGROUND] Total bruto: 0 detecções
⚪ VAZIOS: 6 slots [1, 2, 3, 4, 5, 6]
⚠️ Slot 1: Sem varas disponíveis no baú
```

**Problema:**
- Baú **provavelmente não está aberto** (por isso 0 detecções)
- OU screenshot captura antes do baú carregar

**Evidência** (3ª tentativa detectou 11 iscas):
```
🥩 Isca no BAÚ: carneurso (prioridade 2) | Captura=(1271,481)
[...] (11 iscas no total)
```

Isso confirma que **detecção funciona QUANDO o baú está aberto**.

**Conclusão:** O problema é que **o baú não abre**, então não há nada para detectar.

---

## 🎯 PLANO DE AÇÃO

### Prioridade 1: Confirmar Arduino está funcionando

**Teste isolado:**
```arduino
// No Serial Monitor do Arduino IDE:
PING              → deve responder PONG
KEYDOWN:a         → deve pressionar A
KEYUP:a           → deve soltar A
KEYPRESS:e        → deve pressionar E por 50ms
```

**Se funciona no Serial Monitor mas não no jogo:**
→ **Problema é no JOGO** (configuração, anti-cheat, modo fullscreen)

---

### Prioridade 2: Verificar configuração do jogo Rust

**Checklist:**

1. **Modo de exibição:**
   - [ ] Jogo está em **Windowed** ou **Borderless Window**?
   - [ ] Se fullscreen, mudar para Borderless

2. **Foco da janela:**
   - [ ] Jogo está em primeiro plano?
   - [ ] Nenhuma janela sobreposta?

3. **Resolução:**
   - [ ] Jogo está em 1920x1080?
   - [ ] Coordenadas do baú estão corretas?

---

### Prioridade 3: Adicionar logs de debug Arduino

**No sketch Arduino, adicionar logs:**

```cpp
void handleKeyDown(String key) {
  KeyboardKeycode keyCode = parseKey(key);
  if (keyCode != 0) {
    Keyboard.press(keyCode);
    Serial.print("OK:KEYDOWN:");
    Serial.println(key);  // ✅ ADICIONAR: confirmar qual tecla foi pressionada
  } else {
    Serial.print("ERROR:INVALID_KEY:");
    Serial.println(key);  // ✅ ADICIONAR: mostrar tecla inválida
  }
  Serial.flush();
}
```

---

### Prioridade 4: Aumentar delays e verificar ordem

**Problema potencial:** Comandos estão sendo enviados rápido demais

**Solução:**

```python
# ANTES (chest_operation_coordinator.py):
self.input_manager.key_down('ALT')
time.sleep(0.5)
self._camera_turn_in_game(delta_x, dy)
time.sleep(0.3)
self.input_manager.press_key('e')

# TESTE COM DELAYS MAIORES:
self.input_manager.key_down('ALT')
time.sleep(1.0)  # ✅ Dobrar delay do ALT
self._camera_turn_in_game(delta_x, dy)
time.sleep(0.8)  # ✅ Aumentar delay após movimento
self.input_manager.press_key('e')
time.sleep(0.2)
```

---

### Prioridade 5: Fallback PyAutoGUI + Arduino híbrido

**Se Arduino não funciona para ALT/E, usar PyAutoGUI:**

```python
# Tentar Arduino primeiro, fallback PyAutoGUI se não funcionar
if self.input_manager and hasattr(self.input_manager, 'key_down'):
    _safe_print("   🔍 [TEST] Enviando ALT via Arduino...")
    self.input_manager.key_down('ALT')
    time.sleep(0.2)

    # ✅ VERIFICAR se ALT foi pressionado (testar no jogo)
    # Se não funcionar, usar PyAutoGUI como fallback
    _safe_print("   ⚠️ [FALLBACK] Tentando ALT via PyAutoGUI...")
    pyautogui.keyDown('alt')
```

---

## 🧪 TESTES IMEDIATOS

### Teste 1: Arduino funciona fora do jogo?

1. Abrir **Notepad**
2. Dar foco no Notepad
3. No bot, pressionar **Page Down**
4. **Resultado esperado:** Texto digitado no Notepad

**Se funciona:** Arduino OK, problema é no jogo
**Se não funciona:** Arduino não está enviando inputs

---

### Teste 2: PyAutoGUI funciona no jogo?

1. Comentar código Arduino temporariamente
2. Usar **apenas PyAutoGUI**:
   ```python
   pyautogui.keyDown('alt')
   time.sleep(1.0)
   # movimento câmera
   pyautogui.press('e')
   pyautogui.keyUp('alt')
   ```
3. Testar **Page Down**

**Se funciona:** Jogo aceita PyAutoGUI mas não Arduino HID
**Se não funciona:** Problema é nas coordenadas ou timing

---

### Teste 3: Timing do movimento da câmera

**Hipótese:** Movimento API Windows não está funcionando

**Teste:**
1. Comentar movimento da câmera
2. Apenas ALT + E (sem movimento)
3. Ver se baú abre (provavelmente baú errado, mas vai confirmar ALT+E)

```python
# TESTE SEM MOVIMENTO:
self.input_manager.key_down('ALT')
time.sleep(1.5)
# self._camera_turn_in_game(delta_x, dy)  # ❌ COMENTAR
# time.sleep(0.3)
self.input_manager.press_key('e')
```

---

## 📋 CHECKLIST DE DIAGNÓSTICO

Execute na ordem:

- [ ] **1. Corrigir `_safe_print()` erro** (✅ JÁ FEITO)
- [ ] **2. Testar Arduino no Notepad** (confirmar HID funciona)
- [ ] **3. Verificar modo de exibição do Rust** (Borderless Window)
- [ ] **4. Aumentar delays ALT/E** (1.0s ALT, 0.8s após movimento)
- [ ] **5. Adicionar logs debug no sketch Arduino** (confirmar teclas)
- [ ] **6. Testar PyAutoGUI puro** (sem Arduino)
- [ ] **7. Testar ALT+E sem movimento** (confirmar teclas funcionam)
- [ ] **8. Investigar ESC automático** (desabilitar hooks ESC)
- [ ] **9. Screenshot do jogo quando baú "abre"** (confirmar se realmente abre)
- [ ] **10. Testar coordenadas chest_side/distance** (pode estar olhando lugar errado)

---

## 🔍 LOGS PARA COLETA

**Próximo teste, coletar:**

1. **Serial Monitor Arduino:**
   - Abrir Arduino IDE
   - Tools → Serial Monitor (115200 baud)
   - Pressionar Page Down
   - Copiar TUDO que aparece

2. **Screenshot do jogo:**
   - Exatamente quando baú "deveria estar aberto"
   - Confirmar se baú está visível ou não

3. **Configuração do jogo:**
   - Settings → Graphics → Display Mode: ?
   - Resolução: ?
   - Fullscreen: Yes/No?

---

## 💡 SOLUÇÃO RÁPIDA (WORKAROUND)

**Se Arduino não funcionar no Rust:**

**Usar HÍBRIDO - PyAutoGUI para teclas, Arduino para mouse:**

```python
# ALT + E via PyAutoGUI (jogo detecta)
pyautogui.keyDown('alt')
time.sleep(1.0)
self._camera_turn_in_game(delta_x, dy)  # API Windows
time.sleep(0.5)
pyautogui.press('e')
pyautogui.keyUp('alt')

# Mouse/drag operations via Arduino (mais preciso)
self.input_manager.mouse_abs(x, y)
self.input_manager.drag(x1, y1, x2, y2)
```

Isso mantém precisão do Arduino para mouse absoluto, mas usa PyAutoGUI para teclas que o jogo aceita melhor.

---

**Próximo passo:** Execute **Teste 1** (Arduino no Notepad) e reporte resultado.
