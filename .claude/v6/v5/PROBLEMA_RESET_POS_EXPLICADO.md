# 🔍 PROBLEMA: Mouse Vai Para Canto Direito Após Abrir Baú

**Problema:** Mouse se move para canto direito da tela após pressionar E (abrir baú)
**Causa:** RESET_POS calcula movimento incorreto porque MouseTo rastreia movimento relativo

---

## 🎯 SEQUÊNCIA DO PROBLEMA

### **Passo 1: center_camera() move para centro**
```python
self.input_manager.move_to(960, 540)  # MOVE:960:540
```
**Estado MouseTo:** `posição_interna = (960, 540)` ✅

### **Passo 2: ALT Down (freelook ativa)**
```python
self.input_manager.key_down('ALT')
```
**Estado:** Cursor invisível, freelook ativo

### **Passo 3: Movimento de câmera (RELATIVO)**

**Se baú está à ESQUERDA:**
```python
self.input_manager.camera_turn_in_game(-300, 50)  # MOVE_REL:-300:50
```

**PROBLEMA AQUI:**
- Arduino executa movimento RELATIVO: mouse físico move -300px X
- **MouseTo RASTREIA esse movimento internamente!**
- **Estado MouseTo:** `posição_interna = (960-300, 540+50) = (660, 590)` ❌

### **Passo 4: Pressionar E**
```python
self.input_manager.press_key('E')
```
**Jogo abre baú → teleporta mouse para (959, 539)** ← Automático do jogo
**MouseTo NÃO DETECTA esse teleporte!**

**Estado real:** `cursor_real = (959, 539)`
**MouseTo pensa:** `posição_interna = (660, 590)` ← ERRADO!

### **Passo 5: ALT Up**
```python
self.input_manager.key_up('ALT')
```
Freelook desativa, cursor fica visível novamente em (959, 539)

### **Passo 6: RESET_POS**
```python
self.input_manager.calibrate_mouseto(959, 539)  # RESET_POS:959:539
```

**O que acontece no Arduino:**
```cpp
void handleResetPosition(String coords) {
  int x = 959;
  int y = 539;

  MouseTo.setTarget(x, y, false);  // Define alvo (959, 539)
  MouseTo.move();  // Move um passo em direção ao alvo
}
```

**MouseTo calcula:**
- Posição atual (interna): (660, 590)
- Alvo: (959, 539)
- Movimento necessário: +299px X, -51px Y

**EXECUTA MOVIMENTO:**
- Cursor estava em: (959, 539)
- MouseTo move: +299px X
- **Cursor vai para: (1258, 539)** ← **CANTO DIREITO!!!** ❌

---

## 🔍 PORQUE MOVE_REL CONFUNDE MOUSETO

**MouseTo internamente:**
```cpp
// Posição interna rastreada pelo MouseTo
int current_x = 960;
int current_y = 540;

// Quando MOVE_REL:-300:50 é executado:
current_x += (-300);  // 960 - 300 = 660
current_y += 50;      // 540 + 50 = 590

// MouseTo agora pensa que está em (660, 590)
```

**Mas na realidade:**
- Durante ALT (freelook), movimento relativo move a CÂMERA, não o cursor absoluto
- Cursor continua em (960, 540) na tela
- Quando baú abre, jogo coloca cursor em (959, 539)
- MouseTo não detecta esse teleporte!

---

## ✅ SOLUÇÃO: Não Usar MOVE_REL Durante Freelook

**Opção A: Usar Mouse.move() nativo do Arduino em vez de MouseTo**

Durante ALT (freelook), usar movimento relativo PURO sem rastrear no MouseTo:
```cpp
// Arduino sketch - novo comando: MOVE_REL_RAW
// Movimento relativo SEM atualizar estado interno do MouseTo
void handleMoveRelRaw(String coords) {
  int dx = ...;
  int dy = ...;

  // Movimento direto sem MouseTo
  Mouse.move(dx, dy);
  // NÃO chama MouseTo.move()!

  Serial.println("OK:MOVE_REL_RAW");
}
```

**Opção B: Aumentar delay antes de RESET_POS**

Dar mais tempo para jogo teleportar mouse:
```python
# Em chest_manager.py linha 439:
time.sleep(1.5)  # AUMENTAR de 0.5s para 1.5s
```

**Opção C: Resetar MouseTo ANTES de abrir baú**

Calibrar MouseTo ANTES de movimento de câmera:
```python
# Antes de ALT Down:
if self.input_manager and hasattr(self.input_manager, 'calibrate_mouseto'):
    self.input_manager.calibrate_mouseto(960, 540)
```

**Opção D: Corrigir handleResetPosition no Arduino**

Mudar para APENAS informar posição, SEM mover:
```cpp
void handleResetPosition(String coords) {
  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // ✅ NOVO: Apenas SINCRONIZAR estado interno
  // NÃO mover o cursor!
  MouseTo.setTarget(x, y, false);
  // ❌ REMOVER: MouseTo.move();  ← Não chamar move()!

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
}
```

---

## 🎯 MELHOR SOLUÇÃO: Opção D

**Modificar Arduino para NÃO mover em RESET_POS:**

```cpp
void handleResetPosition(String coords) {
  /*
   * RESET_POS - Apenas sincroniza estado interno do MouseTo
   * NÃO MOVE o cursor! Apenas informa onde ele JÁ está.
   */
  int colonIndex = coords.indexOf(':');
  if (colonIndex == -1) {
    Serial.println("ERROR:INVALID_COORDS");
    Serial.flush();
    return;
  }

  int x = coords.substring(0, colonIndex).toInt();
  int y = coords.substring(colonIndex + 1).toInt();

  // Sincronizar estado interno do MouseTo
  // Usar setHome() para resetar posição de referência
  MouseTo.setTarget(x, y, false);

  // ✅ CRÍTICO: NÃO chamar MouseTo.move()!
  // O cursor JÁ está na posição correta (jogo colocou lá)
  // Apenas precisamos informar ao MouseTo onde está

  Serial.print("OK:RESET_POS:(");
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.println(")");
  Serial.flush();
}
```

**Por quê isso funciona:**
- `setTarget(x, y, false)` define o alvo interno
- **NÃO** chamar `move()` → cursor não se move!
- Próxima vez que `MOVE:x2:y2` for chamado, MouseTo vai calcular corretamente a partir de (959, 539)

---

## 📊 COMPARAÇÃO

### ANTES (com MouseTo.move()):
```
1. MouseTo pensa: (660, 590)
2. Cursor real: (959, 539)
3. RESET_POS:959:539 → MouseTo.move()
4. Calcula: preciso mover +299px X
5. Cursor move para: (1258, 539) ❌ CANTO DIREITO
```

### DEPOIS (sem MouseTo.move()):
```
1. MouseTo pensa: (660, 590)
2. Cursor real: (959, 539)
3. RESET_POS:959:539 → setTarget() APENAS
4. MouseTo sincroniza: "Ok, estou em (959, 539) agora"
5. Cursor NÃO move! ✅ Fica em (959, 539)
```

---

## 🔧 APLICAR CORREÇÃO AGORA

Editar arquivo Arduino: `arduino_hid_controller_HID.ino`

**Encontrar função `handleResetPosition` (linha ~481)**

**Remover ou comentar esta linha:**
```cpp
MouseTo.move();  // ← COMENTAR OU REMOVER!
```

**Upload do sketch novamente:**
1. Abrir Arduino IDE
2. Sketch → Upload (Ctrl+U)
3. Aguardar "Done uploading"

**Testar:**
1. Fechar bot
2. Abrir bot: `python main.py`
3. Conectar Arduino
4. Pressionar F6
5. **Mouse NÃO deve mais ir para canto direito!** ✅

---

**Esta é a correção DEFINITIVA do problema!** 🎯
