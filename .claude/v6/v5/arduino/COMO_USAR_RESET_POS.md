# Como Usar o Sistema RESET_POS

## Conceito

O MouseTo precisa saber onde o mouse está para calcular movimentos absolutos. Em vez de fazer "homing" (ir para o canto) toda vez, fazemos **uma única calibração** quando o baú abre.

## Funcionamento

### 1. **RESET_POS:959:539** (UMA VEZ após abrir baú)

Quando você abre o baú, o jogo coloca o mouse automaticamente em **(959, 539)**.

Nesse momento, envie:
```
RESET_POS:959:539
```

Isso faz:
- Vai para (0,0) uma vez (homing)
- Move para (959, 539)
- Calibra o sistema de coordenadas do MouseTo

**Resposta:**
```
DEBUG:MOVES=54,TIME=58ms
OK:RESET_POS:(959,539)
```

### 2. **MOVE:x:y** (todos os movimentos seguintes)

Depois do `RESET_POS`, **todos** os `MOVE` vão **diretamente** para o destino, sem passar pelo canto.

Exemplo:
```
MOVE:1306:858    # Vai direto de (959,539) → (1306,858)
MOVE:1403:877    # Vai direto de (1306,858) → (1403,877)
MOVE:1083:373    # Vai direto de (1403,877) → (1083,373)
```

Nenhum desses movimentos passa pelo canto superior direito!

## Sequência de Uso

### Alimentação (Feeding)

```python
# 1. Abrir baú
abrir_bau()  # Mouse fica em (959, 539)

# 2. CALIBRAR (UMA VEZ)
arduino.send("RESET_POS:959:539")

# 3. Movimentos diretos
arduino.send("MOVE:1306:858")   # Slot 1 comida
arduino.send("CLICK:1306:858")  # Pegar comida

arduino.send("MOVE:1403:877")   # Slot 2 comida
arduino.send("CLICK:1403:877")  # Pegar comida

arduino.send("MOVE:1083:373")   # Botão "comer"
arduino.send("CLICK:1083:373")  # Clicar N vezes
```

### Manutenção de Varas (Rod Maintenance)

```python
# 1. Abrir baú
abrir_bau()  # Mouse fica em (959, 539)

# 2. CALIBRAR (UMA VEZ)
arduino.send("RESET_POS:959:539")

# 3. Arrastar isca do baú para slot da vara
bait_x, bait_y = detectar_isca_no_bau()  # Ex: (1350, 450)
slot_x, slot_y = (709, 1005)  # Slot 1

arduino.send(f"DRAG:{bait_x}:{bait_y}:{slot_x}:{slot_y}")
# Resultado: Mouse vai direto para isca, arrasta até slot
```

### Limpeza de Inventário (Cleaning)

```python
# 1. Abrir baú
abrir_bau()  # Mouse fica em (959, 539)

# 2. CALIBRAR (UMA VEZ)
arduino.send("RESET_POS:959:539")

# 3. Arrastar itens do inventário para o baú
for item in itens_para_limpar:
    inv_x, inv_y = item.position  # Ex: (850, 750)
    chest_x = 1450  # Área do baú
    chest_y = 400

    arduino.send(f"DRAG:{inv_x}:{inv_y}:{chest_x}:{chest_y}")
    # Todos os drags são diretos, sem passar pelo canto
```

## Por Que Isso Funciona?

### Sem RESET_POS (problema):
```
MOVE:709:1005
  → Mouse vai para (0,0) primeiro [CANTO]
  → Depois vai para (709,1005)
  ❌ Movimento desnecessário, visível, suspeito
```

### Com RESET_POS (solução):
```
RESET_POS:959:539  [uma vez ao abrir baú]
  → Mouse vai para (0,0) [calibração inicial]
  → Move para (959,539)
  → MouseTo sabe: "mouse está em (959,539)"

MOVE:709:1005  [movimento direto]
  → MouseTo calcula: de (959,539) para (709,1005)
  → Move diretamente, sem passar por (0,0)
  ✅ Movimento natural e direto
```

## Coordenadas Importantes

### Posição Após Abrir Baú
```
(959, 539)  ← Posição automática do mouse quando baú abre
```

### Slots de Varas (Rod Slots)
```
Slot 1: (709, 1005)
Slot 2: (805, 1005)
Slot 3: (899, 1005)
Slot 4: (992, 1005)
Slot 5: (1092, 1005)
Slot 6: (1188, 1005)
```

### Alimentação (Feeding)
```
Comida Slot 1: (1306, 858)  ← No baú
Comida Slot 2: (1403, 877)  ← No baú
Botão Comer:   (1083, 373)  ← Na tela
```

## Código Python Exemplo

```python
class ArduinoInputManager:
    def __init__(self, serial_port):
        self.serial = serial.Serial(serial_port, 115200)
        self.calibrated = False

    def open_chest_and_calibrate(self):
        """Abre baú e calibra MouseTo"""
        # 1. Abrir baú (pyautogui ou detecção)
        # ... código para abrir baú ...
        time.sleep(0.5)  # Aguardar baú abrir

        # 2. Calibrar MouseTo com posição conhecida
        self.serial.write(b"RESET_POS:959:539\n")
        response = self.serial.readline().decode().strip()

        if "OK:RESET_POS" in response:
            print("✅ MouseTo calibrado em (959, 539)")
            self.calibrated = True
        else:
            print(f"❌ Erro na calibração: {response}")

    def move_to(self, x, y):
        """Move para posição absoluta"""
        if not self.calibrated:
            print("⚠️ MouseTo não calibrado! Chame open_chest_and_calibrate() primeiro")
            return False

        cmd = f"MOVE:{x}:{y}\n"
        self.serial.write(cmd.encode())
        response = self.serial.readline().decode().strip()

        return "OK:MOVE" in response

    def drag(self, x1, y1, x2, y2):
        """Arrasta de (x1,y1) para (x2,y2)"""
        if not self.calibrated:
            print("⚠️ MouseTo não calibrado! Chame open_chest_and_calibrate() primeiro")
            return False

        cmd = f"DRAG:{x1}:{y1}:{x2}:{y2}\n"
        self.serial.write(cmd.encode())
        response = self.serial.readline().decode().strip()

        return "OK:DRAG" in response

# Uso:
arduino = ArduinoInputManager("COM3")

# Feeding
arduino.open_chest_and_calibrate()  # UMA VEZ
arduino.move_to(1306, 858)          # Direto para comida
arduino.move_to(1083, 373)          # Direto para botão comer

# Rod maintenance
arduino.open_chest_and_calibrate()  # UMA VEZ
arduino.drag(1350, 450, 709, 1005)  # Direto: isca → slot 1
```

## Vantagens

✅ **Uma calibração por sessão**: RESET_POS só é chamado uma vez ao abrir o baú
✅ **Movimentos diretos**: Nenhum movimento passa pelo canto da tela
✅ **Natural**: Movimentos parecem humanos, mouse vai direto ao destino
✅ **Preciso**: MouseTo usa coordenadas absolutas detectadas pelo OpenCV
✅ **Compatível**: Funciona com todo o sistema de detecção existente

## Diferença Visual

### Antes (COM homing automático):
```
Mouse: (959,539) → (0,0) → (709,1005)
       └─────────────┘   └──────────┘
       desnecessário     movimento real
```

### Depois (COM RESET_POS uma vez):
```
RESET_POS: (959,539) → (0,0) → (959,539)  [uma vez]
           └──────────────────────────┘
           calibração inicial

MOVE:      (959,539) ──────→ (709,1005)   [todos os movimentos]
           └──────────────────────────┘
           movimento direto
```

## Resumo

1. **Abriu baú** → Chama `RESET_POS:959:539` (UMA VEZ)
2. **Todos os movimentos seguintes** → Usa `MOVE:x:y` (vai direto)
3. **Fechou baú** → Na próxima abertura, chama `RESET_POS` novamente

Isso resolve o problema do mouse ir para o canto antes de cada movimento! 🎯
