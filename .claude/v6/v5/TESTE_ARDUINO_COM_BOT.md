# Teste Arduino + Bot Python - Page Down (Manutenção de Varas)

## ✅ Status Atual

- **Arduino sketch atualizado** com comando `RESET_POS` e `MOVE`
- **ArduinoInputManager** com método `calibrate_mouseto()`
- **Código testado manualmente** via Serial Monitor (funcionando!)

## 🎯 Próximo Passo: Testar com Bot Python

### Opção 1: Teste Direto com ArduinoInputManager

```python
from core.arduino_input_manager import ArduinoInputManager

# 1. Conectar ao Arduino
arduino = ArduinoInputManager(port="COM3", baudrate=115200)
if not arduino.connect():
    print("❌ Falha ao conectar")
    exit(1)

print("✅ Arduino conectado!")

# 2. Simular abertura de baú
input("📦 Abra o baú no jogo e pressione ENTER...")

# 3. Calibrar MouseTo (RESET_POS)
if arduino.calibrate_mouseto(959, 539):
    print("✅ MouseTo calibrado!")
else:
    print("❌ Falha na calibração")
    exit(1)

# 4. Testar movimentos para slots
slots = {
    1: (709, 1005),
    2: (805, 1005),
    3: (899, 1005),
    4: (992, 1005),
    5: (1092, 1005),
    6: (1188, 1005)
}

for slot_num, (x, y) in slots.items():
    input(f"\n🎯 Mover para Slot {slot_num}? (ENTER)")

    if arduino.move_to(x, y):
        print(f"✅ Mouse em Slot {slot_num}")
    else:
        print(f"❌ Falha ao mover para Slot {slot_num}")

# 5. Limpar
arduino.cleanup()
print("\n✅ Teste completo!")
```

**Salvar como:** `test_arduino_bot_integration.py`

**Executar:**
```bash
python test_arduino_bot_integration.py
```

---

### Opção 2: Integrar com RodManager (Completo)

Para usar com o bot real, precisa integrar o `ArduinoInputManager` no `rod_manager.py`.

**Onde chamar `calibrate_mouseto()`:**

1. **No `ChestManager`** - Após abrir o baú:

```python
# chest_manager.py - linha ~150 (método open_chest)
def open_chest(self):
    # ... código existente ...

    # Detectar baú aberto
    if self.template_engine.detect_template('loot', confidence=0.7).found:
        self.chest_open = True

        # ✅ NOVO: Calibrar Arduino se disponível
        if hasattr(self.input_manager, 'calibrate_mouseto'):
            self.input_manager.calibrate_mouseto(959, 539)

        return True
```

2. **No `RodManager`** - Antes de arrastar iscas:

```python
# rod_manager.py - linha ~XXX (método perform_maintenance)
def perform_maintenance(self):
    # Abrir baú
    self.chest_manager.open_chest()

    # Arduino já foi calibrado pelo ChestManager!

    # Arrastar isca para slot
    bait_x, bait_y = self._detect_bait_in_chest()
    slot_x, slot_y = self.slot_positions[target_slot]

    # Usar drag (que usa move_to internamente)
    self.input_manager.drag(bait_x, bait_y, slot_x, slot_y)
```

---

## 🔧 Configuração do Bot para Usar Arduino

### Modificar main.py

```python
# main.py - linha ~50
from core.arduino_input_manager import ArduinoInputManager

# Criar InputManager baseado em config
USE_ARDUINO = True  # ou ler de config

if USE_ARDUINO:
    input_manager = ArduinoInputManager(port="COM3", baudrate=115200)
    input_manager.connect()
else:
    input_manager = InputManager()

# Resto do código permanece igual!
```

---

## 📋 Checklist de Teste

### Teste Manual (Serial Monitor)
- [x] Arduino responde `READY` ao ligar
- [x] `PING` retorna `PONG`
- [x] `RESET_POS:959:539` calibra corretamente (±2px de erro aceitável)
- [x] `MOVE:709:1005` move diretamente sem passar pelo canto
- [x] Sequência: RESET_POS → MOVE slot1 → MOVE slot2 → MOVE slot3 funciona

### Teste Python (arduino_input_manager.py)
- [ ] `ArduinoInputManager().connect()` conecta em COM3
- [ ] `calibrate_mouseto()` executa RESET_POS e retorna True
- [ ] `move_to(709, 1005)` move para slot 1 corretamente
- [ ] Sequência completa de 6 slots funciona

### Teste Integrado (com bot)
- [ ] Bot inicia normalmente com ArduinoInputManager
- [ ] Page Down abre baú
- [ ] MouseTo calibra automaticamente (959, 539)
- [ ] Detecção de isca funciona
- [ ] Drag de isca para slot funciona
- [ ] Baú fecha corretamente

---

## ⚠️ Troubleshooting

### Arduino não conecta
```python
# Verificar porta disponível
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"{port.device}: {port.description}")
```

### Calibração imprecisa
- Verificar `CorrectionFactor` no sketch (atualmente: 0.97)
- Rodar teste com `pyautogui.position()` após RESET_POS
- Ajustar se erro > 5 pixels

### Mouse vai para canto antes de mover
- **BUG:** `homeFirst` ainda está `true` nos comandos MOVE
- **FIX:** Já corrigido - `setTarget(x, y, false)` em `moveToPosition()`

### Movimento muito rápido/lento
- Ajustar `MOUSETO_MAX_JUMP` (linea 67 do sketch)
  - Atual: 5 (humanizado)
  - Mais rápido: 10-20
  - Mais lento: 2-3
- Ajustar `MOVE_STEP_DELAY_MS` (linha 66)
  - Atual: 3ms
  - Mais lento: 5-10ms

---

## 🎯 Resultado Esperado

Quando tudo estiver funcionando:

1. **Bot inicia** → Arduino conecta automaticamente
2. **Usuário pressiona Page Down** → Abre baú
3. **Baú abre** → Mouse está em (959, 539)
4. **ChestManager detecta baú** → Chama `calibrate_mouseto()`
5. **Arduino executa RESET_POS** → Mouse calibrado (±2px)
6. **RodManager detecta isca** → Ex: (1350, 450)
7. **RodManager chama drag()** → `MOVE:1350:450` → `DRAG` para slot
8. **Mouse move DIRETAMENTE** → Sem passar pelo canto
9. **Isca colocada** → Baú fecha
10. **Volta a pescar** → Ciclo completo!

---

## 📊 Performance Esperada

- **Calibração (RESET_POS):** ~100-200ms
- **Movimento (MOVE):** ~50-150ms por movimento
- **Drag completo:** ~500-800ms (inclui pausas)
- **Manutenção completa:** ~3-5 segundos (6 varas)

---

## ✅ Próximos Passos

1. ✅ **Teste manual via Serial Monitor** - COMPLETO
2. 🔄 **Teste com test_arduino_bot_integration.py** - VOCÊ ESTÁ AQUI
3. ⏳ **Integrar ChestManager para calibrar automaticamente**
4. ⏳ **Testar Page Down (rod maintenance) completo**
5. ⏳ **Testar feeding (alimentação)**
6. ⏳ **Testar inventory cleaning (limpeza)**

---

**Pronto para testar!** 🚀

Execute o teste com o jogo aberto e me diga o resultado!
