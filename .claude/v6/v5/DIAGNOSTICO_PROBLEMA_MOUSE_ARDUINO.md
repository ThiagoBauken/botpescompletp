# 🔍 Diagnóstico: Mouse Arduino Não Posiciona Corretamente

**Data:** 2025-10-22
**Problema Relatado:** Arduino não consegue mover o mouse corretamente para detecções de varas (com/sem isca), iscas no baú e slots.

---

## ❌ SINTOMAS

1. **Detecção funciona** - Template engine encontra isca/vara corretamente
2. **Coordenadas corretas** - Python detecta posição correta (ex: 1350, 450)
3. **Mouse não vai para lá** - Arduino recebe comando mas mouse vai para lugar errado
4. **Slots também falham** - Mouse não chega nos slots (709, 1005), (805, 1005), etc.

---

## 🔍 POSSÍVEIS CAUSAS

### Causa #1: Versão Errada do Arduino Sketch
**Problema:** Existem 3 versões diferentes de código Arduino no projeto!

| Arquivo | Biblioteca | Status | Problema |
|---------|-----------|--------|----------|
| `arduino_hid_controller.ino` | Mouse.h nativo | ❌ Antigo | Usa `serialEvent()` não confiável |
| `arduino_hid_controller_FIXED.ino` | AbsMouse | ⚠️ Parcial | AbsMouse pode ter bugs |
| `arduino_hid_controller_HID.ino` | MouseTo + HID | ✅ **MELHOR** | Mais confiável |

**Qual você está usando?**

### Causa #2: Conversão de Coordenadas Errada
**Problema:** Range de conversão pixel → HID estava ERRADO!

#### ❌ CÓDIGO ERRADO (pode estar no seu Arduino):
```cpp
// ERRADO: Range -32768 a 32767 (valores negativos causam bug!)
int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);
```

**Resultado:**
- Slot 1 (709, 1005) → hidX = **-8564** ❌ (negativo!)
- Mouse vai para **canto inferior esquerdo** ao invés do slot

#### ✅ CÓDIGO CORRETO:
```cpp
// CORRETO: Range 0 a 32767 (apenas valores positivos!)
uint16_t hidX = map(x, 0, SCREEN_WIDTH, 0, 32767);
uint16_t hidY = map(y, 0, SCREEN_HEIGHT, 0, 32767);
```

**Resultado:**
- Slot 1 (709, 1005) → hidX = **12099** ✅
- Mouse vai **exatamente** para o slot!

**📂 Verificar no arquivo:** `arduino_hid_controller_HID.ino` linha ~286-287

### Causa #3: Falta de Calibração (MouseTo)
**Problema:** MouseTo precisa de calibração inicial!

Se você está usando `arduino_hid_controller_HID.ino` (MouseTo):

```cpp
// OBRIGATÓRIO após abrir baú:
RESET_POS:959:539
```

**Por quê?**
- MouseTo rastreia posição internamente
- Quando jogo abre baú, teleporta mouse para (959, 539)
- MouseTo não detecta isso automaticamente
- Precisa `RESET_POS` para sincronizar!

**Onde chamar:**
```python
# Em ChestManager.open_chest() - após detectar baú aberto:
if hasattr(self.input_manager, 'calibrate_mouseto'):
    self.input_manager.calibrate_mouseto(959, 539)
```

### Causa #4: Resolução de Tela Incorreta
**Problema:** Arduino configurado para resolução errada!

```cpp
// Verificar no Arduino sketch:
#define SCREEN_WIDTH 1920   // ← Está correto?
#define SCREEN_HEIGHT 1080  // ← Está correto?
```

Se sua resolução for diferente (ex: 2560x1440, 1366x768), **TODAS** as coordenadas estarão erradas!

**Como verificar:**
```python
import pyautogui
print(pyautogui.size())  # Deve retornar Size(width=1920, height=1080)
```

### Causa #5: Fator de Correção Errado
**Problema:** Mesmo com código correto, pode haver imprecisão de +/- 20 pixels

```cpp
// Em arduino_hid_controller_HID.ino linha ~83:
MouseTo.setCorrectionFactor(0.97);  // ← Ajuste este valor!
```

**Valores sugeridos:**
- Mouse **indo longe demais**: `0.95` - `0.98`
- Mouse **não chegando**: `1.02` - `1.05`
- **Padrão:** `1.0` (sem correção)

---

## 🧪 DIAGNÓSTICO PASSO A PASSO

### Teste 1: Verificar Qual Sketch Está no Arduino

```bash
# Abrir Serial Monitor (Arduino IDE)
# Enviar: PING
# Deve retornar: PONG

# Enviar: MOUSEABS:960:540
# OU: MOVE:960:540
# OU: RESET_POS:960:540

# Se responder OK → Versão está correta
# Se responder ERROR:UNKNOWN_COMMAND → Versão errada!
```

### Teste 2: Verificar Conversão de Coordenadas

**Execute:**
```python
python test_arduino_precision.py
```

**Esperado:**
- Erro médio < 10 pixels ✅
- Erro médio > 20 pixels ❌ (precisa correção)

### Teste 3: Teste Manual de Posicionamento

```python
# Criar arquivo: test_arduino_manual_positioning.py

from core.arduino_input_manager import ArduinoInputManager
import time

arduino = ArduinoInputManager(port="COM10", baudrate=115200)
if not arduino.connect():
    print("❌ Falha ao conectar")
    exit(1)

print("✅ Arduino conectado!")

# Teste 1: Centro da tela
print("\n🎯 Teste 1: Movendo para centro (960, 540)")
input("Abra o jogo e pressione ENTER...")

arduino.move_to(960, 540)
time.sleep(2)

real_pos = input("Onde o mouse foi? (digite 'ok' se correto): ")

# Teste 2: Slot 1
print("\n🎯 Teste 2: Movendo para Slot 1 (709, 1005)")
arduino.move_to(709, 1005)
time.sleep(2)

real_pos = input("Mouse está no Slot 1? (s/n): ")

# Teste 3: Isca no baú (exemplo)
print("\n🎯 Teste 3: Movendo para posição de isca (1350, 450)")
arduino.move_to(1350, 450)
time.sleep(2)

real_pos = input("Mouse está sobre uma isca no baú? (s/n): ")

arduino.cleanup()
print("\n✅ Teste concluído!")
```

**Execute:**
```bash
python test_arduino_manual_positioning.py
```

---

## 🔧 SOLUÇÕES

### Solução #1: Usar o Sketch Correto
**Recomendado:** `arduino_hid_controller_HID.ino` (com MouseTo)

**Passos:**
1. Abrir Arduino IDE
2. File → Open → `arduino/arduino_hid_controller_HID/arduino_hid_controller_HID.ino`
3. **Verificar linhas 286-287:**
   ```cpp
   // DEVE SER uint16_t e range 0 a 32767:
   uint16_t hidX = map(x, 0, SCREEN_WIDTH, 0, 32767);
   uint16_t hidY = map(y, 0, SCREEN_HEIGHT, 0, 32767);
   ```
4. Sketch → Upload (Ctrl+U)
5. Aguardar "Done uploading"

### Solução #2: Corrigir Conversão de Coordenadas
Se estiver usando HID-Project:

**Editar:** `arduino_hid_controller_HID.ino` linhas 286-287

**ANTES:**
```cpp
int16_t hidX = map(x, 0, SCREEN_WIDTH, -32768, 32767);
int16_t hidY = map(y, 0, SCREEN_HEIGHT, -32768, 32767);
```

**DEPOIS:**
```cpp
uint16_t hidX = map(x, 0, SCREEN_WIDTH, 0, 32767);
uint16_t hidY = map(y, 0, SCREEN_HEIGHT, 0, 32767);
```

**Re-upload!**

### Solução #3: Adicionar Calibração Automática
**Editar:** `core/chest_manager.py`

**Adicionar após linha ~150 (método open_chest):**
```python
def open_chest(self):
    # ... código existente ...

    # Detectar baú aberto
    if self.template_engine.detect_template('loot', confidence=0.7).found:
        self.chest_open = True

        # ✅ NOVO: Calibrar Arduino se disponível
        if hasattr(self.input_manager, 'calibrate_mouseto'):
            print("🎯 Calibrando MouseTo após abrir baú...")
            self.input_manager.calibrate_mouseto(959, 539)

        return True
```

### Solução #4: Ajustar Fator de Correção
**Editar:** `arduino_hid_controller_HID.ino` linha ~83

**Teste valores entre 0.95 e 1.05:**
```cpp
MouseTo.setCorrectionFactor(0.97);  // Começar com 0.97

// Se mouse indo LONGE demais: diminuir (0.95)
// Se mouse NÃO CHEGANDO: aumentar (1.02)
```

**Re-upload após cada ajuste!**

---

## 📋 CHECKLIST DE CORREÇÃO

### Passo 1: Verificar Versão do Arduino
- [ ] Abrir Arduino IDE
- [ ] Verificar qual arquivo .ino está aberto
- [ ] Confirmar se é `arduino_hid_controller_HID.ino` (com MouseTo)

### Passo 2: Verificar Conversão de Coordenadas
- [ ] Abrir `arduino_hid_controller_HID.ino`
- [ ] Ir para linhas 286-287
- [ ] Confirmar `uint16_t` (NÃO `int16_t`)
- [ ] Confirmar range `0, 32767` (NÃO `-32768, 32767`)

### Passo 3: Re-Upload do Sketch
- [ ] Sketch → Upload (Ctrl+U)
- [ ] Aguardar "Done uploading"
- [ ] Fechar Arduino IDE

### Passo 4: Testar Conexão
- [ ] Executar `python test_arduino_manual_positioning.py`
- [ ] Verificar se mouse vai para posições corretas
- [ ] Ajustar `CorrectionFactor` se necessário

### Passo 5: Integrar Calibração
- [ ] Adicionar `calibrate_mouseto()` no `ChestManager`
- [ ] Testar Page Down (manutenção de varas)
- [ ] Verificar se drag funciona corretamente

---

## 🎯 RESULTADO ESPERADO

**APÓS CORREÇÕES:**
1. ✅ Mouse move **exatamente** para slots (709, 1005), (805, 1005), etc.
2. ✅ Mouse move **exatamente** para iscas detectadas no baú
3. ✅ Drag & drop funciona **perfeitamente**
4. ✅ Page Down executa manutenção **100% funcional**
5. ✅ Erro de posicionamento < 5 pixels

---

## 🆘 SE AINDA NÃO FUNCIONAR

**Execute o teste de diagnóstico completo:**

```bash
# 1. Teste de precisão
python test_arduino_precision.py

# 2. Verificar logs
# Veja onde o mouse REALMENTE foi vs onde deveria ir

# 3. Ajustar CorrectionFactor
# Editar arduino_hid_controller_HID.ino linha 83
# Testar valores: 0.95, 0.97, 1.0, 1.02, 1.05

# 4. Re-upload após CADA ajuste!
```

**Me envie os resultados:**
- Qual arquivo Arduino você está usando?
- Qual o erro médio no test_arduino_precision.py?
- Mouse vai para onde quando você tenta ir para (709, 1005)?

---

**Desenvolvido para Ultimate Fishing Bot v5**
**Última atualização:** 2025-10-22
