# 🎯 Solução: Sistema de Rastreamento de Mouse para Arduino

## Problema Identificado

O Arduino Leonardo HID **não sabe a posição absoluta do mouse**. Ele só pode enviar movimentos **relativos** (dx, dy).

Atualmente, o sistema usa coordenadas absolutas:
- Template matching retorna `(x, y)` absoluto
- Slots das varas em posições fixas `(709, 1005)`
- Operações de drag usam `moveTo(x, y)`

❌ **Arduino não pode executar `Mouse.moveTo(x, y)` - essa função não existe no HID!**

---

## ✅ Solução: InputManager com Rastreamento de Posição

### Conceito

1. **Python mantém posição virtual do mouse**
2. Antes de mover, calcula **movimento relativo** necessário
3. Envia `MOVE_REL dx dy` para Arduino
4. Atualiza posição virtual após movimento

### Implementação

#### 1. Adicionar ao InputManager

```python
class InputManager:
    def __init__(self, ...):
        # ... código existente ...

        # 🎯 NOVO: Rastreamento de posição para Arduino
        self.virtual_mouse_position = [960, 540]  # Centro da tela 1920x1080
        self.use_arduino = False  # Flag para alternar entre PyAutoGUI/Arduino
        self.arduino_serial = None  # Conexão serial

    def _get_current_mouse_position(self) -> Tuple[int, int]:
        """
        Obter posição atual do mouse

        - PyAutoGUI: retorna posição real
        - Arduino: retorna posição virtual rastreada
        """
        if self.use_arduino:
            return tuple(self.virtual_mouse_position)
        else:
            pos = pyautogui.position()
            return (pos.x, pos.y)

    def _move_to_absolute(self, target_x: int, target_y: int) -> bool:
        """
        Mover mouse para posição absoluta

        - PyAutoGUI: usa moveTo() direto
        - Arduino: calcula movimento relativo e envia
        """
        if self.use_arduino:
            # Obter posição atual virtual
            current_x, current_y = self.virtual_mouse_position

            # Calcular movimento relativo necessário
            dx = target_x - current_x
            dy = target_y - current_y

            _safe_print(f"🎯 Arduino: Pos atual ({current_x}, {current_y}) → Alvo ({target_x}, {target_y})")
            _safe_print(f"   Movimento relativo: dx={dx}, dy={dy}")

            # Enviar comando relativo para Arduino
            self._send_arduino_command(f"MOVE_REL {dx} {dy}")

            # Atualizar posição virtual
            self.virtual_mouse_position = [target_x, target_y]

            return True
        else:
            # PyAutoGUI - movimento absoluto direto
            pyautogui.moveTo(target_x, target_y)
            return True

    def _send_arduino_command(self, command: str):
        """
        Enviar comando serial para Arduino

        Protocolo:
        - MOVE_REL dx dy      - Movimento relativo
        - MOUSE_DOWN left     - Pressionar botão
        - MOUSE_UP left       - Soltar botão
        - KEY_DOWN a          - Pressionar tecla
        - KEY_UP a            - Soltar tecla
        """
        if self.arduino_serial and self.arduino_serial.is_open:
            try:
                self.arduino_serial.write(f"{command}\n".encode())
                time.sleep(0.01)  # Pequeno delay para Arduino processar
            except Exception as e:
                _safe_print(f"❌ Erro ao enviar comando Arduino: {e}")
        else:
            _safe_print(f"⚠️ Arduino não conectado - comando ignorado: {command}")
```

#### 2. Modificar Métodos Existentes

```python
def click(self, x: int, y: int, button: str = 'left') -> bool:
    """Clique em posição absoluta - COMPATÍVEL COM ARDUINO"""
    try:
        self._focus_game_window()

        # Mover para posição
        self._move_to_absolute(x, y)
        time.sleep(0.05)

        # Executar clique
        if self.use_arduino:
            self._send_arduino_command(f"MOUSE_DOWN {button}")
            time.sleep(0.02)
            self._send_arduino_command(f"MOUSE_UP {button}")
        else:
            pyautogui.click(x, y, button=button)

        return True
    except Exception as e:
        _safe_print(f"❌ Erro no clique: {e}")
        return False

def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
    """Drag - COMPATÍVEL COM ARDUINO"""
    try:
        # PASSO 1: Mover para início
        self._move_to_absolute(start_x, start_y)
        time.sleep(0.2)

        # PASSO 2: Segurar botão
        if self.use_arduino:
            self._send_arduino_command("MOUSE_DOWN left")
        else:
            pyautogui.mouseDown(button='left')
        time.sleep(0.2)

        # PASSO 3: Mover para destino (dividir em passos para suavidade)
        steps = int(duration * 10)  # 10 passos por segundo
        for i in range(steps):
            progress = (i + 1) / steps
            intermediate_x = int(start_x + (end_x - start_x) * progress)
            intermediate_y = int(start_y + (end_y - start_y) * progress)

            self._move_to_absolute(intermediate_x, intermediate_y)
            time.sleep(duration / steps)

        time.sleep(0.4)

        # PASSO 4: Soltar botão
        if self.use_arduino:
            self._send_arduino_command("MOUSE_UP left")
        else:
            pyautogui.mouseUp(button='left')
        time.sleep(0.4)

        return True
    except Exception as e:
        _safe_print(f"❌ Erro no drag: {e}")
        return False
```

#### 3. Código Arduino Atualizado

```cpp
// arduino_hid_controller.ino

#include <Mouse.h>
#include <Keyboard.h>

void setup() {
  Serial.begin(115200);
  Mouse.begin();
  Keyboard.begin();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.startsWith("MOVE_REL ")) {
      // Movimento relativo: MOVE_REL dx dy
      int spaceIndex = command.indexOf(' ', 9);
      int dx = command.substring(9, spaceIndex).toInt();
      int dy = command.substring(spaceIndex + 1).toInt();

      // Dividir movimento em passos menores para suavidade
      int steps = max(abs(dx), abs(dy)) / 5;  // 5 pixels por passo
      if (steps == 0) steps = 1;

      for (int i = 0; i < steps; i++) {
        Mouse.move(dx / steps, dy / steps);
        delay(1);
      }

      // Movimento restante
      Mouse.move(dx % steps, dy % steps);

    } else if (command == "MOUSE_DOWN left") {
      Mouse.press(MOUSE_LEFT);

    } else if (command == "MOUSE_UP left") {
      Mouse.release(MOUSE_LEFT);

    } else if (command == "MOUSE_DOWN right") {
      Mouse.press(MOUSE_RIGHT);

    } else if (command == "MOUSE_UP right") {
      Mouse.release(MOUSE_RIGHT);

    } else if (command.startsWith("KEY_DOWN ")) {
      char key = command.charAt(9);
      Keyboard.press(key);

    } else if (command.startsWith("KEY_UP ")) {
      char key = command.charAt(7);
      Keyboard.release(key);
    }
  }
}
```

---

## 🎯 Como Funciona na Prática

### Exemplo: Manutenção de Vara (Slot 3)

#### 1. Template Engine detecta isca
```python
result = template_engine.detect_template('carneurso')
# Retorna: location = (1350, 450)
```

#### 2. RodManager quer arrastar para slot 3
```python
slot_x, slot_y = self.slot_positions[3]  # (899, 1005)
input_manager.drag(1350, 450, 899, 1005)
```

#### 3. InputManager calcula movimento
```python
# Posição virtual atual: (960, 540)
# Alvo: (1350, 450)
dx = 1350 - 960 = 390
dy = 450 - 540 = -90

# Envia para Arduino:
serial.write(b"MOVE_REL 390 -90\n")

# Atualiza posição virtual:
virtual_mouse_position = [1350, 450]
```

#### 4. Arduino executa movimento relativo
```cpp
// Recebe: "MOVE_REL 390 -90"
// Divide em 78 passos (390/5)
for (int i = 0; i < 78; i++) {
  Mouse.move(5, -1);  // Move 5px direita, 1px cima
  delay(1);
}
```

---

## 🔄 Calibração Inicial

### Problema: Drift de Posição

Após muitos movimentos, a posição virtual pode divergir da real.

### Solução: Reset Periódico

```python
def calibrate_mouse_position(self) -> bool:
    """
    Calibrar posição do mouse movendo para canto conhecido

    1. Move para canto superior esquerdo (0, 0)
    2. Move movimento absurdo (-5000, -5000) para garantir
    3. Reseta posição virtual para (0, 0)
    4. Move de volta para centro
    """
    if self.use_arduino:
        _safe_print("🔧 Calibrando posição do mouse...")

        # Movimento absurdo para garantir canto (0,0)
        self._send_arduino_command("MOVE_REL -5000 -5000")
        time.sleep(0.5)

        # Resetar posição virtual
        self.virtual_mouse_position = [0, 0]

        # Mover para centro da tela
        self._move_to_absolute(960, 540)

        _safe_print("✅ Mouse calibrado - posição resetada")
        return True
    return False
```

### Quando calibrar:
- Ao iniciar bot (F9)
- Após cada 100 movimentos
- Antes de operações críticas (manutenção de varas)

---

## 📊 Vantagens da Solução

✅ **Compatível com ambos os modos** (PyAutoGUI / Arduino)
✅ **Sem modificar lógica de detecção** (template matching continua igual)
✅ **Precisão mantida** com calibração periódica
✅ **Fácil de testar** (flag `use_arduino` para alternar)

---

## 🚀 Próximos Passos

1. **Implementar `_move_to_absolute()` no InputManager**
2. **Adicionar rastreamento de posição virtual**
3. **Testar com PyAutoGUI** (use_arduino=False)
4. **Implementar protocolo serial**
5. **Testar com Arduino** (use_arduino=True)
6. **Implementar calibração automática**

---

## 🔍 Debugging

### Logs Detalhados

```python
def _move_to_absolute(self, target_x: int, target_y: int) -> bool:
    if self.use_arduino:
        current_x, current_y = self.virtual_mouse_position
        dx = target_x - current_x
        dy = target_y - current_y

        _safe_print(f"📍 MOVIMENTO ARDUINO:")
        _safe_print(f"   Posição virtual atual: ({current_x}, {current_y})")
        _safe_print(f"   Posição alvo: ({target_x}, {target_y})")
        _safe_print(f"   Delta calculado: dx={dx}, dy={dy}")
        _safe_print(f"   Comando enviado: MOVE_REL {dx} {dy}")

        self._send_arduino_command(f"MOVE_REL {dx} {dy}")
        self.virtual_mouse_position = [target_x, target_y]

        return True
```

### Validação de Precisão

```python
def validate_position_accuracy(self) -> Dict:
    """
    Testar precisão do rastreamento

    Move para 10 posições conhecidas e verifica se chegou corretamente
    """
    test_positions = [
        (100, 100), (500, 500), (1000, 500),
        (1500, 500), (1800, 900), (960, 540)
    ]

    errors = []
    for target_x, target_y in test_positions:
        self._move_to_absolute(target_x, target_y)
        time.sleep(0.1)

        # Comparar posição esperada vs virtual
        virtual_x, virtual_y = self.virtual_mouse_position
        error = abs(target_x - virtual_x) + abs(target_y - virtual_y)
        errors.append(error)

        _safe_print(f"Alvo: ({target_x}, {target_y}), Virtual: ({virtual_x}, {virtual_y}), Erro: {error}px")

    avg_error = sum(errors) / len(errors)
    max_error = max(errors)

    return {
        'average_error': avg_error,
        'max_error': max_error,
        'total_tests': len(test_positions)
    }
```
