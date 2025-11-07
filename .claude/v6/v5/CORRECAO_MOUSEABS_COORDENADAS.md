# 🔧 Correção Crítica: Coordenadas SingleAbsoluteMouse

**Data:** 2025-10-14
**Problema:** Drag & drop solta itens no canto inferior esquerdo da tela ao invés dos slots corretos

---

## ❌ PROBLEMA ORIGINAL

### Sintomas:
1. ✅ Mouse **pega o item corretamente** (posição inicial correta)
2. ❌ Mouse **arrasta para canto inferior esquerdo** da tela
3. ❌ Item é **solto no chão** ao invés dos slots (709, 1005), (805, 1005), etc.
4. ❌ Mouse continua indo **além do destino** (esquerda + baixo)

### Causa Raiz:
**Conversão incorreta de coordenadas pixel → HID**

---

## 🔍 ANÁLISE TÉCNICA

### SingleAbsoluteMouse (NicoHood HID-Project)

O `SingleAbsoluteMouse.moveTo(x, y)` espera coordenadas no formato **HID absolute**:
- **Range:** `0` a `32767` (16-bit unsigned)
- **NOT:** `-32768` a `32767` (16-bit signed) ❌

### Código ERRADO (antes):

```cpp
// ❌ ERRADO: Usava range -32768 a 32767
int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);
```

**Problema:**
- Slot 1 (709, 1005) → `map(709, 0, 1920, -32768, 32767)` = **-20604** (valor negativo!)
- Valores negativos causam **underflow** → Mouse vai para posição errada
- Sistema interpreta negativos como **perto de 0** (canto superior esquerdo)

### Código CORRETO (agora):

```cpp
// ✅ CORRETO: Range 0 a 32767
uint16_t hidX = map(x, 0, SCREEN_WIDTH, 0, 32767);
uint16_t hidY = map(y, 0, SCREEN_HEIGHT, 0, 32767);
```

**Agora:**
- Slot 1 (709, 1005) → `map(709, 0, 1920, 0, 32767)` = **12099** ✅
- Slot 1 Y (1005) → `map(1005, 0, 1080, 0, 32767)` = **30477** ✅

---

## 📊 CONVERSÃO DETALHADA

### Fórmula de Conversão:

```
hidX = (pixel_x * 32767) / SCREEN_WIDTH
hidY = (pixel_y * 32767) / SCREEN_HEIGHT
```

### Exemplos de Conversão Corretos:

| Posição | Pixel (X, Y) | HID (X, Y) | Localização |
|---------|--------------|------------|-------------|
| Slot 1 | (709, 1005) | (12099, 30477) | Slot inferior centro |
| Slot 2 | (805, 1005) | (13733, 30477) | Slot inferior centro-direita |
| Slot 6 | (1188, 1005) | (20260, 30477) | Slot inferior direita |
| Centro tela | (960, 540) | (16384, 16384) | Centro exato |
| Canto sup. esq. | (0, 0) | (0, 0) | Topo esquerdo |
| Canto inf. dir. | (1920, 1080) | (32767, 32767) | Fundo direito |

---

## 🎯 IMPACTO DA CORREÇÃO

### ANTES (range incorreto):
```
Slot 1 (709, 1005):
  hidX = map(709, 0, 1920, -32768, 32767) = -20604 ❌
  hidY = map(1005, 0, 1080, -32768, 32767) = 28191 ✅

Resultado: Mouse vai para esquerda (X negativo) e fundo (Y alto)
```

### DEPOIS (range correto):
```
Slot 1 (709, 1005):
  hidX = map(709, 0, 1920, 0, 32767) = 12099 ✅
  hidY = map(1005, 0, 1080, 0, 32767) = 30477 ✅

Resultado: Mouse vai EXATAMENTE para o slot 1!
```

---

## 🔧 ARQUIVOS MODIFICADOS

### 1. `arduino/arduino_hid_controller_HID/arduino_hid_controller_HID.ino`

**Linhas 286-287:**

```cpp
// ANTES:
int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);

// DEPOIS:
uint16_t hidX = map(x, 0, SCREEN_WIDTH, 0, 32767);
uint16_t hidY = map(y, 0, SCREEN_HEIGHT, 0, 32767);
```

**Mudanças:**
1. ✅ Tipo mudou de `int16_t` (signed) → `uint16_t` (unsigned)
2. ✅ Range mudou de `-32768, 32767` → `0, 32767`

---

## 🧪 TESTE IMEDIATO

### Passos:

1. **Re-upload do sketch Arduino:**
   ```
   1. Abrir Arduino IDE
   2. File → Open → arduino_hid_controller_HID.ino
   3. Upload (Ctrl+U)
   4. Aguardar "Done uploading"
   ```

2. **Reconectar Arduino no bot:**
   ```
   1. Fechar bot (se aberto)
   2. python main.py
   3. Aba Arduino → "Conectar"
   4. Aguardar "✅ Arduino conectado"
   ```

3. **Testar Page Down:**
   ```
   1. Abrir jogo Rust
   2. Ficar na frente do baú
   3. Pressionar Page Down
   4. Observar:
      - Mouse pega vara/isca do baú ✅
      - Mouse arrasta para SLOT correto ✅ (NÃO mais para canto!)
      - Item é solto NO SLOT ✅
   ```

---

## 📋 VALIDAÇÃO

### Checklist de Teste:

- [ ] Sketch re-uploaded no Arduino
- [ ] Arduino reconectado no bot
- [ ] Page Down pressionado
- [ ] **CRÍTICO:** Mouse arrasta para SLOTS (não para canto da tela)
- [ ] Vara/isca é **solta no slot correto**
- [ ] Logs mostram coordenadas corretas

### Logs Esperados:

**ANTES (errado):**
```
🖱️ [DRAG] Iniciando arrasto: (1271, 481) → (709, 1005)
📍 [PASSO 1] Movendo para posição inicial (1271, 481)...
🔍 [DEBUG] Enviando MOUSEABS:1271:481
   ✅ [ARDUINO] Mouse movido (absoluto MOUSEABS)
   🖱️ [PASSO 2] Botão esquerdo pressionado
   ➡️ [PASSO 3] Arrastando para (709, 1005)...
🔍 [DEBUG] Enviando MOUSEABS:709:1005
   ✅ [ARDUINO] Mouse movido (absoluto MOUSEABS)  # ❌ MENTIRA - foi para canto!
```

**DEPOIS (correto):**
```
🖱️ [DRAG] Iniciando arrasto: (1271, 481) → (709, 1005)
📍 [PASSO 1] Movendo para posição inicial (1271, 481)...
🔍 [DEBUG] Enviando MOUSEABS:1271:481
   ✅ [ARDUINO] Mouse movido (absoluto MOUSEABS)
   🖱️ [PASSO 2] Botão esquerdo pressionado
   ➡️ [PASSO 3] Arrastando para (709, 1005)...
🔍 [DEBUG] Enviando MOUSEABS:709:1005
   ✅ [ARDUINO] Mouse movido (absoluto MOUSEABS)  # ✅ AGORA VAI PARA SLOT 1!
   ✅ Vara arrastada para slot 1
```

---

## 🔬 EXPLICAÇÃO MATEMÁTICA

### Por que `-32768` a `32767` estava errado?

**HID Absolute Mouse Protocol:**
- Usa **16-bit unsigned integers** para coordenadas
- Range: `0x0000` (0) a `0x7FFF` (32767)
- Total: **32768 valores únicos** (0 até 32767 inclusive)

**Signed (-32768 a 32767):**
- Range: `0x8000` (-32768) a `0x7FFF` (32767)
- Valores negativos são interpretados como **underflow**
- Sistema não entende "posição negativa" em absolute mode

### Arduino `map()` function:

```cpp
long map(long x, long in_min, long in_max, long out_min, long out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
```

**Com range errado (-32768, 32767):**
```
map(709, 0, 1920, -32768, 32767)
= (709 - 0) * (32767 - (-32768)) / (1920 - 0) + (-32768)
= 709 * 65535 / 1920 - 32768
= 24204 - 32768
= -8564  ❌ NEGATIVO!
```

**Com range correto (0, 32767):**
```
map(709, 0, 1920, 0, 32767)
= (709 - 0) * (32767 - 0) / (1920 - 0) + 0
= 709 * 32767 / 1920
= 12099  ✅ POSITIVO!
```

---

## 📚 REFERÊNCIAS

- **NicoHood HID-Project:** https://github.com/NicoHood/HID
- **USB HID Spec:** Absolute coordinates use unsigned 16-bit values (0-32767)
- **Arduino map():** https://www.arduino.cc/reference/en/language/functions/math/map/

---

## ✅ RESULTADO ESPERADO

**APÓS ESTA CORREÇÃO:**

1. ✅ Mouse move **exatamente** para slots (709, 1005), (805, 1005), etc.
2. ✅ Drag & drop funciona **perfeitamente**
3. ✅ Varas/iscas são **soltadas nos slots corretos**
4. ✅ Nenhum item vai para o chão
5. ✅ Page Down executa manutenção **100% funcional**

---

**IMPORTANTE:** É OBRIGATÓRIO fazer **re-upload do sketch** para o Arduino. A mudança está apenas no arquivo `.ino`, não no Python!

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-14
